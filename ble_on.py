import os
import time


os.system("bluetoothctl")
time.sleep(10)
os.system("power on")
time.sleep(10)
os.system("agent on")
time.sleep(10)
os.system("default-agent")
time.sleep(10)
os.system("pairable on")
time.sleep(10)
os.system("discoverable on")
time.sleep(10)
