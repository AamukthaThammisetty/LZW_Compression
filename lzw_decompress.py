# import os
# import struct

# def decompress(input_file):
#     os.makedirs("decompressed", exist_ok=True)

#     with open(input_file, "rb") as f:
#         # 🔹 Read and decode extension metadata
#         ext_len = struct.unpack("B", f.read(1))[0]
#         extension = f.read(ext_len).decode("utf-8")

#         # 🔹 Read the rest of the compressed data
#         data = f.read()

#     # Initialize dictionary
#     dictionary = {i: bytes([i]) for i in range(256)}
#     dict_size = 256
#     MAX_DICT_SIZE = 65535

#     # Convert data into list of 16-bit codes
#     compressed_codes = []
#     for i in range(0, len(data), 2):
#         if i + 1 < len(data):
#             code = struct.unpack(">H", data[i:i+2])[0]
#             compressed_codes.append(code)

#     # Begin decompression
#     current = dictionary[compressed_codes[0]]
#     decompressed_data = bytearray(current)

#     for code in compressed_codes[1:]:
#         if code in dictionary:
#             entry = dictionary[code]
#         elif code == dict_size:
#             entry = current + current[:1]
#         else:
#             raise ValueError(f"Bad compressed code: {code}")

#         decompressed_data.extend(entry)

#         # Update dictionary
#         if dict_size < MAX_DICT_SIZE:
#             dictionary[dict_size] = current + entry[:1]
#             dict_size += 1
#         else:
#             # Reset dictionary when full (to stay in sync)
#             dictionary = {i: bytes([i]) for i in range(256)}
#             dict_size = 256

#         current = entry

#     # Save decompressed output using the stored extension
#     base_name = os.path.splitext(os.path.basename(input_file))[0]
#     output_file = os.path.join("decompressed", base_name + extension)

#     with open(output_file, "wb") as f:
#         f.write(decompressed_data)

#     print(f"\nFile decompressed successfully: {output_file}")
#     print(f"Restored original format: {extension}")

#     original_size = len(decompressed_data)
#     print(f"Decompressed size: {original_size / 1024:.2f} KB")



import struct
import os

def decompress(input_file):
    with open(input_file, "rb") as f:
        # Read extension info
        ext_len = struct.unpack("B", f.read(1))[0]
        extension = f.read(ext_len).decode("utf-8")
        compressed_data = []

        while True:
            bytes_ = f.read(2)
            if not bytes_:
                break
            compressed_data.append(struct.unpack(">H", bytes_)[0])

    # Build the dictionary
    MAX_DICT_SIZE = 65535
    dictionary = {i: bytes([i]) for i in range(256)}
    dict_size = 256

    current = bytes([compressed_data[0]])
    decompressed_data = bytearray(current)

    for code in compressed_data[1:]:
        if code in dictionary:
            entry = dictionary[code]
        elif code == dict_size:
            entry = current + current[:1]
        else:
            raise ValueError(f"Bad compressed code: {code}")

        decompressed_data.extend(entry)

        if dict_size < MAX_DICT_SIZE:
            dictionary[dict_size] = current + entry[:1]
            dict_size += 1
        else:
            # Reset dictionary if full (matches compressor)
            dictionary = {i: bytes([i]) for i in range(256)}
            dict_size = 256

        current = entry

    # Save decompressed file in "decompressed" folder
    os.makedirs("decompressed", exist_ok=True)
    output_file = os.path.join("decompressed", os.path.splitext(os.path.basename(input_file))[0] + extension)

    with open(output_file, "wb") as f:
        f.write(decompressed_data)

    print(f"\nFile decompressed successfully: {output_file}")
    print(f"Decompressed size: {len(decompressed_data)/1024:.2f} KB")

    # Return path for Streamlit to use
    return output_file
