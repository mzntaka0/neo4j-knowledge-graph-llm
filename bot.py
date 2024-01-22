import streamlit as st

from utils import write_message
from solutions.agent import generate_response

st.set_page_config("Ebert", page_icon=":movie_camera:")
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """このデモでは、映画知識グラフに基づいて回答します。
            ※データセットが英語ですが、requestとresponseの間に翻訳タスクを挟んでいます。""",
        },
    ]


def handle_submit(message):
    with st.spinner("Thinking..."):
        response = generate_response(message)
        write_message("assistant", response)


with st.container():
    for message in st.session_state.messages:
        write_message(message["role"], message["content"], save=False)

    if prompt := st.chat_input("What is up?"):
        write_message("user", prompt)
        handle_submit(prompt)
