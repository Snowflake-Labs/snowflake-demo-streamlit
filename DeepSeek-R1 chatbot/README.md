![](../shared_assets/sis-header.jpeg)

# 🐳💬 DeepSeek-R1 Chatbot

This chatbot is created using the open-source [**DeepSeek-R1**](https://github.com/deepseek-ai/DeepSeek-R1) LLM model.

This reasoning model is made available as part of [Snowflake Cortex](https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions).

## About the app

This app shows how to call the DeepSeek-R1 model to make LLM inference to engage in a conversation with the chatbot. 

Here are some key features of the app
- The chatbot retains memory of the conversation and can be reset at any time via the *clear chat history* button.
- You'll also notice that because this is a reasoning model, the *think* phase is displayed in the output and is encapsulated within the `<think> </think>` tags, which we'll parse and place within the `st.status()` container for aesthetic display and separation from the final answer.
- Users are also able to adjust the various model parameters (*e.g.* `temperature`, `top_p`, `max_tokens`, `presence_penalty` and `frequency_penalty`) and see its influence on the model output.

## Resources
- Read about this in this accompanying blog on [*How to build a DeepSeek-R1 chatbot*](https://medium.com/snowflake/how-to-build-a-deepseek-r1-chatbot-1edbf6e5e9fe)
