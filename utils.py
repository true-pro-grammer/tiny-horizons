from enum import Flag, auto

class Event(Flag):
    START_GAME = auto()
    QUIT_GAME = auto()
    TERMINATE = auto()

def split_evenly(s: str, parts: int) -> list[str]:
    if parts <= 0:
        raise ValueError("parts must be greater than 0")

    length = len(s)
    base, remainder = divmod(length, parts)

    chunks = []
    start = 0

    for i in range(parts):
        size = base + (i < remainder)
        chunks.append(s[start:start + size])
        start += size

    return chunks