import socket
import json


# ==================================================
# SERVER SETTINGS
# ==================================================

HOST = "127.0.0.1"
PORT = 5000


# ==================================================
# CONNECT TO SERVER
# ==================================================

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("Connecting to Colour Code Challenge Server...")

client.connect((HOST, PORT))

print("Connected to server!")


# Create a file-like object for reading
reader = client.makefile("r")


# ==================================================
# RECEIVE JSON MESSAGE
# ==================================================

def receive_message():
    line = reader.readline()

    if not line:
        return None

    return json.loads(line.strip())


# ==================================================
# RECEIVE WELCOME MESSAGE
# ==================================================

message = receive_message()

print()
print("Message from server:")
print(message)


# ==================================================
# RECEIVE PLAYER COUNT
# ==================================================

message = receive_message()

print()
print("Player count message:")
print(message)


# ==================================================
# SEND TEST MESSAGE
# ==================================================

test_message = {
    "type": "test",
    "message": "Hello from client"
}

data = json.dumps(test_message)

client.send((data + "\n").encode())

print()
print("Test message sent to server.")


# ==================================================
# RECEIVE TEST RESPONSE
# ==================================================

response = receive_message()

print()
print("Response from server:")
print(response)


# ==================================================
# CLOSE CONNECTION
# ==================================================

reader.close()
client.close()

print()
print("Disconnected from server.")