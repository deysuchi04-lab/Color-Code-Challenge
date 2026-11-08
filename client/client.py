import socket
import json
import threading
import queue


# ==================================================
# SERVER SETTINGS
# ==================================================

HOST = "127.0.0.1"
PORT = 5000


# ==================================================
# NETWORK CLIENT
# ==================================================

class NetworkClient:

    def __init__(self, host=HOST, port=PORT):

        self.host = host
        self.port = port

        self.client = None
        self.reader = None

        self.running = False

        # Queue stores messages received from server
        self.message_queue = queue.Queue()

        # Thread for receiving messages
        self.receive_thread = None

    # ==================================================
    # CONNECT TO SERVER
    # ==================================================

    def connect(self):

        try:

            self.client = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            self.client.connect(
                (self.host, self.port)
            )

            # File-like reader for
            # newline-separated JSON
            self.reader = self.client.makefile("r")

            self.running = True

            # Start receiving thread
            self.receive_thread = threading.Thread(
                target=self.receive_messages,
                daemon=True
            )

            self.receive_thread.start()

            print("Connected to server!")

            return True

        except Exception as e:

            print(
                "Connection failed:",
                e
            )

            return False

    # ==================================================
    # RECEIVE MESSAGES
    # ==================================================

    def receive_messages(self):

        while self.running:

            try:

                line = self.reader.readline()

                if not line:

                    break

                message = json.loads(
                    line.strip()
                )

                # Put message into queue
                self.message_queue.put(
                    message
                )

            except Exception as e:

                if self.running:

                    print(
                        "Receive error:",
                        e
                    )

                break

        self.running = False

    # ==================================================
    # SEND MESSAGE
    # ==================================================

    def send_message(self, message):

        try:

            data = json.dumps(
                message
            )

            self.client.sendall(
                (data + "\n").encode()
            )

            return True

        except Exception as e:

            print(
                "Send error:",
                e
            )

            return False

    # ==================================================
    # CHECK RECEIVED MESSAGE
    # ==================================================

    def get_message(self):

        if not self.message_queue.empty():

            return self.message_queue.get()

        return None

    # ==================================================
    # CLOSE CONNECTION
    # ==================================================

    def close(self):

        self.running = False

        try:

            if self.reader:
                self.reader.close()

            if self.client:
                self.client.close()

        except Exception:
            pass

        print(
            "Disconnected from server."
        )


# ==================================================
# TEST NETWORK CLIENT
# ==================================================

if __name__ == "__main__":

    import time

    print()
    print("=" * 50)
    print("COLOUR CODE CHALLENGE CLIENT")
    print("=" * 50)

    network = NetworkClient()

    print()
    print("Connecting to server...")

    if network.connect():

        # Give receive thread time to receive
        # welcome/player_count messages
        time.sleep(0.5)

        # --------------------------------------------------
        # DISPLAY RECEIVED MESSAGES
        # --------------------------------------------------

        while True:

            message = network.get_message()

            if message is None:
                break

            print()
            print("Message from server:")
            print(message)

        # --------------------------------------------------
        # SEND TEST MESSAGE
        # --------------------------------------------------

        test_message = {
            "type": "test",
            "message": "Hello from network client"
        }

        network.send_message(
            test_message
        )

        print()
        print("Test message sent to server.")

        # --------------------------------------------------
        # RECEIVE TEST RESPONSE
        # --------------------------------------------------

        for _ in range(20):

            response = network.get_message()

            if response is not None:

                print()
                print("Response from server:")
                print(response)

                if response.get(
                    "type"
                ) == "test_response":

                    break

            time.sleep(0.1)

        network.close()