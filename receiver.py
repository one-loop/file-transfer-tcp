import socket
import tqdm

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 5069))
server.listen(1)
print("Server Listening on Port 5069...")

client, addr = server.accept()
print(f"Connected by {addr}")

# receive the header
header = client.recv(1024).decode()
filename, filesize = header.split("|")
filesize = int(filesize)

print(f"Receiving {filename} ({filesize} bytes)")

# receive file data
file = open("received_" + filename, "wb")
progress = tqdm.tqdm(unit="B", unit_scale=True, total=filesize)

received_bytes = 0

while True:
    data = client.recv(1024)
    if b"<EOF>" in data:
        data = data.replace(b"<EOF>", b"")
        file.write(data)
        progress.update(len(data))
        break
    file.write(data)
    received_bytes += len(data)
    progress.update(len(data))

file.close()
client.close()
server.close()
print(f"File {filename} received successfully.")
