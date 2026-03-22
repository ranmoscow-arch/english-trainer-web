import streamlit as st
import random
import os
import time
from gtts import gTTS
import base64
import re

# Настройка страницы с иконкой
st.set_page_config(page_title="English Trainer PRO", page_icon="🎓")

# Функция для нормализации текста (убираем пунктуацию и раскрываем сокращения)
def normalize(text):
    text = text.lower().strip()
    # Раскрываем основные сокращения для честной проверки
    replacements = {
        "i'm": "i am", "it's": "it is", "don't": "do not", 
        "doesn't": "does not", "can't": "cannot", "you're": "you are",
        "we're": "we are", "they're": "they are", "isn't": "is not", "aren't": "are not"
    }
    for short, full in replacements.items():
        text = text.replace(short, full)
    # Убираем всё, кроме букв и цифр
    return re.sub(r'[^\w\s]', '', text)

def speak(text):
    tts = gTTS(text=text, lang='en')
    ts = int(time.time())
    filename = f"temp_{ts}.mp3"
    tts.save(filename)
    # Используем нативный компонент Streamlit для надежности
    st.audio(filename, format="audio/mp3", autoplay=True)
    # В облаке файлы хранятся временно, поэтому удаление не критично
    # Но для порядка можно оставить, облако само очистит
    # os.remove(filename)

def load_data(file_path):
    if not os.path.exists(file_path): return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip().split(" - ") for line in f if " - " in line]

# --- ЛОГИКА ПЕРЕКЛЮЧЕНИЯ РЕЖИМОВ ---
if 'current_mode' not in st.session_state:
    st.session_state.current_mode = "Предложения"

# Сайдбар с выбором режима
selected_mode = st.sidebar.selectbox("Выберите режим", ["Слова", "Глаголы", "Предложения"], index=["Слова", "Глаголы", "Предложения"].index(st.session_state.current_mode))

# Если режим изменился в меню — сбрасываем текущее задание мгновенно
if selected_mode != st.session_state.current_mode:
    st.session_state.current_mode = selected_mode
    st.session_state.current_pair = None
    st.session_state.answered = False
    st.rerun()

# Инициализация переменных сессии
if 'score' not in st.session_state: st.session_state.score = 0
if 'current_pair' not in st.session_state: st.session_state.current_pair = None
if 'answered' not in st.session_state: st.session_state.answered = False

# Заголовок с иконкой
st.title("English Trainer PRO 🎓")
files = {"Слова": "words.txt", "Глаголы": "verbs.txt", "Предложения": "sentences.txt"}
data = load_data(files[st.session_state.current_mode])

if data:
    if st.session_state.current_pair is None:
        st.session_state.current_pair = random.choice(data)

    eng, rus = st.session_state.current_pair
    st.subheader(f"Как переводится: **{rus}**?")
    
    # Поле ввода с уникальным ключом для очистки
    user_answer = st.text_input("Ваш ответ:", key=f"ans_{eng}", disabled=st.session_state.answered).strip()

    col1, col2 = st.columns(2)
    with col1:
        check_btn = st.button("Проверить ✅")
        if check_btn and not st.session_state.answered:
            st.session_state.answered = True
            # Сравниваем нормализованные версии
            if normalize(user_answer) == normalize(eng):
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
            # Озвучиваем правильный ответ автоматически
            speak(eng)
        else:
            st.error(f"Ошибка! Правильно было: {eng}")
        
        if st.button("Следующее задание ➡️"):
            st.session_state.current_pair = random.choice(data)
            st.session_state.answered = False
            st.rerun()

    # Сайдбар со счетом
    st.sidebar.write(f"### Текущая серия: {st.session_state.score}")

# --- ВАША ПОДПИСЬ ---
st.sidebar.markdown("---") # Разделительная линия
st.sidebar.markdown("#### Разработано Р. Андреем")
st.sidebar.markdown("специально для тебя ❤️")
