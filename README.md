# Agentic AI ChatBot with LangGraph

A modern conversational AI chatbot built with **LangGraph** and **Streamlit**, featuring stateful conversation management and multi-turn dialogue capabilities.

---

## Project Overview

This project implements an intelligent conversational agent that maintains context across multiple interactions. It combines:
- **LangGraph**: For building stateful, agentic workflows
- **LangChain**: For LLM integration and message handling
- **Streamlit**: For a clean, interactive web UI
- **OpenAI**: As the underlying language model

---

## Architecture

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

## Project Structure

```
Agentic AI ChatBot - LangGraph/
├── langgraph_backend.py             # In-memory backend (basic)
├── langgraph_frontend.py            # Standard frontend (blocking invoke)
├── streaming_langgraph_frontend.py  # Streaming frontend (real-time)
├── threading_langgraph_frontend.py  # Threading frontend (multi-thread)
├── database_backend.py              # Database backend (SQLite storage)
├── database_frontend.py             # Database frontend (persistent storage)
├── .env                             # Environment variables (API keys)
├── .gitignore                       # Git ignore file
├── chatbot.db                       # SQLite database (auto-generated)
└── README.md                        # This file
```

---

## Detailed Component Explanation

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

## Complete Execution Flow

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

## Installation & Setup

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

## Running the Application

### Start the Streamlit frontend:
```bash
streamlit run langgraph_frontend.py
```

The application will open in your default browser at `http://localhost:8501`

---

## How to Use

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

## Key Concepts

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

## Configuration Options

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

## Streaming Responses

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
# User waits silently
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
# User sees response appearing in real-time
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

## Project Structure (Updated)

```
Agentic AI ChatBot - LangGraph/
├── langgraph_backend.py             # Core chatbot logic (shared)
├── langgraph_frontend.py            # Standard frontend (blocking invoke)
├── streaming_langgraph_frontend.py  # Streaming frontend (real-time display)
├── threading_langgraph_frontend.py  # Multi-thread frontend (multiple conversations)
└── README.md                        # This file
```

---

## 🧵 Multiple Conversation Threads

### Overview

The **threading** feature enables users to manage multiple independent conversations simultaneously, similar to having multiple chat tabs or threads. Each thread maintains its own context and message history independently.

### Key Concepts

#### Thread ID
- **Unique Identifier**: Each conversation is identified by a unique thread ID
- **Persistence**: Thread ID is stored in `InMemorySaver` checkpoint
- **Isolation**: Messages in one thread don't affect others
- **Generation**: Created using Python's `uuid.uuid4()` for uniqueness

```python
import uuid

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id
```

### Threading Architecture

```
Thread Management System
    ├── Thread 1 (UUID: abc-123)
    │   ├─ Message: "Hi"
    │   ├─ Response: "Hello!"
    │   └─ State: Stored in InMemorySaver
    │
    ├── Thread 2 (UUID: def-456)
    │   ├─ Message: "What is AI?"
    │   ├─ Response: "AI is..."
    │   └─ State: Stored separately
    │
    └── Thread 3 (UUID: ghi-789)
        ├─ Message: "Tell me a joke"
        ├─ Response: "Why did..."
        └─ State: Independent context
```

### Frontend Implementation: `threading_langgraph_frontend.py`

#### Session State Setup

```python
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []
```

**Components:**
- `message_history`: Current thread's messages
- `thread_id`: Currently active thread
- `chat_threads`: List of all thread IDs

#### Thread Management Functions

**1. Generate Thread ID**
```python
def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id
```
- Creates unique identifier for new thread
- Uses UUID4 for global uniqueness

**2. Reset Chat (New Thread)**
```python
def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []
```
- Generates new thread ID
- Sets it as active thread
- Clears message history for new thread
- Registers thread in chat list

**3. Add Thread**
```python
def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
```
- Registers thread ID in the threads list
- Prevents duplicates

