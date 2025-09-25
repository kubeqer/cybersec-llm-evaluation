from dataclasses import dataclass
from typing import Literal

from src.llm.schema import ModelConfig


# todo: add tools web search, thinking
@dataclass(kw_only=True)
class OpenAIConfig(ModelConfig):
    model_name: Literal["gpt-5-nano", "gpt-5-mini", "gpt-5", "gpt-5-codex"]
