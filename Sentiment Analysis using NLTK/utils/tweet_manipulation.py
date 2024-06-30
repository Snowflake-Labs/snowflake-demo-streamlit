from collections import defaultdict, namedtuple
from nltk.corpus import stopwords
from utils.data_access import execute_query_with_params
from utils.helpers import rel_to_abs_date, add_counts, get_counts
from utils.nltk_manager import download_stopwords

import pandas as pd
import re
import streamlit as st
import textblob

if "tweets" not in st.session_state:
    st.session_state.tweets = []
    st.session_state.curr_tweet_page = 0
    st.session_state.curr_raw_tweet_page = 0


TWEET_CRAP_RE = re.compile(r"\bRT\b", re.IGNORECASE)
URL_RE = re.compile(r"(^|\W)https?://[\w./&%]+\b", re.IGNORECASE)
PURE_NUMBERS_RE = re.compile(r"(^|\W)\$?[0-9]+\%?", re.IGNORECASE)
EMOJI_RE = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U00002500-\U00002BEF"  # chinese char
    "\U00002702-\U000027B0"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001f926-\U0001f937"
    "\U00010000-\U0010ffff"
    "\u2640-\u2642"
    "\u2600-\u2B55"
    "\u200d"
    "\u23cf"
    "\u23e9"
    "\u231a"
    "\ufe0f"  # dingbats
    "\u3030"
    "]+",
    re.UNICODE,
)
OTHER_REMOVALS_RE = re.compile(
    "["
    "\u2026"  # Ellipsis
    "]+",
    re.UNICODE,
)
SHORTHAND_STOPWORDS_RE = re.compile(
    r"(?:^|\b)("
    "w|w/|"  # Short for "with"
    "bc|b/c|"  # Short for "because"
    "wo|w/o"  # Short for "without"
    r")(?:\b|$)",
    re.IGNORECASE,
)
AT_MENTION_RE = re.compile(r"(^|\W)@\w+\b", re.IGNORECASE)
HASH_TAG_RE = re.compile(r"(^|\W)#\w+\b", re.IGNORECASE)
PREFIX_CHAR_RE = re.compile(r"(^|\W)[#@]", re.IGNORECASE)


def clean_tweet_text(tweet_text: str) -> str:
    """Cleans tweet text.

    Args:
        tweet_text (str): The tweet text to be cleaned.

    Returns:
        str: The cleaned tweet text.
    """
    download_stopwords()
    stop_words_re = re.compile(
        r"\b(?:" + "|".join(stopwords.words("english")) + r")\b", re.IGNORECASE
    )
    regexes = [
        # AT_MENTION_RE,
        # HASH_TAG_RE,
        EMOJI_RE,
        PREFIX_CHAR_RE,
        PURE_NUMBERS_RE,
        stop_words_re,
        TWEET_CRAP_RE,
        OTHER_REMOVALS_RE,
        SHORTHAND_STOPWORDS_RE,
        URL_RE,
    ]

    for regex in regexes:
        tweet_text = regex.sub("", tweet_text)
    return tweet_text


def display_tweet(tweet: pd.core.series.Series) -> None:
    """Displays a given tweet information formatted with its key and value pairs.

    Args:
        tweet (pd.core.series.Series): The given tweet.
    """
    parsed_tweet = {
        "author": tweet["NAME"],
        "created_at": tweet["TWEET_CREATED"],
        "text": tweet["TEXT"],
    }

    for key, value in parsed_tweet.items():
        dict_col_left, dict_col_rifht = st.columns([1, 4])
        dict_col_left.write(f"**{key}:**")
        dict_col_rifht.write(value)


def search_term_in_twitter_text(search_parameters: dict) -> pd.DataFrame:
    """Searchs a giving termn in the twitter texts.

    Args:
        search_parameters (str): The neccesary search parameters
         to be used to find the right tweets.

    Returns:
        pd.DataFrame: The found tweets as a pandas dataframe.
    """
    days_ago = search_parameters["days_ago"]
    tweet_created_filter = "" if days_ago is None else "AND tweet_created >= ?"
    is_reply_filter = (
        "AND IS_REPLY = FALSE" if st.session_state.chck_excl_replies else ""
    )
    is_retweet_filter = (
        "AND IS_RETWEET = FALSE" if st.session_state.chck_excl_rtweets else ""
    )

    airlines_tweets_query = f"""
    SELECT
        *
    FROM
        airlines_sentiment_db.airlines_sentiment_s.airline_sentiment_table
    where
        text ILIKE ?
        {tweet_created_filter}
        AND retweet_count >= ?
        AND faves >= ?
        AND replies >= ?
        {is_reply_filter}
        {is_retweet_filter}
    limit
        ?
    """

    airlines_tweets_params = [f"%{st.session_state.i_search_term}%"]
    if days_ago is not None:
        airlines_tweets_params.append(f"{ str(rel_to_abs_date(days_ago))}")
    airlines_tweets_params.append(st.session_state.num_i_min_rtweets)
    airlines_tweets_params.append(st.session_state.num_i_min_hearts)
    airlines_tweets_params.append(st.session_state.num_i_min_replies)
    airlines_tweets_params.append(st.session_state.num_i_limit)

    return execute_query_with_params(airlines_tweets_query, airlines_tweets_params)


