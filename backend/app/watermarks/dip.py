import torch
import hashlib
import torch.nn.functional as F
from math import sqrt
from typing import Any, Dict

from app.core import llm_service
from app.watermarks import WatermarkBase, LogitsWatermark


class WatermarkLogitsProcessor:
    """Logits processor for watermarking"""

    def __init__(self, watermark_instance, key):
        self.watermark = watermark_instance
        self.key = key

    def __call__(self, input_ids, scores):
        return self.watermark.embed(scores, self.key, input_ids=input_ids)


class DIPWatermark(LogitsWatermark):
    """DiP watermarking algorithm implementation"""

    def __init__(self, gamma=0.5, alpha=0.45, ignore_history_generation=False,
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

    def embed(self, logits: Any, key: str, input_ids: Any) -> Any:
        """Embed watermark into logits"""
        if input_ids.shape[-1] < self.prefix_length:
            return logits

        hash_key = key.encode() if isinstance(key, str) else key

        # Extract context and get mask/seeds
        batch_size = input_ids.size(0)
        context_codes = [self._extract_context_code(input_ids[i], hash_key) for i in range(batch_size)]

        mask, seeds = zip(*[(context_code in self.cc_history, self._get_rng_seed(context_code, hash_key))
                            for context_code in context_codes])

        # Generate permutation
        rng = [torch.Generator(device=logits.device).manual_seed(seed) for seed in seeds]
        mask = torch.tensor(mask, device=logits.device)
        shuffle = self._from_random(rng, logits.size(1))

        # Apply watermark
        reweighted_logits = self._reweight_logits(shuffle, logits)

        if self.ignore_history_generation:
            return reweighted_logits
        else:
            return torch.where(mask[:, None], logits, reweighted_logits)

    def detect(self, text: str, key: str, **kwargs) -> Dict[str, Any]:
        """Detect watermark in text"""
        self.state_indicator = 1  # Set to detection mode

        # Get tokenizer from kwargs
        tokenizer = llm_service.tokenizer

        # Tokenize text
        encoded_text = tokenizer(text, return_tensors="pt", add_special_tokens=False)["input_ids"][0].to(llm_service.device)

        # Calculate z-score
        hash_key = key.encode() if isinstance(key, str) else key
        z_score, green_token_flags = self._score_sequence(encoded_text, len(tokenizer), hash_key)

        # Clear history
        self.cc_history.clear()

        # Return detection results
        is_watermarked = z_score > self.z_threshold
        return {
            "detected": is_watermarked,
            "confidence": z_score,
            "details":{
                "green_token_flags": green_token_flags
            }

        }

    def visualize(self, text: str, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """Visualize watermark detection results"""
        tokenizer = llm_service.tokenizer

        # Tokenize text
        encoded_text = tokenizer(text, return_tensors="pt", add_special_tokens=False)["input_ids"][0].to(llm_service.device)

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
        }

    def get_processor(self, key: str) -> 'WatermarkLogitsProcessor':
        """Return a logits processor for this watermark"""
        return WatermarkLogitsProcessor(self, key)

    # Helper methods
    def _extract_context_code(self, context, hash_key):
        """Extract context code from input"""
        if self.prefix_length == 0:
            return context.detach().cpu().numpy().tobytes()
        else:
            return context[-self.prefix_length:].detach().cpu().numpy().tobytes()

    def _get_rng_seed(self, context_code, hash_key):
        """Get random seed from context and key"""
        if ((not self.ignore_history_generation and self.state_indicator == 0) or
                (not self.ignore_history_detection and self.state_indicator == 1)):
            self.cc_history.add(context_code)

        m = hashlib.sha256()
        m.update(context_code)
        m.update(hash_key)

        full_hash = m.digest()
        seed = int.from_bytes(full_hash, "big") % (2 ** 32 - 1)
        return seed

    def _from_random(self, rng, vocab_size):
        """Generate permutation from random number generator"""
        if isinstance(rng, list):
            batch_size = len(rng)
            shuffle = torch.stack(
                [torch.randperm(vocab_size, generator=rng[i], device=rng[i].device)
                 for i in range(batch_size)]
            )
        else:
            shuffle = torch.randperm(vocab_size, generator=rng, device=rng.device)
        return shuffle

    def _reweight_logits(self, shuffle, p_logits):
        """Reweight logits using shuffle and alpha"""
        unshuffle = torch.argsort(shuffle, dim=-1)

        s_p_logits = torch.gather(p_logits, -1, shuffle)
        s_log_cumsum = torch.logcumsumexp(s_p_logits, dim=-1)

        # Normalize the log_cumsum
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

    def _get_green_token_quantile(self, input_ids, vocab_size, current_token, hash_key):
        """Get vocab quantile of current token"""
        mask, seeds = self._get_seed_for_cipher(input_ids.unsqueeze(0), hash_key)

        rng = [torch.Generator(device=input_ids.device).manual_seed(seed) for seed in seeds]
        mask = torch.tensor(mask, device=input_ids.device)
        shuffle = self._from_random(rng, vocab_size)

        token_quantile = [(torch.where(shuffle[0] == current_token)[0] + 1) / vocab_size]
        return token_quantile, mask

    def _get_seed_for_cipher(self, input_ids, hash_key):
        """Get mask and seeds for cipher"""
        batch_size = input_ids.size(0)
        context_codes = [self._extract_context_code(input_ids[i], hash_key) for i in range(batch_size)]

        mask, seeds = zip(*[(context_code in self.cc_history, self._get_rng_seed(context_code, hash_key))
                            for context_code in context_codes])

        return mask, seeds

    def _get_dip_score(self, input_ids, vocab_size, hash_key):
        """Get DiP score of input_ids"""
        scores = torch.zeros(input_ids.shape, device=input_ids.device)

        for i in range(input_ids.shape[-1] - 1):
            pre = input_ids[:i + 1]
            cur = input_ids[i + 1]
            token_quantile, mask = self._get_green_token_quantile(pre, vocab_size, cur, hash_key)

            # If current token is in history and ignore_history_detection is False, set score to -1
            if not self.ignore_history_detection and mask[0]:
                scores[i + 1] = -1
            else:
                scores[i + 1] = torch.stack(token_quantile).reshape(-1)

        return scores

    def _score_sequence(self, input_ids, vocab_size, hash_key):
        """Score input_ids and return z_score and green_token_flags"""
        score = self._get_dip_score(input_ids, vocab_size, hash_key)

        green_tokens = torch.sum(score >= self.gamma, dim=-1, keepdim=False)
        green_token_flags = torch.zeros_like(score)
        condition_indices = torch.nonzero(score >= self.gamma, as_tuple=False).reshape(-1)
        green_token_flags[condition_indices] = 1
        green_token_flags[:self.prefix_length] = -1

        # Calculate z-score based on whether to ignore history
        if not self.ignore_history_detection:
            ignored_indices = torch.nonzero(score == -1, as_tuple=False).reshape(-1)

            # Mark ignored tokens
            green_token_flags[ignored_indices] = -1

            # Calculate z-score excluding ignored tokens
            sequence_length_for_calculation = input_ids.size(-1) - ignored_indices.size(0)
            z_score = (green_tokens - (1 - self.gamma) * sequence_length_for_calculation) / sqrt(
                sequence_length_for_calculation)
        else:
            z_score = (green_tokens - (1 - self.gamma) * input_ids.size(-1)) / sqrt(input_ids.size(-1))

        return z_score.item(), green_token_flags.tolist()
