from django.shortcuts import render, redirect
from django.http import JsonResponse
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

tickers = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "BHARTIARTL.NS",
    "SBIN.NS", "INFY.NS", "LICI.NS", "ITC.NS", "HINDUNILVR.NS", "LT.NS",
    "BAJFINANCE.NS", "HCLTECH.NS", "MARUTI.NS", "SUNPHARMA.NS", "ADANIENT.NS",
    "KOTAKBANK.NS", "TITAN.NS", "ONGC.NS", "TATAMOTORS.NS", "NTPC.NS",
    "AXISBANK.NS", "DMART.NS", "ADANIGREEN.NS", "ADANIPORTS.NS", "ULTRACEMCO.NS",
    "ASIANPAINT.NS", "COALINDIA.NS", "BAJAJFINSV.NS", "BAJAJ-AUTO.NS",
    "POWERGRID.NS", "NESTLEIND.NS", "WIPRO.NS", "M&M.NS", "IOC.NS",
    "JIOFIN.NS", "HAL.NS", "DLF.NS", "ADANIPOWER.NS", "JSWSTEEL.NS",
    "TATASTEEL.NS", "SIEMENS.NS", "IRFC.NS", "VBL.NS", "ZOMATO.NS",
    "PIDILITIND.NS", "GRASIM.NS", "SBILIFE.NS", "BEL.NS",
]

def home(request):
    return redirect("stock_chart:display_ticker", "RELIANCE.NS")

def retrieve_data(ticker, interval='1d', period='1mo'):
    """
    Retrieve stock data using yfinance with proper interval and period handling
    """
    try:
        ticker_obj = yf.Ticker(ticker)
        
        interval_map = {
            '1m': '1m', '2m': '2m', '5m': '5m', '15m': '15m',
            '30m': '30m', '60m': '1h', '90m': '1h', 
            '1d': '1d', '5d': '5d', '1wk': '1wk', '1mo': '1mo',
            '3mo': '3mo'
        }
        
        valid_interval = interval_map.get(interval, '1d')
        
        # Adjust period based on interval
        if valid_interval in ['1m', '2m', '5m', '15m', '30m', '1h']:
            period = '1d'
        elif valid_interval == '1d':
            period = '1mo'
        elif valid_interval in ['5d', '1wk']:
            period = '3mo'
        elif valid_interval == '1mo':
            period = '1y'
        elif valid_interval == '3mo':
            period = '2y'
        
        hist_df = ticker_obj.history(interval=valid_interval, period=period)
        print (hist_df, interval, valid_interval, valid_interval)
        
        if hist_df.empty:
            print(f"No data found for ticker: {ticker}")
            return pd.DataFrame(), {}

        hist_df = hist_df.reset_index()
        
        # Ensure Datetime column is consistent
        if 'Datetime' in hist_df.columns:
            hist_df['Datetime'] = hist_df['Datetime'].dt.strftime('%Y-%m-%dT%H:%M:%S')
        elif 'Date' in hist_df.columns:
            hist_df['Datetime'] = hist_df['Date'].dt.strftime('%Y-%m-%dT%H:%M:%S')
            hist_df = hist_df.drop(columns=['Date'])
        
        return hist_df, ticker_obj.info
        
    except Exception as e:
        print(f"Error retrieving data: {str(e)}")
        return pd.DataFrame(), {}

def display_ticker(request, ticker):
    hist_df, info = retrieve_data(ticker)

    if hist_df.empty:
        return render(request, "dashboard/main.html", {
            "tickers": zip(tickers, [yf.Ticker(tkr).info['longName'] for tkr in tickers]),
            "ticker": ticker,
            "hist_data": "[]",
            "name": "No Data",
            "industry": "",
            "sector": "",
        })

    hist_data = hist_df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']].to_json(orient="records")
      # Debugging line to check the data format

    return render(request, "dashboard/main.html", {
        "tickers": zip(tickers, [yf.Ticker(tkr).info['longName'] for tkr in tickers]),
        "ticker": ticker,
        "hist_data": hist_data,
        "name": info.get("longName", "N/A"),
        "industry": info.get("industry", "N/A"),
        "sector": info.get("sector", "N/A"),
    })

def update_data(request, ticker, interval):
    """
    Update chart data based on interval selection
    """
    try:
        hist_df, _ = retrieve_data(ticker, interval=interval)
        
        if hist_df.empty:
            return JsonResponse([], safe=False)

        hist_data = hist_df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']].to_dict(orient="records")
        return JsonResponse(hist_data, safe=False)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)