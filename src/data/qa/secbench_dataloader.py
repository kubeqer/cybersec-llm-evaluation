import json

import pandas as pd
import requests

from src.core.decorators.error_handling import error_handling
from src.core.decorators.log_calls import log_calls
from src.data.schema import InputAnswerDict


class SecBenchDataLoader:
    JSONL_URL = "https://huggingface.co/datasets/secbench-hf/SecBench/resolve/main/data/MCQs_2730.jsonl"

    @log_calls(level="INFO")
    @error_handling(default=[], reraise=True)
    def load(self) -> list[InputAnswerDict]:
        response = requests.get(self.JSONL_URL)
        response.raise_for_status()
        data = []
        for line in response.text.strip().split("\n"):
            if line.strip():
                data.append(json.loads(line))
        df = pd.DataFrame(data)
        result: list[InputAnswerDict] = self._preprocess(df)
        return result

    @log_calls(level="INFO")
    @error_handling(default=[], reraise=True)
    def _preprocess(self, df: pd.DataFrame) -> list[InputAnswerDict]:
        df = df.fillna("")
        df["Input"] = df.apply(self._format_question, axis=1)
        df["Answer"] = df.apply(self._extract_answer, axis=1)
        result: list[InputAnswerDict] = [
            InputAnswerDict(input=str(row.Input), answer=str(row.Answer))
            for row in df[["Input", "Answer"]].itertuples(index=False)
        ]
        return result

    @staticmethod
    def _format_question(row: pd.Series) -> str:
        """Format the question with options."""
        question = row.get("question", "")
        parts = [question]
        answers = row.get("answers")
        if answers and isinstance(answers, list):
            parts.append("\nOptions:")
            for answer in answers:
                parts.append(answer)
        return "\n".join(parts)

    @staticmethod
    def _extract_answer(row: pd.Series) -> str:
        """Extract the answer from the row."""
        return str(row.get("label", ""))
