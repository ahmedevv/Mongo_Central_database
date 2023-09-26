from pymongo import MongoClient
from datetime import datetime as dt
import traceback
import time
from pymongo.errors import DuplicateKeyError


# MongoDB connection settings
mongo_uri = "mongodb+srv://root:root@cluster0.38xyu7x.mongodb.net/?retryWrites=true&w=majority"


DB_NAME = "linear_regression"
COLLECTION_NAME = "daily_bias"

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def insert_1h_into_mongo(current_date,bias_4h_zone,pearson_4h_value,adx,cmf,supertrend,ema_50,ema_200,macd,atr):
    try:
        COLLECTION_NAME = "1h_collection"

        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # current_date = dt.now().strftime("%Y-%m-%d")
        data = {
                
                'Time Note ' : 'The TimeZone is UTC+3 and Timestamp is Candle Open',
                'Linear Regression Zone': bias_4h_zone,
                'Linear Regression Pearson Value' : pearson_4h_value,
                
                'ADX':adx,
                'CMF':cmf,
                'Supertrend':supertrend,
                '50-day EMA':ema_50,
                '200-day EMA':ema_200,
                
                'ATR':atr
            }
        data["_id"] = current_date
        collection.insert_one(data)
    except DuplicateKeyError:
        print("Duplicate key error. Document already exists.")
    except Exception as e:
        time.sleep(10)
        insert_1h_into_mongo(current_date,bias_4h_zone,pearson_4h_value,adx,cmf,supertrend,ema_50,ema_200,macd,atr)



def insert_vix_into_mongo(current_date,pearson_1h_value,pearson_30M_value,midnight_price):
    try:
        COLLECTION_NAME = "vix_collection"

        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # current_date = dt.now().strftime("%Y-%m-%d")
        data = {
                
                'VIX Midnight Price': midnight_price,
                'H1 Pearson R Value' : pearson_1h_value,
                'M30 Pearson R Value' : pearson_30M_value,

            }
        data["_id"] = current_date
        collection.insert_one(data)
        print('Data inserted successfully')
    except DuplicateKeyError:
        print("Duplicate key error. Document already exists.")
    except Exception as e:
        time.sleep(10)
        traceback.print_exc()
        insert_vix_into_mongo(current_date,pearson_1h_value,pearson_30M_value,midnight_price)


def insert_DXY_into_mongo(current_date,pearson_1h_value,pearson_30M_value,midnight_price):
    try:
        COLLECTION_NAME = "dxy_collection"

        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # current_date = dt.now().strftime("%Y-%m-%d")
        data = {
                
                'DXY Midnight Price': midnight_price,
                'H1 Pearson R Value' : pearson_1h_value,
                'M30 Pearson R Value' : pearson_30M_value,

            }
        data["_id"] = current_date
        collection.insert_one(data)
        print('Data inserted successfully')
    except DuplicateKeyError:
        print("Duplicate key error. Document already exists.")
    except Exception as e:
        time.sleep(10)
        traceback.print_exc()
        insert_DXY_into_mongo(current_date,pearson_1h_value,pearson_30M_value,midnight_price)




def insert_4h_into_mongo(current_date,bias_4h_zone,pearson_4h_value,adx,cmf,supertrend,ema_50,ema_200,macd,atr):
    try:
        COLLECTION_NAME = "4h_collection"

        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # current_date = dt.now().strftime("%Y-%m-%d")
        data = {
                'Time Note ' : 'The TimeZone is UTC+3 and Timestamp is Candle Open',
                'Linear Regression Zone': bias_4h_zone,
                'Linear Regression Pearson Value' : pearson_4h_value,
                'ADX':adx,
                'CMF':cmf,
                'Supertrend':supertrend,
                '50-day EMA':ema_50,
                '200-day EMA':ema_200,
                
                'ATR':atr
            }
        data["_id"] = current_date
        collection.insert_one(data)
        print('Data Inserted Successfully')
    except DuplicateKeyError:
        print("Duplicate key error. Document already exists.")
    except Exception as e:
        time.sleep(10)
        insert_4h_into_mongo(current_date,bias_4h_zone,pearson_4h_value,adx,cmf,supertrend,ema_50,ema_200,macd,atr)    



def insert_document(data):
    try:
        collection.insert_one(data)
        print("Document inserted successfully.")
    except DuplicateKeyError:
        print("Duplicate key error. Document already exists.")
    except Exception as e:
        time.sleep(10)
        insert_document(data)


def insert_daily_outcome(mongo_id,open_price,high_price,low_price,close_price,am_session_points,pm_session_points,previous_daily):
    COLLECTION_NAME = "daily_outcomes"

    # Connect to MongoDB
    client = MongoClient(mongo_uri)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    data = {
            'Open Price' : open_price,
            'High Price': high_price,
            'Low Price' : low_price,
            'Close Price':close_price,
            'AM Session Points' : am_session_points,
            'PM Session Points' : pm_session_points,
            'Current Daily Close':previous_daily
        }
    try:
        data["_id"] = mongo_id
        #insert_document(data)
        collection.insert_one(data)
        print('Data inserted successfully\n')
    except DuplicateKeyError:
        print("Duplicate key error. Document already exists.")
    



