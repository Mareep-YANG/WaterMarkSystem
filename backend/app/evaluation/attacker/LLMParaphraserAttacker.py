from typing import Any, Dict

from openai import OpenAI

from app.evaluation.attacker.TextWatermarkAttacker import TextWatermarkAttacker


class LLMParaphraserAttacker(TextWatermarkAttacker):
	"""Paraphrase a text using the GPT model."""
	
	def __init__(self, config: Dict[str, Any] = None):
		"""
			Initialize the GPT paraphraser.
		"""
		super().__init__(config)
		self.provider = config["provider"]
		self.model = config["model"]
		self.prompt = config["prompt"]
		self.api_key = config["api_key"]
		self.base_url = config["base_url"]
	
	def attack(self, text: str, **kwargs) -> str:
		if self.provider == "openai":
			openai_client = OpenAI(api_key=self.api_key, base_url=self.base_url)
			completion = openai_client.chat.completions.create(
				messages=[
					{
						'role': 'system',
						'content': "Your are a helpful assistant to rewrite the text."
					},
					{'role': 'user', 'content': self.prompt + text},
				],
				model=self.model,  # 调用的模型
			)
			paraphrased_text = completion.choices[0].message.content
			return paraphrased_text
		else:
			raise ValueError(f"Unsupported provider: {self.provider}")
