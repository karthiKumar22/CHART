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

def retrieve_data(ticker, interval='1d'):
    """
    Retrieve stock data using yfinance with proper interval and period handling
    """
    try:
        ticker_obj = yf.Ticker(ticker)
        
        # Clean up the interval string
        interval = interval.lower().replace(' ', '').replace('minute', 'm').replace('hour', 'h').replace('day', 'd').replace('week', 'wk').replace('  month', 'mo').replace('year', 'y')
        print(f"Received interval: {interval}")

        # Updated interval mapping with proper periods
        interval_map = {
            '1m': ('1m', '5d'),    
            '2m': ('2m', '5d'),    
            '5m': ('5m', '5d'),   
            '15m': ('15m', '5d'),  # 15 minute data for 7 days
            '30m': ('30m', '5d'),  # 30 minute data for 7 days
            '60m': ('1h', '5d'),   # 1 hour data for 7 days
            '1h': ('1h', '1mo'),
            '1d': ('1d', '1mo'),   # Daily data for 1 month
            '5d': ('5d', '3mo'),   # 5-day data for 3 months
            '1wk': ('1wk', '1y'),  # Weekly data for 1 year
            '1mo': ('1mo', '5y'),  # Monthly data for 5 years
            '1y': ('1y', 'max')  # 3-month data for max period
        }
        
        # Get interval and period from mapping
        if interval in interval_map:
            valid_interval, period = interval_map[interval]
        else:
            valid_interval, period = '1d', '1mo'  # Default values
            
        print(f"Mapped interval: {valid_interval}, Period: {period}")
        
        # Fetch historical data with proper interval and period
        hist_df = ticker_obj.history(interval=valid_interval, period=period)
        print(f"Data retrieved: {hist_df.shape[0]} rows, Interval: {interval}, Valid Interval: {valid_interval}, Period: {period}")
        
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