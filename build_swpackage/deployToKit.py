# Install requirements 
# pip install "python-socketio[client]" requests
# run: python3 main.py dreamKIT-331b898a

import sys
import base64
import socketio

import os

# Check command line arguments
if len(sys.argv) < 1:
    print("Error: not enough params.\nSyntax: python main.py kit_id execType fileName filePath codeName codePath")
    sys.exit(1)

g_kit_id = sys.argv[1]
print("g_kit_id:", g_kit_id)

g_is_kit_registered = False
g_kit_online = False

# Socket.IO client
sio = socketio.Client()

kitArray = []

@sio.event
def connect():
    print("Socket connected !!!")
    sio.emit("register_client", {
        "username": "etas_user1",
        "user_id": "etas_user1",
        "domain": "domain"
    })
    print("register done !!!")

@sio.event
def disconnect():
    print("socket disconnected !!!")

@sio.on("list-all-kits-result")
def on_list_all_kits_result(data):
    global g_is_kit_registered, g_kit_online, kitArray
    print("list-all-kits-result")

    if not data:
        print("list-all-kits-result: null data")
        return

    kitArray = data
    for dataItem in kitArray:
        if dataItem.get('name') == g_kit_id:
            g_is_kit_registered = True
            print(f"{dataItem.get('name')} online status is {dataItem.get('is_online')}")
            if dataItem.get('is_online'):
                g_kit_online = True
                pkgPath = "/home/developer/workspace/etas_app_deployment/build_swpackage/swpackage.zip"
                deploySwPackageToKit(g_kit_id, pkgPath)
            else:
                g_kit_online = False

@sio.on("messageToKit-kitReply")
def on_kit_reply(payload):
    if not payload:
        print("onKitReply: null payload")
        return
    print("payload:")
    print(payload)
    cmd = payload.get("cmd")
    result = payload.get("result")
    if cmd in ("deploy_AraApp_Request", "dreamos_patch_update"):
        if result == "success":
            print("Sent araApp.\Fota on dreamKIT is successful !!!")
        else:
            print("Error: deployment failed !!!")
    sio.disconnect()

def deploySwPackageToKit(kit_id, pkgPath):
    global g_kit_online
    print(f"kit_id: {kit_id}")

    if not os.path.isfile(pkgPath):
        print(f"Error: package file '{pkgPath}' does not exist.")
        return

    try:
        with open(pkgPath, "rb") as f:
            pkgBuf = f.read()
    except Exception as e:
        print(f"Error reading package file: {e}")
        return

    print(f"testing deploy new sw package .............. {pkgPath}")

    p_payload = {
        "cmd": "dreamos_patch_update",
        "to_kit_id": kit_id,
        "data": {
            "deployFrom": "ETAS",
            "pkgContent": base64.b64encode(pkgBuf).decode('utf-8')
        }
    }

    print("prepare sw pdk done ....")

    if g_kit_online:
        print("Kit is online. Trying to send !")
        sio.emit("messageToKit", p_payload)
    else:
        print("Kit is NOT online. Hold on.")

def main():
    try:
        sio.connect("https://kit.digitalauto.tech")
        sio.wait()
    except Exception as e:
        print(f"Connection error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
