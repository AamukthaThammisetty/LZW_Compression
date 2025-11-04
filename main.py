# import os
# from lzw_compress import compress
# from lzw_decompress import decompress

# def main():
#     print("LZW File Compression & Decompression (Enhanced Version)")
#     print("1. Compress a file")
#     print("2. Decompress a file")

#     choice = input("Enter your choice (1/2): ").strip()

#     if choice == "1":
#         input_file = input("Enter input file path: ").strip()
#         if not os.path.exists(input_file):
#             print("Input file not found!")
#             return

#         # Ask user where to save
#         output_dir = input("Enter output folder path (or press Enter for default 'output/'): ").strip()
#         if not output_dir:
#             output_dir = "output"
#         os.makedirs(output_dir, exist_ok=True)

#         output_file = os.path.join(
#             output_dir, os.path.splitext(os.path.basename(input_file))[0] + ".lzw"
#         )

#         compress(input_file, output_file)
#         print(f"Compressed file saved at: {os.path.abspath(output_file)}")

#     elif choice == "2":
#         input_file = input("Enter compressed (.lzw) file path: ").strip()
#         if not os.path.exists(input_file):
#             print("Compressed file not found!")
#             return

#         # No need to specify .bin — decompressor restores the correct extension
#         decompress(input_file)

#     else:
#         print("Invalid choice!")

# if __name__ == "__main__":
#     main()


import streamlit as st
import os
import tempfile
from lzw_compress import compress
from lzw_decompress import decompress

st.set_page_config(page_title="LZW Compression Tool", page_icon="📦", layout="centered")

st.title("LZW File Compression & Decompression")
st.write("Upload any file (CSV, TXT, etc.) to compress or decompress using the LZW algorithm.")

# Sidebar for mode selection
st.sidebar.header("Select Operation")
action = st.sidebar.radio("Choose an option:", ["Compress File", "Decompress File"])

# Temporary directory for file handling
temp_dir = tempfile.mkdtemp()

# --------------------- COMPRESSION ---------------------
if action == "Compress File":
    st.header(" Compress a File")

    uploaded_file = st.file_uploader("Upload a file to compress", type=None)

    if uploaded_file is not None:
        input_path = os.path.join(temp_dir, uploaded_file.name)
        with open(input_path, "wb") as f:
            f.write(uploaded_file.read())

        st.success(f"File uploaded: {uploaded_file.name}")

        if st.button("Compress Now"):
            output_file = os.path.splitext(uploaded_file.name)[0] + ".lzw"
            output_path = os.path.join(temp_dir, output_file)

            compress(input_path, output_path)

            # Calculate sizes and ratio
            original_size = os.path.getsize(input_path)
            compressed_size = os.path.getsize(output_path)
            ratio = ((original_size - compressed_size) / original_size) * 100

            st.subheader("Compression Summary")
            st.write(f"**Original size:** {original_size / 1024:.2f} KB")
            st.write(f"**Compressed size:** {compressed_size / 1024:.2f} KB")

            if ratio >= 0:
                st.success(f"**Compression Ratio:** {ratio:.2f}% smaller")
            else:
                st.warning(f"**Compression Ratio:** {abs(ratio):.2f}% larger (file expanded slightly)")

            st.download_button(
                label="Download Compressed File",
                data=open(output_path, "rb").read(),
                file_name=output_file,
                mime="application/octet-stream"
            )

# --------------------- DECOMPRESSION ---------------------
elif action == "Decompress File":
    st.header("Decompress a File")

    uploaded_file = st.file_uploader("Upload a .lzw file to decompress", type=["lzw"])

    if uploaded_file is not None:
        input_path = os.path.join(temp_dir, uploaded_file.name)
        with open(input_path, "wb") as f:
            f.write(uploaded_file.read())

        st.success(f"File uploaded: {uploaded_file.name}")

        if st.button("Decompress Now"):
            output_path = decompress(input_path)

            # Calculate decompressed file size
            decompressed_size = os.path.getsize(output_path)
            compressed_size = os.path.getsize(input_path)

            st.subheader("Decompression Summary")
            st.write(f"**Compressed size:** {compressed_size / 1024:.2f} KB")
            st.write(f"**Decompressed size:** {decompressed_size / 1024:.2f} KB")

            st.download_button(
                label="Download Decompressed File",
                data=open(output_path, "rb").read(),
                file_name=os.path.basename(output_path),
                mime="application/octet-stream"
            )
