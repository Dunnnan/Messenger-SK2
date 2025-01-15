import struct

# Klasa używana do przesyłu flag w wiadomościach
class Message:
    def __init__(self,flag):
        self.flag = flag

    def to_bytes(self):
        return struct.pack("i",self.flag)
