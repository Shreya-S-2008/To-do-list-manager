import streamlit as st
import os
from datetime import datetime
import time

FILE_NAME = "todo_with_alarms.txt"

def load_tasks():
    tasks = []
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            for line in file:
                if " | " in line:
                    task_text, task_time = line.strip().split(" | ", 1)
                    tasks.append({"text": task_text, "time": task_time})
                else:
                    tasks.append({"text": line.strip(), "time": "No Time Set"})
    return tasks

def save_tasks(tasks):
    with open(FILE_NAME, "w", encoding="utf-8") as file:
        for task in tasks:
            file.write(f"{task['text']} | {task['time']}\n")

# --- STREAMLIT UI CONFIG ---
st.set_page_config(page_title="Alarm To-Do App", page_icon="⏰", layout="centered")

st.title("⏰ Smart To-Do List with Audio Alarms")
st.write("Set a starting time for your tasks. The browser will ring out loud when it's time!")

# Active Time Tracking
current_time_str = datetime.now().strftime("%H:%M")
st.metric(label="🕒 Current System Time", value=current_time_str)

tasks = load_tasks()

# --- ALARM CHECKER & AUDIO TRACKER ---
alarm_triggered = False
triggered_tasks = []

for task in tasks:
    if task["time"] != "No Time Set" and task["time"] == current_time_str:
        alarm_triggered = True
        triggered_tasks.append(task["text"])

if alarm_triggered:
    for task_name in triggered_tasks:
        st.error(f"🚨 ALARM ACTIVE: It is time to start: **{task_name}**!")
    # Injects a native browser alert system beep that bypasses security blocks
    st.components.v1.html(
        """
        <script>
        // Creates an instant synthesizer beep directly inside the browser speaker
        var context = new (window.AudioContext || window.webkitAudioContext)();
        var osc = context.createOscillator();
        osc.type = "sine";
        osc.frequency.value = 900; // Sets a clear, high pitch for the beep
        osc.connect(context.destination);
        osc.start();
        setTimeout(() => { osc.stop(); }, 1500); // Ring loudly for 1.5 seconds
        </script>
        """,
        height=0
    )
    

st.markdown("---")

# --- INPUT SECTION ---
st.subheader("➕ Add a Task & Set Start Time")
new_task = st.text_input("What task needs to start?", placeholder="e.g., Study for exams...")

alarm_time = st.time_input("What time should it ring?", value=datetime.now().time())
formatted_alarm_time = alarm_time.strftime("%H:%M")

if st.button("Add Task with Alarm", use_container_width=True):
    if new_task.strip():
        tasks.append({"text": new_task.strip(), "time": formatted_alarm_time})
        save_tasks(tasks)
        st.success(f"Successfully scheduled '{new_task.strip()}' for {formatted_alarm_time}!")
        st.rerun()
    else:
        st.error("Please type a task name first!")

st.markdown("---")

# --- DISPLAY SECTION ---
st.subheader("📋 Your Scheduled Tasks")
if not tasks:
    st.info("Your schedule is empty. Add a task above to set an alarm!")
else:
    for index, task in enumerate(tasks):
        col1, col2, col3 = st.columns([0.5, 0.3, 0.2])
        with col1:
            st.write(f"**{index + 1}.** {task['text']}")
        with col2:
            st.markdown(f"🔔 Start Time: `{task['time']}`")
        with col3:
            if st.button("Done ✅", key=f"done_{index}"):
                tasks.pop(index)
                save_tasks(tasks)
                st.rerun()

# Auto-updates every 10 seconds to watch the system clock
time.sleep(10)
st.rerun()