def get_tweets_paginated(
    tweets_df: pd.DataFrame, session_state_current_page_key: str, page_size: int
):
    """Gets given data frame paginated by provided page size.

    Args:
        tweets_df (pd.DataFrame): The tweet data frame.
        session_state_current_page_key (str): The session state key to identify current page.
        page_size (int): The page size to be paginated.

    Returns:
        _type_: _description_
    """
    curr_page = getattr(st.session_state, session_state_current_page_key)
    p_left_column, p_center_column, p_right_column = st.columns(3)

    def decrement_page():
        curr_page = getattr(st.session_state, session_state_current_page_key)
        if curr_page > 0:
            setattr(st.session_state, session_state_current_page_key, curr_page - 1)

    def increment_page():
        curr_page = getattr(st.session_state, session_state_current_page_key)
        if curr_page + 1 < len(tweets_df) // page_size:
            setattr(st.session_state, session_state_current_page_key, curr_page + 1)

    def set_page():
        setattr(
            st.session_state,
            session_state_current_page_key,
            getattr(st.session_state, f"{session_state_current_page_key}_selected_page")
            - 1,
        )

    p_left_column.write(" ")
    p_left_column.write(" ")
    p_left_column.button(
        "Previous page",
        on_click=decrement_page,
        key=f"{session_state_current_page_key}_prev_b",
    )
    p_center_column.write(" ")
    p_center_column.write(" ")
    p_center_column.button(
        "Next page",
        on_click=increment_page,
        key=f"{session_state_current_page_key}_next_b",
    )

    p_right_column.selectbox(
        "Select a page",
        range(1, len(tweets_df) // page_size + 1),
        curr_page,
        on_change=set_page,
        key=f"{session_state_current_page_key}_selected_page",
    )

    curr_page = getattr(st.session_state, session_state_current_page_key)

    page_start = curr_page * page_size
    page_end = page_start + page_size

    return tweets_df[page_start:page_end]


def get_text_blob_statistics(tweets_df: pd.DataFrame) -> dict:
    """Process tweets to get sentiment, word count, bigram count,
    trigram count and noun phrase count.

    Args:
        tweets (pd.DataFrame): Tweets as a pandas data frame.

    Returns:
        dict: A dictionay with sentiment value, word count, bigram count,
    trigram count and noun phrase count.
    """
    word_counts = defaultdict(int)
    bigram_counts = defaultdict(int)
    trigram_counts = defaultdict(int)
    nounphrase_counts = defaultdict(int)
    sentiment_list = []

    SentimentListItem = namedtuple(
        "SentimentListItem", ("date", "polarity", "subjectivity")
    )

    for _, tweet in tweets_df.iterrows():
        clean_text = clean_tweet_text(tweet["TEXT"]).lower()
        blob = textblob.TextBlob(clean_text)

        add_counts(word_counts, blob.word_counts)
        add_counts(bigram_counts, get_counts(blob.ngrams(2), key_sep=" "))
        add_counts(trigram_counts, get_counts(blob.ngrams(3), key_sep=" "))
        add_counts(nounphrase_counts, get_counts(blob.noun_phrases, key_sep=""))

        sentiment_list.append(
            SentimentListItem(
                tweet["TWEET_CREATED"],
                blob.sentiment.polarity,
                blob.sentiment.subjectivity,
            )
        )

    def to_df(the_dict):
        items = the_dict.items()
        items = ((term, count, len(term.split(" "))) for (term, count) in items)
        return pd.DataFrame(items, columns=("term", "count", "num_words"))

    return {
        "word_counts": to_df(word_counts),
        "bigram_counts": to_df(bigram_counts),
        "trigram_counts": to_df(trigram_counts),
        "nounphrase_counts": to_df(nounphrase_counts),
        "sentiment_list": sentiment_list,
    }
