import asyncio
import threading
from datetime import datetime as dt
from concurrent.futures import ProcessPoolExecutor
from eeg import EEGParser
from vr import VRParser

eeg_host = "localhost"
eeg_port = 8844

vr_host = "localhost"
vr_port = 8080

'''
eeg = EEGParser(eeg_host, eeg_port)

future_eeg_data = eeg.get_data()

df = future_eeg_data.result()

df.to_csv("eeg_data.csv")
'''

# Wrapper for starting the EEG from the asyncio thingy
def run_eeg():
    print(f"[{dt.now()}] Connecting to EEG headset")
    eeg = EEGParser(eeg_host, eeg_port)
    eeg.parse_data()
    return eeg.df

if __name__ == "__main__":
    # Start VR websocket server
    vr = VRParser(vr_host, vr_port)

    loop = asyncio.get_event_loop()
    executor = ProcessPoolExecutor(2)

    vr.event_loop = loop


    eeg_data = loop.run_in_executor(executor, run_eeg)
    _ = loop.run_until_complete(vr.start_server())

    loop.run_forever()

    vr_data = vr.df
    print(vr_data)
    print(eeg_data)

    timestamp = dt.now()
    eeg_data.to_csv(f"output/{timestamp}.csv")
