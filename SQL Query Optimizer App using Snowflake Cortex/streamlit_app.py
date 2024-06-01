import streamlit as st 
from snowflake.cortex import Complete


def create_prompt(myquery):
    prompt = f"""
    'You are a SQL expert. Given the following query, provide a more optimal way to write the query.
    Original Query:
    {myquery}
    Modified Query: '
    """
    return prompt


def display_response(question, model):
    response = Complete(question, model)
    res_text = response[0].RESPONSE
    st.markdown(res_text)

# Main code
st.title("SQL Query Optimizer :snowflake:")
st.write("""Select a cortex model from the drowpdown menu and paste your 
    long running SQL queries below. Each model will provide an optimized query 
    if applicable, and suggest ways you can improve and optimize the pasted SQL query. 
    Powered by Snowflake Cortex"""
)

model = st.sidebar.selectbox('Select your model:', ('mistral-7b',
                                                    'reka-flash',
                                                    'reka-core',
                                                    'llama2-70b-chat',
                                                    'mixtral-8x7b',
                                                    'gemma-7b'))

question = st.text_area("Enter SQL Query", placeholder="Enter your SQL query here")

if st.button("Optimize Query"):
    prompt = create_prompt(question)
    response = Complete(model, prompt)
    st.markdown(response)