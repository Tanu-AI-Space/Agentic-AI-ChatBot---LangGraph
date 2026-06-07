# Agentic AI ChatBot with LangGraph

A modern conversational AI chatbot built with **LangGraph** and **Streamlit**, featuring stateful conversation management and multi-turn dialogue capabilities.

---

## 📋 Project Overview

This project implements an intelligent conversational agent that maintains context across multiple interactions. It combines:
- **LangGraph**: For building stateful, agentic workflows
- **LangChain**: For LLM integration and message handling
- **Streamlit**: For a clean, interactive web UI
- **OpenAI**: As the underlying language model

---

## 🏗️ Architecture

### High-Level Flow Diagram

```
User Input (Streamlit UI)
    ↓
Frontend: langgraph_frontend.py
    ├─ Displays conversation history
    ├─ Captures user input
    └─ Sends message to backend chatbot
    ↓
Backend: langgraph_backend.py
    ├─ LangGraph State Graph
    ├─ ChatState (messages)
    ├─ chat_node (LLM processing)
    └─ InMemorySaver (conversation persistence)
    ↓
OpenAI ChatOpenAI LLM
    ├─ Processes user message
    └─ Generates response
    ↓
Response returned to Frontend
    ↓
Display in Streamlit UI
```

---

## 🔧 Project Structure

```
Agentic AI ChatBot - LangGraph/
├── langgraph_backend.py      # LangGraph chatbot logic & state management
├── langgraph_frontend.py     # Streamlit UI & conversation handler
└── README.md                 # This file
```

---

## 📖 Detailed Component Explanation

### 1. **Backend: `langgraph_backend.py`**

#### Imports & Setup
```python
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
```

#### Key Components:

**ChatState (State Definition)**
- A `TypedDict` that defines the structure of conversation state
- Contains a list of `BaseMessage` objects (user and assistant messages)
- Uses `add_messages` reducer to append new messages to the history

**LLM Instance**
```python
llm = ChatOpenAI()  # Uses OpenAI's GPT model
```
- Initialized with environment variables from `.env`
- Processes user messages and generates responses

**chat_node (Processing Function)**
```python
def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {'messages': response}
```
- Receives the current conversation state
- Sends all messages to the LLM
- Returns the LLM response as a new message
- The `add_messages` reducer automatically appends it to the history

**InMemorySaver (Checkpointer)**
```python
checkpointer = InMemorySaver()
```
- Persists conversation state in memory
- Enables conversation resumption across API calls
- Keyed by `thread_id` for multi-session support

**StateGraph (Workflow Graph)**
```python
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)
chatbot = graph.compile(checkpointer=checkpointer)
```
- Defines workflow: START → chat_node → END
- Compiles to an executable chatbot with state persistence
- Returns a compiled `RunnableGraph` object

---

### 2. **Frontend: `langgraph_frontend.py`**

#### Imports & Setup
```python
import streamlit as st
from langchain_core.messages import HumanMessage
from langgraph_backend import chatbot
```

#### Configuration
```python
CONFIG = {'configurable': {'thread_id': 'thread-1'}}
```
- Thread ID for session-based conversation tracking
- Allows the backend to maintain separate conversation threads

#### Session State Management
```python
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
```
- Streamlit's session state maintains message history across reruns
- Prevents loss of conversation when page refreshes
- Stores all messages locally on the client side

#### Message Display Loop
```python
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])
```
- Iterates through stored messages
- Displays each message with appropriate role styling (user vs assistant)
- Recreates conversation history on every Streamlit rerun

#### User Input Handling
```python
user_input = st.chat_input('Type here')
```
- Captures user typing input with a native chat interface
- Only triggers code below when user actually submits a message

#### Message Processing Flow
1. **Add to History**: User message stored in session state
2. **Display User Message**: Shown immediately in the UI
3. **Backend Invocation**: Sends HumanMessage to the chatbot graph
4. **Store Response**: Assistant response stored in session state
5. **Display Response**: Shows assistant message in the UI

---

## 🔄 Complete Execution Flow

### Step-by-Step Walkthrough

**User types: "Hello, how are you?"**

