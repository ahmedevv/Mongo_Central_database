import time
from DXY.DXY_bias_assessment import get_DXY_data
from VIX.VIX_bias_assessment import get_VIX_data

def execute_functions():
    #thread1 = threading.Thread(target=get_DXY_data)
    #thread2 = threading.Thread(target=get_VIX_data)

    #thread1.start()
    #thread2.start()

    #thread1.join()
    #thread2.join()
    get_DXY_data()
    get_VIX_data()


while True:
    current_time = time.localtime()
    
    if current_time.tm_min == 30 or current_time.tm_min == 0:
        print(current_time)
        execute_functions()
        time.sleep(60)
    
    time.sleep(15)  # Sleep for 1 minute before checking again



