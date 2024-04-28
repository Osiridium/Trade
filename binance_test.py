import time
import datetime
import json
import os
from binance.spot import Spot
from binance.error import ClientError
from multiprocessing import Process

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
os.chdir(script_dir)

client = Spot(api_key='', 
              api_secret='',
              base_url='https://api2.binance.com'
              )

def Store(*dicts, file_name='log.txt'):
    with open(file_name, 'a') as file:
        for data_dict in dicts:
            json_str = json.dumps(data_dict, indent=4)
            file.write(json_str + '\n')  

def Wait(target_time):
    while datetime.datetime.now() < target_time:
        time_to_wait = (target_time - datetime.datetime.now()).total_seconds()
        time.sleep(min(time_to_wait, 0.1))

def Order(ticket, amount, price, attempts=50, start_time=datetime.datetime.now(),action='BUY'):
    Wait(start_time)
    t1 = time.time()
    _order = {
    'symbol': ticket,
    'side': action,
    'type': 'LIMIT',
    'quantity': amount,
    'price' : price,
    'timeInForce': 'GTC'
    }
    for attempt in range(attempts):
        try:
            r1 = client.new_order(**_order)
            Store(r1)
            if(float(r1['executedQty']) != 0):
                average_price = float(r1['cummulativeQuoteQty'])/float(r1['executedQty'])
                print(f"Executed successfully at average price of {average_price} at {datetime.datetime.now()}")
            else:
                print(f"Order Placed at {datetime.datetime.now()}")
            break
        except ClientError as e:
            if e.error_code==-1121:
                print(f"Not yet {attempt+1} at {datetime.datetime.now()}")
            else:
                print(f"Unexpected error at {datetime.datetime.now()}")
    t2 = time.time()
    average_interval = (t2 - t1) / attempts
    print(f"Average interval: {average_interval} seconds per iteration")
    print(client.get_order_rate_limit())

if __name__ == '__main__':
    start_time = datetime.datetime(2024, 3, 18, 19, 59, 50)
    orders = [
        {'ticket': 'ETHFIUSDT', 'amount': 4000, 'price': 9.9, 'action': 'SELL'},
        {'ticket': 'ETHFIUSDT', 'amount': 1500, 'price': 8.9, 'action': 'SELL'},
        {'ticket': 'ETHFIUSDT', 'amount': 1500, 'price': 7.9, 'action': 'SELL'},
        {'ticket': 'ETHFIUSDT', 'amount': 1000, 'price': 7.4, 'action': 'SELL'},
        {'ticket': 'ETHFIUSDT', 'amount': 1000, 'price': 6.9, 'action': 'SELL'},
        {'ticket': 'ETHFIUSDT', 'amount': 500, 'price': 6.7, 'action': 'SELL'},
        {'ticket': 'ETHFIUSDT', 'amount': 500, 'price': 6.6, 'action': 'SELL'},
        {'ticket': 'ETHFIUSDT', 'amount': 1000, 'price': 6.5, 'action': 'SELL'}
    ]

    processes = []
    for order in orders:
        p = Process(target=Order, kwargs={**order, 'attempts': 100, 'start_time': start_time})
        processes.append(p)
        p.start()

    for p in processes:
        p.join()