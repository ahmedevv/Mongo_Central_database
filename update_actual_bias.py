import pandas as pd
from AirtableManager import AirtableManager
import MetaTrader5 as mt5
import parameters
import datetime
import parameters
import time

def appending_bias(diff):

    date_ = datetime.datetime.now()
    date_ = date_.strftime('%m/%d/%Y')
    airtable=AirtableManager(parameters.airtable_base_id, parameters.airtable_tbl_id2,parameters.airtable_access_key)
    entry = airtable.read_record()
    
    # Getting the Ticket ID from Airtable  
    for key in range(0,len(entry)):
        print(entry[key]['fields'])
        # exit(0)
        if entry[key]['fields']['Date'] == date_:
            # Details of Trade
            record_id = entry[key]['fields']['Record ID']
            if diff >0: 
                diff = 'Long'
            if diff < 0:
                diff = 'Short'
            fields = {
                'Actual Bias' : diff
            }
            record = airtable.match_record('Record ID',record_id)
            print(record)
            airtable.update_record(record['id'],fields)
