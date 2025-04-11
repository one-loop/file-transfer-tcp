import socket
import threading
import os
import sys

# Default port for the peer server
DEFAULT_PORT = 7001
# make a directory to store the chunks
CHUNK_DIR = "chunks"
os.makedirs(CHUNK_DIR, exist_ok=True)

def is_port_in_use(port):
    """Check if the port is in use by attempting to bind to it."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("0.0.0.0", port))
            return False
        except socket.error:
            return True

def get_available_port(start_port=DEFAULT_PORT):
    """Find an available port starting from `start_port`."""
    port = start_port
    while is_port_in_use(port):
        port += 1
    return port

def handle_client(conn, addr):
    # this function handles incoming connections from peers
    try:
        request = conn.recv(1024).decode()
    except UnicodeDecodeError as e:
        print(f"[PEER] Error decoding request from {addr}: {e}")
        conn.close()
        return
    
    # if bob sends a request for a chunk, the peer will send the chunk
    if request.startswith("SEND"):
        _, chunk_name = request.split("|")
        try:
            # we read the chunk file and send its raw data back to bob
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

def start_peer(port):
    # this function starts the peer server to listen for incoming connections from Alice and Bob
    peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    peer.bind(("0.0.0.0", port))
    peer.listen()
    print(f"[PEER] Listening on port {port}...")
    
    # this loop will keep the peer server running and accepting incoming connections
    while True:
        # accept incoming connections from Alice and Bob and spawn a new thread to handle each connection simultaneously
        # this allows multiple connections to be handled at the same time
        conn, addr = peer.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

def register_with_tracker(port):
    with socket.socket() as s:
        s.connect(("localhost", 6000))
        s.send(f"PEER_REGISTER|{port}".encode())
        s.recv(1024)
        print(f"[PEER] Registered with tracker on port {port}")

def main():
    # Get the port from the command-line argument or find an available port
    if len(sys.argv) > 1:
        try:
            PEER_PORT = int(sys.argv[1])
            if is_port_in_use(PEER_PORT):
                print(f"[PEER] Port {PEER_PORT} is already in use. Trying another port...")
                PEER_PORT = get_available_port(PEER_PORT + 1)
                print(f"[PEER] Using available port: {PEER_PORT}")
        except ValueError:
            print("[PEER] Invalid port number provided. Exiting...")
            sys.exit(1)
    else:
        PEER_PORT = get_available_port(DEFAULT_PORT)
        print(f"[PEER] No port specified. Using available port: {PEER_PORT}")
    
    register_with_tracker(PEER_PORT)
    start_peer(PEER_PORT)

if __name__ == "__main__":
    main()