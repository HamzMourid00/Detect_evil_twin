import subprocess
import json
import time
import smtplib
import ssl
import platform
import os
import subprocess
import psutil
import re

with open("config.json", "r") as f:
    config = json.load(f)

channel = config["data"]["channel"]
interface = config["data"]["interface"]
essid = config["data"]["essid"]
bssid = config["data"]["bssid"]
sender_email = config["data"]["sender"]
password = config["data"]["password"]
receiver_email = config["data"]["receiver"]
smtp_server = config["data"]["server"]
port = config["data"]["port"]
n = len(essid)
regex = rf"\b(\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)\b.*{essid}.*"
process_names = ["aireplay-ng","mdk4"]
ps_names = []

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
possible_ssid = [f'{essid}']

def get_channel():
    airodump_process = subprocess.Popen(['airodump-ng', interface], stdout=subprocess.PIPE)
    grep_process = subprocess.Popen(['grep', '-i', '-E', '|'.join(possible_ssid)], stdin=airodump_process.stdout, stdout=subprocess.PIPE)
    airodump_process.stdout.close()

    for line in iter(grep_process.stdout.readline, b''):
        decoded_line = line.decode('utf-8')
        ssid = subprocess.check_output(['cut', '-d', ',', '-f', '1'], input=decoded_line, universal_newlines=True).strip()
        words = ssid.split()
        last_word = words[-7]
        return last_word
message = f"""\
Subject: Evil Twin Attack Detected

WARNING: We have detected a Wi-Fi network with the same name SSID {essid}
as our legitimate network. This is known as an 'evil twin' network and it
may be operated by an attacker in an attempt to
steal your personal information. Please do not connect to this network."""

proc = subprocess.Popen(['airodump-ng', '--channel', channel, interface], stdout=subprocess.PIPE)
line = proc.stdout.readline()
get_mac_address = False
while line:
    try:
        line = proc.stdout.readline().decode('utf-8').strip()

        if line == '' and proc.poll() is not None:
            break

        match = re.search(regex, line)
        if match:
            mac_address = match.group(1)
            if not get_mac_address:
                get_mac_address = True
                if essid in line and mac_address not in bssid:
                    print("Attack Detected ..!")
                    print(f"BSSID: {mac_address}")
                    send()
                    for process in psutil.process_iter():
                        name = process.name()
                        ps_names.append(name)
                    for ps in process_names:
                        if ps not in ps_names:
                            print('Start Defence ..')
                            if essid in line and process.name() not in process_names:
                                print(f"Attacking the rogue point {mac_address}")
                                os.system(f"/usr/sbin/mdk4 {interface} a -a {mac_address} -m > /dev/null 2>&1 & /usr/sbin/aireplay-ng --deauth 1000000 -a {mac_address} {interface} > /dev/null 2>&1 &")
                                time.sleep(20) 
                elif essid not in line and mac_address not in line:
                    print("Attack stopped !")
                    os.system('killall -9 /usr/sbin/mdk4 > /dev/null 2>&1 & killall -9 /usr/sbin/airodump-ng > /dev/null 2>&1 & killall -9 /usr/sbin/aireplay-ng > /dev/null 2>&1 &')    
    
    except KeyboardInterrupt:
        proc.terminate()
        sys.exit(0)
proc.wait()
