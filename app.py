import streamlit as st
import sqlite3
from datetime import datetime

# Initialize Database
conn = sqlite3.connect("tasks.db", check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task TEXT NOT NULL,
                    date TEXT NOT NULL,
                    status TEXT CHECK(status IN ('Pending', 'Fulfilled', 'Partially Fulfilled')) NOT NULL DEFAULT 'Pending',
                    notes TEXT
                )''')
conn.commit()

# Streamlit App
st.title("📋 Task Manager")

# Task Input
task = st.text_input("Task")
date = st.date_input("Date", datetime.today())
status = st.selectbox("Status", ["Pending", "Fulfilled", "Partially Fulfilled"])
notes = st.text_area("Notes")

if st.button("Add Task"):
    c.execute("INSERT INTO tasks (task, date, status, notes) VALUES (?, ?, ?, ?)", 
              (task, date.strftime('%Y-%m-%d'), status, notes))
    conn.commit()
    st.success("Task Added!")

# Display Tasks
st.subheader("📌 Tasks List")

c.execute("SELECT * FROM tasks ORDER BY date DESC")
tasks = c.fetchall()

for task in tasks:
    st.write(f"📝 **{task[1]}** | 📅 {task[2]} | ✅ {task[3]}")
    st.text_area(f"Notes ({task[1]})", task[4], key=task[0])

    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"Update {task[0]}", key=f"update_{task[0]}"):
            new_status = st.selectbox(f"Update Status ({task[0]})", ["Pending", "Fulfilled", "Partially Fulfilled"])
            new_notes = st.text_area(f"Update Notes ({task[0]})", task[4])
            c.execute("UPDATE tasks SET status=?, notes=? WHERE id=?", (new_status, new_notes, task[0]))
            conn.commit()
            st.success("Task Updated!")

    with col2:
        if st.button(f"Delete {task[0]}", key=f"delete_{task[0]}"):
            c.execute("DELETE FROM tasks WHERE id=?", (task[0],))
            conn.commit()
            st.warning("Task Deleted!")

conn.close()
