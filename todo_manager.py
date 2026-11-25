import streamlit as st
from datetime import datetime
from supabase import create_client, Client

# --- SUPABASE CONNECTION ---
SUPABASE_URL = "https://vewcwpprejcmfttbirfx.supabase.co"
SUPABASE_KEY = "sb_publishable_Iw0gLfIHCG2QwRNw6mhiog_YBnFauZk"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- DATABASE FUNCTIONS ---
def load_tasks():
    response = supabase.table("todos").select("*").execute()
    return response.data

def add_task(task_text, task_time):
    supabase.table("todos").insert({
        "text": task_text,
        "time": task_time
    }).execute()

def delete_task(task_id):
    supabase.table("todos").delete().eq("id", task_id).execute()

# --- STREAMLIT UI CONFIG ---
st.set_page_config(page_title="Alarm To-Do App", page_icon="⏰", layout="centered")

# Auto-refresh the page every 15 seconds so alarms trigger automatically
st.markdown('<meta http-equiv="refresh" content="15">', unsafe_allow_html=True)

st.title("⏰ Smart To-Do List with Audio Alarms")
st.write("Connected to Supabase cloud database! (Page auto-checks every 15s)")

# Active Time Tracking
current_time_str = datetime.now().strftime("%H:%M")
st.metric(label="🕒 Current System Time", value=current_time_str)

tasks = load_tasks()

# --- ALARM CHECKER & AUDIO TRACKER ---
triggered_tasks = [
    task["text"] for task in tasks
    if task.get("time") and task["time"] == current_time_str
]

if triggered_tasks:
    for task_name in triggered_tasks:
        st.error(f"🚨 ALARM ACTIVE: It is time to start: **{task_name}**!")
    st.components.v1.html(
        """
        <script>
        function playBeep(delay) {
            setTimeout(() => {
                var context = new (window.AudioContext || window.webkitAudioContext)();
                var osc = context.createOscillator();
                osc.type = "square";
                osc.frequency.value = 880;
                osc.connect(context.destination);
                osc.start();
                setTimeout(() => { osc.stop(); }, 400);
            }, delay);
        }
        playBeep(0);
        playBeep(600);
        playBeep(1200);
        </script>
        """,
        height=0
    )

st.markdown("---")

# --- INPUT SECTION (Inside a Form so Add Task always shows) ---
st.subheader("➕ Add a Task & Set Start Time")
with st.form("add_task_form", clear_on_submit=True):
    new_task = st.text_input("What task needs to start?", placeholder="e.g., Study for exams...")
    alarm_time = st.time_input("What time should it ring?")
    submitted = st.form_submit_button("Add Task")

    if submitted:
        if new_task.strip():
            formatted_time = alarm_time.strftime("%H:%M")
            add_task(new_task.strip(), formatted_time)
            st.success(f"Added '{new_task}' for {formatted_time}!")
            st.rerun()
        else:
            st.warning("Please enter a task first.")

st.markdown("---")

# --- TASK LIST DISPLAY ---
st.subheader("📋 Your Saved Tasks")
if not tasks:
    st.info("No tasks in Supabase yet.")
else:
    for task in tasks:
        col1, col2 = st.columns([4, 1])
        col1.write(f"**{task['text']}** — ⏰ `{task['time']}`")
        if col2.button("Delete", key=f"del_{task['id']}"):
            delete_task(task["id"])
            st.rerun()