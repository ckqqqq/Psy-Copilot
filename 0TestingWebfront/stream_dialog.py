import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
st.title("ChatGPT-like clone")
with st.expander("Disclaimer"):
    st.caption(
        """We appreciate your engagement! Please note, this demo is designed to
        process a maximum of 10 interactions and may be unavailable if too many
        people use the service concurrently. Thank you for your understanding.
        """
    )

load_dotenv("../.env")
key_list=["OPENAI_API_KEY","OPENAI_API_BASE","MODEL"]
env_vars = {key: os.getenv(key) for key in key_list}
client = OpenAI(api_key=env_vars["OPENAI_API_KEY"],base_url=env_vars["OPENAI_API_BASE"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = env_vars["MODEL"]

if "messages" not in st.session_state:
    st.session_state.messages = []

if "max_messages" not in st.session_state:
    # Counting both user and assistant messages, so 10 rounds of conversation
    st.session_state.max_messages = 100

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# if len(st.session_state.messages) >= st.session_state.max_messages:
#     st.info(
#         """Notice: The maximum message limit for this demo version has been reached. We value your interest!
#         We encourage you to experience further interactions by building your own application with instructions
#         from Streamlit's [Build a basic LLM chat app](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)
#         tutorial. Thank you for your understanding."""
#     )

# else:
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = st.write_stream(stream)
            
            st.session_state.messages.append(
                {"role": "assistant", "content": response}
            )

            
        except Exception as e:
            st.session_state.max_messages = len(st.session_state.messages)
            rate_limit_message = """
                Oops! Sorry, I can't talk now. Too many people have used
                this service recently.str()
            """+str(e)
            st.session_state.messages.append(
                {"role": "assistant", "content": rate_limit_message}
            )
            st.rerun()