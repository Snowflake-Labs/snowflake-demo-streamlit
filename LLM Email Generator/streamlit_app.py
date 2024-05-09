from snowflake.cortex import Complete
import streamlit as st


def get_generated_email(
    email_content: str,
    email_sender: str,
    email_recipient: str,
    email_style: str,
    model: str,
) -> str:
    """
    Generate an email based on the inputs using Snowflake Cortex.
    """
    rephrased_content = Complete(
        model,
        f"""
        Rewrite the text to be elaborate and polite, it must sound {email_style}.
        The sender of the email is: {email_sender}.
        The recipient is: {email_recipient}.
        Abbreviations need to be replaced.
        The body of the email is: {email_content}
        """,
    )
    return rephrased_content


st.header("Email Generator :incoming_envelope:", anchor=False)
st.write(
    """
    This app generates professional emails customized to your selected topic based on the details you provide.
    Powered by [Snowflake Cortex](https://www.snowflake.com/en/data-cloud/cortex/) :snowflake:
    """
)

st.subheader("What is your email about?", anchor=False)
with st.expander("Email Input", expanded=True):

    email_subject = st.text_input("Email Subject")

    email_text = ""
    # Initialize columns variables
    sender_col, recipient_col = st.columns([5, 5])
    style_col, model_col = st.columns([5, 5])
    with sender_col:
        email_sender = st.text_input("Sender Name")
    with recipient_col:
        email_recipient = st.text_input("Recipient Name")
    with style_col:
        email_style = st.selectbox(
            "Writing Style",
            ("Formal", "Motivated", "Concerned", "Disappointed"),
        )
    with model_col:
        selected_model = st.selectbox(
            "Choose a model", (
                "snowflake-arctic", "llama2-70b-chat", "mixtral-8x7b", 
                "mistral-7b", "mistral-large", "reka-flash"
            )
        )

    if st.button("Generate Email", use_container_width=True):
        with st.spinner():
            if email_subject == "" or email_sender == "" or email_recipient == "":
                st.session_state.error = True
                if st.session_state.error:
                    st.error("You must enter values for all the inputs.")
            else:
                email_text = get_generated_email(
                    email_subject,
                    email_sender,
                    email_recipient,
                    email_style,
                    selected_model,
                )
if email_text != "":
    with st.expander("Email Output", expanded=True):
        st.write(email_text)
