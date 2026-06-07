import streamlit as st
from langchain_core.messages import HumanMessage 
from langgraph_backend import chatbot

CONFIG = {'configurable':{'thread_id':'thread-1'}}

# st.session_state -> dict
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []


# {'role':'user','content':'Hi'}
# {'role':'assistant','content':'Hello'}

# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:

    # first add that message to that message history
    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)
    
    response = chatbot.invoke({'message':[HumanMessage(content=user_input)]},config=CONFIG)
    st.session_state['message_history'].append({'role':'assistant','content':user_input})
    with st.chat_message('assistant'):
        st.text(user_input)