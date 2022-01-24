from dataclasses import dataclass
from .Server import Server
from .Channel import Channel

@dataclass
class ServerChannel:
	server: Server
	channel: Channel
	timestamp: str