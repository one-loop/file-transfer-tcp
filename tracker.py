# tracker.py
import socket
import threading
import json

# { filename: [ (chunk_name, peer_address), ... ] }
file_registry = {}

def handle_client(conn, addr):
    print(f"[TRACKER] Connected by {addr}")
    data = conn.recv(4096).decode()
    
    if data.startswith("REGISTER"):
        _, filename, chunk_name, peer_port = data.split("|")
        if filename not in file_registry:
            file_registry[filename] = []
        file_registry[filename].append((chunk_name, addr[0], int(peer_port)))
        conn.send(b"REGISTERED")
        print(f"[TRACKER] Registered: {chunk_name} of {filename} from {addr[0]}")
    
    elif data.startswith("GET"):
        _, filename = data.split("|")
        chunks = file_registry.get(filename, [])
        conn.send(json.dumps(chunks).encode())
        print(f"[TRACKER] Sent chunk list for {filename}")

    conn.close()

def start_tracker():
    tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tracker.bind(("0.0.0.0", 6000))
    tracker.listen()
    print("[TRACKER] Listening on port 6000...")
    while True:
        conn, addr = tracker.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_tracker()

# The tracker server listens for incoming connections from peers.
# When a peer registers a chunk, it updates the file registry.
# When a peer requests the list of chunks for a file, it sends the list back.
# The tracker server uses threading to handle multiple connections simultaneously.
# This allows multiple peers to register or request chunks at the same time.
# The file registry is a dictionary that maps filenames to a list of chunks and their respective peer addresses.
# The tracker server uses JSON to encode and decode the list of chunks.
# The tracker server runs indefinitely, listening for incoming connections.
# The tracker server can be run in a separate terminal or process.
# The tracker server can be stopped by terminating the process.