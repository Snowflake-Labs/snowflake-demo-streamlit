import streamlit as st
from snowflake.cortex import Complete

st.title('Chat with models in Snowflake Cortex', anchor=False)

# Instructions appended to every chat, and always used 
instructions = "Be concise. Do not hallucinate"

# Choose a Cortex model
model = st.selectbox("Choose a model", 
                     [
                         'snowflake-arctic',
                         'mistral-large',
                         'reka-flash',
                         'llama2-70b-chat', 
                         'mixtral-8x7b', 
                         'mistral-7b',
                    ]
)

# Initialize message history in session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            'role': 'assistant',
            'content': 'how can I help?'
        }
    ]

# Show the conversation history
st.subheader(f"Conversation with {model}", anchor=False, divider="gray")
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])


prompt = st.chat_input("Type your message")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):  
        context = ",".join(f"role:{message['role']} content:{message['content']}" for message in st.session_state.messages)
        response = Complete(model, f"Instructions:{instructions}, Context:{context}, Prompt:{prompt}")
        st.markdown(response)
    
        st.session_state.messages.append({
            'role': 'assistant',
            'content': response
        })