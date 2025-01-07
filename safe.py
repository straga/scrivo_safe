
from time import sleep
import network
import asyncio


# Read secret file
def secret(search, default=False, path="./secret"):
    result = default
    try:
        with open(path) as f:
            for line in f:
                if line.startswith(search):
                    result = line.split(":")[-1].rstrip()
    except Exception as e:
        print(f"Error: secret file: {e}")
    return result


def find_strongest_network(sta, target_key):
    strongest_signal = None
    strongest_strength = float("-inf")

    for network in sta:
        try:
            print("scan: {}".format(network))
            ssid, _, _, signal_strength, _, _ = network
            if ssid.decode() == target_key and signal_strength > strongest_strength:
                strongest_signal = network
                strongest_strength = signal_strength
        except Exception as e:
            print("scan: {}".format(e))
            pass
    return strongest_signal



class Safe():
    def __init__(self):
        self.sta = None
        print("Safe: Init")
        self.wifi_init()
        self.net_init()
        self.telnet_init()
        self.wait = secret("safe_sleep", 10)


    def wifi_init(self):
        print("WIFI: Init")
        self.sta = network.WLAN(network.STA_IF)
        self.sta.active(True)


    def telnet_init(self):
        # Telnet
        print(f"Telnet: Init:")
        try:
            import utelnetserver
            utelnetserver.start()
        except Exception as e:
            print(f"Telnet: {e}")

    def net_init(self):
        # Hostname
        print("WIFI:Hostname: Init")
        hostname = secret("hostname")
        try:
            if hostname:
                network.hostname(hostname)
        except Exception as e:
            print(f"ERROR:Hostname: {e}")
        print(f"WIFI:Hostname: {network.hostname()}")


    def ntp_init(self):
        print("NTP: Init")
        try:
            import time
            import ntptime
            ntptime.settime()
            print(f"Get time: {time.localtime()}")
        except Exception as e:
            print(f"ERROR:NTP: {e}")



    async def touch(self):

        if not self.sta.isconnected():
            # Scan networks
            sta_scan = []
            try:
                sta_scan = self.sta.scan()
            except Exception as e:
                print("ERROR:WIFI:STA scan: {}".format(e))

            print("WIFI:STA: scan: {}".format(sta_scan))


            # Connect to network
            try:
                safe_wifi_ssid = secret("safe_wifi_ssid")
                safe_wifi_key = secret("safe_wifi_key")

                signal = find_strongest_network(sta_scan, safe_wifi_ssid)

                if signal:
                    #self.sta.connect(safe_wifi_ssid, safe_wifi_key)
                    self.sta.connect(safe_wifi_ssid, safe_wifi_key, bssid=signal[1])
                    print("WIFI:STA - wait 5 sec")

                # check 5 time if connected break for
                for i in range(5):
                    sta_connect = self.sta.isconnected()
                    if sta_connect:
                        self.ntp_init()
                        break
                    await asyncio.sleep(1)

                print(f"STA: {self.sta.ifconfig()}, channel: {self.sta.config('channel')}")

            except Exception as e:
                print(f"ERROR:WIFI:STA {e}")


