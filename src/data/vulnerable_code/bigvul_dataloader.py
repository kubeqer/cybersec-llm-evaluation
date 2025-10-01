import pandas as pd
from datasets import load_dataset  # type: ignore[import-untyped]

from src.core.decorators.error_handling import error_handling
from src.core.decorators.log_calls import log_calls
from src.data.schema import InputAnswerDict


class BigVulDataLoader:
    # can add identifying by cve
    DATASET_SLUG = "bstee615/bigvul"
    SPLIT = "test"
    FEATURE_COLUMNS = [
        "func_before",
        "func_after",
        "vul",
        "commit_message",
    ]
    INPUT_TEMPLATE = "Commit before:\n{func_before}\nCommit after:\n{func_after}\n"
    ANSWER_TEMPLATE = "Vulnerable: {target}"

    @log_calls(level="INFO")
    @error_handling(default=[], reraise=True)
    def load(self):
        dataset = load_dataset(self.DATASET_SLUG, split=self.SPLIT)
        df = pd.DataFrame(dataset)
        return self._preprocess(df)

    @log_calls(level="INFO")
    @error_handling(default=[], reraise=True)
    def _preprocess(self, df: pd.DataFrame) -> list[InputAnswerDict]:
        df = df.fillna("")
        df["Input"] = df.apply(lambda row: self.INPUT_TEMPLATE.format(**row), axis=1)
        df["Answer"] = df.apply(lambda row: self.ANSWER_TEMPLATE.format(**row), axis=1)
        return [
            InputAnswerDict(input=str(row.Input), answer=str(row.Answer))
            for row in df[["Input", "Answer"]].itertuples(index=False)
        ]
