import os
import struct
import time

def compress(input_file):
    start_time = time.time()

    # Detect file extension
    extension = os.path.splitext(input_file)[1]
    output_file = f"compressed/{os.path.basename(input_file)}.lzw"

    os.makedirs("compressed", exist_ok=True)

    # Read input data
    with open(input_file, "rb") as f:
        data = f.read()

    # Initialize dictionary
    MAX_DICT_SIZE = 65535
    dictionary = {bytes([i]): i for i in range(256)}
    dict_size = 256
    current = bytes()
    compressed_data = []

    # Compression logic
    for byte in data:
        next_seq = current + bytes([byte])
        if next_seq in dictionary:
            current = next_seq
        else:
            compressed_data.append(dictionary[current])
            if dict_size < MAX_DICT_SIZE:
                dictionary[next_seq] = dict_size
                dict_size += 1
            else:
                # Reset dictionary if full
                dictionary = {bytes([i]): i for i in range(256)}
                dict_size = 256
            current = bytes([byte])

    if current:
        compressed_data.append(dictionary[current])

    # Write compressed data
    with open(output_file, "wb") as f:
        f.write(struct.pack("B", len(extension)))
        f.write(extension.encode("utf-8"))
        for code in compressed_data:
            f.write(struct.pack(">H", code))

    end_time = time.time()
    original_size = os.path.getsize(input_file)
    compressed_size = os.path.getsize(output_file)
    duration = end_time - start_time

    return output_file, original_size, compressed_size, duration
