from typing import cast

import pandas as pd
import requests
from loguru import logger
from requests import HTTPError, RequestException, Timeout

from src.core.paths import DATA_DIR
from src.data.schema import InputAnswerDict


class PhishingWebsiteDataLoader:
    URL = "https://raw.githubusercontent.com/GregaVrbancic/Phishing-Dataset/master/dataset_small.csv"
    FILE_PATH = DATA_DIR / "phishing_website_dataset_small.csv"
    FEATURE_COLUMNS = [
        "qty_dot_url",
        "qty_hyphen_url",
        "qty_underline_url",
        "qty_slash_url",
        "qty_questionmark_url",
        "qty_equal_url",
        "qty_at_url",
        "qty_and_url",
        "qty_exclamation_url",
        "qty_space_url",
        "qty_tilde_url",
        "qty_comma_url",
        "qty_plus_url",
        "qty_asterisk_url",
        "qty_hashtag_url",
        "qty_dollar_url",
        "qty_percent_url",
        "qty_tld_url",
        "length_url",
        "qty_dot_domain",
        "qty_hyphen_domain",
        "qty_underline_domain",
        "qty_slash_domain",
        "qty_questionmark_domain",
        "qty_equal_domain",
        "qty_at_domain",
        "qty_and_domain",
        "qty_exclamation_domain",
        "qty_space_domain",
        "qty_tilde_domain",
        "qty_comma_domain",
        "qty_plus_domain",
        "qty_asterisk_domain",
        "qty_hashtag_domain",
        "qty_dollar_domain",
        "qty_percent_domain",
        "qty_vowels_domain",
        "domain_length",
        "domain_in_ip",
        "server_client_domain",
        "qty_dot_directory",
        "qty_hyphen_directory",
        "qty_underline_directory",
        "qty_slash_directory",
        "qty_questionmark_directory",
        "qty_equal_directory",
        "qty_at_directory",
        "qty_and_directory",
        "qty_exclamation_directory",
        "qty_space_directory",
        "qty_tilde_directory",
        "qty_comma_directory",
        "qty_plus_directory",
        "qty_asterisk_directory",
        "qty_hashtag_directory",
        "qty_dollar_directory",
        "qty_percent_directory",
        "directory_length",
        "qty_dot_file",
        "qty_hyphen_file",
        "qty_underline_file",
        "qty_slash_file",
        "qty_questionmark_file",
        "qty_equal_file",
        "qty_at_file",
        "qty_and_file",
        "qty_exclamation_file",
        "qty_space_file",
        "qty_tilde_file",
        "qty_comma_file",
        "qty_plus_file",
        "qty_asterisk_file",
        "qty_hashtag_file",
        "qty_dollar_file",
        "qty_percent_file",
        "file_length",
        "qty_dot_params",
        "qty_hyphen_params",
        "qty_underline_params",
        "qty_slash_params",
        "qty_questionmark_params",
        "qty_equal_params",
        "qty_at_params",
        "qty_and_params",
        "qty_exclamation_params",
        "qty_space_params",
        "qty_tilde_params",
        "qty_comma_params",
        "qty_plus_params",
        "qty_asterisk_params",
        "qty_hashtag_params",
        "qty_dollar_params",
        "qty_percent_params",
        "params_length",
        "tld_present_params",
        "qty_params",
        "email_in_url",
        "time_response",
        "domain_spf",
        "asn_ip",
        "time_domain_activation",
        "time_domain_expiration",
        "qty_ip_resolved",
        "qty_nameservers",
        "qty_mx_servers",
        "ttl_hostname",
        "tls_ssl_certificate",
        "qty_redirects",
        "url_google_index",
        "domain_google_index",
        "url_shortened",
    ]

    def load(self):
        if not self.FILE_PATH.exists():
            self._download_dataset_small()
        df = pd.read_csv(self.FILE_PATH)
        return self._preprocess(df)

    def _preprocess(self, df: pd.DataFrame) -> list[InputAnswerDict]:
        if not all(col in df.columns for col in self.FEATURE_COLUMNS):
            missing = [col for col in self.FEATURE_COLUMNS if col not in df.columns]
            logger.error(f"DataFrame is missing required feature columns: {missing}")
            raise ValueError("Required feature columns are missing.")

        if "phishing" in df.columns:
            try:
                df["phishing"] = df["phishing"].astype(int)
                logger.info("Normalized 'phishing' column to integer type.")
            except ValueError:
                logger.error(
                    "Could not convert 'phishing' column to integer. Check data values."
                )
        else:
            logger.warning("'phishing' target column not found.")
        df["Input"] = df[self.FEATURE_COLUMNS].apply(
            lambda row: ", ".join(
                [f"{col}: {row[col]}" for col in self.FEATURE_COLUMNS]
            ),
            axis=1,
        )
        return [
            InputAnswerDict(input=str(row.Input), answer=int(cast(int, row.phishing)))
            for row in df[["Input", "phishing"]].itertuples(index=False)
        ]

    def _download_dataset_small(self) -> None:
        logger.info(f"Starting download of phishing dataset from {self.URL}")
        try:
            response = requests.get(self.URL, timeout=60)
            response.raise_for_status()
            logger.debug(
                f"Download completed, response size: {len(response.content)} bytes"
            )
            with open(self.FILE_PATH, "wb") as f:
                f.write(response.content)
            logger.info("File downloaded successfully")
        except (HTTPError, Timeout, RequestException) as e:
            logger.error(f"Failed to download dataset from {self.URL}: {e}")
            raise RuntimeError(f"Failed to download dataset: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during dataset download: {e}")
            raise
