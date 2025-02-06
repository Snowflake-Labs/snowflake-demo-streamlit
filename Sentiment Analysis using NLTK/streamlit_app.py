from utils.helpers import get_airlines, get_relative_dates
from utils.nltk_manager import download_ntlk_depencies
from utils.tweet_manipulation import (
    display_tweet,
    get_text_blob_statistics,
    get_tweets_paginated,
    search_term_in_twitter_text,
)
from utils.rendering import chart_mark_line, chart_mark_point, display_count_table

import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(layout="wide")
download_ntlk_depencies()
st.title("AirTweet Analyzer :balloon:")
st.write(
    """
    Introducing AirTweet Analyzer, your go-to solution for unlocking 
    the sentiment behind airline-related tweets. With AirTweet Analyzer, 
    gain valuable insights into the emotions, opinions, and experiences 
    shared by travelers on social media platforms like Twitter. 
    """
)
relative_dates = get_relative_dates()
search_params = {}
query_term = st.selectbox(
    "Search Term:",
    ["SouthwestAir", "VirginAmerica", "united", "JetBlue", "USAirways", "AmericanAir"],
    placeholder="Select airline...",
    key="i_search_term",
)

col_sel_relative_dates, col_tweets_limit = st.columns([2, 1])
selected_rel_date = col_sel_relative_dates.selectbox(
    "Search:", list(relative_dates.keys()), 0, key="sel_relative_dates"
)
search_params["days_ago"] = relative_dates[selected_rel_date]
col_tweets_limit.number_input("Limit", 1, None, 10000, key="num_i_limit")

col_num_i_min_replies, col_num_i_min_rtweets, col_num_i_min_hearts = st.columns(3)
col_num_i_min_replies.number_input(
    "Minimum replies", 0, None, 0, key="num_i_min_replies"
)
col_num_i_min_rtweets.number_input(
    "Minimum retweets", 0, None, 0, key="num_i_min_rtweets"
)
col_num_i_min_hearts.number_input("Minimum hearts", 0, None, 0, key="num_i_min_hearts")
col_num_i_min_replies.checkbox("Exclude replies", False, key="chck_excl_replies")
col_num_i_min_hearts.checkbox("Exclude retweets", False, key="chck_excl_rtweets")

if not query_term:
    st.stop()

tweets = search_term_in_twitter_text(search_params)

if len(tweets) == 0:
    st.write("No results")
    st.stop()

