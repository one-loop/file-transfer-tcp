# peer.py
import socket
import threading
import os
import sys

# Use command-line argument for the port, default to 7002
if len(sys.argv) > 1:
    PEER_PORT = int(sys.argv[1])
else:
    PEER_PORT = 7001

CHUNK_DIR = "chunks"
os.makedirs(CHUNK_DIR, exist_ok=True)

def handle_client(conn, addr):
    try:
        request = conn.recv(1024).decode()
    except UnicodeDecodeError as e:
        print(f"[PEER] Error decoding request from {addr}: {e}")
        conn.close()
        return
    
    if request.startswith("SEND"):
        _, chunk_name = request.split("|")
        try:
            with open(os.path.join(CHUNK_DIR, chunk_name), "rb") as f:
                conn.sendall(f.read())
            print(f"[PEER] Sent {chunk_name} to {addr}")
        except FileNotFoundError:
            error_message = f"ERROR: File {chunk_name} not found."
            conn.sendall(error_message.encode())
            print(f"[PEER] {error_message}")
    
    elif request.startswith("UPLOAD"):
        _, chunk_name = request.split("|")
        conn.send(b"READY")  # send handshake ack before receiving file data
        with open(os.path.join(CHUNK_DIR, chunk_name), "wb") as f:
            while True:
                bytes_read = conn.recv(4096)
                if not bytes_read:
                    break
                f.write(bytes_read)
        print(f"[PEER] Stored chunk: {chunk_name}")
    
    conn.close()

def start_peer():
    peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer.bind(("0.0.0.0", PEER_PORT))
    peer.listen()
    print(f"[PEER] Listening on port {PEER_PORT}...")
    while True:
        conn, addr = peer.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_peer()
