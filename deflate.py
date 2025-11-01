import heapq
import pickle
import time
from collections import defaultdict

# -----------------------------
# LZ77 Compression
# -----------------------------
def lz77_compress(text, window_size=1000, lookahead_buffer=200):
    i = 0
    tokens = []
    while i < len(text):
        best_length = 0
        best_distance = 0
        start_index = max(0, i - window_size)
        for j in range(start_index, i):
            length = 0
            while (length < lookahead_buffer and
                   i + length < len(text) and
                   text[j + length] == text[i + length]):
                length += 1
            if length > best_length:
                best_length = length
                best_distance = i - j
        next_char = text[i + best_length] if i + best_length < len(text) else ""
        tokens.append((best_distance, best_length, next_char))
        i += best_length + (1 if next_char else 0)
    return tokens


def lz77_decompress(tokens):
    output = ""
    for distance, length, next_char in tokens:
        distance = int(distance)
        length = int(length)
        if distance == 0:
            output += next_char
        else:
            start = len(output) - distance
            for k in range(length):
                output += output[start + k]
            output += next_char
    return output


# -----------------------------
# Huffman Coding
# -----------------------------
class Node:
    def __init__(self, symbol=None, freq=0):
        self.symbol = symbol
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


def build_huffman_tree(data):
    if not data:
        return Node()
    freq = defaultdict(int)
    for item in data:
        freq[item] += 1
    heap = [Node(sym, f) for sym, f in freq.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)
        merged = Node(freq=node1.freq + node2.freq)
        merged.left = node1
        merged.right = node2
        heapq.heappush(heap, merged)
    return heap[0]


def build_huffman_codes(node, prefix="", codebook=None):
    if codebook is None:
        codebook = {}
    if node is None:
        return codebook
    if node.symbol is not None:
        codebook[node.symbol] = prefix
    else:
        build_huffman_codes(node.left, prefix + "0", codebook)
        build_huffman_codes(node.right, prefix + "1", codebook)
    return codebook


def huffman_encode(data, codebook):
    return "".join(codebook[item] for item in data)


def huffman_decode(encoded_str, root):
    if root is None:
        return []
    decoded = []
    node = root
    for bit in encoded_str:
        node = node.left if bit == '0' else node.right
        if node.symbol is not None:
            decoded.append(node.symbol)
            node = root
    return decoded


# -----------------------------
# Tokens ↔ Strings
# -----------------------------
def tokens_to_symbols(tokens):
    return [f"{d},{l},{c}" for d, l, c in tokens]


def symbols_to_tokens(symbols):
    return [tuple(s.split(',', 2)) for s in symbols]


# -----------------------------
# Main Program
# -----------------------------
def compress_file(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    original_size = len(text.encode("utf-8"))

    paragraph_len = max((len(p) for p in text.split('\n') if p.strip()), default=0)
    window_size = max(1000, paragraph_len)
    lookahead_buffer = max(500, paragraph_len)

    start = time.time()
    tokens = lz77_compress(text, window_size, lookahead_buffer)
    symbols = tokens_to_symbols(tokens)
    huff_root = build_huffman_tree(symbols)
    huff_codes = build_huffman_codes(huff_root)
    encoded = huffman_encode(symbols, huff_codes)

    with open(output_file, "wb") as f:
        pickle.dump({"encoded": encoded, "huff_tree": huff_root}, f)

    compressed_size = len(encoded.encode("utf-8"))
    ratio = (1 - compressed_size / max(original_size, 1)) * 100
    end = time.time()

    print("✅ Compression complete!")
    print(f"Original Size: {original_size} bytes")
    print(f"Compressed Size: {compressed_size} bytes")
    print(f"Compression Ratio: {ratio:.2f}%")
    print(f"Time Taken: {end - start:.4f} s")


def decompress_file(input_file, output_file):
    with open(input_file, "rb") as f:
        obj = pickle.load(f)

    start = time.time()
    encoded = obj["encoded"]
    huff_root = obj["huff_tree"]
    decoded_symbols = huffman_decode(encoded, huff_root)
    tokens = symbols_to_tokens(decoded_symbols)
    decompressed_text = lz77_decompress(tokens)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(decompressed_text)

    end = time.time()
    print("✅ Decompression complete!")
    print(f"Decompressed Size: {len(decompressed_text.encode('utf-8'))} bytes")
    print(f"Time Taken: {end - start:.4f} s")