with st.spinner("Analysing Results"):
    results = get_text_blob_statistics(tweets)

    st.divider()
    st.header("Analysis results")

    st.write("Number of matching tweets:", len(tweets))
    st.subheader("Sentiment")

    sentiment_df = pd.DataFrame(results["sentiment_list"])
    col_a, col_b = st.columns(2)

    mean_polarity = sentiment_df["polarity"].mean()
    mean_subjectivity = sentiment_df["subjectivity"].mean()
    col_a.metric("POLARITY", f"{mean_polarity:.2f}", delta=f"{mean_polarity:2f}")
    col_b.metric(
        "SUBJECTIVITY", f"{mean_subjectivity:.2f}", delta=f"{mean_subjectivity:2f}"
    )

    TIMEUNIT = "yearmonthdate"
    if search_params["days_ago"] is None:
        pass
    elif search_params["days_ago"] <= 1:
        TIMEUNIT = "hours"
    elif search_params["days_ago"] <= 30:
        TIMEUNIT = "monthdate"

    chart = alt.Chart(sentiment_df, title="")

    avg_subjectivity = chart.mark_line(
        interpolate="catmull-rom",
        tooltip=True,
    ).encode(
        x=alt.X("date:T", timeUnit=TIMEUNIT, title="date"),
        y=alt.Y(
            "mean(subjectivity):Q", title="subjectivity", scale=alt.Scale(domain=[0, 1])
        ),
    )

    subjectivity_values = chart.mark_point(
        tooltip=True,
        size=75,
        filled=True,
    ).encode(
        x=alt.X("date:T", timeUnit=TIMEUNIT, title="date"),
        y=alt.Y("subjectivity:Q", title="subjectivity"),
    )

    chart = alt.Chart(sentiment_df, title="")
    avg_polarity = chart_mark_line(
        chart, TIMEUNIT, "mean(polarity):Q", "polarity", [-1, 1]
    )
    polarity_values = chart_mark_point(chart, TIMEUNIT, "polarity:Q", "polarity", None)

    with st.expander("Sentiment Polarity"):
        st.write(
            """
            Sentiment polarity, in the context of sentiment analysis, refers to the degree of
            positivity, neutrality, or negativity expressed in a piece of text. 
            
            Scores closer to 1 indicate strong positive sentiment, reflecting expressions of 
            joy, enthusiasm, or satisfaction, such as "I'm very pleased with my flight!"
            
            Conversely, scores closer to -1 signify strong negative sentiment, capturing emotions 
            of disappointment, frustration, or anger, as in "The service was terrible, and 
            I'm extremely dissatisfied."
            
            In contrast, scores close to 0 denote neutral sentiment, indicating a lack of emotional
            bias or a balanced viewpoint, like "The flight went as expected!" 
            
            Sentiment polarity analysis is valuable for understanding the overall emotional tone 
            conveyed in textual data, enabling insights into public opinion, customer feedback, and
            social media sentiment, among other applications.
            """
        )
    st.altair_chart(avg_polarity + polarity_values, use_container_width=True)

    with st.expander("Sentiment Subjectivity"):
        st.write(
            """
            Sentiment subjectivity refers to the degree to which 
            opinions expressed about the airline are influenced by personal experiences, 
            emotions, or biases rather than objective facts.
            
            Scores close to 1 indicate highly subjective sentiments, where passengers' opinions 
            are strongly influenced by their individual experiences and emotional reactions, 
            such as "I had the most wonderful flight experience with this airline; the crew 
            was so attentive and friendly!"
            
            On the other hand, scores close to -1 suggest highly objective sentiments, where 
            opinions are based primarily on factual aspects of the airline's service without
            much personal bias, as in "The flight departed on time and arrived at the
            scheduled destination without any issues."
            
            Scores close to 0 represent a balance between subjective and objective elements,
            indicating that opinions about the airline are moderately influenced by personal 
            experiences but also take into account factual aspects, like "My flight was delayed, but 
            the airline provided clear communication and assistance, which I appreciated."

            Recognizing sentiment subjectivity is essential for accurately gauging passengers'
            attitudes toward the airline and understanding the factors driving their opinions.
            """
        )
    st.altair_chart(avg_subjectivity + subjectivity_values, use_container_width=True)

    terms = pd.concat(
        [
            results["word_counts"],
            results["bigram_counts"],
            results["trigram_counts"],
            results["nounphrase_counts"],
        ]
    )

    col_a, col_b = st.columns(2)
    adjustment_factor = col_a.slider(
        "Prioritize long expressions", 0.0, 1.0, 0.2, 0.001
    )
    max_threshold = terms["count"].max()
    threshold = col_b.slider("Threshold", 0.0, 1.0, 0.3) * max_threshold
    weights = (terms["num_words"] * adjustment_factor * (terms["count"] - 1)) + terms[
        "count"
    ]
    filtered_terms = terms[weights > threshold]
    st.altair_chart(
        alt.Chart(filtered_terms)
        .mark_bar(tooltip=True)
        .encode(
            x="count:Q",
            y=alt.Y("term:N", sort="-x"),
        ),
        use_container_width=True,
    )

    st.subheader("Raw data")

    if st.checkbox("Show term counts"):
        display_count_table("Term count cut-off", terms, 5)

    if st.checkbox("Show word counts"):
        display_count_table("Word count cut-off", results["word_counts"], 5)

    if st.checkbox("Show bigram counts"):
        display_count_table("Bigram count cut-off", results["bigram_counts"], 3)

    if st.checkbox("Show trigram counts"):
        display_count_table("Trigram count cut-off", results["trigram_counts"], 2)

    if st.checkbox("Show noun-phrase counts"):
        display_count_table("Word count cut-off", results["nounphrase_counts"], 3)

    if st.checkbox("Show tweets"):
        paginated_results = get_tweets_paginated(tweets, "curr_tweet_page", 10)
        for index, row in paginated_results.iterrows():
            display_tweet(row)
            st.divider()

    if st.checkbox("Show raw tweets"):
        for index, result in get_tweets_paginated(
            tweets, "curr_raw_tweet_page", 1
        ).iterrows():
            column_names = result.index
            for col_name in column_names:
                row_col_left, row_col_rifht = st.columns([1, 4])
                row_col_left.write(f"**{col_name}:**")
                row_col_rifht.write(result[col_name])
            st.divider()