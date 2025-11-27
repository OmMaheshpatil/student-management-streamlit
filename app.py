import streamlit as st
import sqlite3
import qrcode
from datetime import datetime
from PIL import Image
import os
import time


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Student Management System",
    page_icon="🎓",
    layout="centered"
)


# --------------------------------------------------
# GLOBAL PREMIUM CSS
# --------------------------------------------------
st.markdown("""
<style>

    /* ---------------- MAIN BACKGROUND ---------------- */
    .main {
        background-color: #f4f6fc !important;
        padding: 20px;
    }

    /* ---------------- HEADINGS ---------------- */
    h1, h2, h3 {
        color: #2b2d42 !important;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 700;
    }

    /* ---------------- BUTTON (Premium Purple) ---------------- */
    .stButton > button {
        background: linear-gradient(45deg, #5a4ff3, #8a78ff);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 12px;
        font-size: 16px;
        font-weight: 600;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
        cursor: pointer;
        transition: 0.25s ease-in-out;
    }

    .stButton > button:hover {
        transform: scale(1.05);
        background: linear-gradient(45deg, #4b3cf0, #7a66ff);
    }

    /* ---------------- SIDEBAR STYLING ---------------- */
    section[data-testid="stSidebar"] {
        background: #1c1c27 !important;
        padding: 20px;
    }

    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    section[data-testid="stSidebar"] label {
        color: #ffffff !important;
        font-size: 18px !important;
        font-weight: 600 !important;
    }

    .stSelectbox > div {
        background: #ffffff !important;
        border-radius: 10px !important;
    }

    /* ---------------- INPUT FIELD ---------------- */
    .stTextInput input {
        border-radius: 8px !important;
        padding: 10px !important;
        border: 2px solid #5a4ff3 !important;
    }

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# DATABASE
# --------------------------------------------------
DB = "student_db.db"

def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE,
            name TEXT,
            course TEXT,
            email TEXT
        )
    """)
    con.commit()
    con.close()

init_db()


# CRUD Functions
def add_student(student_id, name, course, email):
    try:
        con = sqlite3.connect(DB)
        cur = con.cursor()
        cur.execute("INSERT INTO students (student_id, name, course, email) VALUES (?, ?, ?, ?)",
                    (student_id, name, course, email))
        con.commit()
        con.close()
        return True
    except:
        return False


def get_students():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT * FROM students")
    rows = cur.fetchall()
    con.close()
    return rows


def update_student(old_id, new_id, name, course, email):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""
        UPDATE students SET student_id=?, name=?, course=?, email=? WHERE student_id=?
    """, (new_id, name, course, email, old_id))
    con.commit()
    con.close()


def delete_student(student_id):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("DELETE FROM students WHERE student_id=?", (student_id,))
    con.commit()
    con.close()


def search_students(query):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""
        SELECT * FROM students
        WHERE student_id LIKE ? OR name LIKE ? OR course LIKE ? OR email LIKE ?
    """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
    rows = cur.fetchall()
    con.close()
    return rows


# --------------------------------------------------
# SIDEBAR MENU
# --------------------------------------------------
menu = ["Dashboard", "Add Student", "View Students", "Update Student",
        "Delete Student", "QR Code Generator", "Digital Clock"]

choice = st.sidebar.selectbox("📌 Choose Menu", menu)


# --------------------------------------------------
# 1. DASHBOARD
# --------------------------------------------------
if choice == "Dashboard":
    st.title("🎓 Student Management Dashboard")
    st.write("Welcome to your premium student system baby ❤️")

    total = len(get_students())
    st.metric("Total Students", total)


# --------------------------------------------------
# 2. ADD STUDENT
# --------------------------------------------------
elif choice == "Add Student":
    st.title("➕ Add New Student")

    student_id = st.text_input("Student ID")
    name = st.text_input("Full Name")
    course = st.text_input("Course")
    email = st.text_input("Email")

    if st.button("Save Student"):
        if student_id and name:
            if add_student(student_id, name, course, email):
                st.success("Student added successfully!")
            else:
                st.error("Student ID already exists!")
        else:
            st.error("Student ID & Name are required!")


# --------------------------------------------------
# 3. VIEW STUDENTS
# --------------------------------------------------
elif choice == "View Students":
    st.title("📖 Student Records")

    data = get_students()

    import pandas as pd

    df = pd.DataFrame(data, columns=["ID", "Student ID", "Name", "Course", "Email"])

    st.dataframe(df, use_container_width=True)


# --------------------------------------------------
# 4. UPDATE STUDENT
# --------------------------------------------------
elif choice == "Update Student":
    st.title("✏ Update Student")

    data = get_students()
    ids = [s[1] for s in data]

    old = st.selectbox("Select Student to Edit", ids)

    new_id = st.text_input("New Student ID")
    name = st.text_input("Name")
    course = st.text_input("Course")
    email = st.text_input("Email")

    if st.button("Update"):
        update_student(old, new_id, name, course, email)
        st.success("Student updated successfully!")


# --------------------------------------------------
# 5. DELETE STUDENT
# --------------------------------------------------
elif choice == "Delete Student":
    st.title("🗑 Delete Student")

    data = get_students()
    ids = [s[1] for s in data]

    sid = st.selectbox("Select Student ID", ids)

    if st.button("Delete"):
        delete_student(sid)
        st.success("Student deleted!")


# --------------------------------------------------
# 6. QR CODE GENERATOR
# --------------------------------------------------
elif choice == "QR Code Generator":
    st.title("🔳 QR Code Generator")

    text = st.text_input("Enter Text/URL")
    filename = st.text_input("File Name", "my_qrcode")

    if st.button("Generate"):
        qr = qrcode.make(text)
        path = filename + ".png"
        qr.save(path)

        st.image(path, caption="QR Code")
        st.success(f"Saved as {path}")


# --------------------------------------------------
# 7. DIGITAL CLOCK
# --------------------------------------------------
elif choice == "Digital Clock":
    st.title("⏰ Live Digital Clock")

    st.markdown("""
    <style>
        .clock-box {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            padding: 40px;
            border-radius: 20px;
            text-align: center;
            color: white;
            box-shadow: 0px 0px 20px rgba(0,0,0,0.3);
            margin-top: 30px;
        }
        .time {
            font-size: 80px;
            font-weight: bold;
            font-family: 'Courier New', monospace;
            text-shadow: 0px 0px 20px #00ffea;
        }
        .date {
            font-size: 32px;
            margin-top: 10px;
            font-weight: 500;
            text-shadow: 0px 0px 10px #ffd700;
        }
    </style>
    """, unsafe_allow_html=True)

    placeholder = st.empty()

    while True:
        now = datetime.now()
        t = now.strftime("%H:%M:%S")
        d = now.strftime("%A, %B %d, %Y")

        placeholder.markdown(f"""
            <div class="clock-box">
                <div class="time">{t}</div>
                <div class="date">{d}</div>
            </div>
        """, unsafe_allow_html=True)

        time.sleep(1)
