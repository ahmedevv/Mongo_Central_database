import os
import datetime
import warnings
import numpy as np
import pandas as pd
import MetaTrader5 as mt5
import statsmodels.api as sm
from datetime import timedelta
from datetime import datetime as dt
import parameters
import time
import traceback
# from VIX_U3 import get_VIX_data
from mongodb_connection import * 
from mongo_airtable_connector import *
from update_actual_bias import appending_bias
from mt_data_download import initialize_mt5, download_save_data, shutdown_mt5
warnings.filterwarnings("ignore")