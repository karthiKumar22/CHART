from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
from django.shortcuts import redirect

def home(request):
    return redirect("stock_chart:display_ticker", ticker="RELIANCE.NS")

def retrieve_data(ticker, interval='1d'):
    try:
        ticker_obj = yf.Ticker(ticker)
        interval = interval.lower().replace(' ', '').replace('minute', 'm').replace('hour', 'h').replace('day', 'd')
        
        interval_map = {
            '1m': ('1m', '5d'),    
            '2m': ('2m', '5d'),    
            '5m': ('5m', '5d'),   
            '15m': ('15m', '5d'),
            '30m': ('30m', '5d'),
            '60m': ('1h', '5d'),
            '1h': ('1h', '1mo'),
            '1d': ('1d', '1mo'),
            '5d': ('5d', '3mo'),
            '1wk': ('1wk', '1y'),
            '1mo': ('1mo', '5y'),
        }
        
        if interval in interval_map:
            valid_interval, period = interval_map[interval]
        else:
            valid_interval, period = '1d', '1mo'
            
        hist_df = ticker_obj.history(interval=valid_interval, period=period)
        
        if hist_df.empty:
            return pd.DataFrame(), {}

        hist_df = hist_df.reset_index()
        
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
            "ticker": ticker,
            "hist_data": "[]",
            "name": "No Data",
            "industry": "",
            "sector": "",
            "watchlist": request.session.get('watchlist', [])
        })

    hist_data = hist_df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']].to_json(orient="records")
    watchlist = request.session.get('watchlist', [])

    return render(request, "dashboard/main.html", {
        "ticker": ticker,
        "hist_data": hist_data,
        "name": info.get("longName", "N/A"),
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
            ticker = request.POST.get('ticker')
            try:
                ticker_info = yf.Ticker(ticker).info
                last_price = ticker_info.get('regularMarketPrice', 0)
                prev_close = ticker_info.get('previousClose', 0)
                change = last_price - prev_close
                change_percent = (change / prev_close * 100) if prev_close else 0
                
                watchlist.append({
                    'symbol': ticker,
                    'name': ticker_info.get('longName', ''),
                    'last_price': last_price,
                    'change': change,
                    'change_percent': change_percent
                })
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        elif action == 'delete':
            ticker = request.POST.get('ticker')
            watchlist = [item for item in watchlist if item['symbol'] != ticker]
        elif action == 'import':
            symbols = json.loads(request.POST.get('symbols', '[]'))
            for symbol in symbols:
                try:
                    ticker_info = yf.Ticker(symbol).info
                    last_price = ticker_info.get('regularMarketPrice', 0)
                    prev_close = ticker_info.get('previousClose', 0)
                    change = last_price - prev_close
                    change_percent = (change / prev_close * 100) if prev_close else 0
                    
                    watchlist.append({
                        'symbol': symbol,
                        'name': ticker_info.get('longName', ''),
                        'last_price': last_price,
                        'change': change,
                        'change_percent': change_percent
                    })
                except Exception as e:
                    # If there's an error with one symbol, continue with the others
                    print(f"Error adding {symbol}: {str(e)}")
                    continue
        
        request.session['watchlist'] = watchlist
        request.session.modified = True
        return JsonResponse({'status': 'success', 'watchlist': watchlist})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def update_watchlist_data(request):
    watchlist = request.session.get('watchlist', [])
    updated_watchlist = []
    
    for item in watchlist:
        try:
            ticker = yf.Ticker(item['symbol'])
            info = ticker.info
            last_price = info.get('regularMarketPrice', 0)
            prev_close = info.get('previousClose', 0)
            change = last_price - prev_close
            change_percent = (change / prev_close * 100) if prev_close else 0
            
            updated_watchlist.append({
                'symbol': item['symbol'],
                'name': item['name'],
                'last_price': last_price,
                'change': change,
                'change_percent': change_percent
            })
        except:
            updated_watchlist.append(item)
    
    return JsonResponse({'watchlist': updated_watchlist})



def update_data(request, ticker, interval):
    hist_df, _ = retrieve_data(ticker, interval)
    
    if hist_df.empty:
        return JsonResponse([], safe=False)

    hist_data = hist_df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']].to_dict(orient="records")
    return JsonResponse(hist_data, safe=False)