**4. Load Conversation**
```python
def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable':{'thread_id':thread_id}})
    return state.values.get('messages',[])
```
- Retrieves conversation history for specific thread
- Accesses backend state using thread_id
- Returns list of messages or empty list

#### Sidebar UI for Thread Management

```python
st.sidebar.title("My ChatBot")

if st.sidebar.button("New Chat"):
    reset_chat()  # Create new thread

st.sidebar.header("My Chats")

for thread_id in st.session_state['chat_threads']:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)
        # Convert to display format and load
```

**Features:**
- "New Chat" button: Creates and switches to new thread
- Thread list: Shows all available threads
- Click to switch: Clicking thread button loads that conversation
- Persistent display: All threads visible in sidebar

#### Message Display with Thread Context

```python
# Loading the conversation history for active thread
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])
```
- Displays only messages from current thread
- Message history is specific to active thread_id

#### User Input Processing with Thread ID

```python
if user_input:
    # Add to current thread's history
    st.session_state['message_history'].append({'role':'user','content':user_input})
    
    # Create config with current thread ID
    CONFIG = {'configurable':{'thread_id':st.session_state['thread_id']}}
    
    # Send to chatbot with thread context
    ai_message = st.write_stream(
        message_chunk.content for message_chunk, metadata in chatbot.stream(
            {'messages':[HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode='messages'
        )
    )
```

**Flow:**
1. User message added to current thread's history
2. CONFIG includes current thread_id
3. Backend receives thread_id and maintains separate state
4. Response stored in current thread's history only

### Threading Execution Flow

```
User Creates Thread 1
    ↓
User message: "Hello"
    ├─ Added to Thread 1 history
    ├─ Backend receives thread_id='thread-1'
    ├─ LLM processes in Thread 1 context
    └─ Response stored in Thread 1
    ↓
User Creates Thread 2 ("New Chat")
    ├─ New UUID generated
    ├─ Thread 1 saved in chat_threads
    ├─ Thread 2 becomes active
    └─ Message history cleared
    ↓
User message in Thread 2: "What is AI?"
    ├─ Added to Thread 2 history
    ├─ Backend receives thread_id='thread-2'
    ├─ Thread 1 context is NOT used
    ├─ LLM processes independently
    └─ Response stored in Thread 2
    ↓
User Switches Back to Thread 1
    ├─ load_conversation(thread-1) called
    ├─ Backend retrieves Thread 1 state
    ├─ Message history reloaded
    └─ Displays full Thread 1 conversation
    ↓
User Continues Thread 1: "How are you?"
    ├─ Message added to Thread 1 (not Thread 2)
    ├─ Backend receives thread_id='thread-1'
    ├─ LLM has full Thread 1 context
    └─ Response maintains Thread 1 context
```

### Benefits of Threading

| Benefit | Description |
|---------|-------------|
| **Context Isolation** | Different threads don't interfere with each other |
| **Multi-tasking** | Handle multiple conversations without losing context |
| **Easy Switching** | Switch between conversations with one click |
| **Parallel Planning** | Work on different topics simultaneously |
| **Conversation History** | Easy access to all previous conversations |
| **Clean Separation** | Each thread has independent LLM context |

### Running with Threading

```bash
streamlit run threading_langgraph_frontend.py
```

This loads the enhanced frontend with multiple conversation thread support.

### User Workflow

1. **Start Default Thread**
   - App opens with Thread 1
   - Chat normally with the AI

2. **Create New Thread**
   - Click "New Chat" in sidebar
   - Fresh conversation starts
   - Previous thread saved

3. **Switch Between Threads**
   - Click thread UUID in "My Chats" sidebar
   - Full conversation history loads
   - Continue where you left off

4. **Multiple Independent Conversations**
   - Each thread maintains complete context
   - No message leakage between threads
   - Can switch freely without losing data

### Threading vs Standard Frontend

| Feature | Standard | Streaming | Threading |
|---------|----------|-----------|----------|
| Multiple Conversations | ❌ | ❌ | ✅ |
| Real-time Streaming | ❌ | ✅ | ✅ |
| Thread Switching | ❌ | ❌ | ✅ |
| Persistent Threads | ❌ | ❌ | ✅ |
| Session State | ✅ | ✅ | ✅ |
| Context Isolation | N/A | N/A | ✅ |


