import streamlit as st
import random
import os
import time
from gtts import gTTS
import re

# Настройка страницы
st.set_page_config(page_title="English Trainer PRO", page_icon="🎓")

def normalize(text):
    """Очистка текста для корректного сравнения."""
    text = text.lower().strip()
    replacements = {
        "i'm": "i am", "it's": "it is", "don't": "do not", 
        "doesn't": "does not", "can't": "cannot", "you're": "you are",
        "we're": "we are", "they're": "they are", "isn't": "is not", "aren't": "are not"
    }
    for short, full in replacements.items():
        text = text.replace(short, full)
    
    text = re.sub(r'[^\w\s]', '', text)
    
    # Игнорируем только 'some' (артикли проверяются строго)
    ignored_words = {'some'}
    words = text.split()
    filtered_words = [w for w in words if w not in ignored_words]
    
    synonyms = {"subway": "metro", "metro": "subway", "taxi": "cab", "cab": "taxi"}
    final_words = [synonyms.get(w, w) for w in filtered_words]
    
    return " ".join(final_words)

def speak(text):
    """Генерация и воспроизведение озвучки без использования параметра key."""
    try:
        clean_audio_text = text.split('/')[0].strip()
        tts = gTTS(text=clean_audio_text, lang='en')
        
        # Создаем уникальное имя файла через время и случайное число
        # Это гарантирует, что браузер (особенно на iOS) увидит "новый" файл
        ts = int(time.time() * 1000)
        filename = f"temp_{ts}_{random.randint(1, 9999)}.mp3"
        
        tts.save(filename)
        st.audio(filename, format="audio/mp3")
        
        # Небольшая пауза, чтобы файл успел подгрузиться в плеер перед удалением
        time.sleep(0.5) 
        if os.path.exists(filename):
            os.remove(filename)
            
    except Exception as e:
        st.error(f"Ошибка озвучки: {e}")

def load_data(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip().split(" - ") for line in f if " - " in line]

# --- ИНТЕРФЕЙС ---
modes = ["Слова", "Неправильные глаголы", "Предложения"]

if 'current_mode' not in st.session_state:
    st.session_state.current_mode = "Предложения"

st.sidebar.markdown("# 📚 Меню")
selected_mode = st.sidebar.selectbox("Выберите режим", modes, 
                                     index=modes.index(st.session_state.current_mode))

if selected_mode != st.session_state.current_mode:
    st.session_state.current_mode = selected_mode
    st.session_state.current_pair = None
    st.session_state.answered = False
    st.rerun()

if st.session_state.current_mode == "Неправильные глаголы":
    st.sidebar.markdown("---")
    st.sidebar.info("**Правила ввода:**\n\nНапишите все 3 формы через пробел. Если V2=V3, пишите только две.")

if 'score' not in st.session_state: st.session_state.score = 0
if 'current_pair' not in st.session_state: st.session_state.current_pair = None
if 'answered' not in st.session_state: st.session_state.answered = False

st.title("English Trainer PRO 🎓")
st.sidebar.write("---")
st.sidebar.title("🇬🇧 📖 ✍️")

file_map = {"Слова": "words.txt", "Неправильные глаголы": "verbs.txt", "Предложения": "sentences.txt"}
data = load_data(file_map[st.session_state.current_mode])

if data:
    if st.session_state.current_pair is None:
        st.session_state.current_pair = random.choice(data)

    eng, rus = st.session_state.current_pair
    st.subheader("Переведите на английский:")
    st.info(f"👉 {rus}")
    
    user_answer = st.text_input("Ваш ответ:", key=f"input_{eng}", disabled=st.session_state.answered).strip()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Проверить ✅") and not st.session_state.answered:
            st.session_state.answered = True
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
        else:
            st.error(f"Ошибка! Правильно было: {eng}")
        
        if st.button("Следующее задание ➡️"):
            st.session_state.current_pair = random.choice(data)
            st.session_state.answered = False
            st.rerun()

    st.sidebar.write(f"### Текущая серия: {st.session_state.score}")
else:
    st.warning("Файлы с данными не найдены.")

st.sidebar.markdown("---")
st.sidebar.markdown("### 👨‍💻 Автор проекта:\n**Р. Андрей**\n\nСпециально для тебя ❤️")
