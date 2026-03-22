import streamlit as st
import random
import os
import time
from gtts import gTTS
import base64
import re

st.set_page_config(page_title="English Trainer PRO", page_icon="🎓")

# 1. СЛОВАРЬ СИНОНИМОВ (можно дополнять через запятую)
SYNONYMS = {
    "subway": "metro",
    "metro": "subway",
    "taxi": "cab",
    "cab": "taxi",
    "pavement": "sidewalk",
    "sidewalk": "pavement",
    "autumn": "fall",
    "fall": "autumn",
    "film": "movie",
    "movie": "film"
}

def normalize(text):
    text = text.lower().strip()
    # Раскрываем сокращения
    replacements = {
        "i'm": "i am", "it's": "it is", "don't": "do not", 
        "doesn't": "does not", "can't": "cannot", "you're": "you are",
        "we're": "we are", "they're": "they are", "isn't": "is not", "aren't": "are not"
    }
    for short, full in replacements.items():
        text = text.replace(short, full)
    
    # Убираем пунктуацию
    text = re.sub(r'[^\w\s]', '', text)
    
    # ЗАМЕНА СИНОНИМОВ: разбиваем фразу на слова и проверяем каждое
    words = text.split()
    final_words = [SYNONYMS.get(w, w) for w in words]
    return " ".join(final_words)

def speak(text):
    tts = gTTS(text=text, lang='en')
    ts = int(time.time())
    filename = f"temp_{ts}.mp3"
    tts.save(filename)
    # Используем стандартный плеер для стабильности на Mac/iOS
    st.audio(filename, format="audio/mp3", autoplay=True)
    # Файл удалится сам при следующем запуске или очистке сервера

def load_data(file_path):
    if not os.path.exists(file_path): return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip().split(" - ") for line in f if " - " in line]

# --- ЛОГИКА ПЕРЕКЛЮЧЕНИЯ РЕЖИМОВ ---
if 'current_mode' not in st.session_state:
    st.session_state.current_mode = "Предложения"

selected_mode = st.sidebar.selectbox("Выберите режим", ["Слова", "Глаголы", "Предложения"], 
                                     index=["Слова", "Глаголы", "Предложения"].index(st.session_state.current_mode))

if selected_mode != st.session_state.current_mode:
    st.session_state.current_mode = selected_mode
    st.session_state.current_pair = None
    st.session_state.answered = False
    st.rerun()

if 'score' not in st.session_state: st.session_state.score = 0
if 'current_pair' not in st.session_state: st.session_state.current_pair = None
if 'answered' not in st.session_state: st.session_state.answered = False

st.title("English Trainer PRO 🎓")
files = {"Слова": "words.txt", "Глаголы": "verbs.txt", "Предложения": "sentences.txt"}
data = load_data(files[st.session_state.current_mode])

if data:
    if st.session_state.current_pair is None:
        st.session_state.current_pair = random.choice(data)

    eng, rus = st.session_state.current_pair
    st.subheader(f"Как переводится: **{rus}**?")
    
    # Генерация уникального ключа для поля ввода, чтобы оно очищалось
    user_answer = st.text_input("Ваш ответ:", key=f"ans_{eng}_{st.session_state.current_mode}", disabled=st.session_state.answered).strip()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Проверить ✅") and not st.session_state.answered:
            st.session_state.answered = True
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
            # Автоматическая озвучка при правильном ответе (по желанию)
            # speak(eng) 
        else:
            st.error(f"Ошибка! Правильно было: {eng}")
        
        if st.button("Следующее задание ➡️"):
            st.session_state.current_pair = random.choice(data)
            st.session_state.answered = False
            st.rerun()

    st.sidebar.write(f"### Текущая серия: {st.session_state.score}")
