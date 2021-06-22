import asyncio
from concurrent.futures import ProcessPoolExecutor
from eeg import EEGParser
from vr import VRParser

eeg_host = "localhost"
eeg_port = 8844

vr_host = "localhost"
vr_port = 8080


eeg = EEGParser(eeg_host, eeg_port)

future_eeg_data = eeg.get_data()

df = future_eeg_data.result()

df.to_csv("eeg_data.csv")



'''
def run_eeg():
    eeg = EEGParser(eeg_host, eeg_port)
    eeg.parse_data()
    return eeg.df
    #print("EEG is totally connected and running")
    #eturn "super real eeg data"

def run_vr():

vr = VRParser(vr_host, vr_port)
server = vr.run_server()

loop = asyncio.get_event_loop()
tasks = run_eeg()

eeg_data = loop.run_until_complete(asyncio.gather(*tasks))
loop.run_forever()

eeg_data.to_csv("eeg_data.csv")
'''