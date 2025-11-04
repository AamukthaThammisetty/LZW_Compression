import os
import streamlit as st
from lzw_compress import compress
from lzw_decompress import decompress

def main():
    st.title("LZW Compression & Decompression Tool")
    st.write("Efficient file compression and decompression using the Lempel–Ziv–Welch (LZW) algorithm.")

    mode = st.radio("Select Operation:", ("Compress a File", "Decompress a File"))

    if mode == "Compress a File":
        uploaded_file = st.file_uploader("Upload a file to compress", type=None)
        if uploaded_file is not None:
            input_path = f"temp_{uploaded_file.name}"
            with open(input_path, "wb") as f:
                f.write(uploaded_file.read())

            if st.button("Compress"):
                output_file, original_size, compressed_size, duration = compress(input_path)

                st.success("File compressed successfully!")
                st.write(f"Original Size: {original_size / 1024:.2f} KB")
                st.write(f"Compressed Size: {compressed_size / 1024:.2f} KB")
                st.write(f"Compression Ratio: {(compressed_size / original_size) * 100:.2f}%")
                st.write(f"Time Taken: {duration:.3f} seconds")

                with open(output_file, "rb") as f:
                    st.download_button(
                        label= "Download Compressed File",
                        data=f,
                        file_name=os.path.basename(output_file),
                        mime="application/octet-stream"
                    )

    elif mode == "Decompress a File":
        uploaded_file = st.file_uploader("Upload a .lzw file to decompress", type=["lzw"])
        if uploaded_file is not None:
            input_path = f"temp_{uploaded_file.name}"
            with open(input_path, "wb") as f:
                f.write(uploaded_file.read())

            if st.button("Decompress"):
                try:
                    output_file, decompressed_size, duration = decompress(input_path)

                    st.success("File decompressed successfully!")
                    st.write(f"Decompressed Size: {decompressed_size / 1024:.2f} KB")
                    st.write(f"Time Taken: {duration:.3f} seconds")

                    with open(output_file, "rb") as f:
                        st.download_button(
                            label="Download Decompressed File",
                            data=f,
                            file_name=os.path.basename(output_file),
                            mime="application/octet-stream"
                        )
                except Exception as e:
                    st.error(f"Decompression failed: {e}")

if __name__ == "__main__":
    main()
