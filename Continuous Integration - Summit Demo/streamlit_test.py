from unittest.mock import patch
from streamlit.testing.v1 import AppTest
import pandas as pd


class MockSnowparkDF:
    def __init__(self, df):
        self.df = df

    def to_pandas(self):
        return self.df


# @patch replaces the Snowflake calls with MagicMocks passed as arguments
# This enables mocking the Snowflake sql() and Complete() calls. See:
# https://docs.python.org/3/library/unittest.mock.html#quick-guide
@patch("snowflake.cortex.Complete")
@patch("streamlit.connection")
def test_app(conn, complete):
    """Test the app output"""
    at = AppTest.from_file("streamlit_app.py")

    # Set up the mocks
    user_feedback = pd.DataFrame({
        "TIMESTAMP": ["2022-01-01", "2022-01-02", "2022-01-03"],
        "FEEDBACK": [
            "Streamlit in Snowflake has revolutionized our data visualization process ...",
            "I appreciate the integration of Streamlit in Snowflake, ...",
            "Streamlit in Snowflake is powerful, but ..."
        ],
        "USER_ID": ["user7", "user1", "user3"],
    })
    
    # app calls st.connection().session().sql()
    conn.return_value.session.return_value.sql.return_value = MockSnowparkDF(user_feedback)

    # Ensure the DF ends up in call to Complete, and return a dummy response
    DUMMY_RESPONSE = "Users love Streamlit in Snowflake, while some want more integrations"
    def complete_response(model, prompt, session):
        assert model == "mistral-large"
        assert "Streamlit in Snowflake has revolutionized our data visualization process" in prompt
        return DUMMY_RESPONSE
    complete.side_effect = complete_response

    # Run the script and compare results
    at.run()
    # print(at) # use for debugging

    # Sections display in proper order
    assert at.subheader[0].value == "Number of customers"
    assert at.subheader[1].value == "Views per day"
    assert at.subheader[2].value == "Views per customer"
    
    # Dummy response was returned and rendered as markdown
    assert at.markdown[-1].value == DUMMY_RESPONSE
    
    # No exceptions
    assert not at.exception
