from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json

def home(request):
    return redirect("stock_chart:display_ticker", ticker="RELIANCE")

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils.intervals import get_interval_config
import yfinance as yf
import pandas as pd

def retrieve_data(ticker, interval='1d'):
    try:
        ticker = ticker.replace('.NS', '') + '.NS'
        ticker_obj = yf.Ticker(ticker)
        
        valid_interval, period = get_interval_config(interval)
        print(f"Fetching data for {ticker} with interval: {valid_interval}, period: {period}")
        
        hist_df = ticker_obj.history(interval=valid_interval, period=period)
        
        if hist_df.empty:
            raise ValueError(f"No data found for {ticker}")

        hist_df = hist_df.reset_index()
        
        if 'Datetime' in hist_df.columns:
            hist_df['Datetime'] = hist_df['Datetime'].dt.strftime('%Y-%m-%dT%H:%M:%S')
        elif 'Date' in hist_df.columns:
            hist_df['Datetime'] = hist_df['Date'].dt.strftime('%Y-%m-%dT%H:%M:%S')
            hist_df = hist_df.drop(columns=['Date'])
        
        return hist_df, ticker_obj.info
        
    except Exception as e:
        print(f"Error retrieving data for {ticker}: {str(e)}")
        return pd.DataFrame(), {}

def display_ticker(request, ticker):
    hist_df, info = retrieve_data(ticker)
    
    if hist_df.empty:
        return render(request, "dashboard/main.html", {
            "ticker": ticker,
            "hist_data": "[]",
            "name": f"No Data Available for {ticker}",
            "industry": "N/A",
            "sector": "N/A",
            "watchlist": request.session.get('watchlist', [])
        })

    hist_data = hist_df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']].to_json(orient="records")
    watchlist = request.session.get('watchlist', [])

    return render(request, "dashboard/main.html", {
        "ticker": ticker,
        "hist_data": hist_data,
        "name": info.get("longName", ticker),
        "industry": info.get("industry", "N/A"),
        "sector": info.get("sector", "N/A"),
        "watchlist": watchlist
    })

@csrf_exempt
def manage_watchlist(request):
    if request.method == "POST":
        action = request.POST.get('action')
        
        if 'watchlist' not in request.session:
            request.session['watchlist'] = []
        
        watchlist = request.session['watchlist']
        
        if action == 'add':
            symbols = request.POST.get('ticker').split(',')  # Handle multiple symbols
            response_data = {'status': 'success', 'watchlist': []}
            
            for symbol in symbols:
                symbol = symbol.strip().replace('.NS', '')
                
                # Check if symbol already exists
                if any(item['symbol'] == symbol for item in watchlist):
                    continue
                    
                try:
                    ticker_obj = yf.Ticker(f"{symbol}.NS")
                    hist = ticker_obj.history(period='5d', interval='1d')
                    
                    if len(hist) >= 2:
                        last_price = hist['Close'].iloc[-1]
                        prev_close = hist['Close'].iloc[-2]
                        change = last_price - prev_close
                        change_percent = (change / prev_close * 100)
                        
                        watchlist.append({
                            'symbol': symbol,
                            'last_price': float(last_price),
                            'change_percent': float(change_percent)
                        })
                    else:
                        raise ValueError(f"Insufficient data for {symbol}")
                except Exception as e:
                    response_data['errors'] = response_data.get('errors', [])
                    response_data['errors'].append(f"Error adding {symbol}: {str(e)}")
                    
        elif action == 'delete':
            symbol = request.POST.get('ticker').replace('.NS', '')
            watchlist = [item for item in watchlist if item['symbol'] != symbol]
        
        elif action == 'clear':
            watchlist = []  # Clear the entire watchlist
            
        request.session['watchlist'] = watchlist
        request.session.modified = True
        return JsonResponse({'status': 'success', 'watchlist': watchlist})
    
    elif request.method == "GET":
        # Handle GET request to fetch current watchlist
        watchlist = request.session.get('watchlist', [])
        return JsonResponse({'status': 'success', 'watchlist': watchlist})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def update_watchlist_data(request):
    watchlist = request.session.get('watchlist', [])
    updated_watchlist = []
    
    for item in watchlist:
        try:
            ticker_obj = yf.Ticker(f"{item['symbol']}.NS")
            hist = ticker_obj.history(period='5d', interval='1d')
            
            if len(hist) >= 2:
                last_price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2]
                change = last_price - prev_close
                change_percent = (change / prev_close * 100)
                
                updated_watchlist.append({
                    'symbol': item['symbol'],
                    'last_price': float(last_price),
                    'change_percent': float(change_percent)
                })
            else:
                updated_watchlist.append({
                    'symbol': item['symbol'],
                    'error': 'Insufficient data'
                })
        except Exception as e:
            updated_watchlist.append({
                'symbol': item['symbol'],
                'error': str(e)
            })
    
    return JsonResponse({'status': 'success', 'watchlist': updated_watchlist})



def update_data(request, ticker, interval):
    hist_df, _ = retrieve_data(ticker, interval)
    
    if hist_df.empty:
        return JsonResponse([], safe=False)

    hist_data = hist_df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']].to_dict(orient="records")
    return JsonResponse(hist_data, safe=False)

