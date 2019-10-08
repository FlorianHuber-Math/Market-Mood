# For web scraping and news
from bs4 import BeautifulSoup
#from newsapi import NewsApiClient
from newsapi.newsapi_client import NewsApiClient
import requests
# Stock market data
import numpy as np
import pandas as pd
import pandas_datareader as web
import yfinance as yf
import datetime
from datetime import datetime, timedelta

# Twitter
import os
import tweepy as tw

# General
import re
import matplotlib.pyplot as plt
import re
import argparse
import logging
# import unicode
import unicodedata
from tqdm import tqdm

# Sentiment analysis
import flair
import nltk
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# plot
from mpl_finance import candlestick_ohlc
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib import style
import io


flair_sentiment = flair.models.TextClassifier.load('en-sentiment')

# Init
newsapi = NewsApiClient(api_key='')
use_news = True
# Twitter
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''
use_twitter = True
# News API things

def convert_date_to_datetime_for_news_api(News_df,publishedAt):
  dates = News_df[publishedAt]
  count = 0
  for date in dates:
    year = int(date[0:4])
    month = int(date[5:7])
    day = int(date[8:10])
    hour = int(date[11:13])
    minute = int(date[14:16])
    temp = datetime(year,month,day,0,0)
    # uncomment in case of minute stock data
    # temp = datetime(year,month,day,hour,minute)
    News_df[publishedAt][count] = temp
    count = count + 1
  return News_df

def get_news_api_news(Input):
    Stock = yf.Ticker(Input)
    Short_name = Stock.info.get('shortName')
    Short_name_original = Short_name

    # Clean the short name
    Short_name = Short_name.replace('Inc.','')
    Short_name = Short_name.replace('Company','')
    Short_name = Short_name.rstrip()


    # /v2/top-headlines
    News_bloomberg_ticker = newsapi.get_everything(q=Input,sources = 'bloomberg')
    News_reuters_ticker = newsapi.get_everything(q=Input,sources = 'reuters')
    News_cnbc_ticker = newsapi.get_everything(q=Input,sources = 'cnbc')
    News_google_ticker = newsapi.get_everything(q=Input,sources = 'google-news')

    News_df = pd.DataFrame(News_bloomberg_ticker.get('articles'))
    News_df_reuters = pd.DataFrame(News_reuters_ticker.get('articles'))
    News_df_cnbc = pd.DataFrame(News_cnbc_ticker.get('articles'))
    News_df = News_df.append(News_df_reuters, ignore_index=True)
    News_df = News_df.append(News_df_cnbc, ignore_index=True)

    News_df = convert_date_to_datetime_for_news_api(News_df,'publishedAt')

     # Get date of the first article
    Oldest_article_dt = News_df['publishedAt'].min()

    return News_df, Oldest_article_dt

# Twitter Stuff
def remove_url(txt):
    """Replace URLs found in a text string with nothing
    (i.e. it will remove the URL from the string).

    Parameters
    ----------
    txt : string
        A text string that you want to parse and remove urls.

    Returns
    -------
    The same txt string with url's removed.
    """

    return " ".join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", txt).split())

def get_twitter_news(Input, Start_Date):
    auth = tw.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tw.API(auth, wait_on_rate_limit=True)

    search_words = str(Input)+'-filter:retweets'
    date_since = Start_Date

    #Twitter_list =[14886375,20402945,44060322,15897179,28571999,28164923,1754641,21328656]
    Twitter_list =[14886375,20402945]

    all_tweets_by_list = []
    for id_number in Twitter_list:
        tweets = tw.Cursor(api.user_timeline, id=id_number,since=date_since, include_rts=False, exclude_replies=False).items(500)
        for tweet in tweets:
            if Input in str(tweet):
                all_tweets_by_list.append([tweet.text, tweet.created_at])


    twitter_df_selected = pd.DataFrame(data=all_tweets_by_list,
                    columns=['Tweet', 'Date'])

    for i in range(0,len(twitter_df_selected['Tweet'])):
        twitter_df_selected['Tweet'][i] = remove_url(twitter_df_selected['Tweet'][i])

# Get first date twitter selected
    Oldest_twitter_selected_dt = twitter_df_selected['Date'].min().to_pydatetime()


    return twitter_df_selected, Oldest_twitter_selected_dt

# Stock Stuff

def get_stock_data(Input, start_date):

    df_stock = web.DataReader(Input, 'yahoo', start_date, datetime.today().date())

    return df_stock

# Sentiment

def get_stock_sentiment(news):
    sentiment = 0
    # work on that
    s = flair.data.Sentence(news)
    flair_sentiment.predict(s)
    total_sentiment = s.labels


    return str(total_sentiment)

