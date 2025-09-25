from dataclasses import dataclass
from typing import Literal

from src.llm.schema import ModelConfig


@dataclass(kw_only=True)
class HFConfig(ModelConfig):
    model_name: str
    provider: Literal[
        "black-forest-labs",
        "cerebras",
        "cohere",
        "fal-ai",
        "featherless-ai",
        "fireworks-ai",
        "groq",
        "hf-inference",
        "hyperbolic",
        "nebius",
        "novita",
        "nscale",
        "openai",
        "publicai",
        "replicate",
        "sambanova",
        "scaleway",
        "together",
        "auto",
    ] = "auto"
