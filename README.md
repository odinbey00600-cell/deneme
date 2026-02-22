# Institutional-Grade Binance USDT-M Futures Trading Bot

Bu repo, Binance USDT-M Futures üzerinde **ML + RL + kural tabanlı hibrit** mimari ile çalışan otomatik trading botu içerir.

## Özellikler
- Live Futures execution (UMFutures)
- Low-risk scalping (1m) + swing (15m)
- ML supervised filter (RandomForest / Logistic Regression)
- RL DQN timing destek katmanı
- Multi-symbol portfolio (BTC, ETH, SOL, BNB)
- ATR bazlı SL/TP + RR >= 1:2 + dinamik leverage
- Daily loss stop, consecutive loss cooldown, safe mode
- Docker ile 7/24 deployment
- Telegram alert + log + analytics

## Kurulum
```bash
cp .env.example .env
# .env dosyasına key/secret gir
pip install -r requirements.txt
```

## Eğitim
```bash
python scripts/train_ml.py
python scripts/train_rl.py
```

## Çalıştırma
```bash
python src/main.py
```

## Docker
```bash
docker compose up -d --build
```

## Güvenlik Notları
- API anahtarları sadece `.env` içinde saklanır.
- Varsayılan risk per trade `%0.5` sınırındadır.
- Daily max loss tetiklenince yeni işlem açılmaz.
- Safe mode tetiklenince bot kendini durdurur.
