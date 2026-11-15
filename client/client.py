import socket
import json
import threading
import queue


# ==================================================
# SERVER SETTINGS
# ==================================================

# OpenPort public server address
# Players from different locations will connect here.
HOST = "193.26.115.30"
PORT = 35438


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

        self.message_queue = queue.Queue()

        self.receive_thread = None

    # ==================================================
    # CONNECT TO SERVER
    # ==================================================

    def connect(self):

        try:

            print()
            print("Connecting to server...")
            print(f"Server: {self.host}:{self.port}")

            self.client = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            # Connection timeout
            self.client.settimeout(10)

            self.client.connect(
                (self.host, self.port)
            )

            # Remove timeout after connection
            # because the game needs a persistent connection
            self.client.settimeout(None)

            # Create file-like reader
            # for newline-separated JSON messages
            self.reader = self.client.makefile(
                "r",
                encoding="utf-8"
            )

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

            print()
            print("Connection failed:")
            print(e)

            try:

                if self.client:
                    self.client.close()

            except Exception:
                pass

            self.client = None
            self.reader = None
            self.running = False

            return False

    # ==================================================
    # RECEIVE MESSAGES
    # ==================================================

    def receive_messages(self):

        while self.running:

            try:

                line = self.reader.readline()

                # Server closed connection
                if not line:
                    break

                # Convert JSON text to Python dictionary
                message = json.loads(
                    line.strip()
                )

                # Store message in queue
                self.message_queue.put(
                    message
                )

            except json.JSONDecodeError as e:

                if self.running:

                    print(
                        "Invalid JSON received:",
                        e
                    )

                continue

            except Exception as e:

                if self.running:

                    print(
                        "Receive error:",
                        e
                    )

                break

        self.running = False

        print(
            "Connection to server closed."
        )

    # ==================================================
    # SEND MESSAGE
    # ==================================================

    def send_message(self, message):

        if not self.client or not self.running:

            print(
                "Not connected to server."
            )

            return False

        try:

            # Convert Python dictionary
            # into JSON
            data = json.dumps(
                message
            )

            # Send one JSON message per line
            self.client.sendall(
                (
                    data + "\n"
                ).encode("utf-8")
            )

            return True

        except Exception as e:

            print(
                "Send error:",
                e
            )

            self.running = False

            return False

    # ==================================================
    # CHECK RECEIVED MESSAGE
    # ==================================================

    def get_message(self):

        if not self.message_queue.empty():

            return (
                self.message_queue.get()
            )

        return None

    # ==================================================
    # CLOSE CONNECTION
    # ==================================================

    def close(self):

        self.running = False

        try:

            if self.reader:
                self.reader.close()

        except Exception:
            pass

        try:

            if self.client:

                self.client.shutdown(
                    socket.SHUT_RDWR
                )

        except Exception:
            pass

        try:

            if self.client:
                self.client.close()

        except Exception:
            pass

        self.reader = None
        self.client = None

        print(
            "Disconnected from server."
        )


# ==================================================
# TEST NETWORK CLIENT
# ==================================================

if __name__ == "__main__":

    import argparse
    import time

    # --------------------------------------------------
    # COMMAND LINE SETTINGS
    # --------------------------------------------------

    parser = argparse.ArgumentParser(
        description=(
            "Colour Code Challenge "
            "Network Client"
        )
    )

    parser.add_argument(
        "--host",
        default=HOST,
        help=(
            "Server IP address "
            "or hostname"
        )
    )

    parser.add_argument(
        "--port",
        type=int,
        default=PORT,
        help=(
            "Server TCP port"
        )
    )

    args = parser.parse_args()

    # --------------------------------------------------
    # START CLIENT
    # --------------------------------------------------

    print()
    print("=" * 50)
    print("COLOUR CODE CHALLENGE CLIENT")
    print("=" * 50)

    print()
    print(
        "Internet multiplayer mode"
    )

    print(
        f"Server: {args.host}:{args.port}"
    )

    # --------------------------------------------------
    # CREATE NETWORK CLIENT
    # --------------------------------------------------

    network = NetworkClient(
        host=args.host,
        port=args.port
    )

    # --------------------------------------------------
    # CONNECT
    # --------------------------------------------------

    if network.connect():

        # Give receiving thread
        # some time to receive
        # initial server messages

        time.sleep(0.5)

        # ------------------------------------------------
        # DISPLAY INITIAL MESSAGES
        # ------------------------------------------------

        while True:

            message = (
                network.get_message()
            )

            if message is None:
                break

            print()
            print(
                "Message from server:"
            )

            print(
                message
            )

        # ------------------------------------------------
        # SEND TEST MESSAGE
        # ------------------------------------------------

        test_message = {

            "type": "test",

            "message": (
                "Hello from "
                "Internet network client"
            )

        }

        network.send_message(
            test_message
        )

        print()
        print(
            "Test message sent to server."
        )

        # ------------------------------------------------
        # WAIT FOR TEST RESPONSE
        # ------------------------------------------------

        for _ in range(30):

            response = (
                network.get_message()
            )

            if response is not None:

                print()
                print(
                    "Response from server:"
                )

                print(
                    response
                )

                if (
                    response.get("type")
                    == "test_response"
                ):

                    break

            time.sleep(0.1)

        # ------------------------------------------------
        # CLOSE
        # ------------------------------------------------

        network.close()

    else:

        print()
        print(
            "Could not connect to "
            "Colour Code Challenge server."
        )

        print()
        print(
            "Make sure:"
        )

        print(
            "1. server.py is running"
        )

        print(
            "2. OpenPort is connected"
        )

        print(
            "3. OpenPort forwards "
            "port 35438 to local port 5000"
        )