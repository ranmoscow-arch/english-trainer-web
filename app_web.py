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
    
    # 3. Игнорируем только 'some' (артикли a, an, the проверяются строго)
    ignored_words = {'some'}
    words = text.split()
    filtered_words = [w for w in words if w not in ignored_words]
    
    # 4. Проверка базовых синонимов
    synonyms = {"subway": "metro", "metro": "subway", "taxi": "cab", "cab": "taxi"}
    final_words = [synonyms.get(w, w) for w in filtered_words]
    
    return " ".join(final_words)

def speak(text, key="default"):
    """Генерация и воспроизведение озвучки."""
    try:
        # Озвучиваем только первый вариант (до знака /)
        clean_audio_text = text.split('/')[0].strip()
        tts = gTTS(text=clean_audio_text, lang='en')
        ts = int(time.time())
        # Создаем уникальное имя файла
        filename = f"temp_{ts}_{random.randint(0, 1000)}.mp3"
        tts.save(filename)
        
        # Убираем параметр key из st.audio, так как ваша версия Streamlit его не поддерживает
        st.audio(filename, format="audio/mp3")
    except Exception as e:
        st.error(f"Ошибка озвучки: {e}")

# ... в блоке с кнопками ...

    with col2:
        if st.button("Прослушать 🔊"):
            speak(eng) # Просто вызываем без ключа

def load_data(file_path):
    """Загрузка строк из текстовых файлов."""
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip().split(" - ") for line in f if " - " in line]

# --- ИНИЦИАЛИЗАЦИЯ И МЕНЮ ---
modes = ["Слова", "Неправильные глаголы", "Предложения"]

if 'current_mode' not in st.session_state:
    st.session_state.current_mode = "Предложения"

st.sidebar.markdown("# 📚 Меню")
selected_mode = st.sidebar.selectbox("Выберите режим", modes, 
                                     index=modes.index(st.session_state.current_mode))

# Сброс состояния при смене режима
if selected_mode != st.session_state.current_mode:
    st.session_state.current_mode = selected_mode
    st.session_state.current_pair = None
    st.session_state.answered = False
    st.rerun()

# Правила ввода для неправильных глаголов
if st.session_state.current_mode == "Неправильные глаголы":
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **Правила ввода:**
    Напишите все 3 формы глагола через пробел. 
    Если V2 = V3, напишите только две формы.
    """)

if 'score' not in st.session_state: st.session_state.score = 0
if 'current_pair' not in st.session_state: st.session_state.current_pair = None
if 'answered' not in st.session_state: st.session_state.answered = False

st.title("English Trainer PRO 🎓")
st.sidebar.write("---")
st.sidebar.title("🇬🇧 📖 ✍️")

# Маппинг режимов на файлы
file_map = {
    "Слова": "words.txt", 
    "Неправильные глаголы": "verbs.txt", 
    "Предложения": "sentences.txt"
}

data = load_data(file_map[st.session_state.current_mode])

if data:
    if st.session_state.current_pair is None:
        st.session_state.current_pair = random.choice(data)

    eng, rus = st.session_state.current_pair
    st.subheader("Переведите на английский:")
    st.info(f"👉 {rus}")
    
    # Поле ввода
    user_answer = st.text_input("Ваш ответ:", key=f"input_{eng}", disabled=st.session_state.answered).strip()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Проверить ✅") and not st.session_state.answered:
            st.session_state.answered = True
            # Проверка всех вариантов, разделенных слэшем
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
            speak(eng, key="manual")

    # Отображение результата
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
    st.warning(f"Файл {file_map[st.session_state.current_mode]} не найден или пуст.")

st.sidebar.markdown("---")
st.sidebar.markdown("### 👨‍💻 Автор проекта:")
st.sidebar.subheader("Р. Андрей")
st.sidebar.write("Специально для тебя ❤️")