### Comparison: Single vs Multi-Thread Flow

**Single Thread (Standard Frontend)**
```
User 1: "Hi"
 Assistant: "Hello!"
User 2: "What is AI?"  ← Context includes "Hi" and "Hello!"
Assistant: "AI is..."  ← Mixed context
```

**Multi-Thread (Threading Frontend)**
```
Thread 1:
  User: "Hi"
  Assistant: "Hello!"

Thread 2:
  User: "What is AI?"
  Assistant: "AI is..."  ← No "Hi" context
```

### When to Use Threading

**Use Threading when:**
- Users need to manage multiple conversations
- Working on different topics simultaneously
- Need conversation history and easy switching
- Building multi-project or multi-topic applications
- Requiring context isolation between conversations

**Use Standard/Streaming when:**
- Single, focused conversation
- Simple chatbot applications
- No need for conversation history
- Building minimal interfaces

---

## 💾 Persistent Database Storage

### Overview

The **database** feature enables permanent storage of conversations using SQLite, replacing in-memory storage. This ensures all chat histories persist across application restarts and multiple sessions.

### Key Differences: In-Memory vs Database

#### In-Memory Storage (Threading Frontend)
- Conversations lost when app restarts
- Data stored only in RAM
- Fast but temporary
- Good for development/testing

#### Database Storage (Database Frontend)
- Permanent conversation persistence
- Data stored in SQLite file (`chatbot.db`)
- Survives application crashes
- Production-ready
- Queryable via SQL

### Backend Implementation: `database_backend.py`

#### Key Changes from In-Memory Backend

**Standard Backend**
```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()
```

**Database Backend**
```python
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

conn = sqlite3.connect('chatbot.db', check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)
```

#### Components Explanation

**SQLite Connection**
```python
conn = sqlite3.connect('chatbot.db', check_same_thread=False)
```
- Creates/connects to `chatbot.db` SQLite database file
- `check_same_thread=False`: Allows multi-threaded access
- Database file persists on disk

**SqliteSaver Checkpointer**
```python
checkpointer = SqliteSaver(conn=conn)
```
- LangGraph's built-in SQLite checkpoint manager
- Automatically creates schema for conversation storage
- Saves state after each interaction
- Retrieves state when needed

**Thread Retrieval Function**
```python
def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    return list(all_threads)
```
- Queries all stored threads from database
- Fetches checkpoint history
- Extracts unique thread IDs
- Returns list of all conversations

#### Graph Setup (Unchanged)
```python
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)
```
- Same graph structure
- Now uses database checkpointer instead of memory
- All state saves go to SQLite

### Frontend Implementation: `database_frontend.py`

#### Enhanced Configuration

**Extended CONFIG Structure**
```python
CONFIG = {
    "configurable": {
        'thread_id': st.session_state['thread_id']
    },
    "metadata": {
        "thread_id": st.session_state['thread_id']
    },
    "run_name": "chat_turn"
}
```

**Components:**
- `configurable.thread_id`: For state retrieval/storage
- `metadata.thread_id`: Additional context for queries
- `run_name`: Labels each interaction for logging

#### Thread Management with Database

```python
def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable':{'thread_id':thread_id}})
    return state.values.get('messages',[])
```

**Database Query Process:**
1. `get_state()` queries SQLite for thread_id
2. Checkpoint manager retrieves stored state
3. Messages extracted from returned state
4. Returned to frontend for display

#### Persistence Flow

```
User Input
    ↓
Message added to session history
    ↓
Message sent to LLM via chatbot.stream()
    ↓
Backend processes with thread_id
    ↓
LLM generates response
    ↓
SqliteSaver checkpointer captures state
    ↓
State saved to chatbot.db:
    ├─ Thread ID
    ├─ Messages
    ├─ Timestamps
    └─ Metadata
    ↓
Response returned to frontend
    ↓
Frontend displays response
    ↓
Next session: Data persists in database
```

