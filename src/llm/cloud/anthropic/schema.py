from dataclasses import dataclass
from typing import Literal

from src.llm.schema import ModelConfig


# todo: add thinking
@dataclass(kw_only=True)
class AnthropicConfig(ModelConfig):
    model_name: Literal[
        "claude-opus-4-1",
        "claude-sonnet-4-0",
    ]
