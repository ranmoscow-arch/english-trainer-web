import streamlit as st
import random
import os
import time
from gtts import gTTS
import base64
import re

st.set_page_config(page_title="English Trainer PRO", page_icon="🎓")

# Функция для очистки текста от пунктуации для сравнения
def clean_text(text):
    return re.sub(r'[^\w\s]', '', text).lower().strip()

def speak(text):
    tts = gTTS(text=text, lang='en')
    # Добавляем уникальный маркер времени, чтобы браузер не кэшировал звук
    ts = int(time.time())
    filename = f"temp_{ts}.mp3"
    tts.save(filename)
    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        # autoplay="true" запустит звук сразу
        md = f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>'
        st.markdown(md, unsafe_allow_html=True)
    os.remove(filename)

def load_data(file_path):
    if not os.path.exists(file_path): return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip().split(" - ") for line in f if " - " in line]

if 'score' not in st.session_state: st.session_state.score = 0
if 'current_pair' not in st.session_state: st.session_state.current_pair = None
if 'answered' not in st.session_state: st.session_state.answered = False

st.title("English Trainer PRO 🎓")
mode = st.sidebar.selectbox("Режим", ["Слова", "Глаголы", "Предложения"])
files = {"Слова": "words.txt", "Глаголы": "verbs.txt", "Предложения": "sentences.txt"}
data = load_data(files[mode])

if data:
    if st.session_state.current_pair is None:
        st.session_state.current_pair = random.choice(data)

    eng, rus = st.session_state.current_pair
    st.subheader(f"Как переводится: **{rus}**?")
    
    user_answer = st.text_input("Ваш ответ:", key="ans", disabled=st.session_state.answered).strip()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Проверить ✅") and not st.session_state.answered:
            st.session_state.answered = True
            # Сравниваем "чистые" версии текстов без знаков препинания
            if clean_text(user_answer) == clean_text(eng):
                st.session_state.correct = True
                st.session_state.score += 1
            else:
                st.session_state.correct = False
                st.session_state.score = 0
            st.rerun()

    with col2:
        if st.button("Прослушать 🔊"):
            speak(eng)

    if st.session_state.answered:
        if st.session_state.correct:
            st.success(f"Правильно! 🎉 Оригинал: {eng}")
        else:
            st.error(f"Ошибка! Правильно было: {eng}")
        
        if st.button("Следующее задание ➡️"):
            st.session_state.current_pair = random.choice(data)
            st.session_state.answered = False
            st.rerun()

    st.sidebar.write(f"### Текущая серия: {st.session_state.score}")
