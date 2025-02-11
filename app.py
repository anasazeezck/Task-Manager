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

# Streamlit App Styling
st.set_page_config(page_title="Task Manager", page_icon="✅", layout="wide")
st.title("📋 Task Manager")
st.markdown("---")

# Task Input Form with Sidebar
st.sidebar.header("Add New Task")
task = st.sidebar.text_input("Task")
date = st.sidebar.date_input("Date", datetime.today())
status = st.sidebar.selectbox("Status", ["Pending", "Fulfilled", "Partially Fulfilled"])
notes = st.sidebar.text_area("Notes")

if st.sidebar.button("Add Task", use_container_width=True):
    c.execute("INSERT INTO tasks (task, date, status, notes) VALUES (?, ?, ?, ?)", 
              (task, date.strftime('%Y-%m-%d'), status, notes))
    conn.commit()
    st.sidebar.success("✅ Task Added!")
    st.experimental_rerun()

# Filtering Options
st.subheader("📌 View Tasks")
filter_status = st.radio("Filter by Status:", ["All", "Pending", "Fulfilled", "Partially Fulfilled"], horizontal=True)

# Fetch Tasks
query = "SELECT * FROM tasks"
if filter_status != "All":
    query += f" WHERE status = '{filter_status}'"
query += " ORDER BY date DESC"
c.execute(query)
tasks = c.fetchall()

# Display Tasks Date-wise
if tasks:
    grouped_tasks = {}
    for task in tasks:
        task_date = task[2]
        if task_date not in grouped_tasks:
            grouped_tasks[task_date] = []
        grouped_tasks[task_date].append(task)
    
    for date, date_tasks in grouped_tasks.items():
        st.markdown(f"### 📅 {date}")
        for task in date_tasks:
            with st.expander(f"📝 {task[1]} | ✅ {task[3]}"):
                st.write(f"**Notes:** {task[4]}")
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    new_status = st.selectbox(f"Update Status ({task[0]})", ["Pending", "Fulfilled", "Partially Fulfilled"], index=["Pending", "Fulfilled", "Partially Fulfilled"].index(task[3]))
                with col2:
                    new_notes = st.text_area(f"Update Notes ({task[0]})", task[4], key=f"notes_{task[0]}")
                with col3:
                    if st.button(f"Update {task[0]}", key=f"update_{task[0]}"):
                        c.execute("UPDATE tasks SET status=?, notes=? WHERE id=?", (new_status, new_notes, task[0]))
                        conn.commit()
                        st.experimental_rerun()
                if st.button(f"❌ Delete Task {task[0]}", key=f"delete_{task[0]}", use_container_width=True):
                    c.execute("DELETE FROM tasks WHERE id=?", (task[0],))
                    conn.commit()
                    st.experimental_rerun()
        st.markdown("---")
else:
    st.info("No tasks found for the selected filter.")

conn.close()
