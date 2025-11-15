import heapq
import pickle
import time
from collections import defaultdict

# -----------------------------
# LZ77 Compression
# -----------------------------
def lz77_compress(text, window_size=100, lookahead_buffer=20):
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
        return Node()  # empty tree
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
    return [pickle.dumps(t) for t in tokens]

def symbols_to_tokens(symbols):
    return [pickle.loads(s) for s in symbols]

# -----------------------------
# File-based Compress/Decompress
# -----------------------------
def compress_file(input_text):
    start = time.time()
    original_size = len(input_text.encode("utf-8"))
    tokens = lz77_compress(input_text)
    symbols = tokens_to_symbols(tokens)
    huff_root = build_huffman_tree(symbols)
    huff_codes = build_huffman_codes(huff_root)
    encoded = huffman_encode(symbols, huff_codes)

    compressed_data = {"encoded": encoded, "huff_tree": huff_root}
    compressed_size = len(pickle.dumps(compressed_data))
    ratio = (1 - compressed_size / max(original_size, 1)) * 100
    end = time.time()

    return compressed_data, original_size, compressed_size, ratio, end - start

def decompress_file(compressed_data):
    start = time.time()
    encoded = compressed_data.get("encoded", "")
    huff_root = compressed_data.get("huff_tree", None)
    decoded_symbols = huffman_decode(encoded, huff_root)
    tokens = symbols_to_tokens(decoded_symbols)
    decompressed_text = lz77_decompress(tokens)
    end = time.time()
    return decompressed_text, len(decompressed_text.encode("utf-8")), end - start
