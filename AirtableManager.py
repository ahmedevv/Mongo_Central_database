import random
import pandas as pd
from airtable import Airtable
from datetime import datetime, timedelta
import time

# This is the structure format of the URL link from the Airtable Base. The first part before the / is the Base ID, the part after the first / but before the second / is the Table Name. 
# The API key is found under the 'Developers Hub' on Airtable. 

class AirtableManager:
    def __init__(self, base_id, table_name, api_key):
        self.airtable = Airtable(base_id, table_name, api_key)

    def insert_record(self, record):
        return self.airtable.insert(record)
    def read_record(self,view='Master View',fields=['Ticker', 'Position','Alert Date (Gmail)','Alert Time (Gmail)']):
        return self.airtable.get_all()
    def update_record(self, record_id, fields):
        self.airtable.update(record_id,fields)

    def match_record(self,id,toMatchID):
        return self.airtable.match(id,toMatchID)


# Any changes to the View Name, or the Field Columns will need to be updated here. 
