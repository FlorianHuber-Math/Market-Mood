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
    legend = 'Monthly Data'
    labels = ["January", "February", "March", "April", "May", "June", "July", "August"]
    values = [10, 10, 10, 7, 12, 4, 7, 200]
    #    return render_template('Stock_Sentiment.html', message=message, url='images/new_plot.png')
    return render_template('Stock_Sentiment.html', message=message, url = '',values=values, labels=labels, legend=legend)
'''
        df = model.market_mood(stock_ticker)
        ohlc = model.prepare_market_mood_for_plot(df)

        f1, ax = plt.subplots(3)
        candlestick_ohlc(ax[0], ohlc.values, width=.6, colorup='green', colordown='red')
        ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

        # Creating SMA columns
        ohlc['SMA5'] = ohlc["Close"].rolling(5).mean()
        ohlc['SMA20'] = ohlc["Close"].rolling(20).mean()
        ohlc['SMA10'] = ohlc["Close"].rolling(10).mean()
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

        ax[1].plot(ohlc['Date'],df['Sentiment News'])
        ax[2].plot(ohlc['Date'],df['Sentiment Twitter'])
        plt.savefig('app/static/chart.jpg')
'''
@app.route("/simple_chart")
def chart():
    legend = 'Monthly Data'
    labels = ["January", "February", "March", "April", "May", "June", "July", "August"]
    values = np.random.rand(1,8)
    return render_template('chart.html', values=values, labels=labels, legend=legend)

@app.route('/chart-data')
def chart_data():
    def generate_random_data():
            json_data = json.dumps(
                {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': random.random() * 100})
            yield f"data:{json_data}\n\n"
    return Response(generate_random_data(), mimetype='text/event-stream')

@app.route('/chart', methods=['POST'])
def signUpUser():
    user =  request.form['username'];
    def generate_random_data():
            json_data = json.dumps(
                {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': random.random() * 100})
    return Response(generate_random_data(), mimetype='text/event-stream')


@app.route('/data',  methods=['POST'])
def data():
    return jsonify({'results':random.sample(range(1,10),5)})


@app.route('/background_process')
def background_process():
	#try:
    lang = request.args.get('proglang', 0, type=str)
    return jsonify({'results':random.sample(range(1,10),5)})
		#if lang.lower() == 'python':
			#return jsonify(result='You are wise')
    #return jsonify({'results':random.sample(range(1,10),5)})
		#else:
			#return jsonify(result='Try again.')
    #        return jsonify({'results':random.sample(range(1,10),5)})
	#except Exception as e:
    #    return str(e)


@app.route('/process', methods=['POST'])
def process():

	name = request.form['ticker']

	if name:
		newName = name[::-1]

		return jsonify({'name' : newName})
        #return jsonify({'results':random.sample(range(1,10),5)})
	return jsonify({'error' : 'Missing data!'})
@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')
