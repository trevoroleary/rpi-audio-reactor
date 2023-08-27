import argparse
from datetime import datetime
import struct
import sys
import time
import traceback
from random import normalvariate
import pigpio
from nrf24 import *


class LEDPacket:
    def __init__(self, starting_number: int, brightness: int, led_rgbs: list):
        self.starting_number = starting_number
        self.brightness = brightness
        self.led_rgbs = led_rgbs
    
    def get_payload(self) -> bytes:
        string_format = "@" + "".join(["B" for _ in range(32)])
        
        led_rgb_list = list()
        print(f"Starting Number: {self.starting_number}")
        print(f"Brightness: {self.brightness}")
        for i, (r, g, b) in enumerate(self.led_rgbs):
            led_rgb_list += [r, g, b]
            print(f"LED #{i}   |   r: {r}, g: {g}, b: {b}")
        args = [self.starting_number, self.brightness] + led_rgb_list
        payload = struct.pack(string_format, *args)
        return payload

def send_packet(payload):
    # Send the payload to the address specified above.
    radio.reset_packages_lost()
    radio.send(payload)
    try:
        radio.wait_until_sent()
        
    except TimeoutError:
        print("Timeout waiting for transmission to complete.")
        time.sleep(10)
        return

    if radio.get_packages_lost() == 0:
        print(f"Success: lost={radio.get_packages_lost()}, retries={radio.get_retries()}")
    else:
        print(f"Error: lost={radio.get_packages_lost()}, retries={radio.get_retries()}")


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
    
    count = 0
    print(f'Send to {tx_address}')
    try:
        while True:

            # Emulate that we read temperature and humidity from a sensor, for example
            # a DHT22 sensor.  Add a little random variation so we can see that values
            # sent/received fluctuate a bit.
            packet = LEDPacket(1, 100, [(i, i+1, i+2) for i in range(10)])
            payload = packet.get_payload()
            send_packet(payload)

            time.sleep(5)

    except:
        traceback.print_exc()
        radio.power_down()
        pi.stop()