def sentiment_in_df(News_df, text_column):
    News_df['Sentiment']=0
    for index_news in tqdm(range(0,len(News_df.index))):
        temp_sentiment = get_stock_sentiment(News_df[text_column][index_news])
        string = temp_sentiment
        if 'NEGATIVE' in temp_sentiment:
            sentiment_value = '-' + re.findall("\d+\.\d+", string)[0]
            sentiment_value = float(sentiment_value)
            News_df.loc[ News_df.index[index_news],'Sentiment'] = sentiment_value
        if 'POSITIVE' in temp_sentiment:
            sentiment_value = re.findall("\d+\.\d+", string)[0]
            sentiment_value = float(sentiment_value)
            News_df.loc[ News_df.index[index_news],'Sentiment'] = sentiment_value
    return News_df

# Main program

def update_sentiment_columns(df_to_update,df_with_sentiment,update_column):
    for index_update in range(0,len(df_to_update.index)):
        for index_sentiment in range(0,len(df_with_sentiment.index)):
            if df_to_update.index[index_update].to_pydatetime().date() == df_with_sentiment.index[index_sentiment]:
                df_to_update.loc[ df_to_update.index[index_update],update_column] = df_with_sentiment[index_sentiment]
    return df_to_update


def market_mood(Input):
    today = datetime.today()
    first = today.replace(day=1)
    lastMonth = first - timedelta(days=1)
    Start_Date = str(lastMonth)
    if use_news:
        News_df, news_start = get_news_api_news(Input)
        News_df = sentiment_in_df(News_df, 'title')
        # Average over the sentiments for each day
        News_df = News_df.groupby([News_df['publishedAt'].dt.date])['Sentiment'].mean()
    if use_twitter:
        twitter_df_selected, twitter_start = get_twitter_news(Input, Start_Date)
        twitter_df_selected = sentiment_in_df(twitter_df_selected, 'Tweet')
        # Average over the sentiments for each day
        twitter_df_selected = twitter_df_selected.groupby([twitter_df_selected['Date'].dt.date])['Sentiment'].mean()

    if use_news and use_twitter:
        start_date = min([news_start,twitter_start])
    elif use_news and not use_twitter:
        start_date = news_start
    elif not use_news and use_twitter:
        start_date = twitter_start
    else:
        start_date = datetime.datetime(2019,1,1)

    start_date = str(start_date)[0:10]
    min_start =  start_date


    df_stock = get_stock_data(Input, start_date)
    df_stock['Sentiment News'] = 0
    df_stock['Sentiment Twitter'] = 0
    if use_news:
        df_stock = update_sentiment_columns(df_stock,News_df,'Sentiment News')
    if use_twitter:
        df_stock = update_sentiment_columns(df_stock,twitter_df_selected,'Sentiment Twitter')

    df_stock['Percentage change price']=df_stock['Adj Close'].pct_change()
    df_stock['Percentage change Sentiment News']=df_stock['Sentiment News'].pct_change()
    df_stock['Percentage change Sentiment Twitter']=df_stock['Sentiment Twitter'].pct_change()

    return df_stock


def prepare_market_mood_for_plot(df):
    ohlc = df.copy()
    ohlc.reset_index(level=0, inplace=True)
    ohlc= ohlc[['Date','Open', 'High', 'Low','Close']].copy()
    for i in range(0,len(ohlc['Date'])):
      ohlc['Date'][i] = ohlc['Date'][i].date().toordinal()
    return ohlc

def make_stock_plot(ohlc, News_sentiment, Twitter_sentiment) :
    f1, ax = plt.subplots(3)
    candlestick_ohlc(ax[0], ohlc.values, width=.6, colorup='green', colordown='red')
    ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    # Creating SMA columns
    ohlc['SMA5'] = ohlc["Close"].rolling(5).mean()
    ohlc['SMA10'] = ohlc["Close"].rolling(10).mean()
    ohlc['SMA20'] = ohlc["Close"].rolling(20).mean()
    ohlc['SMA50'] = ohlc["Close"].rolling(50).mean()
    ohlc['SMA100'] = ohlc["Close"].rolling(100).mean()
    ohlc['SMA200'] = ohlc["Close"].rolling(200).mean()

    #Plotting SMA columns
    # ax.plot(ohlc['Date'], ohlc['SMA5'], color = 'blue', label = 'SMA5')
    # ax.plot(ohlc['Date'], ohlc['SMA10'], color = 'blue', label = 'SMA10')
    # ax.plot(ohlc['Date'], ohlc['SMA20'], color = 'blue', label = 'SMA20')
    ax[0].plot(ohlc['Date'], ohlc['SMA50'], color = 'green', label = 'SMA50')
    # ax.plot(ohlc.index, df['SMA100'], color = 'blue', label = 'SMA100')
    ax[0].plot(ohlc['Date'], ohlc['SMA200'], color = 'blue', label = 'SMA200')

    ax[1].plot(ohlc['Date'],News_sentiment)
    ax[2].plot(ohlc['Date'],Twitter_sentiment)

    #plt.savefig('/images/new_plot.png')
    return f1


def save_fig(f1):
    plt.savefig('/images/new_plot.png')
    return None
