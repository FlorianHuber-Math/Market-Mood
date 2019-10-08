from flask import render_template, jsonify, Flask, redirect, url_for, request, Response
from app import app
import json
import random
import time
from datetime import datetime
from app import model
import random
import numpy as np
import os
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib import style
import matplotlib.pyplot as plt
import numpy as np

import plotly
import plotly.graph_objs as go

import pandas as pd
import numpy as np
import json
import requests
from bs4 import BeautifulSoup


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/suggestions')
def suggestions():
    text = request.args.get('jsdata')
    if text:
        df = model.market_mood(text)
        adj_close = df['Adj Close']
        news_sentiment = df['Sentiment News']*max( df['Adj Close'])
        twitter_sentiment = df['Sentiment Twitter']*max( df['Adj Close'])
        labels = df.index.values
        average_twitter =df['Sentiment Twitter']
        average_twitter =average_twitter.replace(0, np.NaN).mean()
        average_news = df['Sentiment News']
        average_news =average_news.replace(0, np.NaN).mean()
        start_date = str(df.index.values[0])[0:10]
        end_date =str(df.index.values[-1])[0:10]




            #print(suggestions_list)

        return render_template('chart.html', values=adj_close, values_twitter=twitter_sentiment, values_news=news_sentiment, labels_date=labels,
        average_twitter=average_twitter, average_news=average_news, start_date=start_date,end_date=end_date)


@app.route('/Stock Sentiment', methods=["GET", "POST"])
def stock_sentiment():
    if request.method == "POST":
        stock_ticker = request.form["stock_ticker"]
        message = stock_ticker
    else:
        message ='no ticker'
    #    return render_template('Stock_Sentiment.html', message=message, url='images/new_plot.png')
    return render_template('Stock_Sentiment.html', message=message, url = '')

@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')
