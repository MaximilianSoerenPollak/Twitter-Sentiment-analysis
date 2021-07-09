import tweepy
import json
import boto3
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import streamlit as st
import sys

from contextlib import contextmanager
from io import StringIO
from streamlit.report_thread import REPORT_CONTEXT_ATTR_NAME
from threading import current_thread
from secrets_file import consumer_key, consumer_secret, access_token, access_token_secret, aws_access_key_id, aws_secret_access_key

# Twitter API Authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
t_api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
#  AWS API Authentication
aws_session = boto3.Session(aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key)
comprehend = aws_session.client(service_name='comprehend', region_name='eu-central-1')


# # -------- FUNCTIONS ---------------
def make_initial_dataframe(twts):
    df = pd.DataFrame()
    df["Tweet"] = twts
    return df

def get_tweets(d=7,min_id=None, max_count=50, max_count_int=0,tweet_list=None, char_count=0, query="AAPL"):
    if tweet_list == None: 
        tweet_list = []
    min_int_id = 0
    max_count_int = max_count_int
    for i in t_api.search(environment_name="30daysearch", q=f"{query}-filter:retweets", count=100, result_type="recent", until=f"2021-07-0{d}", max_id=min_id, lang="en"):
            tweet_list.append(i.text)
            max_count_int += 1
            if min_int_id == 0:
                min_int_id = i.id
            else:
                if i.id < min_int_id:
                    min_int_id = i.id
    character_count = sum(len(i) for i in tweet_list)
    if max_count_int < max_count:
        get_tweets(d=d, min_id=min_int_id, max_count=max_count, max_count_int=max_count_int, tweet_list=tweet_list,char_count=character_count)
    return tweet_list, character_count

def get_sentiment(df):
    """
    This function passes text through the AWS comprehend NLP learning software. And analyzes the snentiment

    Args:
        df ([DataFrame]):  This is the DataFrame containing the Username and Tweet Text. 

    Returns:
        sentiment_list ([list]): Returns  a list of the sentiment analysis of the text. Either NEUTRAL, GOOD, BAD, MIXED. This is for each tweet in the DF
    """
    sentiment_list = []
    for i in df["Tweet"]:
        a = json.dumps(comprehend.detect_sentiment(Text=i, LanguageCode='en'))
        sentiment_dict = json.loads(a)
        sentiment_list.append(sentiment_dict["Sentiment"])
    return sentiment_list

def check_ticker(ticker):
    ticker = yf.Ticker(ticker.upper())
    df = ticker.history(period="7d")
    if len(df) == 0:
        return False
    else:   
        return True

def get_stock_info(ticker, days):
    tick = yf.Ticker(ticker.upper())
    df_price = tick.info
    price = df_price["regularMarketPrice"]
    logo = df_price["logo_url"]
    name = df_price["shortName"]
    website = df_price["website"]
    industry = df_price["industry"]
    df = tick.history(period=f"{days}D")
    per_change = round((df["Close"][days-1] / df["Close"][0]),2)
    plt.style.use('dark_background')
    fig, ax = plt.subplots(1,1, figsize=(12,5))
    ax.plot(df[["Open", "Close"]])
    ax.legend(["Open", "Close"],loc="upper left")
    return fig, price, name, logo, website, per_change, industry

def make_final_df(df, sentiment):
    df["Sentiment"] = sentiment
    return df

def save_df(df, name):
    df.to_csv(f"{name}.csv", index=False, header=True)

def load_df(name):
    df = pd.read_csv(f"{name}.csv")
    return df

def analyze_sentiment(df):
    g_s, g_s_per = analyze_positive(df)
    b_s, b_s_per = analyze_negative(df)
    n_s, n_s_per = analyze_neutral(df)
    m_s, m_s_per = analyze_mixed(df)
    return g_s, g_s_per, b_s, b_s_per, n_s, n_s_per, m_s, m_s_per

def analyze_positive(df):
    df = df["Sentiment"].value_counts()
    all_tweets = df.sum()
    try:
        g_s_per =  round((df[df.index.isin(["POSITIVE"])].values[0] / all_tweets) * 100, 2)
        g_s = df[df.index.isin(["POSITIVE"])].values[0]
        return g_s, g_s_per
    except IndexError as ie:
        str_ = "There are no 'POSITIVE' tweets in this query."
        return str_, ie
    
def analyze_negative(df):
    df = df["Sentiment"].value_counts()
    all_tweets = df.sum()
    try:
        b_s_per =  round((df[df.index.isin(["NEGATIVE"])].values[0] / all_tweets) * 100, 2)
        b_s = df[df.index.isin(["NEGATIVE"])].values[0]
        return b_s, b_s_per
    except IndexError as ie:
        str_ = "There are no 'NEGATIVE' tweets in this query."
        return str_, ie

def analyze_neutral(df):
    df = df["Sentiment"].value_counts()
    all_tweets = df.sum()
    try:
        n_s_per =  round((df[df.index.isin(["NEUTRAL"])].values[0] / all_tweets) * 100, 2)
        n_s = df[df.index.isin(["NEUTRAL"])].values[0]
        return n_s, n_s_per
    except IndexError as ie:
        str_ = "There are no 'NEUTRAL' tweets in this query."
        return str_, ie

