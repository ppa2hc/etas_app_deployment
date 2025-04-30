import sys
import base64
import socketio
import os
import time

# Check command line arguments
if len(sys.argv) < 2:
    print("Error: not enough params.\nSyntax: python main.py kit_id")
    sys.exit(1)

g_kit_id = sys.argv[1]
print("g_kit_id:", g_kit_id)

g_is_kit_registered = False
g_kit_online = False

# Socket.IO client
# sio = socketio.Client()
sio = socketio.Client(
    logger=True,
    engineio_logger=False,
    reconnection=True,
    reconnection_attempts=10,
    reconnection_delay=1,
    reconnection_delay_max=5,
)

kitArray = []

@sio.event
def connect():
    print("[SocketIO] Connected to server.")
    # Register client after connection established
    sio.emit("register_client", {
        "username": "etas_user1",
        "user_id": "etas_user1",
        "domain": "domain"
    })
    print("[SocketIO] Registration event emitted.")

@sio.event
def connect_error(data):
    print(f"[SocketIO] Connection failed: {data}")

@sio.event
def disconnect():
    print("[SocketIO] Disconnected from server.")

@sio.on("list-all-kits-result")
def on_list_all_kits_result(data):
    global g_is_kit_registered, g_kit_online, kitArray
    print("[SocketIO] Received list-all-kits-result")

    if not data:
        print("[SocketIO] list-all-kits-result: no data received")
        return

    kitArray = data
    for dataItem in kitArray:
        if dataItem.get('name') == g_kit_id:
            g_is_kit_registered = True
            online_status = dataItem.get('is_online')
            print(f"Kit {g_kit_id} online status: {online_status}")
            if online_status:
                g_kit_online = True
                pkgPath = "/home/developer/workspace/etas_app_deployment/build_swpackage/swpackage.zip"
                deploySwPackageToKit(g_kit_id, pkgPath)
            else:
                print("Kit is registered but currently offline.")
                g_kit_online = False
            break
    else:
        print(f"Kit {g_kit_id} not found in kit list.")

@sio.on("messageToKit-kitReply")
def on_kit_reply(payload):
    if not payload:
        print("[SocketIO] on_kit_reply: empty payload")
        return
    print("[SocketIO] Kit reply payload:", payload)
    cmd = payload.get("cmd")
    result = payload.get("result")
    if cmd in ("deploy_AraApp_Request", "dreamos_patch_update"):
        if result == "success":
            print("Deployment succeeded on dreamKIT!")
        else:
            print("Deployment failed!")
    # Disconnect after receiving reply
    print("[SocketIO] Disconnecting socket...")
    sio.disconnect()

def deploySwPackageToKit(kit_id, pkgPath):
    global g_kit_online
    print(f"Preparing to deploy package to kit: {kit_id}")

    if not os.path.isfile(pkgPath):
        print(f"Error: package file '{pkgPath}' does not exist.")
        return

    try:
        with open(pkgPath, "rb") as f:
            pkgBuf = f.read()
    except Exception as e:
        print(f"Error reading package file: {e}")
        return

    print(f"Deploying software package from {pkgPath}")

    p_payload = {
        "cmd": "dreamos_patch_update",
        "to_kit_id": kit_id,
        "data": {
            "deployFrom": "ETAS",
            "pkgContent": base64.b64encode(pkgBuf).decode('utf-8')
        }
    }

    print("Payload prepared.")

    if g_kit_online:
        print("Kit is online. Sending deployment message...")
        sio.emit("messageToKit", p_payload)
    else:
        print("Kit is not online. Cannot send deployment message.")

def main():
    try:
        # Connect explicitly to default namespace ("/")
        # sio.connect("https://kit.digitalauto.tech", namespaces=['/'])
        sio.connect("https://kit.digitalauto.tech", transports=['websocket'], namespaces=['/'])
        # Wait for events (this will block)
        sio.wait()
    except Exception as e:
        print(f"Connection error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
    print("Deployment script finished.")
