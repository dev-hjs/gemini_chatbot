import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted

# 페이지 설정
st.set_page_config(
    page_title="Gemini 챗봇",
    page_icon="🤖",
    layout="wide"
)

# API 키 설정
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY가 설정되지 않았습니다. .streamlit/secrets.toml 파일에 API 키를 추가해주세요.")
    st.stop()

# Gemini 모델 초기화
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

# 세션 상태 초기화
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 타이틀 및 설명
st.title("Gemini 챗봇")
st.markdown("Gemini API를 활용한 기본 챗봇 프레임워크입니다.")

# 채팅 인터페이스
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
prompt = st.text_input("메시지를 입력하세요", key="user_input")
if prompt:
    # 사용자 메시지 추가
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gemini 응답 생성
    with st.chat_message("assistant"):
        try:
            response = st.session_state.chat.send_message(prompt)
            st.markdown(response.text)
            st.session_state.chat_history.append({"role": "assistant", "content": response.text})
        except ResourceExhausted:
            st.error("API 할당량이 모두 소진되었습니다.")
            st.info("""
            다음 중 하나를 시도해보세요:
            1. 잠시 후 다시 시도 (약 1시간 후)
            2. API 키를 유료 플랜으로 업그레이드
            3. 다른 API 키 사용
            """)
        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")

# 이전 대화 보기
with st.expander("이전 대화 보기"):
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"]) 
