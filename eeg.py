# DSI_to_Python v.1.0 BETA
# The following script can be used to receive DSI-Streamer Data Packets through DSI-Streamer's TCP/IP Protocol.
# It contains an example parser for converting packet bytearrays to their corresponding formats described in the TCP/IP Socket Protocol Documentation (https://wearablesensing.com/downloads/TCPIP%20Support_20190924.zip).
# The script involves opening a server socket on DSI-Streamer and connecting a client socket on Python.

# As of v.1.0, the script outputs EEG data and timestamps to the command window. In addition, the script is able to plot the data in realtime.
# Keep in mind, however, that the plot functionality is only meant as a demonstration and therefore does not adhere to any current standards.
# The plot function plots the signals on one graph, unlabeled.
# To verify correct plotting, one can introduce an artifact in the data and observe its effects on the plots.

# The sample code is not certified to any specific standard. It is not intended for clinical use.
# The sample code and software that makes use of it, should not be used for diagnostic or other clinical purposes.
# The sample code is intended for research use and is provided on an "AS IS"  basis.
# WEARABLE SENSING, INCLUDING ITS SUBSIDIARIES, DISCLAIMS ANY AND ALL WARRANTIES
# EXPRESSED, STATUTORY OR IMPLIED, INCLUDING BUT NOT LIMITED TO ANY IMPLIED WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT OR THIRD PARTY RIGHTS.
#
# Copyright (c) 2014-2020 Wearable Sensing LLC
import concurrent.futures
import socket, struct, time
import tkinter.filedialog

import numpy as np
import matplotlib.pyplot as plt
import threading
import pandas as pd
from datetime import datetime as dt


