import os
import json
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from binance.client import Client
from binance.exceptions import BinanceAPIException

# -----------------------------
# Benutzerverwaltung
# -----------------------------
USER_FILE = os.path.join(os.path.dirname(__file__), "users.json")
ABO_PREIS = 9.99

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f:
            json.dump({}, f)
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

users = load_users()
current_user = None
session = {}

# -----------------------------
# Login/Register Funktionen
# -----------------------------
def register(username, password):
    global users
    if username.strip() == "" or password.strip() == "":
        return "Benutzername und Passwort dürfen nicht leer sein"
    elif username in users:
        return "Benutzer existiert bereits"
    else:
        users[username] = {"password": hash_password(password), "abo": False, "abo_end_date": None, "is_admin": False}
        save_users(users)
        return "Account erstellt! Bitte einloggen."

def login(username, password):
    global current_user, session
    if username in users and users[username]["password"] == hash_password(password):
        current_user = username
        session["current_user"] = username
        session["is_admin"] = users[username].get("is_admin", False)
        return f"Erfolgreich eingeloggt als {username}"
    else:
        return "Falscher Benutzername oder Passwort"

# -----------------------------
# Abo-Prüfung
# -----------------------------
def check_abo(user_data):
    if user_data["abo"] and user_data["abo_end_date"]:
        return datetime.strptime(user_data["abo_end_date"], '%Y-%m-%d') >= datetime.today()
    return False

def activate_abo(user_data):
    user_data["abo"] = True
    user_data["abo_end_date"] = (datetime.today() + timedelta(days=30)).strftime('%Y-%m-%d')
    users[current_user] = user_data
    save_users(users)

# -----------------------------
# Binance API Platzhalter
# -----------------------------
binance_client = None

def connect_binance(api_key, api_secret):
    global binance_client
    try:
        binance_client = Client(api_key, api_secret)
        return "Binance verbunden"
    except BinanceAPIException as e:
        return f"Fehler: {e}"

# -----------------------------
# Dashboard / Daten
# -----------------------------
coins = ["BTC-USD", "ETH-USD", "BNB-USD", "ADA-USD", "XRP-USD"]
selected_coin = coins[0]

def load_data(coin):
    data = yf.download(coin, period="3mo", interval="1h", auto_adjust=True)
    data.dropna(inplace=True)

    # SMA
    data["SMA50"] = data["Close"].rolling(50).mean()
    data["SMA200"] = data["Close"].rolling(200).mean()
    data["Signal_SMA"] = np.where(data["SMA50"] > data["SMA200"], 1, -1)

    # RSI
    delta = data["Close"].diff()
    gain = delta.copy()
    gain[delta <= 0] = 0
    loss = -delta.copy()
    loss[delta >= 0] = 0
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    data["RSI"] = 100 - (100 / (1 + rs))
    data["Signal_RSI"] = np.where(data["RSI"] < 30, 1, np.where(data["RSI"] > 70, -1, 0))

    # Kombi-Signal
    data["Signal"] = data["Signal_SMA"] + data["Signal_RSI"]
    return data

def generate_chart(data):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=data.index, open=data["Open"], high=data["High"], low=data["Low"], close=data["Close"], name="Preis"))
    fig.add_trace(go.Scatter(x=data.index, y=data["SMA50"], line=dict(color="blue"), name="SMA50"))
    fig.add_trace(go.Scatter(x=data.index, y=data["SMA200"], line=dict(color="orange"), name="SMA200"))

    buy_signals = data[data["Signal"] > 0]
    sell_signals = data[data["Signal"] < 0]

    fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals["Close"],
                             mode="markers", marker=dict(symbol="triangle-up", color="green", size=12), name="Kauf-Signal"))
    fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals["Close"],
                             mode="markers", marker=dict(symbol="triangle-down", color="red", size=12), name="Verkaufs-Signal"))
    return fig

# -----------------------------
# Backtesting
# -----------------------------
def backtest(data):
    # Platzhalter: nur Close-Preise anzeigen
    return data["Close"]

# -----------------------------
# CSV Export
# -----------------------------
def export_csv(logs, filename):
    df = pd.DataFrame(logs)
    df.to_csv(filename, index=False)

# -----------------------------
# Admin Funktionen
# -----------------------------
def list_users():
    return users

def set_admin(username):
    if username in users:
        users[username]["is_admin"] = True
        save_users(users)

# -----------------------------
# Beispielaufrufe (lokal testen)
# -----------------------------
if __name__ == "__main__":
    # Test-Accounts
    print(register("testuser", "pass123"))
    print(login("testuser", "pass123"))

    user_data = users[current_user]
    print("Abo aktiv:", check_abo(user_data))
    activate_abo(user_data)
    print("Abo aktiv:", check_abo(user_data))

    data = load_data(selected_coin)
    fig = generate_chart(data)
    print("Chart erstellt für", selected_coin)

    export_csv([{"coin": "BTC", "price": 50000}], "logs.csv")
    print("CSV exportiert")

    set_admin("testuser")
    print("Users:", list_users())
