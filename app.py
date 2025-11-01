#option 2
import streamlit as st
import lzw
import deflate
import os
import matplotlib.pyplot as plt
import pickle

# --- PAGE CONFIG ---
st.set_page_config(page_title="Dual-Algorithm Compression Tool", layout="centered", page_icon="📦")

# --- SIDEBAR SETTINGS ---
st.sidebar.header("⚙️ Options")
mode = st.sidebar.radio("Select Mode", ["Compress", "Decompress"])
algorithm = st.sidebar.selectbox("Choose Algorithm", ["LZW", "Deflate"])

# --- BASE STYLING ---
bg_light = """
    background: linear-gradient(135deg, #e0f2ff 0%, #ffffff 100%);
    color: #1e3a8a;
"""
bg_dark = """
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: #f1f5f9;
"""
text_color = "#1e3a8a"
card_bg = "#ffffff"
card_shadow = "rgba(0,0,0,0.1)"

# --- CUSTOM CSS ---
st.markdown(f"""
    <style>
        body {{
            {bg_light}
        }}
        .title {{
            background: linear-gradient(to right, #1e3a8a, #3b82f6);
            color: white;
            padding: 20px 0;
            border-radius: 10px;
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 15px;
        }}
        section[data-testid="stSidebar"] {{
            background-color: {"#e0ebff"};
        }}
        div.stButton > button {{
            background: linear-gradient(90deg, #1e40af, #3b82f6);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 10px 20px;
            font-weight: 600;
            transition: 0.3s;
        }}
        div.stButton > button:hover {{
            background: linear-gradient(90deg, #2563eb, #60a5fa);
            transform: scale(1.05);
        }}
        .card {{
            background-color: {card_bg};
            border-radius: 15px;
            box-shadow: 0 4px 12px {card_shadow};
            padding: 25px;
            margin-top: 20px;
            transition: 0.3s ease-in-out;
        }}
        .card:hover {{
            transform: scale(1.02);
            box-shadow: 0 6px 16px {card_shadow};
        }}
        .details {{
            background-color: {"#eff6ff"};
            border-left: 5px solid #3b82f6;
            padding: 10px 15px;
            border-radius: 10px;
            margin-top: 10px;
            color: {text_color};
        }}
        footer {{
            text-align: center;
            color: gray;
            margin-top: 50px;
            font-size: 14px;
        }}
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="title"> Dual-Algorithm File Compression Tool</div>', unsafe_allow_html=True)
st.write("Easily **compress** or **decompress** any file using algorithms like **LZW** or **Deflate**.")

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("📁 Upload any file", type=None)

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    file_name = uploaded_file.name
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📂 File Details")

    # --- FILE PREVIEW ---
    st.write(f"**Name:** {file_name}")
    st.write(f"**Size:** {len(file_bytes)} bytes")

    if file_name.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
        st.image(uploaded_file, caption="Image Preview", use_container_width=True)
    elif file_name.lower().endswith((".txt", ".csv", ".py", ".json")):
        st.text_area("📄 File Preview (First 500 chars)", file_bytes[:500].decode(errors="ignore"), height=200)
    else:
        st.info("🗂️ No preview available for this file type.")

    st.markdown('</div>', unsafe_allow_html=True)

    # --- MAIN ACTION ---
    if mode == "Compress":
        st.markdown('<div class="card"><h4>🗜️ Compression Process</h4>', unsafe_allow_html=True)

        if st.button("Start Compression 🚀"):
            with st.spinner("Compressing... please wait ⏳"):
                if algorithm == "LZW":
                    temp_path = os.path.join("compressed_" + file_name)
                    with open(temp_path, "wb") as temp_file:
                        temp_file.write(file_bytes)
                    compressed_path = lzw.compress_file(temp_path)
                    os.remove(temp_path)

                    compressed_size = os.path.getsize(compressed_path)
                    original_size = len(file_bytes)
                    ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0

                elif algorithm == "Deflate":
                    text_data = file_bytes.decode(errors="ignore")
                    compressed_data, original_size, compressed_size, ratio, duration = deflate.compress_file(text_data)
                    compressed_path = file_name + ".deflate"
                    with open(compressed_path, "wb") as f:
                        pickle_bytes = pickle.dumps(compressed_data)
                        f.write(pickle_bytes)
                else:
                    st.error("Unknown algorithm selected.")
                    st.stop()

            st.success(f"✅ Compression Successful with {algorithm}!")

            st.markdown(f"""
                <div class="details">
                <b>Original Size:</b> {original_size} bytes<br>
                <b>Compressed Size:</b> {compressed_size} bytes<br>
                <b>Compression Ratio:</b> {ratio:.2f}%<br>
                </div>
            """, unsafe_allow_html=True)

            # --- CHART VISUALIZATION ---
            st.write("### 📊 Compression Overview")
            labels = ['Compressed', 'Saved Space']
            sizes = [compressed_size, max(original_size - compressed_size, 0)]
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis("equal")
            st.pyplot(fig)

            with open(compressed_path, "rb") as f:
                st.download_button(
                    label=f"💾 Download Compressed ({algorithm}) File",
                    data=f,
                    file_name=os.path.basename(compressed_path),
                    mime="application/octet-stream",
                )

        st.markdown('</div>', unsafe_allow_html=True)

    elif mode == "Decompress":
        st.markdown('<div class="card"><h4>🔄 Decompression Process</h4>', unsafe_allow_html=True)

        if st.button("Start Decompression ♻️"):
            with st.spinner("Decompressing... please wait 🔧"):
                if algorithm == "LZW":
                    temp_path = os.path.join("decompressed_" + file_name)
                    with open(temp_path, "wb") as temp_file:
                        temp_file.write(file_bytes)
                    restored_path = lzw.decompress_file(temp_path)
                    os.remove(temp_path)

                    with open(restored_path, "rb") as f:
                        data_bytes = f.read()

                elif algorithm == "Deflate":
                    import pickle
                    compressed_data = pickle.loads(file_bytes)
                    decompressed_text, decompressed_size, duration = deflate.decompress_file(compressed_data)
                    data_bytes = decompressed_text.encode()
                    restored_path = "restored_" + file_name.replace(".deflate", "")

                else:
                    st.error("Unknown algorithm selected.")
                    st.stop()

            st.success(f"✅ Decompression Successful using {algorithm}!")

            st.download_button(
                label=f"💾 Download Restored File",
                data=data_bytes,
                file_name=os.path.basename(restored_path),
                mime="application/octet-stream",
            )

        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("👆 Upload a file above to begin.")

# --- FOOTER ---
st.markdown("""
<footer>
<hr>
<p>Built with 💙 | Powered by Streamlit</p>
</footer>
""", unsafe_allow_html=True)