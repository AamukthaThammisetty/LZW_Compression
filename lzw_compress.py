import struct
import os

def compress(input_file, output_file=None):
    # Detect and store file extension for decompression
    extension = os.path.splitext(input_file)[1]

    # If output file not specified, save under 'compressed/'
    if output_file is None:
        os.makedirs("compressed", exist_ok=True)
        output_file = os.path.join("compressed", os.path.basename(input_file) + ".lzw")
    else:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(input_file, "rb") as f:
        data = f.read()

    MAX_DICT_SIZE = 65535
    dictionary = {bytes([i]): i for i in range(256)}
    dict_size = 256
    current = bytes()
    compressed_data = []

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
                # Reset dictionary to stay in sync with decompressor
                dictionary = {bytes([i]): i for i in range(256)}
                dict_size = 256
            current = bytes([byte])

    if current:
        compressed_data.append(dictionary[current])

    # Write extension and compressed codes
    with open(output_file, "wb") as f:
        # Save extension length + extension itself
        f.write(struct.pack("B", len(extension)))
        f.write(extension.encode("utf-8"))

        # Save codes as 16-bit values
        for code in compressed_data:
            f.write(struct.pack(">H", code))  # Big-endian 2-byte code

    # Show stats
    original_size = os.path.getsize(input_file)
    compressed_size = os.path.getsize(output_file)
    compression_ratio = ((original_size - compressed_size) / original_size) * 100

    print(f"\nFile compressed successfully: {output_file}")
    print(f"Original size:   {original_size/1024:.2f} KB")
    print(f"Compressed size: {compressed_size/1024:.2f} KB")

    if compression_ratio > 0:
        print(f"Compression ratio: {compression_ratio:.2f}% smaller\n")
    else:
        print(f"Compressed file is {abs(compression_ratio):.2f}% larger than original.\n")