```
1. Frontend captures input in st.chat_input()
   └─ user_input = "Hello, how are you?"

2. Add message to session state
   └─ st.session_state['message_history'].append({'role': 'user', 'content': user_input})

3. Display user message immediately
   └─ st.chat_message('user') → st.text("Hello, how are you?")

4. Invoke backend chatbot
   └─ chatbot.invoke(
        {'messages': [HumanMessage(content="Hello, how are you?")]},
        config={'configurable': {'thread_id': 'thread-1'}}
      )

5. Backend Processing:
   a) ChatState receives messages
   b) chat_node calls llm.invoke(messages)
   c) ChatOpenAI generates response
   d) InMemorySaver stores updated state with new response

6. Response returned to frontend
   └─ response = {"messages": [AssistantMessage(content="Hello! I'm doing well...")]}

7. Store response in session state
   └─ st.session_state['message_history'].append({'role': 'assistant', 'content': response})

8. Display assistant message
   └─ st.chat_message('assistant') → st.text("Hello! I'm doing well...")

9. Streamlit reruns with updated state
   └─ On next rerun, displays entire conversation history
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation Steps

1. **Clone/Download the project**
```bash
cd "Agentic AI ChatBot - LangGraph"
```

2. **Create a virtual environment** (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install langgraph langchain langchain-openai streamlit python-dotenv
```

4. **Set up environment variables**
   - Create a `.env` file in the project root
   - Add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

---

## 🎯 Running the Application

### Start the Streamlit frontend:
```bash
streamlit run langgraph_frontend.py
```

The application will open in your default browser at `http://localhost:8501`

---

## 💬 How to Use

1. **Type a message** in the chat input box at the bottom
2. **Press Enter** to send your message
3. **Wait for the response** - the AI will process and reply
4. **Continue the conversation** - context is maintained across messages
5. **Refresh the page** - your conversation history is preserved in session state

### Example Conversations

```
User: "What is machine learning?"
Assistant: [Provides comprehensive explanation]

User: "Can you give me an example?"
Assistant: [References previous context, provides specific example]

User: "Explain it differently"
Assistant: [Reformulates explanation based on conversation context]
```

---

## 🔑 Key Concepts

### State Management
- **State Graph**: Defines the flow of data through nodes
- **ChatState**: Contains conversation messages
- **add_messages**: Reducer that appends new messages to the list

### Conversation Persistence
- **InMemorySaver**: Stores state snapshots indexed by thread_id
- **Thread ID**: Unique identifier for each conversation session
- **Checkpointing**: Enables resuming conversations

### Message Types
- **HumanMessage**: User input messages
- **BaseMessage**: Parent class for all message types
- **AIMessage**: Generated responses (created by the LLM)

### Graph Execution
- **START**: Entry point
- **chat_node**: Processing step where LLM invocation happens
- **END**: Exit point

---

## ⚙️ Configuration Options

### Modify LLM Model
In `langgraph_backend.py`:
```python
llm = ChatOpenAI(model="gpt-4")  # or "gpt-3.5-turbo"
```

### Change Thread ID for Different Sessions
In `langgraph_frontend.py`:
```python
CONFIG = {'configurable': {'thread_id': 'thread-2'}}  # Different conversation
```

### Customize UI
In `langgraph_frontend.py`:
```python
st.title("My Custom Chatbot")  # Add custom title
st.sidebar.info("Info about your bot")  # Add sidebar info
```

---


## Dependencies

| Package | Purpose |
|---------|---------|
| `langgraph` | State graph & agentic workflow orchestration |
| `langchain` | LLM abstractions & message handling |
| `langchain-openai` | OpenAI API integration |
| `streamlit` | Web UI framework |
| `python-dotenv` | Environment variable management |

---

## 🌊 Streaming Responses

### Overview

The **streaming** feature enables real-time response display, improving user experience by showing AI responses as they're generated instead of waiting for the complete response.

### Key Difference: Invoke vs Stream

#### **Standard Approach (Blocking)**
```python
response = chatbot.invoke(
    {'messages': [HumanMessage(content=user_input)]},
    config=CONFIG
)
# User must wait for entire response before seeing anything
```

#### **Streaming Approach (Non-Blocking)**
```python
for message_chunk, metadata in chatbot.stream(
    {'messages': [HumanMessage(content=user_input)]},
    config=CONFIG,
    stream_mode='messages'
):
    # Process each chunk as it arrives
    print(message_chunk.content)
```

---

### Streaming Frontend Implementation

