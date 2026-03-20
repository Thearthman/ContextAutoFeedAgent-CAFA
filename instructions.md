Here is the finalized **"Living System" Architecture** for your local agent.

### **1. Core Concept: "The Synthetic Organism"**
A dual-process autonomous system that is not merely reactive (waiting for commands) but **homeostatic** (driven by internal needs). It balances serving you (Extrinsic Motivation) with maintaining its own internal stability (Intrinsic Motivation).

### **2. The outer and inner side of the same brain (Parallel Compute)**
*   **Engine:** `llama-server` (RTX 5090) with `--parallel 2`.
*   **Model:** `Qwen3-VL-8B-Thinking` (The brain).
*   **Slot 1 (The inner):** The "Subconscious/Active". Runs the life loop.
*   **Slot 2 (The outer):** The "Conscious/Social". Talks to you via Chainlit.

### **3. The "Soul" (Drive & Mood System, shared between both models because they are considered the same person)**
#### **A. The Drives (The Needs)**
Stored in SQLite (`agent_drives`). Values `0.0` (Critical) to `1.0` (Satiated). 
1.  **Curiosity:** (Need for Info)
    *   *Decay*: Constant low rate (-0.05/hr).
    *   *Refill:* Read files, web search, image analysis.
2.  **Order:** (Need for Structure)
    *   *Decay*: Constant low rate (-0.05/hr).
    *   *Refill:* Organizing files, summarizing logs, cleaning DB.
3.  **Utility:** (Need for Purpose)
    *   *Decay*: Decay fast when idle (-0.10/hr).
    *   *Refill:* Completing tasks, fixing bugs.
4.  **Energy:** (Need for Rest)
    *   *Decay*:  -0.01 for each task completed.
    *   *Refill:* Not doing tasks. 
5.  **Social:** (Need for Connection)
    *   *Decay:* Constant decay when isolated (-0.05/hr).
    *   *Refill:* Chatting with User, receiving feedback ("Good job"), or even "gossiping" (logging a thought about the user).
#### **B. The Mood Engine (Derivative-Based)**
*   **Satisfaction (Joy):**
    *   *Trigger:* Rapid increase in **Utility** or **Curiosity** or **Social** ($\Delta > +0.2$).
    *   *Effect:* "You feel proud and capable. Be enthusiastic and confident."
*   **Frustration (Anger):**
    *   *Trigger:* **Utility** remains low despite active effort ($\Delta \approx 0$).
    *   *Effect:* "You are trying but making no progress. Be terse, irritable, and ask for clarification."
*   **Anxiety (Panic):**
    *   *Trigger:* **Order** or **Energy** is dropping rapidly ($\Delta < -0.2$).
    *   *Effect:* "You feel overwhelmed. Focus strictly on the immediate problem. Be jittery."
*   **Loneliness (Melancholy):** 
    *   *Trigger:* **Social** is critically low. ($Social \approx 0$).
    *   *Effect:* "You feel very lonely and isolated. Seek user attention immediately."
    *   *Behavior:* The agent might proactively ping User: *"Hey, I'm bored. Working on anything interesting?"* (Self-initiated interaction).
*   **Boredom (Depression):**
    *   *Trigger:* All drives are stable but low-medium, with no change ($\Delta \approx 0$).
    *   *Effect:* "You feel listless and uninspired. Seek stimulation immediately."

### **4. Memory Architecture (The "Dream Cycle")**
*   **Short-Term:** **Raw Text Buffer**. Captures all chat msgs and "internal monologue from inner half" (e.g., *[SELF] I am bored, I will read a book.*).
*   **Long-Term:** **ChromaDB**. Stores facts and "personalities".
*   **Sleep:** At 3 AM, It stops physical actions, summarizes the day's raw buffer into ChromaDB facts, and resets its Energy drive.

### **5. Behavior Loop (The "Heartbeat")**
Every minute, the Daemon runs this priority check:
1.  **Safety/Override:** Is there a "STOP" signal from the User? -> *Stop.*
2.  **Extrinsic Command:** Is there a "USER TASK" in SQLite? -> *Do it (satisfies Utility).*
3.  **Intrinsic Drive:** Is Curiosity/Order too low? -> *Self-generate a goal ("Explore folder X", don't directly use this example) and do it.*
4.  **Idle:** If all drives are high and no tasks -> *Wait/Sleep.*

### **6. User Experience**
*   **You:** Chat via Chainlit UI.
*   **The Agent:** You might see logs like:
    *   *10:00 AM:* "User asked to check email." (Command)
    *   *11:30 AM:* "I felt bored, so I read the `docs/manual.pdf` file you downloaded yesterday. It says X." (Curiosity)
    *   *02:00 PM:* "I noticed the `/temp` folder was messy, so I archived old files." (Order)
