import argparse
from datetime import datetime
import struct
import sys
import time
import traceback

import pigpio
from nrf24 import *


#
# A simple NRF24L receiver that connects to a PIGPIO instance on a hostname and port, default "localhost" and 8888, and
# starts receiving data on the address specified.  Use the companion program "simple-sender.py" to send data to it from
# a different Raspberry Pi.
#
if __name__ == "__main__":

    print("Python NRF24 Simple Receiver Example.")

    hostname = 'localhost'
    port = 8888
    rx_address = "RAPI"
    tx_address = "EXWLL"
    
    # Connect to pigpiod
    print(f'Connecting to GPIO daemon on {hostname}:{port} ...')
    pi = pigpio.pi(hostname, port)
    if not pi.connected:
        print("Not connected to Raspberry Pi ... goodbye.")
        sys.exit()

    # Create NRF24 object.
    # PLEASE NOTE: PA level is set to MIN, because test sender/receivers are often close to each other, and then MIN works better.
    radio = NRF24(pi, ce=25, payload_size=RF24_PAYLOAD.DYNAMIC, channel=100, data_rate=RF24_DATA_RATE.RATE_250KBPS, pa_level=RF24_PA.MIN)
    radio.set_address_bytes(len(tx_address))

    # Listen on the address specified as parameter
    # radio.open_reading_pipe(RF24_RX_ADDR.P1, rx_address)

    # Write to the specified address
    radio.open_writing_pipe(tx_address)
    
    # Display the content of NRF24L01 device registers.
    radio.show_registers()
    
    while True:
        message = "Hello World"
        radio.send(27)
        print(f"We sent a message")
        time.sleep(1)