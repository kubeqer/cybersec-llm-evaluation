import pandas as pd
from datasets import load_dataset

from src.core.decorators.error_handling import error_handling
from src.core.decorators.log_calls import log_calls
from src.data.qa.utils import format_options
from src.data.schema import InputAnswerDict


class CyberBenchDataLoader:
    DATASET_SLUG = "zefang-liu/cyberbench"
    SPLIT = "test"

    def __init__(self, task_name: str | None = None, split: str = "test"):
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
        if "question" in df.columns and "answer" in df.columns:
            df["Input"] = df["question"]
            if "options" in df.columns:
                df["Input"] = df.apply(
                    lambda row: f"{row['question']}\n"
                    f"Options:\n{format_options(row.get('options', []))}",
                    axis=1,
                )
            df["Answer"] = df["answer"]
        elif "text" in df.columns and "label" in df.columns:
            df["Input"] = df["text"]
            df["Answer"] = df["label"]
        elif "text" in df.columns and "entities" in df.columns:
            df["Input"] = df["text"]
            df["Answer"] = df.apply(lambda row: str(row.get("entities", [])), axis=1)
        else:
            cols = df.columns.tolist()
            df["Input"] = df[cols[0]].astype(str)
            df["Answer"] = df[cols[1] if len(cols) > 1 else cols[0]].astype(str)
        result: list[InputAnswerDict] = [
            InputAnswerDict(input=str(row.Input), answer=str(row.Answer))
            for row in df[["Input", "Answer"]].itertuples(index=False)
        ]
        return result
