from message import Message

class PeerConnection:
    # Setting maximum buffer size as 1 MB
    MAX_BUFFER_SIZE = 1024 * 1024

    def __init__(self, sock, address):
        self.peer_id = None
        self.socket = sock
        self.address = address
        self.inbound_buffer = b""
        self.outbound_buffer = b""
        self.is_handshake_complete = False

    def queue_message(self, message):
        json_message = message.to_json()
        message_bytes = (json_message + "\n").encode("utf-8")

        # Handling maximum buffer size overflow
        if len(self.outbound_buffer) + len(message_bytes) > self.MAX_BUFFER_SIZE:
            print(f"Maximum buffer sized reached on outbound buffer for {self.address}")
            return False
        
        self.outbound_buffer += message_bytes
        return True

    def is_message_complete(self):
        """Return True when a full newline-terminated message is available.

        Messages are framed by newlines in this simple protocol.
        """
        return b"\n" in self.inbound_buffer
    
    def extract_message(self):
        """Pop a single message from the inbound buffer and parse it.

        Returns a Message object or None on parse error.
        """
        if not self.is_message_complete():
            return None

        try:
            line, self.inbound_buffer = self.inbound_buffer.split(b"\n", 1)
            return Message.from_json(line.decode("utf-8"))
        except Exception as e:
            print(f"Error extracting the message: {e}")
            return None
        
    def send_buffered_data(self):
        """Attempt to flush outbound buffer to the socket.

        Returns:
            True  - buffer fully sent
            False - still data remaining or would block
            None  - connection closed/broken
        """
        if not self.outbound_buffer:
            return True

        try:
            sent = self.socket.send(self.outbound_buffer)
            self.outbound_buffer = self.outbound_buffer[sent:]
            return True if not self.outbound_buffer else False
        except BlockingIOError:
            # OS send buffer full - try again later
            return False
        except ConnectionResetError:
            # Remote closed the connection
            return None
