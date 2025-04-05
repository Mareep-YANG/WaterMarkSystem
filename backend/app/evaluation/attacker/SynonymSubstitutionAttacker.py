import random
from typing import Any, Dict

import nltk
from nltk.corpus import wordnet

from app.evaluation.attacker.TextWatermarkAttacker import TextWatermarkAttacker


class SynonymSubstitutionAttacker(TextWatermarkAttacker):
	"""Randomly replace words with synonyms from WordNet."""
	
	def __init__(self, config: Dict[str, Any] = None):
		"""
			Initialize the synonym substitution editor.
		"""
		super().__init__(config)
		nltk.download('wordnet')
		self.ratio = self.config["ratio"]
	
	def attack(self, text: str, **kwargs) -> str:
		"""Randomly replace words with synonyms from WordNet."""
		
		words = text.split()
		num_words = len(words)
		
		# Dictionary to cache synonyms for words
		word_synonyms = {}
		
		# First pass: Identify replaceable words and cache their synonyms
		replaceable_indices = []
		for i, word in enumerate(words):
			if word not in word_synonyms:
				synonyms = [syn for syn in wordnet.synsets(word) if len(syn.lemmas()) > 1]
				word_synonyms[word] = synonyms
			if word_synonyms[word]:
				replaceable_indices.append(i)
		
		# Calculate the number of words to replace
		num_to_replace = min(int(self.ratio * num_words), len(replaceable_indices))
		
		# Randomly select words to replace
		if num_to_replace > 0:
			indices_to_replace = random.sample(replaceable_indices, num_to_replace)
			
			# Perform replacement
			for i in indices_to_replace:
				synonyms = word_synonyms[words[i]]
				chosen_syn = random.choice(synonyms)
				new_word = random.choice(chosen_syn.lemmas()[1:]).name().replace('_', ' ')
				words[i] = new_word
		
		# Join the words back into a single string
		replaced_text = ' '.join(words)
		
		return replaced_text
