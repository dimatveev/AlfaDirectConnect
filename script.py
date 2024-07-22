import time
import requests
import os
from tinkoff.invest import Client, CandleInterval
import pandas as pd
from datetime import datetime, timedelta

TOKEN = os.environ.get('TINKOFF_TOKEN')
FAST_WINDOW = 7  # Окно для быстрой скользящей средней
SLOW_WINDOW = 15  # Окно для медленной скользящей средней
SYMBOLS = ['SBER', 'GAZP', 'LKOH']  # Список тикеров инструментов
POLLING_INTERVAL = 1  # Интервал обновления в секундах


def get_figi_by_ticker(ticker, client):
    response = client.instruments.shares()
    for share in response.instruments:
        if share.ticker == ticker:
            return share.figi
    raise ValueError("Ticker not found")


def get_candles(client, symbol, interval, from_date, to_date):
    figi = get_figi_by_ticker(symbol, client)
    candles = client.market_data.get_candles(
        figi=figi,
        interval=interval,
        from_=from_date,
        to=to_date
    )
    return candles


def calculate_sma(data, window):
    return data['close'].rolling(window=window).mean()


def send_signal(ticker, signal):
    url = f'http://localhost:5000/postsignal/{ticker}'
    data = {'signal': signal}
    try:
        response = requests.post(url, json=data)
        print(f"Signal sent for {ticker}. Server response: {response.text}")
    except Exception as e:
        print(f"Failed to send signal for {ticker}: {e}")


def get_signal(ticker):
    url = f'http://localhost:5000/getsignal/{ticker}'
    try:
        response = requests.get(url)
        return response.text.strip()
    except Exception as e:
        print(f"Failed to get signal for {ticker}: {e}")
        return None


def main():
    with Client(TOKEN) as client:
        while True:
            to_date = datetime.now()
            from_date = to_date - timedelta(days=1)  # минутные свечи за последние сутки

            for symbol in SYMBOLS:
                candles = get_candles(client, symbol, CandleInterval.CANDLE_INTERVAL_1_MIN, from_date, to_date)

                data = pd.DataFrame([{
                    'time': candle.time,
                    'open': candle.open.units + candle.open.nano / 10 ** 9,
                    'close': candle.close.units + candle.close.nano / 10 ** 9,
                    'high': candle.high.units + candle.high.nano / 10 ** 9,
                    'low': candle.low.units + candle.low.nano / 10 ** 9,
                    'volume': candle.volume
                } for candle in candles.candles])

                if not data.empty:
                    data['fast_sma'] = calculate_sma(data, FAST_WINDOW)
                    data['slow_sma'] = calculate_sma(data, SLOW_WINDOW)

                    data['signal'] = 'No Signal'
                    data.loc[(data['fast_sma'].shift(1) >= data['slow_sma'].shift(1)) & (
                                data['fast_sma'] >= data['slow_sma']), 'signal'] = 'В лонге'
                    data.loc[(data['fast_sma'].shift(1) <= data['slow_sma'].shift(1)) & (
                                data['fast_sma'] <= data['slow_sma']), 'signal'] = 'В шорте'
                    data.loc[(data['fast_sma'].shift(1) <= data['slow_sma'].shift(1)) & (
                                data['fast_sma'] >= data['slow_sma']), 'signal'] = 'Вошли в лонг'
                    data.loc[(data['fast_sma'].shift(1) >= data['slow_sma'].shift(1)) & (
                                data['fast_sma'] <= data['slow_sma']), 'signal'] = 'Вошли в шорт'

                    # Проверка на сигналы и отправка
                    last_signal = data.iloc[-1]['signal']
                    current_flag = get_signal(symbol)

                    if current_flag == "NULL":
                        if last_signal == 'Вошли в лонг':
                            send_signal(symbol, "1")
                        elif last_signal == 'Вошли в шорт':
                            send_signal(symbol, "-1")

                    print(data[['time', 'close', 'fast_sma', 'slow_sma', 'signal']].tail(1))

            time.sleep(POLLING_INTERVAL)


if __name__ == "__main__":
    main()
