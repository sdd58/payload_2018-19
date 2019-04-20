#!/usr/local/bin/python3

from RFM69 import Radio, FREQ_915MHZ
import datetime
import time

node_id = 1
network_id = 100
recipient_id = 2
t_tot = 0

with Radio(FREQ_915MHZ, node_id, network_id, isHighPower=True, verbose=True) as radio:
    print("Starting loop...\n")

    rx_cnt = 0
    tx_cnt = 0

    while t_tot < 30:
        
        if rx_cnt > 10:
            rx_cnt = 0;

            for packet in radio.get_packets():
                print(packet)

        if tx_cnt > 5:
            tx_cnt = 0

            print("Sending...\n")
            if radio.send(2,"TEST", attempts=3, waitTime=100):
                print("Ack Recieved\n")
            else:
                print("No Ack Recieved\n")
        print("Listening...",len(radio.packets), radio.mode_name)
        delay = 0.5
        rx_cnt += delay
        tx_cnt += delay
        t_tot  += delay
        time.sleep(delay)
