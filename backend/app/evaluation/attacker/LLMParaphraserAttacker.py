from typing import Dict, Any

from openai import OpenAI

from app.core.Configurable import configurable, ConfigField
from app.evaluation.attacker.TextWatermarkAttacker import TextWatermarkAttacker


class LLMParaphraserAttacker(TextWatermarkAttacker):
    """Paraphrase a text using the GPT model."""
    provider = ConfigField()
    model = ConfigField()
    prompt = ConfigField()
    api_key = ConfigField()
    base_url = ConfigField()
    def __init__(self, provider="openai", model="gpt-3.5-turbo", prompt="Please paraphrase the following text: ",
                 api_key=None, base_url=None):
        """
            Initialize the GPT paraphraser.
        """
        self.provider = provider
        self.model = model
        self.prompt = prompt
        self.api_key = api_key
        self.base_url = base_url



    def attack(self, text: str, **kwargs) -> str:
        if self.provider == "openai":
            openai_client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            completion = openai_client.chat.completions.create(
                messages=[
                    {'role': 'system', 'content': "Your are a helpful assistant to rewrite the text."},
                    {'role': 'user', 'content': self.prompt + text},
                ],
                model=self.model,  # 调用的模型
            )
            paraphrased_text = completion.choices[0].message.content
            return paraphrased_text
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
