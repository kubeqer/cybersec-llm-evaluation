from dataclasses import dataclass
from typing import Literal

from src.llm.schema import ModelConfig


@dataclass(kw_only=True)
class GrokConfig(ModelConfig):
    model_name: Literal["grok-4-fast-reasoning", "grok-code-fast-1"]
    max_tokens: int = 4096
    temperature: float = 0.0
