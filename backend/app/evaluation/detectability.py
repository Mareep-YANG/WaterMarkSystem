from typing import Dict, Any

from datasets import Dataset

from app.evaluation.attacker import TextWatermarkAttacker
from app.watermarks import WatermarkBase


def evaluation_detectability(watermark: WatermarkBase,  dataset: Dataset) -> Dict[
    str, Any]:
    pass