class EEGParser:  # The script contains one main class which handles DSI-Streamer data packet parsing.

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.done = False
        self.data_log = b''
        self.latest_packets = []
        self.latest_packet_headers = []
        self.latest_packet_data = np.zeros((1, 1))
        self.signal_log = np.zeros((1, 20))
        self.time_log = np.zeros((1, 20))
        self.montage = []
        self.fsample = 0
        self.fmains = 0

        self.df = None  # Set the dataframe to None until we know the shape of the data

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def parse_data(self, app):
        self.app = app
        # parse_data() receives DSI-Streamer TCP/IP packets and updates the signal_log and time_log attributes
        # which capture EEG data and time data, respectively, from the last 100 EEG data packets (by default) into a numpy array.
        while not self.done:
            data = self.sock.recv(921600)
            self.data_log += data
            if self.data_log.find(b'@ABCD', 0,
                                  len(self.data_log)) != -1:  # The script looks for the '@ABCD' header start sequence to find packets.
                for index, packet in enumerate(self.data_log.split(b'@ABCD')[
                                               1:]):  # The script then splits the inbound transmission by the header start sequence to collect the individual packets.
                    self.latest_packets.append(b'@ABCD' + packet)
                for packet in self.latest_packets:
                    self.latest_packet_headers.append(struct.unpack('>BHI', packet[5:12]))
                self.data_log = b''

                for index, packet_header in enumerate(self.latest_packet_headers):
                    # For each packet in the transmission, the script will append the signal data and timestamps to their respective logs.
                    if packet_header[0] == 1:
                        if np.shape(self.signal_log)[
                            0] == 1:  # The signal_log must be initialized based on the headset and number of available channels.
                            self.signal_log = np.zeros((int(len(self.latest_packets[index][23:]) / 4), 20))
                            self.time_log = np.zeros((1, 20))
                            self.latest_packet_data = np.zeros((int(len(self.latest_packets[index][23:]) / 4), 1))

                        self.latest_packet_data = np.reshape(
                            struct.unpack('>%df' % (len(self.latest_packets[index][23:]) / 4),
                                          self.latest_packets[index][23:]), (len(self.latest_packet_data), 1))
                        self.latest_packet_data_timestamp = np.reshape(
                            struct.unpack('>f', self.latest_packets[index][12:16]), (1, 1))

                        #print("Timestamps: " + str(self.latest_packet_data_timestamp))
                        #print("Signal Data: " + str(len(self.latest_packet_data)))

                        # Add latest packet data to the dataframe if it has been instantiated already
                        # (Reasonably it will always be instantiated by this point)
                        if self.df is not None:
                            #print(self.latest_packet_data)
                            self.app.data_count += 1
                            self.app.data_status.set(f"Data points collected: {self.app.data_count}")
                            #latest_packet_series = pd.Series(self.latest_packet_data.reshape(-1), index=self.montage)
                            timestamp = dt.now()

                            new_row = pd.DataFrame(self.latest_packet_data.reshape(1, -1), columns=self.montage, index=[timestamp])

                            #print(new_row)
                            self.df = pd.concat([self.df, pd.DataFrame(new_row)], ignore_index=False)

                        self.signal_log = np.append(self.signal_log, self.latest_packet_data, 1)
                        self.time_log = np.append(self.time_log, self.latest_packet_data_timestamp, 1)
                        self.signal_log = self.signal_log[:, -100:]
                        self.time_log = self.time_log[:, -100:]
                    ## Non-data packet handling
                    if packet_header[0] == 5:
                        (event_code, event_node) = struct.unpack('>II', self.latest_packets[index][12:20])
                        if len(self.latest_packets[index]) > 24:
                            message_length = struct.unpack('>I', self.latest_packets[index][20:24])[0]
                        print("Event code = " + str(event_code) + "  Node = " + str(event_node))

                        # The stop event
                        if event_code == 3:
                            print("Received stop signal, finishing up EEG data collection")
                            print(self.df)

                            output_path = tkinter.filedialog.asksaveasfilename()
                            self.df.to_csv(output_path)

                            self.app.data_status.set(f"Saved to {output_path}")
                            self.done = True

                        if event_code == 9:
                            self.app.connection_status.set("Connected")
                            montage = self.latest_packets[index][24:24 + message_length].decode()
                            montage = montage.strip()
                            print("Montage = " + montage)
                            self.montage = montage.split(',')

                            # Instantiate self.df once the montage layout comes in
                            if self.df is None:
                                self.df = pd.DataFrame(columns=self.montage)

                        if event_code == 10:
                            frequencies = self.latest_packets[index][24:24 + message_length].decode()
                            print("Mains,Sample = " + frequencies)
                            mains, sample = frequencies.split(',')
                            self.fsample = float(sample)
                            self.fmains = float(mains)
            self.latest_packets = []
            self.latest_packet_headers = []
        return self.df

    def example_plot(self):
        # example_plot() uses the threading Python library and matplotlib to plot the EEG data in realtime.
        # The plots are unlabeled but users can refer to the TCP/IP Socket Protocol Documentation to understand how to discern the different plots given their indices.
        # Ideally, each EEG plot should have its own subplot but for demonstrative purposes, they are all plotted on the same figure.
        data_thread = threading.Thread(target=self.parse_data)
        data_thread.start()

        refresh_rate = 0.03
        duration = 60  # The default plot duration is 60 seconds.
        runtime = 0

        fig = plt.figure()

        while True:  # runtime < duration/refresh_rate:
            self.signal_log = self.signal_log[:, -1000:]
            self.time_log = self.time_log[:, -1000:]
            plt.clf()
            try:
                plt.plot(self.time_log.T, self.signal_log.T)
            except:
                pass
            plt.gca().legend(self.montage)
            plt.xlabel('Timestamp')
            plt.ylabel('Peak-to-Peak uV')
            plt.title('DSI-Streamer TCP/IP EEG Sensor Data Output')
            plt.pause(refresh_rate)
            runtime += 1
        plt.show()

        self.done = True
        data_thread.join()

    def get_data(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.parse_data)
            return future


if __name__ == "__main__":
    # The script will automatically run the example_plot() method if not called from another script.
    tcp = EEGParser('localhost', 8844)
    tcp.example_plot()
