import streamlit as st
import random
import os
import time
from gtts import gTTS
import re
import base64

# Настройка страницы
st.set_page_config(page_title="English Trainer PRO", page_icon="🎓")

# --- СТИЛИЗАЦИЯ (КРУПНЫЙ ШРИФТ, ЯРКОСТЬ И ПЕРЕНОС СТРОК) ---
st.markdown("""
    <style>
    /* Поле ввода: крупный текст и яркость на iPhone */
    .stTextArea textarea {
        font-size: 22px !important;
        color: #31333F !important;
        -webkit-text-fill-color: #31333F !important;
        opacity: 1 !important;
    }
    
    /* Делаем поле ввода более заметным */
    .stTextArea [data-baseweb="textarea"] {
        background-color: #ffffff !important;
        border: 2px solid #e0e0e0 !important;
    }

    /* Увеличиваем шрифт заголовков заданий */
    .stSecondaryBlock {
        font-size: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

def normalize(text):
    """Улучшенная очистка текста: убирает точки и фиксирует апострофы iPhone."""
    if not text:
        return ""
        
    text = text.lower().strip()
    
    # Исправляем специфические апострофы iPhone и убираем точки
    text = text.replace('’', "'").replace('‘', "'")
    text = re.sub(r'[.,!?]', '', text)
    
    # Раскрываем сокращения
    replacements = {
        "i'm": "i am", "it's": "it is", "don't": "do not", 
        "doesn't": "does not", "can't": "cannot", "you're": "you are",
        "we're": "we are", "they're": "they are", "isn't": "is not", "aren't": "are not"
    }
    for short, full in replacements.items():
        text = text.replace(short, full)
    
    # Очистка от двойных пробелов и лишних символов
    text = re.sub(r'[^\w\s]', '', text)
    text = " ".join(text.split())
    
    # Синонимы
    synonyms = {"subway": "metro", "metro": "subway", "taxi": "cab", "cab": "taxi"}
    words = text.split()
    final_words = [synonyms.get(w, w) for w in words]
    
    return " ".join(final_words)

def speak(text):
    """Воспроизведение звука для iOS через Base64 (без ошибок)."""
    try:
        clean_audio_text = text.split('/')[0].strip()
        tts = gTTS(text=clean_audio_text, lang='en')
        filename = f"temp_audio_{random.randint(1, 1000)}.mp3"
        tts.save(filename)
        
        with open(filename, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            # Автоплей для iPhone
            md = f"""
                <audio autoplay="true">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                """
            st.markdown(md, unsafe_allow_html=True)
        os.remove(filename)
    except Exception as e:
        st.error(f"Ошибка озвучки: {e}")

def load_data(file_path):
    if not os.path.exists(file_path): return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip().split(" - ") for line in f if " - " in line]

# --- ОСНОВНАЯ ЛОГИКА ---
modes = ["Слова", "Неправильные глаголы", "Предложения"]
if 'current_mode' not in st.session_state: st.session_state.current_mode = "Предложения"

st.sidebar.markdown("# 📚 Меню")
selected_mode = st.sidebar.selectbox("Выберите режим", modes, index=modes.index(st.session_state.current_mode))

if selected_mode != st.session_state.current_mode:
    st.session_state.current_mode = selected_mode
    st.session_state.current_pair = None
    st.session_state.answered = False
    st.rerun()

# Правила только для глаголов
if st.session_state.current_mode == "Неправильные глаголы":
    st.sidebar.markdown("---")
    st.sidebar.info("Напишите 3 формы через пробел. Если V2 = V3, пишите только две.")

if 'score' not in st.session_state: st.session_state.score = 0
if 'current_pair' not in st.session_state: st.session_state.current_pair = None
if 'answered' not in st.session_state: st.session_state.answered = False

st.title("English Trainer PRO 🎓")

file_map = {"Слова": "words.txt", "Неправильные глаголы": "verbs.txt", "Предложения": "sentences.txt"}
data = load_data(file_map[st.session_state.current_mode])

if data:
    if st.session_state.current_pair is None:
        st.session_state.current_pair = random.choice(data)

    eng, rus = st.session_state.current_pair
    st.subheader("Переведите на английский:")
    st.info(f"👉 {rus}")
    
    # Используем TextArea для переноса строк и толщины
    user_answer = st.text_area(
        "Ваш ответ:", 
        key=f"input_{hash(eng)}", 
        disabled=st.session_state.answered, 
        placeholder="Введите перевод здесь...",
        height=100
    ).strip()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Проверить ✅") and not st.session_state.answered:
            st.session_state.answered = True
            correct_options = [opt.strip() for opt in eng.split('/')]
            is_correct = any(normalize(user_answer) == normalize(opt) for opt in correct_options)
            st.session_state.correct = is_correct
            if is_correct: st.session_state.score += 1
            else: st.session_state.score = 0
            st.rerun()

    with col2:
        if st.button("Прослушать 🔊"):
            speak(eng)

    if st.session_state.answered:
        if st.session_state.correct: st.success(f"Правильно! 🎉 {eng}")
        else: st.error(f"Ошибка! Правильно: {eng}")
        
        if st.button("Следующее задание ➡️"):
            st.session_state.current_pair = random.choice(data)
            st.session_state.answered = False
            st.rerun()

    st.sidebar.write(f"### Текущая серия: {st.session_state.score}")
else:
    st.warning("Файлы .txt не найдены в репозитории.")

# Подпись и сердечко
st.sidebar.markdown("---")
st.sidebar.markdown("### 👨‍💻 Автор проекта:")
st.sidebar.subheader("Р. Андрей")
st.sidebar.write("Специально для тебя ❤️")
