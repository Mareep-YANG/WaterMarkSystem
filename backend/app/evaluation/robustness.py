from typing import Dict, Any

from datasets import Dataset

from .attacker import TextWatermarkAttacker
from  ..watermarks.base import WatermarkBase


def evaluation_robustness(watermark: WatermarkBase, attacker: TextWatermarkAttacker, dataset: Dataset) -> Dict[
    str, Any]:
    total_samples = 0
    watermark_detected_before_attack = 0
    watermark_detected_after_attack = 0
    attack_successes = 0

    # 遍历数据集
    for data in dataset:
        total_samples += 1

        # 获取文本
        prompt = data["prompt"]

        # 嵌入水印
        watermarked_text = watermark.embed(prompt)

        # 检测水印
        first_detection_result = watermark.detect(watermarked_text)
        watermark_present_before = first_detection_result["detected"]

        # 执行攻击
        attacked_text = attacker.attack(watermarked_text)

        # 检测水印
        second_detection_result = watermark.detect(attacked_text)
        watermark_present_after = second_detection_result["detected"]

        # 更新计数
        if watermark_present_before:
            watermark_detected_before_attack += 1
            if not watermark_present_after:
                attack_successes += 1

        if watermark_present_after:
            watermark_detected_after_attack += 1

    # 计算相关指标
    watermark_detection_rate_before_attack = watermark_detected_before_attack / total_samples if total_samples > 0 else 0.0
    watermark_detection_rate_after_attack = watermark_detected_after_attack / total_samples if total_samples > 0 else 0.0
    attack_success_rate = attack_successes / watermark_detected_before_attack if watermark_detected_before_attack > 0 else 0.0

    return {
        "total_samples": total_samples,
        "watermark_detected_before_attack": watermark_detected_before_attack,
        "watermark_detected_after_attack": watermark_detected_after_attack,
        "attack_successes": attack_successes,
        "watermark_detection_rate_before_attack": watermark_detection_rate_before_attack,
        "watermark_detection_rate_after_attack": watermark_detection_rate_after_attack,
        "attack_success_rate": attack_success_rate
    }