def insert_data_into_mongo(current_date,direction_daily_points,result,bias_4h_zone,pearson_4h_value,h4_ema,diff_4h_pearson,bias_1h_zone,pearson_1h_value,h1_ema,diff_1h_pearson,sentiment,am_session_points,pm_session_points,previous_daily_close):
    #print(sentiment,'Sentiment')
    if result == 'bearish': 
        daily_bias = 'Short'
    elif result == 'bullish':
        daily_bias = 'Long'
    
    # print('bias zone')
    # print(bias_4h_zone,'4h')
    # print(bias_1h_zone,'1h')
    
    # current_date = dt.now().strftime("%Y-%m-%d")
    data = {
            'Predicted Daily Bias' : daily_bias,
            'Midnight H4 LR Band': bias_4h_zone,
            'Midnight H4 Pearson ' : pearson_4h_value,
            'Midnight H4 Pearson Difference':diff_4h_pearson,
            'Midnight H1 LR Band' : bias_1h_zone ,
            'Midnight H1 Pearson' : pearson_1h_value,
            'Midnight H1 Pearson Difference': diff_1h_pearson,
            'Current Daily Close':previous_daily_close,
            'H4 EMA-50' : h4_ema,
            'H1 EMA-50' : h1_ema
            #'AM Session Points ': am_session_points,
            #'PM Session Points ':pm_session_points,
        }
    data["_id"] = current_date
    insert_document(data)



def update_am_session_points(am_session_points,document_id):
    try:
        document_id = document_id.strftime('%Y-%m-%d %H:%M:%S')
        update_data = {'AM Session Points':am_session_points}
        result = collection.update_one(
        {"_id": document_id},
        {"$set": update_data}
        )   
    except DuplicateKeyError:
        print("Duplicate key error. Document already exists.")
    except Exception as e:
        traceback.print_exc()


def update_am_session_points_daily_outcome(am_session_points,document_id):
    try:
        COLLECTION_NAME = "daily_outcomes"

        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]


        document_id = document_id.strftime('%Y-%m-%d %H:%M:%S')

        update_data = {'AM Session Points':am_session_points}
        result = collection.update_one(
        {"_id": document_id},
        {"$set": update_data}
        )
        print("Document updated successfully")

        print(am_session_points,'AM Session Points')
        updated_document = collection.find_one({"_id": document_id})
        print("Updated Document:")
        print(updated_document)
   
    except DuplicateKeyError:
        print("Duplicate key error. Document already exists.")
    except Exception as e:
        traceback.print_exc()

def update_pm_session_points(am_session_points,document_id):
    try:
        document_id = document_id.strftime('%Y-%m-%d %H:%M:%S')
        update_data = {'PM Session Points':am_session_points}
        result = collection.update_one(
        {"_id": document_id},
        {"$set": update_data}
        )   
        #print(result.modified_count)
    except DuplicateKeyError:
        print("Duplicate key error. Document already exists.")
    except Exception as e:
        print(e)
        traceback.print_exc()

def update_pm_session_points_daily_outcome(am_session_points,current_day_date):
    try:
        COLLECTION_NAME = "daily_outcomes"

        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        document_id = current_day_date.strftime('%Y-%m-%d %H:%M:%S')
        update_data = {'PM Session Points':am_session_points}
        result = collection.update_one(
        {"_id": document_id},
        {"$set": update_data}
        )   
        #print(result.modified_count)
    except DuplicateKeyError:
        print("Duplicate key error. Document already exists.")
    except Exception as e:
        print(e)
        traceback.print_exc()



def update_daily_close(previous_daily_close,document_id):
    try:
        document_id_str = document_id.strftime('%Y-%m-%d %H:%M:%S')
        update_data = {'Current Daily Close': previous_daily_close}
        
        # Update "daily_outcomes" collection
        outcomes_collection = db['daily_outcomes']
        outcomes_result = outcomes_collection.update_one(
            {"_id": document_id_str},
            {"$set": update_data}
        )
        
        # Update "daily_bias" collection
        bias_collection = db['daily_bias']
        bias_result = bias_collection.update_one(
            {"_id": document_id_str},
            {"$set": update_data}
        )
        
        # Check if any document was modified in both collections
        if outcomes_result.modified_count or bias_result.modified_count:
            print("Update successful.")
        else:
            print("No documents were updated.")
    except DuplicateKeyError:
        print("Duplicate key error. Document already exists.")
    except Exception as e:
        print(e)



def return_daily_outcome_date():

    # Connect to MongoDB
    client = MongoClient(mongo_uri)
    db = client[DB_NAME]
    collection = db["daily_outcomes"]

    last_entry = collection.find().sort("_id", -1).limit(1)
    id = None
    last_entry_ = None
    last_entry_ = next(last_entry, None)
    if last_entry_:
        id = last_entry_['_id']
        print(id)
    
    return id

