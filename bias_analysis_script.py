from common_imports import *
from mongodb_connection import * 
from mongo_airtable_connector import *



def calcualte_actual_bias(first_candle_df_1h,current_day_hour,current_day_minute,first_candle_price,actual_bias_time):
    desired_candle = first_candle_df_1h[first_candle_df_1h['time'].dt.time == actual_bias_time]
    
    if not desired_candle.empty:
        #if current_day_hour == 13 and current_day_minute == 0:
        if len(desired_candle)>1:
            desired_candle = desired_candle.iloc[0]
        actual_bias_close_price = desired_candle.iloc[0]['close']
        actual_bias_diff = actual_bias_close_price - first_candle_price
        return actual_bias_diff
            ##appending_bias(actual_bias_diff)
    else:
        return 0



def read_data(file_path):
    """Reads data from a CSV file and returns a DataFrame."""
    return pd.read_csv(file_path)



def generate_signals(df_5m, df_30m, df_1h, df_4h, target_date_):
    time_horizons = {"5m": df_5m, "30m": df_30m, "1h": df_1h, "4h": df_4h}

    am_session_points = None
    pm_session_points = None
    previous_daily_close = None
    actual_bias_time = dt.strptime('13:00', '%H:%M').time()

    # Ensure the 'time' column is in datetime format for each DataFrame
    for df in time_horizons.values():
        df["time"] = pd.to_datetime(df["time"])
        df["time"] = df["time"] - timedelta(hours=2)

    current_day = df_5m.iloc[-1]['time']
    current_day_date = current_day.date()
    
    current_day_hour = current_day.hour
    current_day_minute = current_day.minute
    first_candle_df_1h = df_1h[df_1h['time'].dt.date == current_day_date]
    first_candle_df_1h.reset_index(drop=True,inplace=True)
    first_candle_price = first_candle_df_1h.iloc[0]['open']

    ### OHLC for Daily Outcome
    open_price_ = first_candle_df_1h.iloc[0]['open']
    close_price_ = first_candle_df_1h.iloc[0]['close']
    high_price_ = first_candle_df_1h.iloc[0]['high']
    low_price_ = first_candle_df_1h.iloc[0]['low']
    
    #### Current Day Date
    current_day_date = pd.to_datetime(current_day_date)
    previous_day_date = current_day_date - timedelta(days=1)
    day_before_yesterday_date = current_day_date - timedelta(days=2)

    # Filter rows with the given date
    current_day_data = df_1h[df_1h['time'].dt.date == current_day_date.date()]
    previous_day_data = df_1h[df_1h['time'].dt.date == previous_day_date.date()]
    day_before_yesterday_data = df_1h[df_1h['time'].dt.date == day_before_yesterday_date.date()]




    ############## CURRENT DAY DATAFRAME
    previous_day_12pm = previous_day_data[previous_day_data['time'].dt.hour == 12]
    current_day_00am  = current_day_data[current_day_data['time'].dt.hour == 1] 
    current_day_12pm = current_day_data[current_day_data['time'].dt.hour == 12]

    if not current_day_00am.empty and not previous_day_12pm.empty: #and current_day_hour == 1: #and current_day_minute == 0:
        current_day_00am.reset_index(drop=True,inplace=True)
        previous_day_12pm.reset_index(drop=True,inplace=True)
        pm_session_points = current_day_00am.iloc[0]['open'] - previous_day_12pm.iloc[0]['close']
        update_pm_session_points(pm_session_points,previous_day_date)
        update_pm_session_points_daily_outcome(pm_session_points,previous_day_date)

        ############### Update Daily Outcome -- Current Daily Closed --------------------------------
        high = day_before_yesterday_data['high'].max()
        low = day_before_yesterday_data['low'].min()
        if previous_day_data.iloc[-1]['close']> high:
            previous_daily_close = 'Bullish'
        elif previous_day_data.iloc[-1]['close'] < low:
            previous_daily_close = 'Bearish'
        else:
            previous_daily_close = 'Neutral'

        if previous_daily_close is not None:
            update_daily_close(previous_daily_close,previous_day_date)




    if not current_day_00am.empty and not current_day_12pm.empty:
        current_day_00am.reset_index(drop=True, inplace=True)
        current_day_12pm.reset_index(drop=True,inplace=True)
        am_session_points = current_day_12pm.iloc[0]['close'] - current_day_00am.iloc[0]['open']    
        update_am_session_points(am_session_points,current_day_date)
        update_am_session_points_daily_outcome(am_session_points,current_day_date)
    


    
    time_filter_start = "01:00:00"
    df_30m_day_open_candles = df_30m[
        df_30m["time"].dt.time == pd.to_datetime(time_filter_start).time()]

    
    df_30m_filtered = df_30m_day_open_candles[df_30m_day_open_candles["time"] > target_date_]

    for i in range(1,len(df_30m_filtered)):

        current_row = df_30m_filtered.iloc[i]
        previous_row = df_30m_filtered.iloc[i - 1]

        current_time = current_row["time"]
        previous_time = previous_row['time']
   
        ## start and end date to filter out chunk of dataframe
        start_date = current_time
        end_date = current_time + datetime.timedelta(days=1)

        ## change to pd datetime datatype
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        time_minus_2h = pd.to_datetime(current_time) - pd.Timedelta(hours=3)
        prev_time_minus_2h = pd.to_datetime(previous_time) - pd.Timedelta(hours=3)


        df_1h_row = df_1h[df_1h["time"] == current_time]
        df_4h_row = df_4h[df_4h["time"] == time_minus_2h]

        result = None
        bias_4h_zone = None
        bias_1h_zone = None
        sentiment_result = None
        bias__list = []
        bias_score_list = []
        biasness_hour = None
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
            prev_4h_data = df_4h[df_4h["time"] == prev_time_minus_2h]

            if not df_4h_row.empty:

                if df_4h_row.iloc[0]['close'] > linear_regression_4h:
                    bias_4h_zone = 'Short'
                    biasness_hour = "4H"
                    bias__list.append(biasness_hour)
                elif df_4h_row.iloc[0]['close'] <= linear_regression_4h:
                    bias_4h_zone = 'Long'
                    biasness_hour = "4H"
                    bias__list.append(biasness_hour)
            #print(bias_4h_zone)


        ################################################################
        ###################  CHECK 1H Biasness  ########################

        if not df_1h_row.empty:
            back_100_candles = df_1h_row.index-100
            df_1h_100back_row = df_1h.iloc[back_100_candles]

            df_1h_100back_row.reset_index(drop=True,inplace=True)
            df_1h_row.reset_index(drop=True, inplace=True)

            linear_regression_1h_100_back = df_1h_100back_row.iloc[0]['real']
            linear_regression_1h = df_1h_row.iloc[0]["real"]
            prev_1h_data = df_1h[df_1h["time"] == previous_time]
            if not df_1h_row.empty:
                if df_1h_row.iloc[0]['close'] > linear_regression_1h:
                    bias_1h_zone = 'Short'
                    biasness_hour = "1H"
                    bias__list.append(biasness_hour)
                elif df_1h_row.iloc[0]['close'] <= linear_regression_1h:
                    bias_1h_zone = 'Long'
                    biasness_hour = "1H"
                    bias__list.append(biasness_hour)
            #print(bias_1h_zone)
            
    
        ### bias_score_list on basis of 4H Zone and 1H Zone
        bias_score_dict = {'Long': 1, 'Short': -1}
        bias_score_list = [bias_score_dict.get(bias_4h_zone, 0), bias_score_dict.get(bias_1h_zone, 0)]

        ############################################################################################
        ######## Pearson Values Calculations on basis of linear regression difference------ ########
        if not df_4h_row.empty:        
            pearson_4h_value = df_4h_row.iloc[0]['pearson_r']
            pearson_1h_value = df_1h_row.iloc[0]['pearson_r']        

            ### Pearson R Values on basis of last 100 candles linear regression
            candles_100_diff_4h = linear_regression_4h - linear_regression_4h_100_back
            if candles_100_diff_4h != 0:
                pearson_4h_value = abs(pearson_4h_value) if candles_100_diff_4h > 0 else -1 * abs(pearson_4h_value)

            candles_100_diff_1h = linear_regression_1h - linear_regression_1h_100_back
            if candles_100_diff_1h != 0:
                pearson_1h_value = abs(pearson_1h_value) if candles_100_diff_1h > 0 else -1 * abs(pearson_1h_value)

            bias_score_dict = {True: 1, False: -1}
            bias_score_list.extend([bias_score_dict[pearson_4h_value > 0],
                                    bias_score_dict[pearson_1h_value > 0]])



        ###############################################################################################
        ############### Previous Data -- Previous Pearson Values --- Previous Preason Values Differences       
        prev_4h_data.reset_index(drop=True,inplace=True)
        prev_1h_data.reset_index(drop=True,inplace=True)
        

        if len(prev_1h_data)>0:
            prev_pearson_4h_value = prev_4h_data.iloc[0]['pearson_r']
            prev_pearson_1h_value = prev_1h_data.iloc[0]['pearson_r']
            
            if pearson_4h_value>0:
                diff_4h_pearson = pearson_4h_value - prev_pearson_4h_value 
            else:
                diff_4h_pearson = abs(pearson_4h_value) - abs(prev_pearson_4h_value) 
                diff_4h_pearson = diff_4h_pearson*-1

            if pearson_1h_value>0:
                diff_1h_pearson = pearson_1h_value - prev_pearson_1h_value 
            else:
                diff_1h_pearson = abs(pearson_1h_value) - abs(prev_pearson_1h_value) 
                diff_1h_pearson = diff_1h_pearson*-1

            #### Calculate bias scores based on differences and append them to the existing bias_score_list
            bias_score_list.extend([1 if diff_4h_pearson > 0 else -1,
                                    1 if diff_1h_pearson > 0 else -1])

            

        # Determine the bias based on the sentiment_result value
        sentiment_result = sum(bias_score_list)
        result = 'bullish' if sentiment_result > 0 else 'bearish'

    
        ### If there are elements in the bias__list, assign the first element to biasness_hour
        biasness_hour = bias__list[0] if bias__list else None

            
        ### Append to airtable
        if current_day.day==current_time.day:# and current_day_minute == 0:#current_day_minute == 0:
        
           
            # Attempt to get data from the get_VIX_data() function
            #vix_bias_30M_zone, vix_bias_1h_zone, vix_pearson_30M_value, vix_pearson_1h_value, vix_diff_1h_pearson, vix_diff_30M_pearson, vix_first_candle_price = get_VIX_data()
        


            
            #print(current_day_hour)
            actual_bias = calcualte_actual_bias(first_candle_df_1h,current_day_hour,current_day_minute,first_candle_price,actual_bias_time)
            if current_day_hour == 1: #and current_day_minute == 0:
                mongo_id = str(current_day_date)

                h4_ema50 = df_4h.iloc[-1]['ema_50_signal']
                h1_ema50 = df_1h.iloc[-1]['ema_50_signal']
               
                
                ###### Insert into Daily Bias Collection MongoCloud
                insert_data_into_mongo(mongo_id,actual_bias,result,bias_4h_zone,pearson_4h_value,h4_ema50,diff_4h_pearson,bias_1h_zone,pearson_1h_value,h1_ema50,diff_1h_pearson,sentiment_result,am_session_points,pm_session_points,previous_daily_close)

                ### Insert into Daily Outcome Collectin
                insert_daily_outcome(mongo_id,open_price_,high_price_,low_price_,close_price_,am_session_points,pm_session_points,previous_daily_close)


                ####### Insert Daily Outcome into Airtable
                daily_outcome_airtable_id = 'tblNZRreXiWulokaP'
                fetch_last_document('daily_outcomes',daily_outcome_airtable_id)

                ####### Insert Daily Bias into Airtable
                daily_bias_id = 'tbl8vi3JZgwkcJhyN'
                vix_first_candle_price = vix_pearson_1h_value = vix_pearson_30M_value = 0
                insert_daily_bias_airtable(daily_bias_id,bias_4h_zone,pearson_4h_value,h4_ema50,bias_1h_zone,pearson_1h_value,h1_ema50,previous_daily_close,vix_first_candle_price,vix_pearson_1h_value,vix_pearson_30M_value)

                print(current_day.day,'Complete')


def get_data():
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
    

    STRING_DATE = dt.now().date() - timedelta(days=4)
    target_date_ = pd.to_datetime(STRING_DATE)
    
    last_timestamp = df_1h.iloc[-1]['time']
    current_hour = last_timestamp.hour
    
    if True:#int(current_hour) == 1:
        df_4h = df_4h.drop(df_4h.index[-1])
        df_4h.reset_index(drop=True,inplace=True)

        df_1h = df_1h.drop(df_1h.index[-1])
        df_1h.reset_index(drop=True,inplace=True)

        #df_5m = df_5m.drop(df_5m.index[-1])
        #df_5m.reset_index(drop=True,inplace=True)
        print('================================================================')
        print(f"Data Downloaded Successfully! Current Hour:{current_hour}")
        print('================================================================')
        generate_signals(df_5m, df_30m, df_1h, df_4h, target_date_)
    

#get_data()
previous_hour = 2
while True:
    current_hour = dt.now().hour
    if current_hour != previous_hour:
        previous_hour = current_hour
        get_data()
    time.sleep(10)
