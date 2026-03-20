import chainlit as cl
import os
import asyncio
from chainlit.context import context_var
from langchain_core.messages import HumanMessage, SystemMessage
from src.agent import get_agent_executor, manage_memory, get_system_message
from src.soul import Soul

# Initialize the agent
agent_executor = get_agent_executor()

@cl.on_chat_start
async def on_chat_start():
    # Set up the agent for this user session
    cl.user_session.set("agent", agent_executor)
    
    # Clean up any existing poller for this session if it exists
    old_poller = cl.user_session.get("poller_task")
    if old_poller:
        old_poller.cancel()
        
    # Start the proactive message poller for this session
    new_poller = asyncio.create_task(poll_for_messages(context_var.get()))
    cl.user_session.set("poller_task", new_poller)
    
    await cl.Message(content="Agent ready! You can ask questions or upload images.").send()

async def poll_for_messages(context):
    """Checks the Soul for pending outgoing messages every 10s."""
    # Set the context for this background task
    context_var.set(context)
    session_id = context.session.id
    
    print(f"[Poller] Started for session {session_id}")
    
    while True:
        try:
            soul = Soul()
            messages = soul.get_pending_messages()
            
            if messages:
                print(f"[Poller] Session {session_id} found {len(messages)} pending messages.")
            
            for msg in messages:
                # Send the message to the user
                content = msg['content']
                print(f"[Poller] Session {session_id} attempting to send: {content[:30]}...")
                
                try:
                    await cl.Message(content=f"*[Proactive]* {content}").send()
                    # Mark as sent ONLY after successful send
                    soul.mark_message_sent(msg['id'])
                    print(f"[Poller] Session {session_id} successfully sent and marked msg {msg['id']}")
                except Exception as send_error:
                    print(f"[Poller] Session {session_id} failed to send message: {send_error}")
            
            soul.close()
        except Exception as e:
            print(f"Error polling messages in session {session_id}: {e}")
        
        await asyncio.sleep(10)

@cl.on_message
async def on_message(message: cl.Message):
    agent = cl.user_session.get("agent")
    
    # 1. Handle Images
    # Chainlit captures uploaded files in message.elements
    images = [file for file in message.elements if "image" in file.mime] if message.elements else []
    
    user_text = message.content
    if images:
        # In this specific agent implementation, we pass the path in the text
        # as seen in src/main.py
        user_text += f"\n\n[Friend attached image for analysis: {images[0].path}]"

    # 2. Run Agent with Streaming
    # Using the same logic as src/main.py but adapted for Chainlit
    
    # Unique thread id for this session
    config = {"configurable": {"thread_id": cl.user_session.get("id")}}
    
    # Inject dynamic mood-based system prompt
    system_msg = get_system_message()
    


    input_data = {
        "messages": [
            SystemMessage(content=system_msg),
            HumanMessage(content=user_text)
        ]
    }
    
    # We'll use cl.Message to stream the final answer
    msg = cl.Message(content="")
    
    # Track steps
    thinking_step = None
    current_step = None

    # Use stream_mode="messages" to get token-by-token streaming
    async for chunk, metadata in agent.astream(
        input_data,
        config=config,
        stream_mode="messages"
    ):
        node = metadata.get("langgraph_node")
        
        if node == "agent":
            # Debug: print(f"CHUNK: {chunk}")
            
            # 1. Handle reasoning/thinking if present
            reasoning = None
            if hasattr(chunk, "reasoning_content") and chunk.reasoning_content:
                reasoning = chunk.reasoning_content
            elif hasattr(chunk, "additional_kwargs"):
                reasoning = chunk.additional_kwargs.get("reasoning_content")
            
            # Special case for some providers where thinking is in a specific chunk type
            if not reasoning and hasattr(chunk, "invalid_tool_calls"):
                # Sometimes reasoning is misclassified in early chunks
                pass

            if reasoning:
                if not thinking_step:
                    thinking_step = cl.Step(name="Thinking", root=True)
                    await thinking_step.send()
                await thinking_step.stream_token(reasoning)

            # 2. Stream the main content
            if hasattr(chunk, "content") and chunk.content:
                # If there's content and we were thinking, it means thinking is over
                if thinking_step:
                    await thinking_step.update()
                    thinking_step = None
                
                if not msg.content:
                    await msg.send()
                
                # Check if content itself contains <think> tags (fallback)
                content = chunk.content
                await msg.stream_token(content)
                
            # 3. Detect tool calls
            if hasattr(chunk, "tool_call_chunks") and chunk.tool_call_chunks:
                # If we were thinking, finish that step
                if thinking_step:
                    await thinking_step.update()
                    thinking_step = None

                for tool_chunk in chunk.tool_call_chunks:
                    if tool_chunk.get("name"):
                        # Start a new step for the tool call
                        # Display arguments if available
                        args = tool_chunk.get("args", "")
                        current_step = cl.Step(name=f"Calling: {tool_chunk['name']}")
                        if args:
                            current_step.input = args
                        await current_step.send()
                    elif tool_chunk.get("args") and current_step:
                        # Stream arguments if they are being streamed
                        current_step.input += tool_chunk['args']
                        await current_step.update()

        elif node == "tools":
            # 4. Handle tool output
            if current_step:
                if hasattr(chunk, "content"):
                    current_step.output = str(chunk.content)
                    await current_step.update()
                    current_step = None
    
    # Final cleanup
    if thinking_step:
        await thinking_step.update()
    if current_step:
        await current_step.update()
    
    # 5. Display Usage / Context Size
    try:
        state = agent.get_state(config)
        messages = state.values.get("messages", [])
        
        # Simple character-based estimate if token data isn't in metadata
        # (Since we don't have tiktoken installed here)
        total_chars = sum(len(str(m.content)) for m in messages)
        est_tokens = total_chars // 4 # Rough heuristic
        
        # Check if latest message has actual usage metadata
        usage_info = ""
        if messages and hasattr(messages[-1], "response_metadata"):
            usage = messages[-1].response_metadata.get("token_usage")
            if usage:
                usage_info = f" (Prompt: {usage.get('prompt_tokens')}, Completion: {usage.get('completion_tokens')})"
        
        status_msg = f"*Context: {len(messages)} messages | ~{est_tokens} tokens{usage_info}*"
        await cl.Message(content=status_msg).send()
    except Exception as e:
        print(f"Error displaying context size: {e}")
    
    # Update System after displaying msg
    manage_memory(agent, config)
    try:
        soul = Soul()
        soul.record_user_interaction()
        soul.satisfy_drive("social", 0.05)
        soul.close()
    except Exception as e:
        print(f"Error updating soul: {e}")
        
    await msg.update()
