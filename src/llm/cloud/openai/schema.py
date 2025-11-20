from dataclasses import dataclass
from typing import Literal

from src.llm.schema import ModelConfig


@dataclass(kw_only=True)
class OpenAIConfig(ModelConfig):
    model_name: Literal["gpt-5-nano", "gpt-5", "gpt-5.1-codex", "gpt-5.1", "gpt-5-pro"]
    max_tokens: int = 1
