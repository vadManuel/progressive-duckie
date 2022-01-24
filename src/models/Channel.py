from dataclasses import dataclass

@dataclass
class Channel:
	rowid: str
	type: str
	timestamp: str