### Database Schema (Auto-Generated)

SqliteSaver automatically creates the following tables:

```sql
-- Checkpoints table
CREATE TABLE IF NOT EXISTS checkpoints (
    thread_id TEXT,
    checkpoint_ns TEXT,
    checkpoint_id TEXT,
    parent_checkpoint_id TEXT,
    checkpoint BLOB,
    metadata JSONB,
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
);
```

**Table Structure:**
- `thread_id`: Conversation identifier
- `checkpoint_ns`: Namespace for different graph instances
- `checkpoint_id`: Unique checkpoint identifier
- `parent_checkpoint_id`: Reference to previous state
- `checkpoint`: Serialized state data (BLOB)
- `metadata`: Additional context (JSON)

### Running with Database

```bash
streamlit run database_frontend.py
```

### Benefits of Database Storage

| Benefit | Description |
|---------|-------------|
| **Persistent Storage** | Conversations survive app restarts |
| **Reliability** | No data loss on crashes or errors |
| **Queryability** | Access conversations via SQL queries |
| **Scalability** | Support unlimited conversations |
| **Auditability** | Track conversation history and changes |
| **Multi-user** | Share database across multiple instances |
| **Backup** | Easy file-based backups (copy chatbot.db) |

### Database Operations

#### Retrieve All Threads from Database
```python
from database_backend import retrieve_all_threads

all_threads = retrieve_all_threads()
for thread_id in all_threads:
    print(f"Thread: {thread_id}")
```

#### Query Specific Thread State
```python
state = chatbot.get_state(
    config={'configurable': {'thread_id': 'thread-uuid'}}
)
messages = state.values.get('messages', [])
```

#### Clear Specific Thread (Delete)
```python
# Note: SqliteSaver doesn't have built-in delete
# Manual SQL deletion:
import sqlite3
conn = sqlite3.connect('chatbot.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
conn.commit()
```

### Comparison: Storage Methods

| Feature | In-Memory | Threading | Database |
|---------|-----------|-----------|----------|
| **Persistence** | ❌ | ❌ | ✅ |
| **App Restarts** | Lost | Lost | Preserved |
| **Queryable** | ❌ | ❌ | ✅ |
| **Multi-Instance** | ❌ | ❌ | ✅ |
| **Multiple Threads** | ❌ | ✅ | ✅ |
| **Real-time Streaming** | ❌ | ✅ | ✅ |
| **SQL Queries** | ❌ | ❌ | ✅ |
| **Memory Usage** | Low | Medium | High |


### When to Use Database Storage

**Use Database when:**
- Production applications
- Need permanent conversation history
- Multi-user scenarios
- Conversation search/analytics required
- Long-running applications
- Backup/recovery needed
- Multi-instance deployments

**Use In-Memory when:**
- Development/testing only
- Single temporary sessions
- Privacy-first (no storage)
- Minimal resource usage
- Disposable conversations

### Migration Path: In-Memory to Database

1. **Set up Database Backend**
   ```bash
   # Replace imports
   from database_backend import chatbot
   from langgraph.checkpoint.sqlite import SqliteSaver
   ```

2. **Update Frontend**
   ```bash
   streamlit run database_frontend.py
   ```

3. **Existing Sessions**
   - Previous in-memory data is not migrated
   - Start fresh with database
   - Or export and reimport data

### Project Structure (Final)

```
Agentic AI ChatBot - LangGraph/
├── langgraph_backend.py             # In-memory backend (basic)
├── langgraph_frontend.py            # Standard frontend (blocking invoke)
├── streaming_langgraph_frontend.py  # Streaming frontend (real-time)
├── threading_langgraph_frontend.py  # Threading frontend (multi-thread)
├── database_backend.py              # Database backend (SQLite storage)
├── database_frontend.py             # Database frontend (persistent storage)
├── chatbot.db                       # SQLite database (auto-generated)
└── README.md                        # This file
```

---


