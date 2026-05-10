import streamlit as st
from openpyxl import load_workbook
import random
import os

# Konfiguracja strony
st.set_page_config(page_title="Quiz Kolejowy", layout="wide")

# ===== TWOJE ORGINALNE STYLE CSS =====
st.markdown("""
<style>
.stApp { background-color: #0e1117; color: white; }
.card { background: #1c1f26; padding: 25px; border-radius: 15px; border: 1px solid #30363d; margin-bottom: 20px; }
.question-number { color: #8b949e; font-size: 14px; margin-bottom: 5px; }
.question-text { font-size: 22px; font-weight: bold; margin-bottom: 20px; color: #e6edf3; }
.answer { padding: 15px; border-radius: 10px; margin: 10px 0; background: #2a2e38; border: 1px solid #30363d; }
.correct { background: #238636 !important; border-color: #2ea043 !important; color: white; }
.wrong { background: #da3633 !important; border-color: #f85149 !important; color: white; }
div[role="radiogroup"] > label { background: #1c1f26; border: 1px solid #30363d; padding: 15px; border-radius: 10px; margin-bottom: 10px; color: white; }
</style>
""", unsafe_allow_html=True)

# ===== FUNKCJA WCZYTYWANIA DANYCH (Z CACHE) =====
@st.cache_data
def load_all_questions(file_path):
    if not os.path.exists(file_path):
        return []
    
    wb = load_workbook(file_path, data_only=True)
    ws = wb.active
    data = []
    
    # Czytamy od 5 wiersza
    for row in ws.iter_rows(min_row=5):
        q_nr = row[0].value
        q_txt = row[1].value
        if not q_txt: continue
        
        # Tworzymy listę odpowiedzi i od razu ją mieszamy
        ans_options = [
            ("a", row[2].value),
            ("b", row[3].value),
            ("c", row[4].value)
        ]
        # Filtrujemy puste odpowiedzi
        ans_options = [opt for opt in ans_options if opt[1] is not None]
        
        # Zapamiętujemy która litera była poprawna (z kolumny F/index 5)
        correct_letter = str(row[5].value).lower().strip() if row[5].value else "a"
        
        data.append({
            "nr": q_nr,
            "q": q_txt,
            "options": ans_options, # Lista krotek (litera, tekst)
            "correct": correct_letter,
            "section": row[7].value if len(row) > 7 else ""
        })
    return data

# ===== INICJALIZACJA STANU SESJI =====
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False

# ===== EKRAN LOGOWANIA =====
if not st.session_state.logged_in:
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.markdown("<div class='card' style='text-align:center;'>", unsafe_allow_html=True)
        st.title("🚂 System Szkoleniowy")
        user = st.text_input("Użytkownik")
        if st.button("Zaloguj"):
            if user:
                st.session_state.user = user
                st.session_state.logged_in = True
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ===== EKRAN WYBORU QUIZU =====
elif not st.session_state.quiz_started:
    st.title(f"Witaj, {st.session_state.user}!")
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Wybierz tryb nauki")
        num_q = st.radio("Liczba pytań:", [10, 25, 50, "Wszystkie"], horizontal=True)
        
        if st.button("Rozpocznij Quiz"):
            all_data = load_all_questions("quiz.xlsx")
            if all_data:
                random.shuffle(all_data)
                if num_q != "Wszystkie":
                    all_data = all_data[:int(num_q)]
                
                st.session_state.questions = all_data
                st.session_state.index = 0
                st.session_state.score = 0
                st.session_state.answered = False
                st.session_state.quiz_started = True
                st.session_state.answers_log = []
                st.rerun()
            else:
                st.error("Błąd wczytywania pliku quiz.xlsx")
        st.markdown("</div>", unsafe_allow_html=True)

# ===== GŁÓWNY MODUŁ QUIZU =====
else:
    if st.session_state.index < len(st.session_state.questions):
        q = st.session_state.questions[st.session_state.index]
        
        # Pasek postępu
        progress = (st.session_state.index) / len(st.session_state.questions)
        st.progress(progress)
        
        st.markdown(f"""
        <div class="card">
            <div class="question-number">Pytanie {st.session_state.index + 1} z {len(st.session_state.questions)} (Nr sur.: {q['nr']})</div>
            <div class="question-text">{q['q']}</div>
            <div style="color: #8b949e; font-size: 12px;">Dział: {q['section']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Wyświetlanie odpowiedzi
        if not st.session_state.answered:
            # Używamy formularza, aby uniknąć przeładowania przed zaznaczeniem
            with st.form("quiz_form"):
                options_dict = {f"{opt[0].upper()}: {opt[1]}": opt[0] for opt in q['options']}
                choice_label = st.radio("Wybierz odpowiedź:", list(options_dict.keys()))
                submit = st.form_submit_button("Zatwierdź odpowiedź")
                
                if submit:
                    user_choice = options_dict[choice_label]
                    st.session_state.answered = True
                    st.session_state.last_choice = user_choice
                    if user_choice == q['correct']:
                        st.session_state.score += 1
                    
                    # Logowanie odpowiedzi
                    st.session_state.answers_log.append({
                        "nr": q['nr'],
                        "correct": user_choice == q['correct']
                    })
                    st.rerun()
        else:
            # Widok po udzieleniu odpowiedzi (kolory)
            for opt_letter, opt_text in q['options']:
                display_text = f"{opt_letter.upper()}: {opt_text}"
                css_class = "answer"
                
                if opt_letter == q['correct']:
                    css_class += " correct"
                elif opt_letter == st.session_state.last_choice:
                    css_class += " wrong"
                
                st.markdown(f'<div class="{css_class}">{display_text}</div>', unsafe_allow_html=True)

            if st.button("➡ Następne pytanie"):
                st.session_state.index += 1
                st.session_state.answered = False
                st.rerun()

    else:
        # PODSUMOWANIE
        st.balloons()
        st.markdown("<div class='card' style='text-align:center;'>", unsafe_allow_html=True)
        st.title("Koniec Quizu!")
        st.header(f"Twój wynik: {st.session_state.score} / {len(st.session_state.questions)}")
        
        if st.button("Wróć do menu"):
            st.session_state.quiz_started = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# Sidebar z informacjami
if st.session_state.quiz_started:
    st.sidebar.title("Statystyki")
    st.sidebar.write(f"Użytkownik: {st.session_state.user}")
    st.sidebar.metric("Wynik", f"{st.session_state.score}")
    if st.sidebar.button("Zakończ quiz"):
        st.session_state.quiz_started = False
        st.rerun()
