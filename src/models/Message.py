from dataclasses import dataclass

@dataclass
class Message:
	rowid: str
	server_id: str
	channel_id: str
	author_id: str
	content: str
	timestamp: str = None