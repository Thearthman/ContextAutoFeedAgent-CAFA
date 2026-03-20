import sys
import os
from src.agent import get_agent_executor, manage_memory, get_system_message
from src.soul import Soul
from langchain_core.messages import HumanMessage, SystemMessage, AIMessageChunk

def main():
    print("Initializing Agent...")
    try:
        agent_executor = get_agent_executor()
        print("Agent Initialized.")
        print("Commands:")
        print("  /image <path>  - Attach an image to your next query")
        print("  exit           - Quit")
        print("-" * 50)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error initializing agent: {e}")
        print("Make sure the LLM server is running (start_agent.bat)")
        return

    current_image = None
    config = {"configurable": {"thread_id": "default-session"}}

    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["exit", "quit"]:
                break
            
            # Update Soul

                
            # Handle image command
            if user_input.startswith("/image "):
                path = user_input[7:].strip().strip('"').strip("'")
                if os.path.exists(path):
                    current_image = path
                    print(f"Image attached: {path}")
                    print("Type your question about the image:")
                    continue
                else:
                    print(f"Error: Image not found at {path}")
                    continue
            
            # Construct input with image context if present
            agent_input = user_input
            if current_image:
                agent_input += f"\n\n[User attached image for analysis: {current_image}]"
                print(f"(Sending with attachment: {current_image})")
                current_image = None # Reset after sending


            # For session memory, we only send the NEW human message. 
            # The checkpointer automatically includes previous messages.
            # We also inject the dynamic System Message here.
            system_msg = get_system_message()
            
            input_data = {
                "messages": [
                    SystemMessage(content=system_msg),
                    HumanMessage(content=agent_input)
                ]
            }
            
            # Use stream_mode="messages" for token-by-token streaming
            stream = agent_executor.stream(
                input_data,
                config=config,
                stream_mode="messages" 
            )
            
            print("Agent: ", end="", flush=True)
            last_node = None

            for msg, metadata in stream:
                node = metadata.get("langgraph_node")
                
                # Transparency: Show node transitions
                if node != last_node:
                    if node == "agent" and last_node == "tools":
                        print("\n[Agent is processing tool results...]", flush=True)
                    elif node == "tools":
                        print("\n[Switching to tool execution node...]", flush=True)
                    last_node = node

                if node == "agent":
                    # Check for reasoning/thinking content (standard for Qwen/DeepSeek reasoning models)
                    reasoning = getattr(msg, "reasoning_content", None)
                    if not reasoning and hasattr(msg, "additional_kwargs"):
                        reasoning = msg.additional_kwargs.get("reasoning_content")
                    
                    if reasoning:
                        print(reasoning, end="", flush=True)

                    # Some chunks might have content (text/thinking)
                    if msg.content:
                        print(msg.content, end="", flush=True)
                    
                    # Detect the start of tool calls in the message stream
                    if hasattr(msg, "tool_call_chunks") and msg.tool_call_chunks:
                        for chunk in msg.tool_call_chunks:
                            if chunk.get("name"):
                                print(f"\n[Agent decided to call tool: {chunk['name']}]", flush=True)
                
                # feedback for tools
                elif node == "tools" and getattr(msg, 'name', None):
                    # Tool messages are yielded after the tool finishes
                    content_preview = str(msg.content)[:100].replace('\n', ' ')
                    print(f"\n[Tool: {msg.name} finished. Result: {content_preview}...]", flush=True)
                    print("Agent: ", end="", flush=True)

            print() # Newline at end          
            
            # System Updates
            manage_memory(agent_executor, config)
            
            try:
                soul = Soul()
                soul.satisfy_drive("social", 0.05)
                soul.close()
            except Exception as e:
                print(f"Error updating soul: {e}")
                
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()
