import streamlit as st

st.title("🔧 관리자 페이지")
st.write("여기서 기존 질문을 수정/삭제할 수 있어요!")

questions = ["질문1", "질문2", "질문3"]
selected_question = st.selectbox("수정할 질문을 선택하세요:", questions)

new_text = st.text_input("새로운 질문 내용:", selected_question)
if st.button("수정 완료"):
    st.success(f"'{selected_question}' → '{new_text}'로 수정되었습니다!")

if st.button("질문 삭제"):
    st.warning(f"'{selected_question}' 질문이 삭제되었습니다!")

st.markdown("[🤖 챗봇 화면으로 돌아가기](https://gurichatbotproject-wf5lhflb5xj8nviv6mthmn.streamlit.app/)")