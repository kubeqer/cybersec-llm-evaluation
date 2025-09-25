from dataclasses import dataclass
from typing import Literal

from src.llm.schema import ModelConfig


# todo: add thinking, tools web search,
@dataclass(kw_only=True)
class GoogleConfig(ModelConfig):
    model_name: Literal["gemini-2.5-pro", "gemini-2.5-flash"]
