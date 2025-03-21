import streamlit as st
import sqlite3
from rapidfuzz import process  # 문자열 유사도 비교 라이브러리
import re
import os

# ✅ DB 경로 강제 지정
DB_PATH = r"C:\Users\user\Desktop\챗봇 프로젝트\faq.db"

# 🌟 Streamlit 페이지 설정
st.set_page_config(
    page_title="구리시청 내부 민원 챗봇",
    page_icon="🤖",
    layout="centered"
)

# ✅ 현재 사용 중인 DB 경로 출력
st.write("📂 사용 중인 DB 경로:", DB_PATH)

# 🌟 DB 연결 함수 (경로 강제 지정)
def connect_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# ✅ `faq` 테이블이 존재하는지 확인 후 없으면 생성
def initialize_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT UNIQUE,
            response TEXT
        )
    """)
    conn.commit()
    conn.close()

    # 🔥 `faq.db`가 올바르게 설정되었는지 확인하고 테이블 초기화
initialize_db()


# ✅ 현재 DB에 저장된 데이터 가져오기
conn = connect_db()
cursor = conn.cursor()
cursor.execute("SELECT * FROM faq")  
data = cursor.fetchall()  # 🔥 `data` 변수를 여기에 정의!
conn.close()

if data:
    st.write("📂 현재 DB에 저장된 데이터:", data)
else:
    st.write("📂 현재 DB에 저장된 데이터가 없습니다.")

def get_questions():
    conn = connect_db()  # ✅ 올바른 들여쓰기
    cursor = conn.cursor()
    cursor.execute("SELECT keyword FROM faq")
    questions = [row[0] for row in cursor.fetchall()]
    conn.close()
    return questions  # ✅ 들여쓰기 문제 해결!

st.write("📂 현재 DB에 저장된 데이터:", data)  # ✅ 추가한 질문이 보이면 정상!

# ✅ 챗봇에서 불러온 질문 목록 확인
questions = get_questions()
st.write("📂 챗봇 페이지에서 불러온 질문 목록:", questions)  # ✅ 이거 확인하기!

def convert_urls_to_links(text):
    url_pattern = r"(https?://\S+)"
    return re.sub(url_pattern, r'[\1](\1)', text)  # 마크다운 링크로 변환



# 🌟 DB 연결 함수
def connect_db():
    db_path = r"C:\Users\user\Desktop\챗봇 프로젝트\faq.db"  # ✅ DB 경로 강제 지정!
    return sqlite3.connect(db_path, check_same_thread=False)

# 🌟 DB에서 질문에 대한 답변 가져오는 함수 (유사 질문도 포함!)
def get_response_from_db(prompt):
    conn = connect_db()
    cursor = conn.cursor()

    # ✅ 모든 키워드 가져오기
    cursor.execute("SELECT keyword FROM faq")
    keywords = [row[0] for row in cursor.fetchall()]

    # 🔍 디버깅용 - 현재 키워드 목록 출력
    st.write("📂 DB에서 불러온 키워드 목록:", keywords)

    # ✅ 사용자의 질문과 정확히 일치하는 답변 확인
    cursor.execute("SELECT response FROM faq WHERE keyword = ?", (prompt,))
    response = cursor.fetchone()
    
    if response:
        conn.close()
        return response[0]  # 정확한 키워드가 있으면 바로 반환

    # ✅ 유사한 키워드 5개 찾기
    if keywords:
        matches = process.extract(prompt, keywords, limit=5)  # 🔥 최대 5개의 유사 키워드 반환

        # 🔍 유사도 검사 출력 (디버깅용)
        st.write(f"🔍 유사도 검사 결과: {matches}")

        result_text = "⚠️ 정확한 답변을 찾을 수 없어요.\n\n"
        found = False  # 하나라도 찾았는지 확인

        for best_match, score, _ in matches:
            if score > 75:  # 🔥 유사도가 75% 이상인 질문만 출력
                cursor.execute("SELECT response FROM faq WHERE keyword = ?", (best_match,))
                suggested_response = cursor.fetchone()
                
                if suggested_response:
                    result_text += f"**{best_match}에 대한 답변:**\n{suggested_response[0]}\n\n"
                    found = True

        conn.close()

        if found:
            return result_text
        else:
            return "⚠️ 죄송해요! 해당 질문에 대한 답변을 찾을 수 없어요."

    conn.close()
    return "⚠️ 죄송해요! 해당 질문에 대한 답변을 찾을 수 없어요."

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
    conn.commit()  # ✅ 반드시 있어야 함!
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
