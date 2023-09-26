from pymongo import MongoClient
import parameters
from AirtableManager import AirtableManager
import traceback

base_id = 'app3e2OqH7Vlb1aXY'
connection_string = "mongodb+srv://root:root@cluster0.38xyu7x.mongodb.net/?retryWrites=true&w=majority"
# airtable=AirtableManager(parameters.airtable_base_id, parameters.airtable_tbl_id2,parameters.airtable_access_key)
#===================================================================================================================

def update_airtable_biasness(record_dict,id):
    try:
        airtable=AirtableManager(base_id, id,parameters.airtable_access_key)
        airtable.insert_record(record = record_dict)
        print("\n--------------> Done Appending on Airtable!\n")
    except Exception as e:
        print('Airtable Error')  
        print(e)
        traceback.print_exc()


def insert_daily_bias_airtable(id,h4_lr,h4_pearson,h4_ema50,h1_lr,h1_pearson,h1_ema50,previous_day_close,vix_mid_price,vix_h1_pearson_r,vix_m30_pearson_r):
    airtable=AirtableManager(base_id, id,parameters.airtable_access_key)
    daily_bias = {
        'H4 LR Zone': h4_lr,
        'H4 LR Pearson R':h4_pearson,
        'H4 EMA-50':h4_ema50,
        'H1 LR Zone':h1_lr,
        'H1 LR Pearson R':h1_pearson,
        'H1 EMA-50':h1_ema50,
        'Previous Day Close':previous_day_close,
        'VIX Midnight Price':vix_mid_price,
        'VIX H1 Pearson R':vix_h1_pearson_r,
        'VIX M30 Pearson R': vix_m30_pearson_r
    }
    daily_bias['Ticker'] = 'SPX500'
    airtable.insert_record(record = daily_bias)


def insert_4h_1h_airtable(mongo_id,bias_4h_zone,pearson_4h_value,adx_4h,cmf_4h,supertrend_4h,ema_50_4h,macd_4h,bias_1h_zone,pearson_1h_value,adx_1h,cmf_1h,supertrend_1h,ema_50_1h,macd_1h):
    #h4_lr,h4_pearson_value,h4_adx,h4_cmf,h4_supertrend,h4_ema50,h4_macd,h1_lr,h1_pearson_value,h1_adx,h1_cmf,h1_supertrend
    data = {
        'H4 LR Band':bias_4h_zone,
        'H4 Pearson Value':pearson_4h_value,
        'H4 ADX':adx_4h,
        'H4 CMF':cmf_4h,
        'H4 Supertrend':supertrend_4h,
        'H4 EMA-50':ema_50_4h,
        'H4 MACD':macd_4h,
        'H1 LR Band':bias_1h_zone,
        'H1 Pearson Value':pearson_1h_value,
        'H1 ADX':adx_1h,
        'H1 CMF':cmf_1h,
        'H1 Supertrend':supertrend_1h,
        'H1 EMA-50':ema_50_1h,
        'H1 MACD':macd_1h,
    }
    data['Ticker'] = 'SPX500'
    id = 'tblDOJv6BUfUB2Dut'
    airtable=AirtableManager(base_id, id,parameters.airtable_access_key)
    airtable.insert_record(record = data)
    print('1H-4H Data Appended to AirTable')





# Function to fetch the last document from a collection
def fetch_last_document(collection_name,id):
    DB_NAME = "linear_regression"
    
    # Connect to MongoDB
    client = MongoClient(connection_string)
    db = client[DB_NAME]
    collection = db[collection_name]
    
    # Find the last document in the collection based on _id field
    last_document = collection.find_one({}, sort=[('_id', -1)])
  
    client.close()
    last_document.pop('_id')
    if collection_name == 'daily_outcomes' and last_document is not None:
        last_document['Daily Candle Close'] = last_document.pop('Current Daily Close')
        last_document['Ticker'] = 'SPX500'

    if collection_name == 'vix_collection':
        # print(type(last_document.pop('VIX Midnight Price')))
        last_document['Midnight Price'] = last_document.pop('VIX Midnight Price')
        #last_document['H4 Pearson R'] = last_document.pop('H4 Pearson R Value')
        last_document['H1 Pearson R'] = last_document.pop('H1 Pearson R Value')
        last_document['M30 Pearson R'] = last_document.pop('M30 Pearson R Value')
        last_document['Ticker'] = 'VIX'
        #print(type(last_document['Midnight Price'])) 
    
    update_airtable_biasness(last_document,id)
    return 



# fetch_last_document("1h_collection")

# # Example usage
# if __name__ == "__main__":
#     collection_names = ["daily_bias", "1h_collection", "vix_collection", "4h_collection", "daily_outcomes"]
    
#     for collection_name in collection_names:
#         last_doc = fetch_last_document(collection_name)
#         print(f"Last document in {collection_name}: {last_doc}")
