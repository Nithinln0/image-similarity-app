import streamlit as st
import os
import torch
import sqlite3
import base64
from PIL import Image
from io import BytesIO
import clip
from datetime import datetime
from src.config import THRESHOLD
from auth import init_user_db, register_user, login_user

# Streamlit page config
st.set_page_config(page_title="Image Similarity App")

# Session state initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# Cache CLIP model loading
@st.cache_resource
def load_clip_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)
    return model, preprocess, device

# Initialize comparison database
def init_db():
    with sqlite3.connect("image_comparisons.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comparisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image1_name TEXT,
                image1_blob BLOB,
                image2_name TEXT,
                image2_blob BLOB,
                similarity REAL,
                result TEXT,
                timestamp TEXT
            )
        ''')
        conn.commit()

# Background image setup (optional, requires background.png)
def set_background():
    if os.path.exists("background.png"):
        with open("background.png", "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background:
                    linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)),
                    url("data:image/png;base64,{encoded}");
                background-size: cover;
                background-position: center;
                color: white;
            }}
            h1 {{
                color: #FFFFFF;
                text-shadow: 2px 2px 5px rgba(0,0,0,0.7);
                font-size: 3em;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

# Image comparison using CLIP
def compare_images(img1, img2, model, preprocess, device):
    try:
        image1 = preprocess(img1).unsqueeze(0).to(device)
        image2 = preprocess(img2).unsqueeze(0).to(device)
        with torch.no_grad():
            features1 = model.encode_image(image1)
            features2 = model.encode_image(image2)
        similarity = torch.cosine_similarity(features1, features2).item()
        return similarity
    except Exception as e:
        st.error(f"Error comparing images: {e}")
        return None

# Save result to database
def save_result(name1, img1_data, name2, img2_data, score, result):
    with sqlite3.connect("image_comparisons.db") as conn:
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO comparisons (image1_name, image1_blob, image2_name, image2_blob, similarity, result, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name1, img1_data, name2, img2_data, score, result, timestamp))
        conn.commit()

# Convert file to bytes
def image_to_bytes(img_file):
    return img_file.getvalue() if img_file else None

# Convert blob to PIL image
def bytes_to_image(blob):
    return Image.open(BytesIO(blob))

# Interactive Login/Register UI
def show_login():
    # Custom CSS for styling
    st.markdown(
        """
        <style>
        /* Animated gradient background */
        .stApp {
            background: linear-gradient(45deg, #1e3c72, #2a5298, #3b5998, #8e44ad);
            background-size: 400%;
            animation: gradient 15s ease infinite;
            color: white;
        }
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* Container for login/register form */
        .login-container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            max-width: 400px;
            margin: 2rem auto;
        }

        /* Title styling */
        .login-title {
            text-align: center;
            font-size: 2.5em;
            color: #fff;
            text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.5);
            animation: fadeIn 1s ease-in;
        }

        /* Tabs styling */
        .stRadio > div {
            display: flex;
            justify-content: center;
            gap: 10px;
        }
        .stRadio label {
            padding: 10px 20px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px 10px 0 0;
            transition: background 0.3s ease;
        }
        .stRadio label:hover {
            background: rgba(255, 255, 255, 0.4);
        }
        .stRadio [aria-checked="true"] label {
            background: rgba(255, 255, 255, 0.6);
        }

        /* Input fields */
        .stTextInput > div > input {
            width: 100%;
            padding: 10px;
            background: transparent;
            border: none;
            border-bottom: 2px solid #fff;
            color: #fff;
            font-size: 1em;
            outline: none;
            transition: border-color 0.3s ease;
        }
        .stTextInput > div > input:focus {
            border-bottom: 2px solid #00ff88;
        }

        /* Button styling */
        .stButton > button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(45deg, #00ff88, #00b4d8);
            border: none;
            border-radius: 25px;
            color: white;
            font-size: 1.1em;
            cursor: pointer;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0, 255, 136, 0.5);
        }

        /* Error and success messages */
        .error, .success {
            text-align: center;
            padding: 10px;
            border-radius: 5px;
            margin: 1rem 0;
            animation: shake 0.5s ease;
        }
        .error {
            background: rgba(255, 0, 0, 0.2);
            color: #ff3333;
        }
        .success {
            background: rgba(0, 255, 136, 0.2);
            color: #00ff88;
        }

        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
            20%, 40%, 60%, 80% { transform: translateX(5px); }
        }
        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(-20px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Login container
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="login-title">🔐 Image Similarity App</h1>', unsafe_allow_html=True)

    # Use tabs to switch between login and register
    tab = st.radio("Choose an action:", ("Login", "Register"), horizontal=True, key="auth_tab")

    # Handle form submissions using Streamlit forms
    if tab == "Login":
        with st.form(key="login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", placeholder="Enter your password", type="password")
            login_submitted = st.form_submit_button("Login")
            if login_submitted:
                print(f"Login submitted with username: {username}, password: {password}")  # Debug print
                if not username or not password:
                    st.markdown('<div class="error">❌ Please fill in all fields.</div>', unsafe_allow_html=True)
                else:
                    login_result = login_user(username, password)
                    print(f"Login result for {username}: {login_result}")  # Debug print
                    if login_result:
                        st.markdown('<div class="success">✅ Login successful! Welcome!</div>', unsafe_allow_html=True)
                        import time
                        time.sleep(1)  # Ensure the success message is visible
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.rerun()
                    else:
                        st.markdown('<div class="error">❌ Invalid username or password.</div>', unsafe_allow_html=True)

    elif tab == "Register":
        with st.form(key="register_form"):
            new_user = st.text_input("New Username", placeholder="Enter a new username")
            new_pass = st.text_input("New Password", placeholder="Enter a new password", type="password")
            register_submitted = st.form_submit_button("Register")
            if register_submitted:
                print(f"Register submitted with username: {new_user}, password: {new_pass}")  # Debug print
                if not new_user or not new_pass:
                    st.markdown('<div class="error">❌ Please fill in all fields.</div>', unsafe_allow_html=True)
                else:
                    register_result = register_user(new_user, new_pass)
                    print(f"Register result for {new_user}: {register_result}")  # Debug print
                    if register_result:
                        st.markdown('<div class="success">🎉 Registered successfully! Please log in.</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="error">⚠️ Username already exists.</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# Main App Interface
def show_main_app():
    set_background()
    st.title("🖼️ Image Similarity Comparison")
    st.write("Upload two images to compare their similarity using the CLIP model.")

    model, preprocess, device = load_clip_model()

    img1 = st.file_uploader("Upload First Image", type=["jpg", "jpeg", "png"], key="img1")
    img2 = st.file_uploader("Upload Second Image", type=["jpg", "jpeg", "png"], key="img2")

    if img1 and img2:
        try:
            image1 = Image.open(img1).convert("RGB")
            image2 = Image.open(img2).convert("RGB")
            st.image([image1, image2], caption=["Image 1", "Image 2"], width=300)

            if st.button("🔍 Compare Images"):
                similarity_score = compare_images(image1, image2, model, preprocess, device)
                if similarity_score is not None:
                    st.success(f"Similarity Score: **{similarity_score:.4f}**")
                    result = "Similar" if similarity_score >= THRESHOLD else "Not Similar"
                    if result == "Similar":
                        st.success("✅ Images are **Similar**.")
                    else:
                        st.warning("❌ Images are **Not Similar**.")
                    save_result(
                        img1.name, image_to_bytes(img1),
                        img2.name, image_to_bytes(img2),
                        similarity_score, result
                    )
                    st.info("Result saved to database.")
        except Exception as e:
            st.error(f"Error processing images: {e}")

    if st.checkbox("📁 Show stored comparisons"):
        with sqlite3.connect("image_comparisons.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT image1_name, image1_blob, image2_name, image2_blob, similarity, result, timestamp FROM comparisons")
            records = cursor.fetchall()

        if records:
            for i, row in enumerate(records):
                col1, blob1, col2, blob2, sim, res, ts = row
                st.markdown(f"### 🔹 Record {i+1} ({ts})")
                try:
                    col1_img, col2_img = bytes_to_image(blob1), bytes_to_image(blob2)
                    st.image([col1_img, col2_img], caption=[col1, col2], width=250)
                    st.write(f"**Similarity:** {sim:.4f} | **Result:** {res}")
                    st.markdown("---")
                except Exception as e:
                    st.warning(f"Error displaying record {i+1}: {e}")
        else:
            st.info("No records found.")

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

# Initialize databases
init_db()
init_user_db()

# App Entry Point
if not st.session_state.logged_in:
    show_login()
else:
    show_main_app()