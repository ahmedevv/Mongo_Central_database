from common_imports import *
from mongodb_connection import * 
from mongo_airtable_connector import *


def read_data(file_path):
    """Reads data from a CSV file and returns a DataFrame."""
    return pd.read_csv(file_path)

def generate_signals(df_5m, df_30m, df_1h, df_4h):
    time_horizons = {"5m": df_5m, "30m": df_30m, "1h": df_1h, "4h": df_4h}

    # Ensure the 'time' column is in datetime format for each DataFrame
    for df in time_horizons.values():
        df["time"] = pd.to_datetime(df["time"])
        df["time"] = df["time"]  # - timedelta(hours=2)

    current_day = df_5m.iloc[-1]['time']

    mongo_id = df_1h.iloc[-1]['time']
    mongo_id=str(mongo_id)

    current_day_date = current_day.date()
    first_candle_df_1h = df_1h[df_1h['time'].dt.date == current_day_date]
    opening_price = first_candle_df_1h.iloc[0]['open']
    closing_price = df_5m.iloc[-1]['open']

    current_day_date = pd.to_datetime(current_day_date)
    bias_4h_zone = None
    bias_1h_zone = None

    biasness_hour = "N/A"
    bias__list = []
    
    current_row = -1
    previous_row = -2

    df_1h_row = df_1h.iloc[[previous_row]]
    df_4h_row = df_4h.iloc[[previous_row]]

    prev_4h_data = pd.DataFrame()
    prev_1h_data = pd.DataFrame()

    ################################################################
    ###################  CHECK 4H Biasness  ########################
    if not df_4h_row.empty:
        back_100_candles = df_4h_row.index-100
        df_4h_100back_row = df_4h.iloc[back_100_candles]
        df_4h_100back_row.reset_index(drop=True,inplace=True)
        df_4h_row.reset_index(drop=True, inplace=True)


        linear_regression_4h_100_back = df_4h_100back_row.iloc[0]['real']
        linear_regression_4h = df_4h_row.iloc[0]["real"]
        prev_4h_data = df_4h.iloc[[previous_row-1]]

        if not df_4h_row.empty:

            if df_4h_row.iloc[0]['close'] > linear_regression_4h:
                bias_4h_zone = 'Short'
                biasness_hour = "4H"
                bias__list.append(biasness_hour)
            elif df_4h_row.iloc[0]['close'] <= linear_regression_4h:
                bias_4h_zone = 'Long'
                biasness_hour = "4H"
                bias__list.append(biasness_hour)
    


    ################################################################
    ###################  CHECK 1H Biasness  ########################

    if not df_1h_row.empty:
        back_100_candles = df_1h_row.index-100
        df_1h_100back_row = df_1h.iloc[back_100_candles]

        df_1h_100back_row.reset_index(drop=True,inplace=True)
        df_1h_row.reset_index(drop=True, inplace=True)

        linear_regression_1h_100_back = df_1h_100back_row.iloc[0]['real']
        linear_regression_1h = df_1h_row.iloc[0]["real"]
        prev_1h_data = df_1h.iloc[[previous_row-1]]
        if not df_1h_row.empty:
            if df_1h_row.iloc[0]['close'] > linear_regression_1h:
                bias_1h_zone = 'Short'
                biasness_hour = "1H"
                bias__list.append(biasness_hour)
            elif df_1h_row.iloc[0]['close'] <= linear_regression_1h:
                bias_1h_zone = 'Long'
                biasness_hour = "1H"
                bias__list.append(biasness_hour)
            
    
    ### Bias_score_list
    bias_score_dict = {'Long': 1, 'Short': -1}
    bias_score_list = [bias_score_dict.get(bias_4h_zone, 0), bias_score_dict.get(bias_1h_zone, 0)]


    ######## Pearson Calculations -------------------------------- ########
    if not df_4h_row.empty:
    
        pearson_4h_value = df_4h_row.iloc[0]['pearson_r']
        pearson_1h_value = df_1h_row.iloc[0]['pearson_r']        

        ### Pearson R Values on basis of last 100 candles linear regression
        candles_100_diff_4h = linear_regression_4h - linear_regression_4h_100_back
        if candles_100_diff_4h>0:
            pearson_4h_value = abs(pearson_4h_value)
        elif candles_100_diff_4h <0:
            pearson_4h_value = -1*(pearson_4h_value)

        candles_100_diff_1h = linear_regression_1h - linear_regression_1h_100_back
        if candles_100_diff_1h>0:
            pearson_1h_value = abs(pearson_1h_value)
        elif candles_100_diff_1h <0:
            pearson_1h_value = -1*(pearson_1h_value)
        
        if pearson_4h_value > 0:
            bias_score_list.append(1)
        elif pearson_4h_value < 0:
            bias_score_list.append(-1)
        if pearson_1h_value > 0:
            bias_score_list.append(1)
        elif pearson_1h_value < 0:
            bias_score_list.append(-1)

    


    prev_4h_data.reset_index(drop=True,inplace=True)
    prev_1h_data.reset_index(drop=True,inplace=True)
    if len(prev_1h_data)>0:

        pre_pearson_4h_value = prev_4h_data.iloc[0]['pearson_r']
        pre_pearson_1h_value = prev_1h_data.iloc[0]['pearson_r']


        diff_4h_pearson = abs(pearson_4h_value) - abs(pre_pearson_4h_value)  #prev_diff_4h.iloc[0]['diff']
        diff_1h_pearson = abs(pearson_1h_value) - abs(pre_pearson_1h_value)  #prev_diff_1h.iloc[0]['diff']
        
        
        if pearson_4h_value>0:
            diff_4h_pearson = pearson_4h_value - pre_pearson_4h_value
        else:
            diff_4h_pearson = abs(pearson_4h_value) - abs(pre_pearson_4h_value)
            diff_4h_pearson = diff_4h_pearson*-1

        if pearson_1h_value>0:
            diff_1h_pearson = pearson_1h_value - pre_pearson_1h_value
        else:
            diff_1h_pearson = abs(pearson_1h_value) - abs(pre_pearson_1h_value)
            diff_1h_pearson = diff_1h_pearson*-1

        ### Calculate Score List and Find Daily Biasness
        if diff_4h_pearson >0:
            bias_score_list.append(1)
        elif diff_4h_pearson <0:
            bias_score_list.append(-1)

        if diff_1h_pearson >0:
            bias_score_list.append(1)
        elif diff_1h_pearson <0:
            bias_score_list.append(-1)
        
    sentiment_result = None
    result = None
    sentiment_result = sum(bias_score_list)
    if sentiment_result > 0:
        result = 'bullish'
    elif sentiment_result < 0:
        result = 'bearish'

    ### Get first occurence if it is 4H or 1H
    if len(bias__list) >0:
        biasness_hour = bias__list[0]
        bias__list = []

    direction_daily_points = closing_price-opening_price
    print('H4 Pearson Value ',pearson_4h_value,'===',' Previous Pearson Value',pre_pearson_4h_value)
    print('H4 Pearson Difference',diff_4h_pearson)
    print('H1 Pearson Value ',pearson_1h_value,'===',' Previous Pearson Value',pre_pearson_1h_value)
    print('H1 Pearson Difference',diff_1h_pearson)
    print('----------------------------------------------------------------')
    
    adx_4h = df_4h.iloc[-1]['adx']
    cmf_4h = df_4h.iloc[-1]['cmf']
    ema_50_4h = df_4h.iloc[-1]['ema_50_signal']
    macd_4h = df_4h.iloc[-1]['macd_signal']
    supertrend_4h = df_4h.iloc[-1]['supertrend']
    close_4h = df_4h.iloc[-1]['close']

    if close_4h>supertrend_4h:
        supertrend_4h = 'Bullish'
    else:
        supertrend_4h = 'Bearish'
    
    
    
    adx_1h = df_1h.iloc[-1]['adx']
    cmf_1h = df_1h.iloc[-1]['cmf']
    supertrend_1h = df_1h.iloc[-1]['supertrend']
    close_1h = df_1h.iloc[-1]['close']
    
    if close_1h > supertrend_1h:
        supertrend_1h = 'Bullish'
    else:
        supertrend_1h = 'Bearish'
    

    ema_50_1h = df_1h.iloc[-1]['ema_50_signal']
    ema_200_1h = df_1h.iloc[-1]['ema_200_signal']
    macd_1h = df_1h.iloc[-1]['macd_signal']
    atr_1h = df_1h.iloc[-1]['atr']

    insert_1h_into_mongo(mongo_id,bias_1h_zone,pearson_1h_value,adx_1h,cmf_1h,supertrend_1h,ema_50_1h,ema_200_1h,macd_1h,atr_1h)
    insert_4h_1h_airtable(mongo_id,bias_4h_zone,pearson_4h_value,adx_4h,cmf_4h,supertrend_4h,ema_50_4h,macd_4h,bias_1h_zone,pearson_1h_value,adx_1h,cmf_1h,supertrend_1h,ema_50_1h,macd_1h)
    print('--------------------------------')

