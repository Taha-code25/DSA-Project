import os
import pickle

from io import BytesIO

# Core Compression (unchanged)
def lzw_compress(uncompressed: bytes):
    """Compress a byte string to a list of output symbols."""
    if not uncompressed:
        return []

    dict_size = 256
    dictionary = {bytes([i]): i for i in range(dict_size)}

    w = b""
    compressed_data = []

    for c_byte in uncompressed:
        c = bytes([c_byte])
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            compressed_data.append(dictionary[w])
            dictionary[wc] = dict_size
            dict_size += 1
            w = c

    if w:
        compressed_data.append(dictionary[w])
    return compressed_data


# Core Decompression (unchanged)
def lzw_decompress(compressed: list[int]):
    """Decompress a list of output codes to a byte string."""
    if not compressed:
        return b""

    dict_size = 256
    dictionary = {i: bytes([i]) for i in range(dict_size)}

    result = BytesIO()
    w = dictionary[compressed[0]]
    result.write(w)

    for k in compressed[1:]:
        if k in dictionary:
            entry = dictionary[k]
        elif k == dict_size:
            entry = w + w[0:1]
        else:
            raise ValueError(f"Bad compressed k: {k}")

        result.write(entry)
        dictionary[dict_size] = w + entry[0:1]
        dict_size += 1
        w = entry

    return result.getvalue()


def compress_file(input_path):
    """Reads a file, compresses its contents using LZW, and saves it to an .lzw file."""
    filename, ext = os.path.splitext(input_path)

    try:
        with open(input_path, "rb") as f:
            data = f.read()
    except IOError as e:
        print(f" Error reading file {input_path}: {e}")
        return ""

    compressed_data = lzw_compress(data)
    output_path = filename + ".lzw"

    try:
        with open(output_path, "wb") as f:
            pickle.dump({"ext": ext, "data": compressed_data}, f)
    except IOError as e:
        print(f" Error writing compressed file to {output_path}: {e}")
        return ""

    print(f" Compression successful! Saved as {output_path}")
    return output_path


def decompress_file(input_path):
    try:
        with open(input_path, "rb") as f:
            content = pickle.load(f)

        # Validate structure
        if not isinstance(content, dict) or "data" not in content or "ext" not in content:
            raise ValueError("Invalid file structure. This is not a valid LZW-compressed file.")

    except (pickle.UnpicklingError, EOFError, ValueError) as e:
        raise ValueError(" The selected file is not a valid LZW-compressed file.") from e

    original_ext = content["ext"]
    compressed_data = content["data"]

    try:
        decompressed_data = lzw_decompress(compressed_data)
    except ValueError as e:
        raise ValueError(" Failed to decompress file content. It may be corrupted or incomplete.") from e

    output_path = input_path.replace(".lzw", "_restored" + original_ext)

    try:
        with open(output_path, "wb") as f:
            f.write(decompressed_data)
    except IOError as e:
        print(f" Error writing restored file to {output_path}: {e}")
        return ""

    print(f" Decompression successful! Restored as {output_path}")
    return output_path