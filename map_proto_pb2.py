# Simulated content for map_proto_pb2.py
from google.protobuf.message import Message

class Map(Message):
    def __init__(self):
        self.name = ""
        self.likes = 0
        self.plays = 0
        self.shares = 0
        self.public_id = ""

class CraftlandMapList(Message):
    def __init__(self):
        self.maps = []
