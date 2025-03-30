import torch
import hashlib
import torch.nn.functional as F
from math import sqrt
from typing import Any, Dict, Union, Tuple

from transformers import LogitsProcessor

from app.models.llm import llm_service
from app.models.GenerationConfig import GenerationConfig
from app.watermarks import LogitsWatermark


class DipProcessor(LogitsProcessor):
    """Logits processor for watermarking"""

    def __init__(self, watermark_instance):
        self.watermark = watermark_instance

    def _apply_watermark(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> Tuple[
        torch.FloatTensor, torch.FloatTensor]:
        """Apply watermark to the scores."""
        mask, seeds = self.watermark.get_seed_for_cipher(input_ids)

        rng = [
            torch.Generator(device=scores.device).manual_seed(seed) for seed in seeds
        ]
        mask = torch.tensor(mask, device=scores.device)
        shuffle = self.watermark.from_random(
            rng, scores.size(1)
        )

        reweighted_scores = self.watermark.reweight_logits(shuffle, scores)

        return mask, reweighted_scores

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:
        """Process logits to add watermark."""
        if input_ids.shape[-1] < self.watermark.prefix_length:
            return scores

        mask, reweighted_scores = self._apply_watermark(input_ids, scores)

        if self.watermark.ignore_history_generation:
            return reweighted_scores
        else:
            return torch.where(mask[:, None], scores, reweighted_scores)


class DIPWatermark(LogitsWatermark):
    """DiP watermarking algorithm implementation"""

    def __init__(self, key: str,gamma=0.5, alpha=0.45, ignore_history_generation=False,
                 ignore_history_detection=False, z_threshold=1.513, prefix_length=5):
        """Initialize the DiP watermark parameters"""
        self.gamma = gamma
        self.alpha = alpha
        self.ignore_history_generation = ignore_history_generation
        self.ignore_history_detection = ignore_history_detection
        self.z_threshold = z_threshold
        self.prefix_length = prefix_length
        self.cc_history = set()
        self.state_indicator = 1  # 0 for generation, 1 for detection
        self.key = key
        llm_service.clear_processors()
        llm_service.add_processor(DipProcessor(self))
        self.generation_config = GenerationConfig(
            logits_processor=llm_service.processors,
            min_length=230,
            max_length=500,
            no_repeat_ngram_size=4
        )
    def embed(self, prompt: str) -> str:
        """Embed watermark into logits"""
        # 生成模式
        self.state_indicator = 0
        # encode prompt
        encoded_prompt = llm_service.tokenizer(prompt, return_tensors="pt", add_special_tokens=True).to(
            llm_service.device)
        # 生成水印文本
        encoded_watermarked_text = llm_service.model.generate(**encoded_prompt,**self.generation_config.to_dict())
        # 解码
        watermarked_text = llm_service.tokenizer.batch_decode(encoded_watermarked_text, skip_special_tokens=True)[0]
        # 清除记录
        self.cc_history.clear()
        return watermarked_text

    def detect(self, text: str,  **kwargs) -> Dict[str, Any]:
        """Detect watermark in text"""
        self.state_indicator = 1  # Set to detection mode

        # Get tokenizer from kwargs

        encoded_text = llm_service.tokenizer(text, return_tensors="pt", add_special_tokens=False)["input_ids"][0].to(llm_service.device)
        # Compute z-score using a utility method
        z_score, _ = self.score_sequence(encoded_text)
        is_watermarked = z_score > self.z_threshold
        # Clear the history
        self.cc_history.clear()
        return {
            "detected": is_watermarked,
            "confidence": z_score,
        }

    def visualize(self, text: str, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """Visualize watermark detection results"""
        tokenizer = llm_service.tokenizer

        # Tokenize text
        encoded_text = tokenizer(text, return_tensors="pt", add_special_tokens=False)["input_ids"][0].to(
            llm_service.device)

        # Get tokens
        decoded_tokens = []
        for token_id in encoded_text:
            token = tokenizer.decode(token_id.item())
            decoded_tokens.append(token)

        # Use the green_token_flags from detection result
        highlight_values = detection_result.get("green_token_flags", [])

        return {
            "tokens": decoded_tokens,
            "highlight_values": highlight_values
        } #TODO 重构

    def get_processor(self, key: str) -> LogitsProcessor:
        """Return a logits processor for this watermark"""
        return DipProcessor(self)

    # Helper methods
    def _get_rng_seed(self, context_code: any) -> int:
        """Get the random seed from the given context code and private key."""
        if (
                (not self.ignore_history_generation and self.state_indicator == 0) or
                (not self.ignore_history_detection and self.state_indicator == 1)
        ):
            self.cc_history.add(context_code)

        m = hashlib.sha256()
        m.update(context_code)
     #   m.update(self.key.encode('utf-8'))

        full_hash = m.digest()
        seed = int.from_bytes(full_hash, "big") % (2 ** 32 - 1)
        return seed

    def _extract_context_code(self, context: torch.LongTensor) -> bytes:
        """Extract context code from the given context."""
        if self.prefix_length == 0:
            return context.detach().cpu().numpy().tobytes()
        else:
            return context[-self.prefix_length:].detach().cpu().numpy().tobytes()

    def from_random(self, rng: Union[torch.Generator, list[torch.Generator]], vocab_size: int) -> torch.LongTensor:
        """Generate a permutation from the random number generator."""
        if isinstance(rng, list):
            batch_size = len(rng)
            shuffle = torch.stack(
                [
                    torch.randperm(vocab_size, generator=rng[i], device=rng[i].device)
                    for i in range(batch_size)
                ]
            )
        else:
            shuffle = torch.randperm(vocab_size, generator=rng, device=rng.device)
        return shuffle

    def reweight_logits(self, shuffle: torch.LongTensor, p_logits: torch.FloatTensor) -> torch.FloatTensor:
        """Reweight the logits using the shuffle and alpha."""
        unshuffle = torch.argsort(shuffle, dim=-1)

        s_p_logits = torch.gather(p_logits, -1, shuffle)
        s_log_cumsum = torch.logcumsumexp(s_p_logits, dim=-1)

        # normalize the log_cumsum to force the last element to be 0
        s_log_cumsum = s_log_cumsum - s_log_cumsum[..., -1:]
        s_cumsum = torch.exp(s_log_cumsum)
        s_p = F.softmax(s_p_logits, dim=-1)

        boundary_1 = torch.argmax((s_cumsum > self.alpha).to(torch.int), dim=-1, keepdim=True)
        p_boundary_1 = torch.gather(s_p, -1, boundary_1)
        portion_in_right_1 = (torch.gather(s_cumsum, -1, boundary_1) - self.alpha) / p_boundary_1
        portion_in_right_1 = torch.clamp(portion_in_right_1, 0, 1)
        s_all_portion_in_right_1 = (s_cumsum > self.alpha).type_as(p_logits)
        s_all_portion_in_right_1.scatter_(-1, boundary_1, portion_in_right_1)

        boundary_2 = torch.argmax((s_cumsum > (1 - self.alpha)).to(torch.int), dim=-1, keepdim=True)
        p_boundary_2 = torch.gather(s_p, -1, boundary_2)
        portion_in_right_2 = (torch.gather(s_cumsum, -1, boundary_2) - (1 - self.alpha)) / p_boundary_2
        portion_in_right_2 = torch.clamp(portion_in_right_2, 0, 1)
        s_all_portion_in_right_2 = (s_cumsum > (1 - self.alpha)).type_as(p_logits)
        s_all_portion_in_right_2.scatter_(-1, boundary_2, portion_in_right_2)

        s_all_portion_in_right = s_all_portion_in_right_2 / 2 + s_all_portion_in_right_1 / 2
        s_shift_logits = torch.log(s_all_portion_in_right)
        shift_logits = torch.gather(s_shift_logits, -1, unshuffle)

        return p_logits + shift_logits

    def get_seed_for_cipher(self, input_ids: torch.LongTensor) -> Tuple[torch.FloatTensor, torch.FloatTensor]:
        """Get the mask and seeds for the cipher."""
        batch_size = input_ids.size(0)
        context_codes = [
            self._extract_context_code(input_ids[i]) for i in range(batch_size)
        ]

        mask, seeds = zip(
            *[
                (context_code in self.cc_history, self._get_rng_seed(context_code))
                for context_code in context_codes
            ]
        )

        return mask, seeds

    def _get_green_token_quantile(self, input_ids: torch.LongTensor, vocab_size, current_token):
        """Get the vocab quantile of current token"""
        mask, seeds = self.get_seed_for_cipher(input_ids.unsqueeze(0))

        rng = [
            torch.Generator(device=input_ids.device).manual_seed(seed) for seed in seeds
        ]

        mask = torch.tensor(mask, device=input_ids.device)
        shuffle = self.from_random(
            rng, vocab_size
        )

        token_quantile = [(torch.where(shuffle[0] == current_token)[0] + 1) / vocab_size]
        return token_quantile, mask

    def _get_dip_score(self, input_ids: torch.LongTensor, vocab_size):
        """Get the DiP score of the input_ids"""
        scores = torch.zeros(input_ids.shape, device=input_ids.device)

        for i in range(input_ids.shape[-1] - 1):
            pre = input_ids[: i + 1]
            cur = input_ids[i + 1]
            token_quantile, mask = self._get_green_token_quantile(pre, vocab_size, cur)
            # if the current token is in the history and ignore_history_detection is False, set the score to -1
            if not self.ignore_history_detection and mask[0]:
                scores[i + 1] = -1
            else:
                scores[i + 1] = torch.stack(token_quantile).reshape(-1)

        return scores

    def score_sequence(self, input_ids: torch.LongTensor) -> tuple[float, list[int]]:
        """Score the input_ids and return z_score and green_token_flags."""
        score = self._get_dip_score(input_ids, 50272)

        green_tokens = torch.sum(score >= self.gamma, dim=-1, keepdim=False)
        green_token_flags = torch.zeros_like(score)
        condition_indices = torch.nonzero(score >= self.gamma, as_tuple=False).reshape(-1)
        green_token_flags[condition_indices] = 1
        green_token_flags[:self.prefix_length] = -1

        # Use two different ways to calculate z_score depending on whether to ignore history
        if not self.ignore_history_detection:
            ignored_indices = torch.nonzero(score == -1, as_tuple=False).reshape(-1)

            # Visualize the ignored tokens as ignored
            green_token_flags[ignored_indices] = -1

            # Calculate z_score using the sequence length after ignoring the ignored tokens
            sequence_length_for_calculation = input_ids.size(-1) - ignored_indices.size(0)
            z_score = (green_tokens - (1 - self.gamma) * sequence_length_for_calculation) / sqrt(
                sequence_length_for_calculation)
        else:
            z_score = (green_tokens - (1 - self.gamma) * input_ids.size(-1)) / sqrt(input_ids.size(-1))

        return z_score.item(), green_token_flags.tolist()
