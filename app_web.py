import streamlit as st
import random
import os
from gtts import gTTS
import base64

# Настройка страницы
st.set_page_config(page_title="English Trainer PRO", page_icon="🎓")

# Функция для озвучки (генерирует аудио и встраивает его в HTML)
def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("temp.mp3")
    with open("temp.mp3", "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        st.markdown(md, unsafe_allow_html=True)
    os.remove("temp.mp3")

# Функция загрузки данных
def load_data(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if " - " in line]
        return [line.split(" - ") for line in lines]

# Инициализация состояния (чтобы данные не сбрасывались при нажатии кнопок)
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_pair' not in st.session_state:
    st.session_state.current_pair = None

# Интерфейс
st.title("English Trainer PRO 🎓")

mode = st.sidebar.selectbox("Выберите режим", ["Слова", "Глаголы", "Предложения"])
files = {"Слова": "words.txt", "Глаголы": "verbs.txt", "Предложения": "sentences.txt"}

data = load_data(files[mode])

if data:
    if st.session_state.current_pair is None:
        st.session_state.current_pair = random.choice(data)

    eng, rus = st.session_state.current_pair
    
    st.subheader(f"Как переводится: **{rus}**?")
    
    user_answer = st.text_input("Ваш ответ:", key="input_ans").strip().lower()

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Проверить"):
            if user_answer == eng.lower().strip():
                st.success("Правильно! 🎉")
                st.session_state.score += 1
                st.session_state.current_pair = random.choice(data)
                st.rerun()
            else:
                st.error(f"Ошибка. Правильно: {eng}")
                st.session_state.score = 0
                st.session_state.current_pair = random.choice(data)
    
    with col2:
        if st.button("Прослушать 🔊"):
            speak(eng)

    st.sidebar.write(f"### Текущая серия: {st.session_state.score}")
else:
    st.error(f"Файл {files[mode]} не найден или пуст.")