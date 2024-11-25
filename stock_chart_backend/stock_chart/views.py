from django.shortcuts import render, redirect
import yfinance as yf
import pandas as pd

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

def retrieve_data(ticker):
    ticker_obj = yf.Ticker(ticker)
    hist_df = ticker_obj.history(period='1d', interval='1m')
    
    # Check if hist_df is empty
    if hist_df.empty:
        print(f"No data found for ticker: {ticker}")
        return pd.DataFrame(), {}

    hist_df = hist_df.reset_index()
    hist_df['Datetime'] = hist_df['Datetime'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    return hist_df, ticker_obj.info

def display_ticker(request, ticker):
    hist_df, info = retrieve_data(ticker)

    if hist_df.empty:
        return render(request, "dashboard/main.html", {
            "tickers": zip(tickers, [yf.Ticker(tkr).info['longName'] for tkr in tickers]),
            "ticker": ticker,
            "hist_data": "[]",  # No data available
            "name": "No Data",
            "industry": "",
            "sector": "",
        })

    # Prepare data for AmCharts
    hist_data = hist_df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']].to_json(orient="records")
    print(hist_data)  # Debugging line to check the data format

    return render(request, "dashboard/main.html", {
        "tickers": zip(tickers, [yf.Ticker(tkr).info['longName'] for tkr in tickers]),
        "ticker": ticker,
        "hist_data": hist_data,
        "name": info["longName"],
        "industry": info["industry"],
        "sector": info["sector"],
    })