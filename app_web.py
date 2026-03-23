import streamlit as st
import random
import os
import time
from gtts import gTTS
import re

st.set_page_config(page_title="English Trainer PRO", page_icon="🎓")

def normalize(text):
    text = text.lower().strip()
    # 1. Раскрываем сокращения
    replacements = {
        "i'm": "i am", "it's": "it is", "don't": "do not", 
        "doesn't": "does not", "can't": "cannot", "you're": "you are",
        "we're": "we are", "they're": "they are", "isn't": "is not", "aren't": "are not"
    }
    for short, full in replacements.items():
        text = text.replace(short, full)
    
    # 2. Убираем пунктуацию
    text = re.sub(r'[^\w\s]', '', text)
    
    # 3. ИГНОРИРУЕМ ТОЛЬКО 'some' (артикли теперь ПРОВЕРЯЮТСЯ)
    ignored_words = {'some'}
    words = text.split()
    filtered_words = [w for w in words if w not in ignored_words]
    
    # 4. ПРОВЕРКА СИНОНИМОВ (метро/сабвей)
    synonyms = {"subway": "metro", "metro": "subway", "taxi": "cab", "cab": "taxi"}
    final_words = [synonyms.get(w, w) for w in filtered_words]
    
    return " ".join(final_words)

def speak(text):
    # Озвучиваем только первый вариант (до знака /)
    clean_audio_text = text.split('/')[0].strip()
    tts = gTTS(text=clean_audio_text, lang='en')
    ts = int(time.time())
    filename = f"temp_{ts}.mp3"
    tts.save(filename)
    st.audio(filename, format="audio/mp3", autoplay=True)

def load_data(file_path):
    if not os.path.exists(file_path): return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip().split(" - ") for line in f if " - " in line]

# --- ИНТЕРФЕЙС ---
if 'current_mode' not in st.session_state:
    st.session_state.current_mode = "Предложения"

st.sidebar.markdown("# 📚 Меню")
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
st.sidebar.write("---")
st.sidebar.title("🇬🇧 📖 ✍️")

data = load_data({"Слова": "words.txt", "Глаголы": "verbs.txt", "Предложения": "sentences.txt"}[st.session_state.current_mode])

if data:
    if st.session_state.current_pair is None:
        st.session_state.current_pair = random.choice(data)

    eng, rus = st.session_state.current_pair
    st.subheader(f"Переведите на английский:")
    st.info(f"👉 {rus}")
    
    user_answer = st.text_input("Ваш ответ:", key=f"ans_{eng}", disabled=st.session_state.answered).strip()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Проверить ✅") and not st.session_state.answered:
            st.session_state.answered = True
            # Разделяем варианты по слэшу и проверяем каждый
            correct_options = [opt.strip() for opt in eng.split('/')]
            is_correct = any(normalize(user_answer) == normalize(opt) for opt in correct_options)
            
            if is_correct:
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
            speak(eng)
        else:
            st.error(f"Ошибка! Правильно было: {eng}")
        
        if st.button("Следующее задание ➡️"):
            st.session_state.current_pair = random.choice(data)
            st.session_state.answered = False
            st.rerun()

    st.sidebar.write(f"### Текущая серия: {st.session_state.score}")

st.sidebar.markdown("---")
st.sidebar.markdown("### 👨‍💻 Автор проекта:")
st.sidebar.subheader("Р. Андрей")
st.sidebar.write("Специально для тебя ❤️")
