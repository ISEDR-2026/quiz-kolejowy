import streamlit as st
from openpyxl import load_workbook
import random
import os

# Konfiguracja strony
st.set_page_config(page_title="Quiz Kolejowy", layout="wide")

# ===== STYLE CSS =====
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .card { background: #1c1f26; padding: 25px; border-radius: 15px; border: 1px solid #30363d; margin-bottom: 20px; }
    .question-number { color: #8b949e; font-size: 14px; margin-bottom: 10px; }
    .question-text { font-size: 22px; font-weight: bold; margin-bottom: 20px; color: #e6edf3; }
    .answer-box { padding: 15px; border-radius: 10px; margin: 10px 0; border: 1px solid #30363d; transition: 0.3s; }
    .correct { background-color: #238636 !important; border-color: #2ea043 !important; color: white; }
    .wrong { background-color: #da3633 !important; border-color: #f85149 !important; color: white; }
    .stButton>button { width: 100%; border-radius: 10px; padding: 10px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ===== WCZYTYWANIE DANYCH (ZABEZPIECZONE) =====
@st.cache_data
def load_quiz_data(file_path):
    if not os.path.exists(file_path):
        return []
    
    wb = load_workbook(file_path, data_only=True)
    ws = wb.active
    loaded_questions = []

    # Iterujemy od 5 wiersza (zgodnie z Twoim plikiem)
    for row in ws.iter_rows(min_row=5):
        # Pobieramy wartości bezpiecznie do zmiennych lokalnych
        q_id = row[0].value
        q_text = row[1].value
        ans_a = row[2].value
        ans_b = row[3].value
        ans_c = row[4].value
        correct_val = row[5].value

        # Pomijamy wiersz tylko jeśli treść pytania jest pusta
        if not q_text:
            continue

        # Tworzymy słownik dla konkretnego wiersza - to gwarantuje spójność
        loaded_questions.append({
            "id": q_id,
            "question": q_text,
            "options": {
                "a": ans_a,
                "b": ans_b,
                "c": ans_c
            },
            "correct": str(correct_val).lower().strip() if correct_val else "a"
        })
    
    return loaded_questions

# ===== INICJALIZACJA SESJI =====
if 'initialized' not in st.session_state:
    raw_data = load_quiz_data("quiz.xlsx")
    if raw_data:
        random.shuffle(raw_data)  # Mieszamy raz na całą sesję
        st.session_state.questions = raw_data
    else:
        st.session_state.questions = []
    
    st.session_state.current_idx = 0
    st.session_state.score = 0
    st.session_state.answered = False
    st.session_state.last_result = None
    st.session_state.initialized = True

# ===== LOGIKA QUIZU =====
def next_question():
    st.session_state.current_idx += 1
    st.session_state.answered = False
    st.session_state.last_result = None

def handle_answer(choice, correct_choice):
    st.session_state.answered = True
    if choice == correct_choice:
        st.session_state.score += 1
        st.session_state.last_result = "correct"
    else:
        st.session_state.last_result = "wrong"

# ===== INTERFEJS UŻYTKOWNIKA =====
st.title("🚂 System Szkoleniowy PKP PLK")

if not st.session_state.questions:
    st.error("Nie znaleziono pytań w pliku quiz.xlsx lub plik jest pusty.")
elif st.session_state.current_idx >= len(st.session_state.questions):
    st.balloons()
    st.success(f"Koniec quizu! Twój wynik: {st.session_state.score} / {len(st.session_state.questions)}")
    if st.button("Zacznij od nowa"):
        del st.session_state.initialized
        st.rerun()
else:
    # Pobieramy bieżące pytanie
    q = st.session_state.questions[st.session_state.current_idx]
    
    # Wyświetlanie postępu
    progress = (st.session_state.current_idx) / len(st.session_state.questions)
    st.progress(progress)
    
    # Karta pytania
    st.markdown(f"""
    <div class="card">
        <div class="question-number">Pytanie nr źródłowe: {q['id']} ({st.session_state.current_idx + 1} z {len(st.session_state.questions)})</div>
        <div class="question-text">{q['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Odpowiedzi
    if not st.session_state.answered:
        # Wyświetlamy przyciski do wyboru
        for key, text in q['options'].items():
            if text: # Wyświetl tylko jeśli odpowiedź nie jest pusta
                if st.button(f"{key.upper()}: {text}", key=f"btn_{key}"):
                    handle_answer(key, q['correct'])
                    st.rerun()
    else:
        # Tryb po udzieleniu odpowiedzi - pokazujemy co było dobrze
        for key, text in q['options'].items():
            if text:
                css_class = "answer-box"
                if key == q['correct']:
                    css_class += " correct"
                elif key == st.session_state.get('user_choice') or (st.session_state.last_result == "wrong" and key != q['correct']):
                    # Tutaj logika kolorowania błędnej odpowiedzi użytkownika (uproszczona dla czytelności)
                    pass 
                
                # Renderowanie wyniku
                st.markdown(f'<div class="{css_class}">{key.upper()}: {text}</div>', unsafe_allow_html=True)
        
        if st.session_state.last_result == "correct":
            st.success("Dobra odpowiedź!")
        else:
            st.error(f"Błąd! Poprawna odpowiedź to: {q['correct'].upper()}")

        if st.button("Następne pytanie ➡"):
            next_question()
            st.rerun()

# Stopka z wynikiem
st.sidebar.metric("Twój wynik", f"{st.session_state.score}")
st.sidebar.write(f"Postęp: {st.session_state.current_idx + 1} / {len(st.session_state.questions)}")
