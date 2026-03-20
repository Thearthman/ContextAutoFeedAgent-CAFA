from src.soul import Soul
import sys

def reset_msgs():
    try:
        soul = Soul()
        soul.conn.execute("UPDATE messages SET status = 'pending'")
        soul.conn.commit()
        print("All messages reset to pending for testing.")
        soul.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    reset_msgs()
