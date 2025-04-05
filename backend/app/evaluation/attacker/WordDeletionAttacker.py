import random
from typing import Any, Dict

from app.evaluation.attacker import TextWatermarkAttacker


class WordDeletionAttacker(TextWatermarkAttacker):
	"""Delete words randomly from the text."""
	
	def __init__(self, config: Dict[str, Any] = None):
		"""
			Initialize the word deletion editor.
		"""
		super().__init__(config)
		self.ratio = self.config["ratio"]
	
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