def get_data_1h():
    initialize_mt5()

    # Define assest list, time_frame list to download data
    assets_list = ['US500']
    timeframes = [mt5.TIMEFRAME_M5, mt5.TIMEFRAME_M30, mt5.TIMEFRAME_H1, mt5.TIMEFRAME_H4]
    
    # Speicfy the folder and candles to download data
    data_folder = "data"  
    num_candles_5m = 800
    num_candles_4h = 800
    num_candles_1h = 500

    # Call the function to download and save data
    downloaded_df_list = download_save_data(assets_list, timeframes, data_folder, num_candles_5m, num_candles_4h, num_candles_1h)
    
    # Shutdown MetaTrader5
    shutdown_mt5()
    
    
    # Read data into pandas DataFrames
    df_5m = downloaded_df_list[0] #read_data(FILE_PATH_5M)
    df_30m = downloaded_df_list[1] #read_data(FILE_PATH_30M)
    df_1h = downloaded_df_list[2] #read_data(FILE_PATH_1H)
    df_4h = downloaded_df_list[3] #read_data(FILE_PATH_4H)

    ### Drop last candle
    df_4h = df_4h.drop(df_4h.index[-1])
    df_4h.reset_index(drop=True,inplace=True)

    df_1h = df_1h.drop(df_1h.index[-1])
    df_1h.reset_index(drop=True,inplace=True)

    df_5m = df_5m.drop(df_5m.index[-1])
    df_5m.reset_index(drop=True,inplace=True)

    
    generate_signals(df_5m, df_30m, df_1h, df_4h)



# Wait for 1 minute
# get_data_1h()

while True:
    current_time = time.localtime()
    if current_time.tm_min == 0:
        print(current_time)
        get_data_1h()
        time.sleep(70)
         
    time.sleep(15)  # Sleep for 1 minute before checking again




