import talib
import pandas_ta as pdta
from ta import momentum, trend, volume
import numpy as np

def calculate_technical_indicators(df):
    df['supertrend'] = pdta.supertrend(df['high'], df['low'], df['close'], length=10, multiplier=2.0)['SUPERT_10_2.0']
    df['adx'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=20)
    df['rsi'] = momentum.rsi(df['close'], window=14)
    df['aroon'] = talib.AROONOSC(df['high'], df['low'], timeperiod=10)
    df['ema_50'] = trend.ema_indicator(df['close'], window=50)
    df['ema_50_signal'] = np.where(df['close'] > df['ema_50'], 'Bullish', 'Bearish')
    
    df['ema_200'] = trend.ema_indicator(df['close'], window=200)
    df['ema_200_signal'] = np.where(df['close'] > df['ema_200'], 'Bullish', 'Bearish')

    df['cmf'] = volume.chaikin_money_flow(df['high'], df['low'], df['close'], df['tick_volume'], window=10)

    macd, signal_line, _ = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['macd_line'] = macd
    df['macd_signal_line'] = signal_line
    df['macd_signal'] = None
    df.loc[signal_line > macd, 'macd_signal'] = 'Bullish'
    df.loc[signal_line <= macd, 'macd_signal'] = 'Bearish'

    atr_period = 14
    atr = talib.ATR(df['high'], df['low'], df['close'], timeperiod=atr_period)
    df['atr'] = atr

    return df