#### File: `streaming_langgraph_frontend.py`

**Key Components:**

```python
with st.chat_message('assistant'):
    ai_message = st.write_stream(
        message_chunk.content for message_chunk, metadata in chatbot.stream(
            {'messages': [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode='messages'
        )
    )
```

**Breaking Down the Streaming Flow:**

1. **`chatbot.stream()`** - Instead of `.invoke()`
   - Returns a generator that yields message chunks as they arrive
   - Processes from the LLM in real-time
   - `stream_mode='messages'` tells LangGraph to stream individual message objects

2. **Iteration: `for message_chunk, metadata in chatbot.stream(...)`**
   - Each `message_chunk` is a partial message object
   - Contains `.content` - the actual text being generated
   - `metadata` provides additional context about the chunk

3. **`st.write_stream(generator)`** - Streamlit's streaming display
   - Accepts a generator/iterator
   - Displays content as it's yielded
   - Shows text appearing character-by-character in the UI
   - Returns the complete accumulated message when done

4. **Accumulation**
   - `ai_message` stores the final complete response
   - This is then saved to session state for history

---

### Streaming Execution Flow

```
User Input
    ↓
Frontend receives message
    ↓
User message displayed immediately
    ↓
Backend: chatbot.stream() starts
    ├─ Connects to OpenAI LLM
    ├─ LLM begins generating response
    └─ Yields chunks as they arrive (e.g., "Hello", " ", "there", "...")
    ↓
Frontend: st.write_stream() processes chunks
    ├─ Displays first chunk: "Hello"
    ├─ Displays next chunk: " "
    ├─ Displays next chunk: "there"
    └─ Continues displaying all chunks in real-time
    ↓
Complete response accumulated
    ↓
Response saved to session history
    ↓
User sees complete message with streaming animation
```

---

### Benefits of Streaming

| Benefit | Description |
|---------|-------------|
| **Better UX** | Users see response appearing in real-time, not sudden block of text |
| **Perception of Speed** | Feels faster because feedback is immediate, not delayed |
| **Lower Latency Feel** | Users aren't staring at a blank screen waiting |
| **Reduced Anxiety** | Immediate visual feedback that the system is working |
| **Resource Efficiency** | Can process partial responses while still generating |

---

### Stream Mode Options

#### `stream_mode='messages'`
- **Streams individual message objects**
- Each chunk is a `BaseMessage` subclass
- Best for chat interfaces
- Shows incremental message updates

#### `stream_mode='values'`
- Streams complete state updates
- Returns entire ChatState object at each step
- Better for debugging state transitions

#### `stream_mode='updates'`
- Streams only the changed portions
- Shows what changed at each step
- Useful for complex graphs

---

### Comparing Standard vs Streaming Implementation

#### Standard Frontend (`langgraph_frontend.py`)
```python
response = chatbot.invoke(
    {'messages': [HumanMessage(content=user_input)]},
    config=CONFIG
)
# ❌ User waits silently
st.session_state['message_history'].append({'role':'assistant','content':response})
```

#### Streaming Frontend (`streaming_langgraph_frontend.py`)
```python
with st.chat_message('assistant'):
    ai_message = st.write_stream(
        message_chunk.content for message_chunk, metadata in chatbot.stream(
            {'messages': [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode='messages'
        )
    )
# ✅ User sees response appearing in real-time
st.session_state['message_history'].append({'role':'assistant','content':ai_message})
```

---

### Running with Streaming

```bash
streamlit run streaming_langgraph_frontend.py
```

This loads the enhanced frontend with real-time response streaming.

---

### When to Use Streaming vs Invoke

**Use Streaming when:**
- Building interactive chat interfaces
- Want immediate visual feedback
- Displaying long-form responses
- Improving perceived performance
- Building real-time applications

**Use Invoke when:**
- Building batch processing pipelines
- Need the complete response before proceeding
- Processing responses programmatically
- Working with non-streaming APIs
- Building background jobs

---

## 🔄 Project Structure (Updated)

```
Agentic AI ChatBot - LangGraph/
├── langgraph_backend.py             # Core chatbot logic (shared)
├── langgraph_frontend.py            # Standard frontend (blocking invoke)
├── streaming_langgraph_frontend.py  # Streaming frontend (real-time display)
└── README.md                        # This file
```

---


