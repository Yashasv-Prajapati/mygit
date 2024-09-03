import binascii
# Function to convert SHA-1 hex string to binary
def hex_to_binary(hex_string):
    return bytes.fromhex(hex_string)

def binary_to_hex(binary_string):
    return bytes.hex(binary_string)

def string_to_binary(string:str):
    return string.encode('utf-8')

def binary_to_string(binary_string: bytes):
    return binary_string.decode("utf-8")