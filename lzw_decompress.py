import os
import struct
import time

def decompress(input_file):
    start_time = time.time()

    with open(input_file, "rb") as f:
        ext_len = struct.unpack("B", f.read(1))[0]
        extension = f.read(ext_len).decode("utf-8")
        compressed_data = []

        while True:
            bytes_read = f.read(2)
            if not bytes_read:
                break
            (code,) = struct.unpack(">H", bytes_read)
            compressed_data.append(code)

    # Initialize dictionary
    MAX_DICT_SIZE = 65535
    dictionary = {i: bytes([i]) for i in range(256)}
    dict_size = 256

    current = bytes([compressed_data.pop(0)])
    result = bytearray(current)

    for code in compressed_data:
        if code in dictionary:
            entry = dictionary[code]
        elif code == dict_size:
            entry = current + current[:1]
        else:
            raise ValueError(f"Bad compressed code: {code}")

        result.extend(entry)

        if dict_size < MAX_DICT_SIZE:
            dictionary[dict_size] = current + entry[:1]
            dict_size += 1
        else:
            # Reset dictionary if full
            dictionary = {i: bytes([i]) for i in range(256)}
            dict_size = 256

        current = entry

    output_file = f"decompressed/{os.path.splitext(os.path.basename(input_file))[0]}_decompressed{extension}"
    os.makedirs("decompressed", exist_ok=True)

    with open(output_file, "wb") as f:
        f.write(result)

    end_time = time.time()
    decompressed_size = os.path.getsize(output_file)
    duration = end_time - start_time

    return output_file, decompressed_size, duration
