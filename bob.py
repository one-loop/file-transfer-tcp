# bob.py
import socket
import json
import os

TRACKER_HOST = "localhost"
TRACKER_PORT = 6000
IMAGE_NAME = "img2.jpg" # important, make sure the image name is the same as in alice.py
# NOTE: make these peers dynamic/not hardcoded


def get_chunk_list(filename):
    # connect to the tracker and request the list of chunks for the given filename
    # the tracker will respond with a list of tuples (chunk_name, peer_host, peer_port)
    # e.g. [("image.png.part0", "localhost", 7001), ("image.png.part1", "localhost", 7002), ...]
    with socket.socket() as s:
        # create a socket and connect to the tracker, and send a GET request to the tracker for the filename
        s.connect((TRACKER_HOST, TRACKER_PORT))
        s.send(f"GET|{filename}".encode())
        # receive the response (list of chunks of the file) from the tracker
        data = s.recv(4096).decode()
        # the response is a JSON string, so we need to parse it into a Python object (list of tuples)
        # e.g. [("image.png.part0", "localhost", 7001), ("image.png.part1", "localhost", 7002), ...]
        return json.loads(data)

def download_chunk(chunk_name, peer_host, peer_port):
    with socket.socket() as s:
        # create a socket and connect to the peer, and send a SEND request to the peer for the chunk
        s.connect((peer_host, peer_port))
        s.send(f"SEND|{chunk_name}".encode())
        with open(chunk_name, "wb") as f:
            # receive the chunk data from the peer and write it to a file
            # print(f"[BOB] Receiving {chunk_name} from {peer_host}:{peer_port}")
            while True:
                data = s.recv(4096)
                if not data:
                    break
                f.write(data)


def reconstruct_file(output_file, chunk_names):
    # sort using the numeric part after 'part'. This is important to ensure the image is reconstructed in the correct order
    sorted_chunks = sorted(chunk_names, key=lambda name: int(name.rsplit("part", 1)[-1]))
    print("Reconstructing the File")
    # open the output file in binary mode and write all the chunks to it
    with open(output_file, "wb") as f:
        for chunk in sorted_chunks:
            # print(chunk)
            with open(chunk, "rb") as c: # read the data of the chunk and write it to the output file
                f.write(c.read())
    
    # delete the chunk files after reconstruction
    for chunk in sorted_chunks:
        os.remove(chunk)


def main():
    # connect to the tracker and get the list of chunks for the given filename
    # the tracker will respond with a list of tuples (chunk_name, peer_host, peer_port)
    # e.g. [("image.png.part0", "localhost", 7001), ("image.png.part1", "localhost", 7002), ...]
    filename = IMAGE_NAME
    chunk_list = get_chunk_list(filename)
    print(chunk_list)

    chunk_names = []
    
    # download each chunk from their respective peers and store in separate files
    for chunk_name, peer_host, peer_port in chunk_list:
        print(f"[BOB] Downloading {chunk_name} from {peer_host}:{peer_port}")
        download_chunk(chunk_name, peer_host, peer_port)
        # add the chunk name to the list of chunk names, which will be used to reconstruct the file
        chunk_names.append(chunk_name)

    # reconstruct the file from all the downloaded chunks
    reconstruct_file("reconstructed_" + filename, chunk_names)
    print("[BOB] File reconstruction complete: reconstructed_" + filename)

if __name__ == "__main__":
    main()
