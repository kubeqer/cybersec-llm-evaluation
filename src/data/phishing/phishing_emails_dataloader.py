import pandas as pd

from src.data.base import BaseDataLoader
from src.data.schema import InputAnswerDict


class PhishingEmailsDataLoader(BaseDataLoader):
    DATASET_SLUG = "kuladeep19/phishing-and-legitimate-emails-dataset"
    FILE_PATH = "phishing_legit_dataset_KD_10000.csv"
    FEATURE_COLUMNS = [
        "text",
        "label",  # 1 = phishing email, 0 = legitimate email.
        "phishing_type",
        "severity",
        "confidence",
    ]
    INPUT_TEMPLATE = "Text: {text} "
    ANSWER_TEMPLATE = "Label: {label}, Phishing Type: {phishing_type}, "

    def __init__(self):
        super().__init__(dataset_slug=self.DATASET_SLUG, file_path=self.FILE_PATH)

    def _preprocess(self, df: pd.DataFrame) -> list[InputAnswerDict]:
        df["Input"] = df.apply(lambda row: self.INPUT_TEMPLATE.format(**row), axis=1)
        df["Answer"] = df.apply(lambda row: self.ANSWER_TEMPLATE.format(**row), axis=1)
        return [
            InputAnswerDict(input=str(row.Input), answer=str(row.Answer))
            for row in df[["Input", "Answer"]].itertuples(index=False)
        ]


print(PhishingEmailsDataLoader().load())
