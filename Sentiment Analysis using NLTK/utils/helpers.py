from typing import Union
from utils.data_access import get_dataframe_from_raw_sql

import datetime
import pandas as pd


def rel_to_abs_date(days: Union[None, int]) -> datetime.date:
    """Returns a date from a specified day count in the past.

    Args:
        days (Union[None, int]): The days to start from.

    Returns:
        datetime.date: The current day minus the giving days.
    """
    if days is None:
        return datetime.date(day=1, month=1, year=1970)
    return_data = datetime.date.today() - datetime.timedelta(days=days)
    return return_data


def add_counts(accumulator: dict, ngrams: dict) -> None:
    """Add counts to the accumulator.

    Args:
        accumulator (dict): The acumulator as a dictionary.
        ngrams (dict): The ngrams as dictionary.
    """
    for ngram, count in ngrams.items():
        accumulator[ngram] += count


def get_counts(blobfield: list, key_sep: str) -> dict:
    """Gets the couns for the blob using the provided key.

    Args:
        blobfield (list): The blobfield.
        key_sep (str): The key separator.

    Returns:
        dict: A dictionary with the blobfields as keys.
    """
    return {key_sep.join(x): blobfield.count(x) for x in blobfield}


def get_relative_dates() -> dict:
    """Get relative dates as a dictionary.

    Returns:
        dict: The relative dates with their day values as a dictionary.
    """
    return {
        "All dates": None,
        "1 day ago": 1,
        "1 week ago": 7,
        "2 weeks ago": 14,
        "1 month ago": 30,
        "3 months ago": 90,
        "6 months ago": 180,
        "1 year ago": 365,
        "5 years ago": 365 * 5,
        "10 years ago": 365 * 10,
    }


def get_airlines() -> pd.DataFrame:
    """Get airlines from the database.

    Returns:
        pd.DataFrame: The airlines query result as a pandas dataframe.
    """
    return get_dataframe_from_raw_sql(
        """
        SELECT
            DISTINCT(airline)
        FROM
            airlines_sentiment_db.airlines_sentiment_s.airline_sentiment_table
        """
    )
