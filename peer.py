# peer.py
import socket
import threading
import os
import sys

# Use command-line argument for the port, default to 7001
if len(sys.argv) > 1:
    # You specify the port the peer should listen on as a command-line argument
    # e.g. python3 peer.py 7001 to creat a peer listening on port 7001, 
    # # python3 peer.py 7002 to create a peer listening on port 7002
    PEER_PORT = int(sys.argv[1])
else:
    PEER_PORT = 7001

# make a directory to store the chunks
CHUNK_DIR = "chunks"
os.makedirs(CHUNK_DIR, exist_ok=True)

def handle_client(conn, addr):
    # this function handles incoming connections from peers
    try:
        request = conn.recv(1024).decode()
    except UnicodeDecodeError as e:
        print(f"[PEER] Error decoding request from {addr}: {e}")
        conn.close()
        return
    
    # if bob sends a requesto for a chunk, the peer will send the chunk
    if request.startswith("SEND"):
        _, chunk_name = request.split("|")
        try:
            # we read the chunk file and send it's raw data back to bob
            with open(os.path.join(CHUNK_DIR, chunk_name), "rb") as f:
                conn.sendall(f.read())
            print(f"[PEER] Sent {chunk_name} to {addr}")
        except FileNotFoundError:
            error_message = f"ERROR: File {chunk_name} not found."
            conn.sendall(error_message.encode())
            print(f"[PEER] {error_message}")
    
    # if alice sends a request to upload a chunk, the peer will receive the chunk
    elif request.startswith("UPLOAD"):
        _, chunk_name = request.split("|")
        conn.send(b"READY")  # send handshake ack before receiving file data
        # we write the data alice sent to us to a chunk file
        # print(f"[PEER] Receiving chunk: {chunk_name}")
        with open(os.path.join(CHUNK_DIR, chunk_name), "wb") as f:
            while True:
                # read the file in 4KB chunks from Alice
                bytes_read = conn.recv(4096)
                if not bytes_read:
                    break
                # write the data to a chunk file
                f.write(bytes_read)
        print(f"[PEER] Stored chunk: {chunk_name}")
    
    # close the server connection
    conn.close()

def start_peer():
    # this function starts the peer server to listen for incoming connections from Alice and Bob
    peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer.bind(("0.0.0.0", PEER_PORT))
    peer.listen()
    print(f"[PEER] Listening on port {PEER_PORT}...")
    # this loop will keep the peer server running and accepting incoming connections
    while True:
        # accept incoming connections from Alice and Bob and spawn a new thread to handle each connection simultaneously
        # this allows multiple connections to be handled at the same time
        conn, addr = peer.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

def register_with_tracker():
    with socket.socket() as s:
        s.connect(("localhost", 6000))
        s.send(f"PEER_REGISTER|{PEER_PORT}".encode())
        s.recv(1024)
        print(f"[PEER] Registered with tracker on port {PEER_PORT}")

if __name__ == "__main__":
    register_with_tracker()
    start_peer()