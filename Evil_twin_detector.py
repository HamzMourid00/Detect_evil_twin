import pywifi
import json
import time
import smtplib
import ssl
import platform
import os
import subprocess
import psutil

with open("config.json", "r") as f:
    config = json.load(f)

interface = config["data"]["interface"]
essid = config["data"]["essid"]
bssid1 = config["data"]["bssid1"]
sender_email = config["data"]["sender"]
password = config["data"]["password"]
receiver_email = config["data"]["receiver"]
smtp_server = config["data"]["server"]
port = config["data"]["port"]
n = len(essid)

wifi = pywifi.PyWiFi()  
iface = wifi.interfaces()[0]  
iface.scan()  
#wifi_list = iface.scan_results()  # get the scan results
context = ssl.create_default_context()

def send():
    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)  # secure the connection
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)   
            #time.sleep(30)
    except Exception as e:
        print(f"An error occurred when sending email: {e}")

def reset_win():
    subprocess.run(["netsh", "interface", "set", "interface", interface, "admin=disable"])
    subprocess.run(["netsh", "interface", "set", "interface", interface, "admin=enable"])

with open('possible_ssid.txt', 'w') as f:
    for i in range(2**n):
        bin_i = bin(i)[2:].zfill(n)
        new_s = ''
        for j in range(n):
            if bin_i[j] == '1':
                new_s += essid[j].upper()
            else:
                new_s += essid[j].lower()
        f.write(new_s + '\n')

message = f"""\
Subject: Evil Twin Attack Detected

WARNING: We have detected a Wi-Fi network with the same name SSID {essid}
as our legitimate network. This is known as an 'evil twin' network and it
may be operated by an attacker in an attempt to
steal your personal information. Please do not connect to this network."""

process_names = ["aireplay-ng","airodump-ng","mdk4"]

while True:
    for network in iface.scan_results():
        with open('possible_ssid.txt', 'r') as f:
            for line in f:
                stripped_line = line.strip()
                if network.ssid in stripped_line and network.bssid != bssid1:
                    print("Attack Detected ..!")
                    print(f"ESSID: {network.ssid}")
                    print(f"BSSID: {network.bssid}")
                    for process in psutil.process_iter():
                        if platform.system() == 'Linux' and process.name() not in process_names:
                            send()
                            freq = network.freq / 1000  # get the frequency of the network in MHz
                            channel = (freq - 2412) // 5 + 1  # calculate the corresponding channel number
                            print('Start Defence ..')
                            os.system(f"xterm -bg black -fg red -geometry 120x30-0-0 -T airodump -e airodump-ng {interface} & xterm -bg black -fg blue -geometry 120x30+0+0 -T aireplay -e aireplay-ng --deauth 100000 -a {network.bssid} {interface} & xterm -bg black -fg white -geometry 120x30-0+0 -T mdk4 -e mdk4 {interface} a -a {network.bssid} -m")
                        else:
                            send()
                            reset_win()
                            time.sleep(5)





            
