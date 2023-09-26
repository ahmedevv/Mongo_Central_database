import os
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import talib
from indicator_utils import calculate_technical_indicators


data_folder = "data"  
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# Timeframe names dictionary
timeframe_names = {
    mt5.TIMEFRAME_M1: 'M1',
    mt5.TIMEFRAME_M5: 'M5',
    mt5.TIMEFRAME_M30: 'M30',
    mt5.TIMEFRAME_H1: 'H1',
    mt5.TIMEFRAME_H4: 'H4'
}

def initialize_mt5():
    mt5.initialize(login=51329254, password="DA7kLBPN", server="ICMarketsSC-Demo")

def shutdown_mt5():
    mt5.shutdown()

def calculate_linear_regression_channel_bands(data):
    std_dev_multiplier = 1
    std_dev = std_dev_multiplier * talib.STDDEV(data, timeperiod=20)
    upper_band = data + std_dev
    lower_band = data - std_dev
    mid_band = (upper_band + lower_band) / 2
    upper_line_50 = mid_band + (0.5 * (upper_band - lower_band))
    lower_line_50 = mid_band - (0.5 * (upper_band - lower_band))
    return upper_band, lower_band, mid_band, upper_line_50, lower_line_50


def download_and_save_data(asset, timeframe, num_candles, data_folder, std_dev_multiplier=3.7, band_percentage=0.5):
    data = mt5.copy_rates_from_pos(asset, timeframe, 0, num_candles)
    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"], unit="s")

    df = calculate_technical_indicators(df)

    df['real']  = None
    df['diff'] = None
    for curr in range(100, len(df)):
        df_chunk = df.iloc[curr - 100:curr]
        close = df_chunk['close']

        if not len(close) == 100:
            print('length issue')
            exit(0)

        if len(close) >= 100:
            df_last_250 = df_chunk
            x = np.arange(len(df_last_250))
            slope, intercept = np.polyfit(x, df_last_250['close'], 1)
            linear_regression_line = slope * x + intercept

            std_dev = np.std(df_last_250['close'])

            upper_channel_line = linear_regression_line + (std_dev_multiplier * std_dev)
            lower_channel_line = linear_regression_line - (std_dev_multiplier * std_dev)

            upper_line_adjust = (upper_channel_line[-1] + linear_regression_line[-1]) / 2
            lower_line_adjust = (lower_channel_line[-1] + linear_regression_line[-1]) / 2

            upper_line_50_adjust = lower_line_adjust + band_percentage * (upper_line_adjust - lower_line_adjust)
            lower_line_50_adjust = upper_line_adjust - band_percentage * (upper_line_adjust - lower_line_adjust)

            df.at[curr, 'real'] = linear_regression_line[-1]
            df.at[curr, 'upper_band'] = upper_line_adjust
            df.at[curr, 'lower_band'] = lower_line_adjust
            df.at[curr, 'mid_band'] = (upper_line_adjust + lower_line_adjust) / 2
            df.at[curr, 'upper_line_50'] = upper_line_50_adjust
            df.at[curr, 'lower_line_50'] = lower_line_50_adjust

    timeframe_str = timeframe_names.get(timeframe, str(timeframe))  # Get timeframe string from dictionary
    filename = f"{asset}_{timeframe_str}.csv"  # Generate filename based on asset and timeframe
    filepath = os.path.join(data_folder, filename)  # Create the full file path
    df = df[df['real'].notna()]
    df.reset_index(drop=True,inplace=True)
    df['real'] = df['real'].astype(int)
    
    df['pearson_r'] = talib.CORREL(df['real'],df['high'], timeperiod=100) #calculate_pearson_r(df, periods)
    df['diff'] = df['pearson_r'] - df['pearson_r'].shift(1)

    # df = df[df['diff'].notna()]
    df.reset_index(drop=True,inplace=True)
    


   
    return df



def download_save_data(assets_list, timeframes, data_folder, num_candles_5m, num_candles_4h, num_candles_1h):
    df_list = []
    for asset in assets_list:
        for timeframe in timeframes:
            if timeframe == mt5.TIMEFRAME_M5:
                df_temp = download_and_save_data(asset, timeframe, num_candles_5m,data_folder)
            elif timeframe == mt5.TIMEFRAME_H4:
                df_temp = download_and_save_data(asset, timeframe, num_candles_4h,data_folder)
            elif timeframe == mt5.TIMEFRAME_H1:
                df_temp = download_and_save_data(asset, timeframe, num_candles_1h,data_folder)
            else:
                df_temp = download_and_save_data(asset, timeframe, 2500,data_folder)  # Download 30000 candles for other timeframes
            df_list.append(df_temp)
    return df_list
# Initialize MetaTrader5
# initialize_mt5()

