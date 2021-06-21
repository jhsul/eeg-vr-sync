from eeg import EEGParser

eeg_host = "localhost"
eeg_port = 8844

eeg = EEGParser(eeg_host, eeg_port)

future_eeg_data = eeg.get_data()

df = future_eeg_data.result()

df.to_csv("eeg_data")