def analyze_mixed(df):
    df = df["Sentiment"].value_counts()
    all_tweets = df.sum()
    try:
        m_s_per =  round((df[df.index.isin(["MIXED"])].values[0] / all_tweets) * 100, 2)
        m_s = df[df.index.isin(["MIXED"])].values[0]
        return m_s, m_s_per
    except IndexError as ie:
        str_ = "There are no 'MIXED' tweets in this query."
        return str_, ie

def get_biggest(list):
    i_int = 0
    for i in list:
        if type(i) == str:
            continue 
        if i > i_int:
            i_int = i
    index = list.index(i_int)
    return index

# # # --- WEBSITE ---
st.header("Welcome to my Sentiment Analyzer")
st.subheader("Enter the amount of days you want to analyze, and entere a STOCK Ticker")
st.text("Please note that this has to be a stock ticker. If the programm can not find any Stock corresponding to it, it will notify you")
st.write("---")
col1, col2, col3 = st.beta_columns([1,1,1])
with col1:
    days_selected = st.slider(label="Enter how many days to go back.", min_value=2, max_value=7, value=5)   
    search_button = st.button(label="Search")
with col2:
    tweets_searched = st.number_input(label="Enter how many tweets you want to search at least. (Between 50 and 500)", max_value=500, min_value=50, value=50)
with col3:
    ticker_search = st.text_input(label="Enter a stock-ticker", max_chars=5)
    clear_button = st.button(label="Clear")
st.write("---")
if search_button:
    if check_ticker(ticker=ticker_search):
        twt_list, counter_tw = get_tweets(d=days_selected ,min_id=None, max_count=tweets_searched, max_count_int=0,tweet_list=None, char_count=0, query=ticker_search)
        fig, price, name, logo, website, per_change, industry = get_stock_info(ticker=ticker_search, days=days_selected)
        df_initial = make_initial_dataframe(twts=twt_list)
        sentiment_list = get_sentiment(df=df_initial)
        final_df = make_final_df(df=df_initial, sentiment=sentiment_list)
        g_s, g_s_per, b_s, b_s_per, n_s, n_s_per, m_s, m_s_per = analyze_sentiment(df=final_df)
        s_m_list_no_per = [g_s,b_s ,n_s, m_s]
        b_index = get_biggest(s_m_list_no_per)
        #--------------------
        col3, col4, col5, col6, col7 = st.beta_columns([.5,.5,1,1,1])
        with col3:
            st.image(logo)
        with col4:
            st.subheader(name)
            st.subheader(ticker_search)
        with col5:
            st.subheader(f"{name} is in the {industry} industry")
            st.subheader(f"Check our their website: [{name}]({website})")
        with col6:
            st.subheader(f"Current Price: {price}$.")
            st.subheader(f"Price change in the last {days_selected} days: {per_change} %.")
        with col7:
            if b_index == 0:
                sent = "POSITIVE"
            elif b_index == 1:
                sent = "NEGATIVE"
            elif b_index == 2:
                sent = "NEUTRAL"
            elif b_index == 3:
                sent = "MIXED"
            st.subheader(f"The overall sentiment on twitter in the recent {days_selected} days is: {sent}")
        st.write("---")
        col8, col9 = st.beta_columns([2,1])
        with col8:
                st.pyplot(fig)
        with col9:
            if type(g_s) == str:
                st.write("There were 0 tweets with 'POSITIVE' sentiment ")
            else:
                st.write(f"The tweets with 'POSITIVE' sentiment are {g_s}, which is {g_s_per}%.")
            if type(b_s) == str:
                st.write("There were 0 tweets with 'NEGATIVE' sentiment ")
            else:
                st.write(f"The tweets with 'NEGATIVE' sentiment are {b_s}, which is {b_s_per}%.")
            if type(n_s) == str:
                st.write("There were 0 tweets with 'NEUTRAL' sentiment ")
            else:
                st.write(f"The tweets with 'NEUTRAL' sentiment are {n_s}, which is {n_s_per}%.")
            if type(m_s) == str:
                st.write("There were 0 tweets with 'MIXED' sentiment ")
            else:
                st.write(f"The tweets with 'MIXED' sentiment are {m_s}, which is {m_s_per}%.")
            st.write(f"With this search, you have analyzed {counter_tw} characters, and {len(final_df)} tweets.")
            st.write(f"")
        df_extender = st.beta_expander(label="Show the DataFrame")
        with df_extender:
            st.write(final_df)
            



    else:
        st.error("Please entere another ticker. This one could not be found.")
if clear_button:
    search_button = False


# THIS IS ALL TO PRINT OUT THE ERROR MESASAGE FROM TWITER API
@contextmanager
def st_redirect(src, dst):
    placeholder = st.empty()
    output_func = getattr(placeholder, dst)

    with StringIO() as buffer:
        old_write = src.write

        def new_write(b):
            if getattr(current_thread(), REPORT_CONTEXT_ATTR_NAME, None):
                buffer.write(b)
                output_func(buffer.getvalue())
            else:
                old_write(b)

        try:
            src.write = new_write
            yield
        finally:
            src.write = old_write


@contextmanager
def st_stdout(dst):
    with st_redirect(sys.stdout, dst):
        yield


@contextmanager
def st_stderr(dst):
    with st_redirect(sys.stderr, dst):
        yield


with st_stdout("code"):
    pass

with st_stdout("info"):
    t_api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
