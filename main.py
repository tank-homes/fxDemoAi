from fastapi import FastAPI, Request, WebSocket
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import asyncio
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 静的ファイル配信
app.mount("/static", StaticFiles(directory="static"), name="static")

# データ取得
def fetch_data(pair, period='1d', interval='1m'):
    df = yf.download(pair, period=period, interval=interval, progress=False)
    return df

def prepare_features(data):
    data['Return'] = data['Close'].pct_change()
    data['Rolling Mean'] = data['Close'].rolling(5).mean()
    data['Rolling Std'] = data['Close'].rolling(5).std()
    data['HighLow'] = (data['Close'].rolling(3).max() - data['Close'].rolling(3).min())
    data['Slope'] = data['Rolling Mean'].diff()
    data = data.dropna()
    X = data[['Return', 'Rolling Mean', 'Rolling Std', 'HighLow', 'Slope']]
    y = data['Close']
    return X, y

# Webページ
@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# WebSocket
@app.websocket("/ws/auto_trade")
async def websocket_auto_trade(ws: WebSocket):
    await ws.accept()
    msg = await ws.receive_json()
    pair = msg.get("pair", "GBPJPY=X")
    balance = float(msg.get("initial_balance", 10000))
    buy_threshold = float(msg.get("buy_threshold", 1.01))
    sell_threshold = float(msg.get("sell_threshold", 0.99))
    duration_seconds = 180
    end_time = pd.Timestamp.now() + pd.Timedelta(seconds=duration_seconds)

    data = fetch_data(pair)
    if data.empty:
        await ws.send_json({"error": "データ取得失敗"})
        return

    X, y = prepare_features(data)
    model = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)
    model.fit(X, y)
    position = 0

    while pd.Timestamp.now() < end_time:
        latest_data = fetch_data(pair).iloc[-50:]
        if latest_data.empty:
            await asyncio.sleep(5)
            continue

        X_latest, _ = prepare_features(latest_data)
        latest_features = X_latest.iloc[-1:].values
        current_price = float(latest_data['Close'].iloc[-1])
        predicted_price = model.predict(latest_features)[0] * 1.002

        action = "hold"
        if predicted_price > current_price * buy_threshold and balance > 0:
            position += balance / current_price
            balance = 0
            action = "buy"
        elif predicted_price < current_price * sell_threshold and position > 0:
            balance += position * current_price
            position = 0
            action = "sell"

        total_assets = balance + position * current_price

        await ws.send_json({
            "time": datetime.now().strftime("%H:%M:%S"),
            "price": current_price,
            "predicted": predicted_price,
            "action": action,
            "balance": balance,
            "position": position,
            "total_assets": total_assets
        })
        await asyncio.sleep(5)
