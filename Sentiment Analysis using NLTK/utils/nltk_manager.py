from textblob.download_corpora import download_all
import nltk
import os
import streamlit as st

# We will use a temporary location for the downloaded dependencies
DOWNLOAD_FOLDER = "/tmp/nlkt_data"


def download_ntlk_depencies() -> None:
    """Download ntlk library dependencies. This will be done only
    the first time the app is booted.
    """
    if not os.path.exists(DOWNLOAD_FOLDER):
        with st.spinner("Downloading library data!"):
            os.makedirs(DOWNLOAD_FOLDER)
            # Here we override the download directory path for
            # the textblob.download_corpora.download_all method
            nltk.downloader._downloader.download_dir = DOWNLOAD_FOLDER
            download_all()


def download_stopwords():
    """Downloads ntlk stopwords package."""
    if not os.path.exists(f"{DOWNLOAD_FOLDER}/corpora/stopwords"):
        nltk.data.path = [DOWNLOAD_FOLDER]
        nltk.download("stopwords")
