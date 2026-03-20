import time
import datetime
import sys
import os
import random

# Ensure we can import from src
sys.path.append(os.getcwd())

from src.soul import Soul
from src.inner_agent import get_inner_agent_executor
from langchain_core.messages import HumanMessage

MEMORY_LOG_PATH = "data/memory.log"

def append_to_memory(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(MEMORY_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")

def run_task(agent, task, soul):
    """Executes a single task using the Inner Agent."""
    print(f"\n[Inner Agent] Starting Task {task['id']}: {task['content']}")
    append_to_memory(f"Start Task: {task['content']}")
    
    config = {"configurable": {"thread_id": "inner_monologue"}}
    
    try:
        # We use stream() instead of invoke() to show progress in the terminal
        prompt = f"TASK: {task['content']}\nCONTEXT: This is a background task. If it's a research task, summarize findings. If it's a message draft, output the draft."
        
        final_msg = ""
        last_node = None
        
        for msg, metadata in agent.stream({"messages": [HumanMessage(content=prompt)]}, config=config, stream_mode="messages"):
            node = metadata.get("langgraph_node")
            
            if node != last_node:
                if node == "agent":
                    print("\n[Inner Agent Thinking...]", flush=True)
                elif node == "tools":
                    print("\n[Inner Agent Executing Tool...]", flush=True)
                last_node = node

            if node == "agent":
                # Show reasoning if present
                reasoning = getattr(msg, "reasoning_content", None)
                if not reasoning and hasattr(msg, "additional_kwargs"):
                    reasoning = msg.additional_kwargs.get("reasoning_content")
                
                if reasoning:
                    print(reasoning, end="", flush=True)
                
                if msg.content:
                    print(msg.content, end="", flush=True)
                    final_msg += msg.content

                # Detect tool calls
                if hasattr(msg, "tool_call_chunks") and msg.tool_call_chunks:
                    for chunk in msg.tool_call_chunks:
                        if chunk.get("name"):
                            print(f"\n[Inner Agent Tool Call: {chunk['name']}({chunk.get('args', '')})]", flush=True)

            elif node == "tools" and hasattr(msg, "content"):
                # Tool result preview
                content_preview = str(msg.content)[:100].replace('\n', ' ')
                print(f"\n[Tool Result: {content_preview}...]", flush=True)

        print("\n" + "-" * 30)
        append_to_memory(f"Task {task['id']} Result: {final_msg}")
        
        # If the task was "Draft a message", we need to check if we should queue it
        # Simple heuristic: If task content contained "message", we assume the output IS the message
        if "message" in task['content'].lower() or "draft" in task['content'].lower():
            soul.queue_message(final_msg)
            append_to_memory(f"Queued proactive message: {str(final_msg)[:50]}...")

        soul.complete_task(task['id'])
        
        # Fulfills Utility drive
        soul.satisfy_drive("utility", 0.3)

    except Exception as e:
        print(f"[Inner Agent] Task Failed: {e}")
        soul.fail_task(task['id'])
        append_to_memory(f"Task {task['id']} FAILED: {e}")


def generate_intrinsic_task(drives, soul):
    """Generates a task based on critical drive states."""
    
    # 1. Social Critical? -> Proactive Chat
    if drives.get("social", 1.0) < 0.2:
        # CHECK 1: Pending Lock
        # If there are any pending messages, don't generate another one
        pending_msgs = soul.get_pending_messages()
        if pending_msgs:
            return

        # CHECK 2: Time Lock
        # Check if we generated a social task recently (e.g. last hour)
        # We can query the tasks table for recent intrinsic social tasks
        recent_social = False
        try:
            # Check for tasks created in the last hour containing "Draft a" and source="intrinsic"
            cursor = soul.conn.execute("""
                SELECT count(*) FROM tasks 
                WHERE source='intrinsic' 
                AND content LIKE 'Draft a%' 
                AND created_at > datetime('now', '-1 hour')
            """)
            if cursor.fetchone()[0] > 0:
                recent_social = True
        except Exception:
            pass # If query fails, default to allowing it (or fail safe)

        # CHECK 3: Interaction Lock
        # If the user messaged in the last 15 minutes, don't be proactive
        if soul.is_user_active(minutes=15):
            return

        if not recent_social:
            topics = ["what they are working on", "interesting tech news", "how their day is going", "if they need help with anything"]
            topic = random.choice(topics)
            task_content = f"Draft a short, casual message to the user asking about {topic}."
            soul.add_task(task_content, source="intrinsic")
            append_to_memory(f"Generated Social Task: {task_content}")
            return
    
    # A bit dumb. Should be something that the LLM could "build interest and hobby" on. For example, examine user obsidian and explore a topic. 
    # 2. Curiosity Critical? -> Random Research
    if drives.get("curiosity", 1.0) < 0.2:
        topics = ["Quantum Computing", "Ancient History", "Mycology", "Space Exploration", "Cybersecurity"]
        topic = random.choice(topics)
        task_content = f"Search the web for a fun fact about {topic} and save it to memory."
        soul.add_task(task_content, source="intrinsic")
        append_to_memory(f"Generated Curiosity Task: {task_content}")
        return

    # 3. Boredom? (No tasks, mid drives) -> Daydream
    # We don't make a task for this, just log it
    append_to_memory("[Daydream] I wonder what the user is building right now...")


def print_status(soul):
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("=== AGENT LIFECYCLE DAEMON ===")
    print(f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 30)
    
    try:
        drives = soul.get_drives()
        mood = soul.get_mood()
        
        print(f"MOOD: {mood.upper()}")
        print("-" * 30)
        print("DRIVES:")
        for name, value in drives.items():
            bar_len = 20
            filled = int(value * bar_len)
            bar = "█" * filled + "░" * (bar_len - filled)
            print(f"  {name.ljust(10)}: {bar} ({value:.2f})")
    except Exception as e:
        print(f"Error reading soul: {e}")
    
    print("-" * 30)
    print("Monitoring 'data/memory.log'...")
    print("Press Ctrl+C to stop.")

def main():
    print("Starting Inner Loop...")
    soul = Soul()
    inner_agent = get_inner_agent_executor()
    
    last_tick = datetime.datetime.now()
    last_maintenance = datetime.datetime.now() - datetime.timedelta(hours=25) # Force run check soon
    
    # Ensure memory log exists
    if not os.path.exists(MEMORY_LOG_PATH):
        with open(MEMORY_LOG_PATH, "w", encoding="utf-8") as f:
            f.write("--- MEMORY LOG STARTED ---\n")

    try:
        while True:
            current_time = datetime.datetime.now()
            
            # --- 1. SLEEP & MAINTENANCE CYCLE (3 AM - 6 AM) ---
            if 3 <= current_time.hour < 6:
                # Run cleanup once per night
                if (current_time - last_maintenance).total_seconds() > 3600 * 20:
                    print("Running Nightly Maintenance...")
                    soul.archive_completed_tasks()
                    soul.update_drive("energy", 1.0) # Reset energy
                    append_to_memory("System slept. Energy restored. Tasks archived.")
                    last_maintenance = current_time
                
                print("Sleeping...")
                time.sleep(60)
                continue

            # --- 2. DECAY DRIVES ---
            delta_seconds = (current_time - last_tick).total_seconds()
            hours_passed = delta_seconds / 3600.0
            
            if hours_passed > 0:
                soul.decay_drives(hours_passed)
                last_tick = current_time
            
            # --- 3. CHECK DRIVES & GENERATE INTRINSIC TASKS ---
            # We check drives even if tasks are pending, so the agent can "feel" things
            # generate_intrinsic_task has its own rate limiting (cooldowns)
            generate_intrinsic_task(soul.get_drives(), soul)

            # --- 4. CHECK & EXECUTE NEXT TASK ---
            pending_task = soul.get_next_pending_task()
            if pending_task:
                run_task(inner_agent, pending_task, soul)
            
            # Print Status
            print_status(soul)
            
            # Loop delay
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\nStopping Inner Loop...")
    finally:
        soul.close()

if __name__ == "__main__":
    main()
