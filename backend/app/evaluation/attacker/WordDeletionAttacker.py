import random
from typing import Dict, Any

from app.core.Configurable import ConfigField
from app.evaluation.attacker import TextWatermarkAttacker


class WordDeletionAttacker(TextWatermarkAttacker):
    """Delete words randomly from the text."""
    ratio = ConfigField()
    def __init__(self, ratio: float = 0.1):
        """
            Initialize the word deletion editor.
        """

        self.ratio = ratio

    def attack(self, text: str, **kwargs) -> str:
        # Handle empty string input
        if not text:
            return text

        # Split the text into words and randomly delete each word based on the ratio
        word_list = text.split()
        edited_words = [word for word in word_list if random.random() >= self.ratio]

        # Join the words back into a single string
        deleted_text = ' '.join(edited_words)

        return deleted_text
