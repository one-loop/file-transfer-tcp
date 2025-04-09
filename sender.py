import os
import socket

# create a TCP client internet socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 5069))  # connect to receiver

# define file details
filename = "img2.jpg"
filesize = os.path.getsize(filename)

# send metadata: "filename|filesize"
header = f"{filename}|{filesize}"
client.send(header.encode())  # send header

# wait a tiny bit (optional, to avoid read collision)
import time; time.sleep(0.1)

# send file data
with open(filename, "rb") as file:
    data = file.read()
    client.sendall(data)

client.send(b"<EOF>")  # send EOF signal
print("File sent successfully.")
client.close()
