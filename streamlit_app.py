import streamlit as st
from openai import OpenAI

# 페이지 설정
st.set_page_config(page_title="데일리 룩 추천 챗봇", page_icon="👔", layout="centered")

# 제목과 설명
st.title("👔 데일리 룩 추천 챗봇")
st.write(
    "성별, 오늘의 날씨, 그리고 기분을 알려주시면 "
    "당신에게 딱 맞는 데일리 룩을 추천해드립니다! 😊"
)

# secrets.toml에서 API 키 로드
try:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
except Exception as e:
    st.error("⚠️ API 키를 찾을 수 없습니다. .streamlit/secrets.toml 파일을 확인해주세요.")
    st.stop()

# OpenAI 클라이언트 생성
client = OpenAI(api_key=openai_api_key)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
    # 시스템 프롬프트 추가
    st.session_state.messages.append({
        "role": "system",
        "content": """당신은 패션 전문가이자 친근한 데일리 룩 추천 챗봇입니다. 
사용자의 성별, 오늘의 날씨, 그리고 기분을 고려하여 적절한 데일리 룩을 추천해주세요.
추천할 때는 다음 사항들을 포함해주세요:
1. 상의, 하의, 신발 등 구체적인 아이템
2. 색상 조합
3. 액세서리나 소품 제안
4. 날씨에 맞는 소재나 레이어링 팁
5. 기분에 어울리는 스타일링 제안

대화는 친근하고 자연스럽게 진행하며, 추가 질문이나 조언을 구하면 성심껏 답변해주세요."""
    })

if "user_info_collected" not in st.session_state:
    st.session_state.user_info_collected = False

# 사이드바에 사용자 정보 입력
with st.sidebar:
    st.header("👤 사용자 정보")
    
    gender = st.selectbox(
        "성별을 선택해주세요",
        ["선택 안 함", "남성", "여성", "기타"],
        key="gender"
    )
    
    weather = st.selectbox(
        "오늘의 날씨는 어떤가요?",
        ["선택 안 함", "맑음 ☀️", "흐림 ☁️", "비 🌧️", "눈 ❄️", "추움 🥶", "더움 🥵"],
        key="weather"
    )
    
    mood = st.text_input(
        "오늘의 기분을 알려주세요",
        placeholder="예: 상쾌해요, 피곤해요, 설레요...",
        key="mood"
    )
    
    if st.button("정보 제출하기", type="primary"):
        if gender != "선택 안 함" and weather != "선택 안 함" and mood:
            user_info = f"성별: {gender}, 날씨: {weather}, 기분: {mood}"
            # 사용자 정보를 메시지로 추가
            st.session_state.messages.append({
                "role": "user",
                "content": f"안녕하세요! 저는 {gender}이고, 오늘 날씨는 {weather}이며, 기분은 {mood}입니다. 오늘의 데일리 룩을 추천해주실 수 있나요?"
            })
            st.session_state.user_info_collected = True
            st.rerun()
        else:
            st.warning("모든 정보를 입력해주세요!")
    
    if st.button("대화 초기화"):
        st.session_state.messages = [st.session_state.messages[0]]  # 시스템 메시지만 유지
        st.session_state.user_info_collected = False
        st.rerun()

# 채팅 메시지 표시 (시스템 메시지 제외)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 사용자 정보가 제출된 후 초기 추천 생성
if st.session_state.user_info_collected and len(st.session_state.messages) == 2:
    with st.chat_message("assistant"):
        with st.spinner("데일리 룩을 추천하고 있습니다..."):
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
                stream=True,
            )
            response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})

# 채팅 입력
if prompt := st.chat_input("추가로 궁금한 점이 있으신가요?"):
    # 사용자 메시지 저장 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # AI 응답 생성
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages,
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
