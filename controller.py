import getpass
import subprocess
import asyncio
import sys
from kasa import Discover, Device

async def connect_plug_to_wifi():
    print("Setting up new plug")
    input("Connect to the plug's wifi network (it should look like TP-LINK_Smart_Plug_####) and press Enter to continue...")
    print("Looking for devices...")
    found_devices = await Discover.discover()
    if len(found_devices) < 1:
        print("No devices found, make sure you are on the right network and the device is on.")
        exit(0)
    device = next(iter(found_devices.values()))
    print(f"Found device {device.alias}" )
    network = input("Enter the name of the wifi network you want the device to connect to: ")
    password = getpass.getpass("Enter the password for the wifi network: ")
    encryption_type = input("Enter the encryption type or leave blank for wpa2_psk: ")
    print(f"Connecting to {network}...")
    await device.wifi_join(network, password, encryption_type)
    print(f"Connected the plug to the wifi network You can now reconnect to your wifi network.")
    input("Once you are back on your network press Enter to continue...")

async def discover_plug():
    found_devices = await Discover.discover()
    if len(found_devices) == 1:
        host_ip = next(iter(found_devices.values())).config.host
        print(f"found device: {host_ip}")
        return host_ip
    elif len(found_devices) > 1:
        input("Found multiple devices")
    else:
        print("No available devices found, try running with the 'setup' argument.")
        exit(0)

def turn_on_factory(host_ip):
    async def turn_on():
        device = await Discover.discover_single(host_ip)
        await device.turn_on()
    return turn_on

def turn_off_factory(host_ip):
    async def turn_off():
        device = await Discover.discover_single(host_ip)
        await device.turn_off()
    return turn_off

def log_controller(predicate, func):

    cmd = f"log stream --predicate '{predicate}'"
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

    skip_first = True
    while True:
        output = process.stdout.readline().decode('utf-8').strip()
        if output:
            if skip_first:
                skip_first = False
            else:
                asyncio.run(func())
                process.kill()
                break

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        asyncio.run(connect_plug_to_wifi())

    host = asyncio.run(discover_plug())
    while True:
        cameraOn = "(eventMessage CONTAINS \"AVCaptureSessionDidStartRunningNotification\")"
        log_controller(cameraOn, turn_on_factory(host))
        cameraOff = "(eventMessage CONTAINS \"AVCaptureSessionDidStopRunningNotification\")"
        log_controller(cameraOff, turn_off_factory(host))