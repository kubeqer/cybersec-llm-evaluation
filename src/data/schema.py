from dataclasses import dataclass
from typing import TypedDict


@dataclass
class InputAnswerDict(TypedDict):
    input: str
    answer: int | str
