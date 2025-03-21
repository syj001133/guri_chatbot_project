import streamlit as st
import sqlite3
from rapidfuzz import process  # 문자열 유사도 비교 라이브러리
import re

def convert_urls_to_links(text):
    url_pattern = r"(https?://\S+)"
    return re.sub(url_pattern, r'[\1](\1)', text)  # 마크다운 링크로 변환

# 🌟 Streamlit 페이지 설정
st.set_page_config(
    page_title="구리시청 내부 민원 챗봇",
    page_icon="🤖",
    layout="centered"
)

# 🌟 DB 연결 함수
def connect_db():
    return sqlite3.connect("faq.db")

# 🌟 DB에서 질문에 대한 답변 가져오는 함수 (유사 질문도 포함!)
def get_response_from_db(prompt):
    conn = connect_db()
    cursor = conn.cursor()
    
    # 모든 키워드 가져오기
    cursor.execute("SELECT keyword FROM faq")
    keywords = [row[0] for row in cursor.fetchall()]
    
    # 사용자의 질문과 정확히 일치하는 답변 확인
    cursor.execute("SELECT response FROM faq WHERE keyword = ?", (prompt,))
    response = cursor.fetchone()
    
    if response:
        conn.close()
        return response[0]  # 정확한 키워드가 있으면 바로 반환
    
    #  유사한 키워드 찾기
    try:
        best_match, score = process.extractOne(prompt, keywords)
        
        # 유사 키워드가 75% 이상 일치하거나, 키워드 일부가 포함되면 해당 답변을 제공
        for keyword in keywords:
            if keyword in prompt or score > 75:
                cursor.execute("SELECT response FROM faq WHERE keyword = ?", (best_match,))
                suggested_response = cursor.fetchone()
                conn.close()
                if suggested_response:
                    return f"⚠️ 정확한 답변을 찾을 수 없어요.\n대신 '{best_match}' 관련 정보를 확인해보세요!\n\n **{best_match}에 대한 답변:**\n{suggested_response[0]}"

        conn.close()
        return "⚠️ 죄송해요! 해당 질문에 대한 답변을 찾을 수 없어요. "
    
    except ValueError:
        conn.close()
        return "유사한 답변을 찾을 수 없습니다."

# 🌟 새로운 질문 & 답변을 DB에 추가하는 함수
def add_faq_to_db(keyword, response):
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM faq WHERE keyword = ?", (keyword,))
    existing = cursor.fetchone()
    
    if existing:
        conn.close()
        return "⚠️ 이미 존재하는 질문입니다!"
    
    cursor.execute("INSERT INTO faq (keyword, response) VALUES (?, ?)", (keyword, response))
    conn.commit()
    conn.close()
    return "✅ 질문과 답변이 추가되었습니다!"

# 🌟 스타일 추가
st.markdown("""
    <style>
    body {
        background-color: #f7f9fc;
    }
    .chat-container {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .bot-msg {
        background-color: #EAEAEA;
        padding: 10px;
        border-radius: 10px;
        display: inline-block;
        max-width: 80%;
        color: #000000;
    }
    </style>
""", unsafe_allow_html=True)

# 🌟 타이틀 & 설명
st.title("🤖 구리시청 내부 민원 챗봇")
st.write("안녕하세요! 궁금한 점을 입력하면 챗봇이 답변을 찾아줄게요!")

# 🌟 사용자 입력 받기
user_input = st.text_input("💬 질문을 입력하세요:")

if user_input:
    response = get_response_from_db(user_input)
    response = convert_urls_to_links(response)  # ✅ URL 자동 변환 적용

    st.markdown(f"🤖 {response}", unsafe_allow_html=False)  # ✅ 마크다운으로 URL 변환 적용

# 🌟 사이드바 (FAQ 추가 기능)
st.sidebar.title("🔧 FAQ 관리")

st.sidebar.subheader("➕ 새로운 질문 추가")
new_keyword = st.sidebar.text_input("새로운 질문 (키워드)")
new_response = st.sidebar.text_area("답변 내용")

if st.sidebar.button("추가하기"):
    if new_keyword and new_response:
        result = add_faq_to_db(new_keyword, new_response)
        st.sidebar.success(result)
    else:
        st.sidebar.error("❌ 질문과 답변을 모두 입력해주세요!")
