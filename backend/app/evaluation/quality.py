from collections import Counter
from typing import Dict, Any, List

import nltk
import numpy as np
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu

from app.watermarks import WatermarkBase
from datasets import Dataset

def evaluation_quality(watermark: WatermarkBase,  dataset: Dataset,metrics: List[str]) -> Dict[str, Any]:
    results = {}

    # 确定文本字段名称
    text_field = None
    for field in ["text", "content", "input","prompt"]:
        if field in dataset.column_names:
            text_field = field
            break

    if text_field is None:
        return {}

    # 将水印应用到数据集中的所有文本
    original_texts = dataset[text_field]
    watermarked_texts = []

    for text in original_texts:
        try:
            watermarked_text = watermark.embed(text)
            watermarked_texts.append(watermarked_text)
        except Exception as e:
            watermarked_texts.append(text)  # 如果水印失败，使用原始文本

    # 计算每个请求的指标
    if "PPL" in metrics:
        try:
            results["PPL"] = calculate_perplexity(watermarked_texts)
        except Exception as e:
            results["PPL"] = None

    if "Log Diversity" in metrics:
        try:
            results["Log Diversity"] = calculate_log_diversity(watermarked_texts)
        except Exception as e:
            results["Log Diversity"] = None

    if "BLEU" in metrics:
        try:
            results["BLEU"] = calculate_bleu(original_texts, watermarked_texts)
        except Exception as e:
            results["BLEU"] = None

    return results


def calculate_perplexity(texts: List[str]) -> float:
    """
    使用预训练语言模型计算文本困惑度。

    Args:
        texts: 要评估的文本列表

    Returns:
        平均困惑度分数
    """
    try:
        from transformers import GPT2LMHeadModel, GPT2Tokenizer
        import torch

        # 加载模型和分词器
        tokenizer = GPT2Tokenizer.from_pretrained('distilgpt2')
        model = GPT2LMHeadModel.from_pretrained('distilgpt2')
        model.eval()

        total_ppl = 0.0
        count = 0

        with torch.no_grad():
            for text in texts:
                # 跳过空文本
                if not text.strip():
                    continue

                # 对输入文本进行分词（对长文本进行截断）
                encodings = tokenizer(text, return_tensors='pt', truncation=True, max_length=1024)
                input_ids = encodings.input_ids

                # 获取模型输出
                outputs = model(input_ids, labels=input_ids)
                loss = outputs.loss

                # 从损失计算困惑度
                ppl = torch.exp(loss).item()
                total_ppl += ppl
                count += 1

        # 返回平均困惑度
        return total_ppl / count if count > 0 else None

    except ImportError:
        return None


def calculate_log_diversity(texts: List[str]) -> float:
    """
    计算文本中词语的对数多样性（熵）。

    Args:
        texts: 要评估的文本列表

    Returns:
        对数多样性分数
    """
    # 确保已下载NLTK包
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)

    # 对所有文本进行分词
    all_words = []
    for text in texts:
        if not text.strip():
            continue
        tokens = nltk.word_tokenize(text.lower())
        all_words.extend(tokens)

    # 统计词频
    word_counts = Counter(all_words)
    total_words = len(all_words)

    # 计算熵/多样性
    log_diversity = 0.0
    if total_words > 0:
        for word, count in word_counts.items():
            probability = count / total_words
            log_diversity -= probability * np.log2(probability)

    return log_diversity


def calculate_bleu(original_texts: List[str], watermarked_texts: List[str]) -> float:
    """
    计算原始文本和水印文本之间的平均BLEU分数。

    Args:
        original_texts: 原始文本列表
        watermarked_texts: 水印文本列表

    Returns:
        平均BLEU分数
    """
    # 确保已下载NLTK包
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)

    smoother = SmoothingFunction().method1
    total_bleu = 0.0
    count = 0

    for original, watermarked in zip(original_texts, watermarked_texts):
        # 跳过空文本
        if not original.strip() or not watermarked.strip():
            continue

        # 对句子进行分词
        reference = [nltk.word_tokenize(original.lower())]
        candidate = nltk.word_tokenize(watermarked.lower())

        # 跳过空或过短的候选文本
        if len(candidate) < 2:
            continue

        # 计算BLEU分数
        bleu = sentence_bleu(reference, candidate, smoothing_function=smoother)
        total_bleu += bleu
        count += 1

    # 返回平均BLEU分数
    return total_bleu / count if count > 0 else None