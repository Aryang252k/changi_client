import streamlit as st
import requests
from langchain_core.messages import AIMessage, HumanMessage


# Configure the page
st.set_page_config(
    page_title="Changi AI Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# API endpoint configuration
API_ENDPOINT = "https://changi-jewel-chatbot-984541274284.europe-west1.run.app"

def send_message_to_api(message: str) -> str:
    """Send message to the API endpoint and return the response"""
    try:
        # Get last 5 messages for context (10 total - 5 pairs of user/assistant)
        recent_history = st.session_state.chat_history[-10:] if len(st.session_state.chat_history) > 10 else st.session_state.chat_history
        
        payload = {
            "message": message,
            "conversation_history": [
                {
                    "role": "assistant" if isinstance(msg, AIMessage) else "user",
                    "content": msg.content
                }
                for msg in recent_history
            ]
        }
        
        # Make the API request
        response = requests.post(
            f"{API_ENDPOINT}/chat", 
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            # Adjust this based on your API's response format
            return result.get("response", "Sorry, I couldn't process that request.")
        else:
            return f"Error: API returned status code {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to the API. Please make sure the server is running."
    except requests.exceptions.Timeout:
        return "Error: Request timed out. Please try again."
    except Exception as e:
        return f"Error: {str(e)}"

# App header
st.title("🤖 Changi AI Chatbot")

# Create a container for the chat interface
chat_container = st.container()

# Display chat history
with chat_container:
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.write(message.content)

# Chat input
user_query = st.chat_input("Type your message here...")

if user_query is not None and user_query.strip() != "":
    # Add user message to chat history
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    
    # Display user message immediately
    with st.chat_message("user"):
        st.write(user_query)
    
    # Show typing indicator
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Get response from API
            ai_response = send_message_to_api(user_query)
    
    # Add AI response to chat history
    st.session_state.chat_history.append(AIMessage(content=ai_response))
    
    # Display AI response
    with st.chat_message("assistant"):
        st.write(ai_response)

# Sidebar with additional features
with st.sidebar:
    st.header("Chat Settings")
    
    # API status check
    st.subheader("API Status")
    try:
        health_response = requests.get(f"{API_ENDPOINT}/health", timeout=5)
        if health_response.status_code == 200:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Error")
    except:
        st.error("❌ API Disconnected")
    
    st.markdown(f"**Endpoint:** `{API_ENDPOINT}`")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
    
    # Chat statistics
    st.subheader("Chat Stats")
    total_messages = len(st.session_state.chat_history)
    user_messages = len([msg for msg in st.session_state.chat_history if isinstance(msg, HumanMessage)])
    ai_messages = len([msg for msg in st.session_state.chat_history if isinstance(msg, AIMessage)])
    
    st.metric("Total Messages", total_messages)
    st.metric("Your Messages", user_messages)
    st.metric("AI Messages", ai_messages)
    
    # Export chat option
    if st.button("💾 Export Chat"):
        chat_export = []
        for msg in st.session_state.chat_history:
            role = "Assistant" if isinstance(msg, AIMessage) else "User"
            chat_export.append(f"{role}: {msg.content}")
        
        export_text = "\n\n".join(chat_export)
        st.download_button(
            label="Download Chat History",
            data=export_text,
            file_name="chat_history.txt",
            mime="text/plain"
        )

