import pandas as pd
from datasets import load_dataset

from src.core.decorators.error_handling import error_handling
from src.core.decorators.log_calls import log_calls
from src.data.schema import InputAnswerDict


class CyberBenchDataLoader:
    DATASET_SLUG = "zefang-liu/cyberbench"
    SPLIT = "train"

    def __init__(self, task_name: str | None = None, split: str = "train"):
        self.task_name = task_name
        self.split = split

    @log_calls(level="INFO")
    @error_handling(default=[], reraise=True)
    def load(self) -> list[InputAnswerDict]:
        if self.task_name:
            dataset = load_dataset(self.DATASET_SLUG, self.task_name, split=self.split)
        else:
            dataset = load_dataset(self.DATASET_SLUG, split=self.split)
        df = pd.DataFrame(dataset)
        result: list[InputAnswerDict] = self._preprocess(df)
        return result

    @log_calls(level="INFO")
    @error_handling(default=[], reraise=True)
    def _preprocess(self, df: pd.DataFrame) -> list[InputAnswerDict]:
        df = df.fillna("")
        if "task" in df.columns:
            df = df[df["task"] == "mc"]
        if "input" in df.columns and "output" in df.columns:
            df["Input"] = df["input"]
            df["Answer"] = df["output"]
        else:
            raise ValueError(
                "Expected 'input' and 'output' columns not found in dataset"
            )
        result: list[InputAnswerDict] = [
            InputAnswerDict(input=str(row.Input), answer=str(row.Answer))
            for row in df[["Input", "Answer"]].itertuples(index=False)
        ]
        return result
