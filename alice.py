import socket
import os
import json

TRACKER_HOST = "localhost"
TRACKER_PORT = 6000
IMAGE_NAME = "img2.jpg"

# Remove hardcoded peers; instead, fetch available peers from tracker
def get_peers():
    with socket.socket() as s:
        s.connect((TRACKER_HOST, TRACKER_PORT))
        s.send("GET_PEERS".encode())
        data = s.recv(4096).decode()
        return json.loads(data)

def chunk_file(filename, size=1024*512):
    chunks = []
    # read the file in raw binary chunks and write each chunk to a seaprate file
    with open(filename, "rb") as f:
        part_num = 0
        # each chunk is 512 KB (1024 * 512), read the file in 512 KB chunks
        while chunk := f.read(size):
            # create a new file for each chunk with a part number at the end
            # e.g. image.png.part0, image.png.part1, etc.
            name = f"{filename}.part{part_num}"
            with open(name, "wb") as c:
                c.write(chunk)
            
            # append the chunk name to the list, this will be used to register 
            # the chunk with the tracker and to upload the chunk to the peer
            chunks.append(name)
            part_num += 1
    
    # return the list of chunk names
    # print(f"[ALICE] Created {len(chunks)} chunks: {chunks}")
    print(f"[ALICE] Created {len(chunks)}")
    return chunks

def upload_chunk(chunk_name, peer_host, peer_port):
    # connect to the peer and send the chunk
    with socket.socket() as s:
        # connect to the peer's upload port, this is the port that the peer is listening on
        # for incoming connections
        s.connect((peer_host, peer_port))
        # notify the peer that we're sending a chunk
        s.send(f"UPLOAD|{chunk_name}".encode())
        # wait for peer's READY acknowledgment
        ack = s.recv(1024).decode()
        # if the peer doesn't acknowledge, return
        if ack != "READY":
            print(f"[ALICE] Unexpected ack: {ack}")
            return
        
        # print(f"[ALICE] Sending {chunk_name} to {peer_host}:{peer_port}")
        # send file data in chunks
        with open(chunk_name, "rb") as f:
            while True:
                # read the file in 4 KB chunks (can be changed, but good size for most cases)
                bytes_read = f.read(4096)
                # if the file is empty, break (we reached the end of the file)
                if not bytes_read:
                    break
                # send chunk to the peer
                s.sendall(bytes_read)

def register_chunk(chunk_name, filename, peer_port):
    # connect to the tracker and register the chunk with it
    with socket.socket() as s:
        s.connect((TRACKER_HOST, TRACKER_PORT))
        # send the register message to the tracker which is listening for messages on the tracker port
        message = f"REGISTER|{filename}|{chunk_name}|{peer_port}"
        s.send(message.encode())
        s.recv(1024)
        print(f"[ALICE] Registered {chunk_name} with tracker.")

def main():
    # get the chunks for the file we want to upload to the peers
    filename = IMAGE_NAME
    chunks = chunk_file(filename)
    peers = get_peers()  # fetch available peers from tracker
    if not peers:
        print("[ALICE] No peers registered. Exiting...")
        return

    # iterate through all the chunks of the file
    for i, chunk in enumerate(chunks):
        # divide the chunks equally between all peers. Do this by storing the
        # first chunk in the first peer, the second in the second, and so on until there are no more peers
        # then start again from the first peer
        peer_host, peer_port = peers[i % len(peers)]

        # upload each chunk to the peer and register it with the tracker
        upload_chunk(chunk, peer_host, peer_port)
        register_chunk(chunk, filename, peer_port)
        # delete the chunk after successful upload/registration
        os.remove(chunk)

    print("[ALICE] Upload and registration complete.")

if __name__ == "__main__":
    main()