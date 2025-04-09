# tracker.py
import socket
import threading
import json

# { filename: [ (chunk_name, peer_address), ... ] }
file_registry = {}

def handle_client(conn, addr):
    # this function handles incoming connections from peers
    print(f"[TRACKER] Connected by {addr}")
    # receive data from the peer
    data = conn.recv(4096).decode()

    # check if the data is a register or a get request
    if data.startswith("REGISTER"):
        # Alice sends a register request to the tracker
        # data format: REGISTER|filename|chunk_name|peer_port
        _, filename, chunk_name, peer_port = data.split("|")
        # create a register for the filename if it doesn't exist
        if filename not in file_registry:
            file_registry[filename] = []
        # add the chunk name and peer address to the file registry
        file_registry[filename].append((chunk_name, addr[0], int(peer_port)))
        # send a response back to Alice saying the files have been registered
        conn.send(b"REGISTERED")
        print(f"[TRACKER] Registered: {chunk_name} of {filename} from {addr[0]}")
    
    elif data.startswith("GET"):
        # Bob sends a get request to the tracker
        # data format: GET|filename
        _, filename = data.split("|")
        # the tracker responds with the list of chunks for the requested file
        chunks = file_registry.get(filename, [])
        conn.send(json.dumps(chunks).encode())
        print(f"[TRACKER] Sent chunk list for {filename}")

    conn.close()

def start_tracker():
    # create a socket for the tracker that listens for incoming connections on port 6000
    tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tracker.bind(("0.0.0.0", 6000))
    tracker.listen()
    print("[TRACKER] Listening on port 6000...")

    # run the tracker server indefinitely
    while True:
        # accept incoming connections from peers (Alice or Bob)
        conn, addr = tracker.accept()
        # spawn a new thread to handle each connection, allowing multiple connections to be handled simultaneously
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