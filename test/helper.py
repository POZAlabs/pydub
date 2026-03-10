import struct


def make_8bit(*samples):
    return struct.pack(f"{len(samples)}b", *samples)


def make_16bit(*samples):
    return struct.pack(f"<{len(samples)}h", *samples)


def make_32bit(*samples):
    return struct.pack(f"<{len(samples)}i", *samples)
