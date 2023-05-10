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
bssid = config["data"]["bssid"]
sender_email = config["data"]["sender"]
password = config["data"]["password"]
receiver_email = config["data"]["receiver"]
smtp_server = config["data"]["server"]
port = config["data"]["port"]
n = len(essid)

wifi = pywifi.PyWiFi()  
iface = wifi.interfaces()[0]  
iface.scan()  
context = ssl.create_default_context()

def send():
    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)  # secure the connection
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)   
            time.sleep(30)
    except Exception as e:
        print(f"An error occurred when sending email: {e}")

def reset_win():
    subprocess.run(["netsh", "interface", "set", "interface", interface, "admin=disable"])
    subprocess.run(["netsh", "interface", "set", "interface", interface, "admin=enable"])
    time.sleep(15)   

possible_ssid = []
for i in range(2**n):
    bin_i = bin(i)[2:].zfill(n)
    new_s = ''
    for j in range(n):
        if bin_i[j] == '1':
            new_s += essid[j].upper()
        else:
            new_s += essid[j].lower()
    possible_ssid.append(new_s)

message = f"""\
Subject: Evil Twin Attack Detected

WARNING: We have detected a Wi-Fi network with the same name SSID {essid}
as our legitimate network. This is known as an 'evil twin' network and it
may be operated by an attacker in an attempt to
steal your personal information. Please do not connect to this network."""

process_names = ["aireplay-ng","airodump-ng","mdk4"]

while True:
    if platform.system() == 'Windows':
        reset_win()       
    else:
        pass    
    for network in iface.scan_results():
        if network.ssid in possible_ssid and network.bssid not in bssid:
            print("Attack Detected ..!")
            print(f"ESSID: {network.ssid}")
            print(f"BSSID: {network.bssid}")
            send()
            reset_win()
            time.sleep(5)





            
