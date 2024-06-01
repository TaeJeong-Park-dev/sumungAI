import streamlit as st
from langchain_core.callbacks.base import BaseCallbackHandler 

# 템플렛
class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

def print_messages():
    # 새로고침될 때 리스트에 저장된 이전대화기록 출력시켜주기
    if "messages" in st.session_state and len(st.session_state["messages"]) > 0: # 리스트에 저장된 메시지가 있을 경우
        for role, message in st.session_state["messages"]: # user랑 assistant 아이콘 구별해서 붙이기 위함
            st.chat_message(role).write(message)