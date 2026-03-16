import streamlit as st
from google import genai
from google.genai import types
import sys
import io
import traceback
import os
from dotenv import load_dotenv

# Load API Key from .env (local) or Streamlit Secrets (cloud)
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-3.1-pro-preview"

st.set_page_config(page_title="Python & Data Science Mentor", layout="wide")

# --- CUSTOM SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are an expert Python and Data Science Interview Coach.
Your goal is to guide the user from Zero to Hero.
1. If the user's code has an error, identify the line and explain the fix.
2. If the code works, explain the Big-O complexity or suggest a more 'Pythonic' or 'Data Science-heavy' way (like using NumPy instead of loops).
3. Be encouraging but rigorous—prepare them for top-tier tech interviews.
"""

# --- THE ROADMAP (Expandable to 150+ tasks) ---
roadmap = {
    "Level 1: Python Basics": [
        {"id": 1, "task": "Reverse a string without using [::-1].", "solution": "s = 'hello'\nres = ''\nfor char in s:\n    res = char + res\nprint(res)"},
        {"id": 2, "task": "Find all prime numbers up to 50.", "solution": "for n in range(2, 51):\n    if all(n % i != 0 for i in range(2, int(n**0.5)+1)):\n        print(n)"}
    ],
    "Level 2: Data Science (Pandas/NumPy)": [
        {"id": 3, "task": "Create a 3x3 identity matrix using NumPy.", "solution": "import numpy as np\nprint(np.eye(3))"},
        {"id": 4, "task": "Group a DataFrame by 'Category' and find the mean price.", "solution": "import pandas as pd\ndf = pd.DataFrame({'Category': ['A', 'A', 'B'], 'Price': [10, 20, 30]})\nprint(df.groupby('Category')['Price'].mean())"}
    ]
}

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🚀 Hero Roadmap")
all_tasks = []
for level, tasks in roadmap.items():
    st.sidebar.subheader(level)
    for t in tasks:
        if st.sidebar.button(t['task'][:30] + "...", key=f"btn_{t['id']}"):
            st.session_state.current_task = t

# Initialize state
if 'current_task' not in st.session_state:
    st.session_state.current_task = roadmap["Level 1: Python Basics"][0]

# --- MAIN UI ---
st.title("🐍 Python & Data Science Mentor")
st.caption(f"Targeting: 150+ Interview Codes | Powered by Gemini 3.1 Pro")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown(f"### Current Task: \n**{st.session_state.current_task['task']}**")
    user_code = st.text_area("Write your code here:", height=300, value="# Start coding...")
    
    if st.button("🚀 Run & Analyze", use_container_width=True):
        # Capture output
        output_capture = io.StringIO()
        sys.stdout = output_capture
        error_msg = None
        
        try:
            exec(user_code)
            result = output_capture.getvalue()
        except Exception:
            result = ""
            error_msg = traceback.format_exc()
        finally:
            sys.stdout = sys.__stdout__

        # Show Output
        st.subheader("Console Output")
        if error_msg:
            st.error(error_msg)
        else:
            st.code(result if result else "Code executed (No output)")

        # Get AI Feedback
        with st.spinner("AI Mentor is reviewing your code..."):
            prompt = f"Task: {st.session_state.current_task['task']}\nUser Code:\n{user_code}\nOutput: {result}\nError: {error_msg}"
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
            )
            st.session_state.ai_feedback = response.text

with col2:
    st.subheader("🤖 AI Mentor Feedback")
    if 'ai_feedback' in st.session_state:
        st.info(st.session_state.ai_feedback)
    else:
        st.write("Run your code to see feedback here.")

    if st.button("🏳 Give Up (Show Solution)"):
        st.warning("Study this carefully before moving to the next task!")
        st.code(st.session_state.current_task['solution'])
