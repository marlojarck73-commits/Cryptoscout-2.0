CryptoScout - quickstart
------------------------

1. Python installieren (3.9+).
2. virtualenv erstellen:
   python -m venv venv
   source venv/bin/activate   # (Windows: venv\Scripts\activate)
3. Abhängigkeiten:
   pip install -r requirements.txt
4. .env ausfüllen (API Keys)
5. Backend starten:
   uvicorn backend.main:app --reload
6. Frontend:
   frontend/index.html im Browser öffnen (oder später per Nginx / Render hosten)
7. Testen:
   /register, /login, /ohlc/BTC-USD, /backtest usw.

Viel Erfolg!
