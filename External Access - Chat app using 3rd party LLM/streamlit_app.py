from openai import OpenAI
import streamlit as st
import _snowflake

st.title(":speech_balloon: Using an External LLM to build a Chatbot app", anchor=False)
st.write("This app demos how to call an External LLM to build a simple chat application. This solution can be extended to call any other LLM API.")

try:
    secret = _snowflake.get_generic_secret_string('my_openai_key')
    client = OpenAI(api_key=secret)
except Exception as e:
    st.error("API key for OpenAI not found.", icon="🚨")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            llm = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=False,
            )
            response = llm.choices[0].message.content
            st.markdown(response)
        except Exception as e:
            st.error(f"An error occured: {e}")
    st.session_state.messages.append({"role": "assistant", "content": response})
