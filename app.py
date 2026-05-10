import streamlit as st
from openpyxl import load_workbook
import random
import os
import time

# Konfiguracja strony - zgodnie z Twoim oryginałem
st.set_page_config(layout="wide", page_title="Quiz Kolejowy")

# ===== TWOJE ORYGINALNE STYLE (1:1) =====
st.markdown("""
<style>
.stApp { background-color: #0e1117; color: white; }
.card { background:#1c1f26; padding:20px; border-radius:15px; margin-bottom:20px; }
.question-number { font-size:14px; color:gray; margin-bottom:5px; }
.question-text { font-size:20px; font-weight:bold; }
.answer { padding:10px; border-radius:10px; margin:5px 0; background:#2a2e38; }
.correct { background:#2ecc71 !important; color:white; }
.wrong { background:#e74c3c !important; color:white; }
.login-box { background:#1c1f26; padding:40px; border-radius:20px; border:1px solid #30363d; }
div[role="radiogroup"] > label { font-size:18px !important; padding:10px !important; color: white; }
button[kind="secondary"], button[kind="primary"] { font-size:18px !important; padding:10px 20px !important; border-radius:10px !important; }
</style>
""", unsafe_allow_html=True)

# ===== POPRAWIONA LOGIKA WCZYTYWANIA (ZABEZPIECZENIE PRZED ROZJAZDEM) =====
@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        return []
    
    # data_only=True gwarantuje, że pobieramy tekst, a nie formuły
    wb = load_workbook(file_path, data_only=True)
    ws = wb.active
    all_q = []
    
    for row in ws.iter_rows(min_row=5):
        nr = row[0].value
        q_text = row[1].value
        if not q_text:
            continue
            
        # Kluczowa zmiana: Pakujemy wszystko z JEDNEGO wiersza do JEDNEGO obiektu
        # To gwarantuje, że odpowiedzi zawsze będą przypisane do właściwego pytania
        options = [
            ("a", row[2].value),
            ("b", row[3].value),
            ("c", row[4].value)
        ]
        # Usuwamy puste opcje, jeśli występują
        options = [opt for opt in options if opt[1] is not None]
        
        all_q.append({
            "nr": nr,
            "q": q_text,
            "options": options,
            "correct": str(row[5].value).lower().strip() if row[5].value else "a",
            "img": row[6].value if len(row) > 6 else None,
            "section": row[7].value if len(row) > 7 else "Ogólne"
        })
    return all_q

# ===== ZARZĄDZANIE STANEM SESJI =====
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False

# ===== EKRAN LOGOWANIA (WIZUALNIE 1:1) =====
if not st.session_state.logged_in:
    empty1, col_login, empty2 = st.columns([1, 2, 1])
    with col_login:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.title("🚂 System Szkoleniowy")
        user = st.text_input("Użytkownik", placeholder="Wpisz swoje imię...")
        if st.button("Zaloguj", use_container_width=True):
            if user:
                st.session_state.user = user
                st.session_state.logged_in = True
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ===== MENU WYBORU (WIZUALNIE 1:1) =====
elif not st.session_state.quiz_started:
    st.title(f"Witaj, {st.session_state.user}!")
    
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Ustawienia Quizu")
    
    questions_data = load_data("quiz.xlsx")
    sections = sorted(list(set([q["section"] for q in questions_data if q["section"]])))
    
    selected_section = st.selectbox("Wybierz zakres (instrukcję):", ["Wszystkie"] + sections)
    num_q = st.radio("Liczba pytań:", [10, 25, 50, "Wszystkie"], horizontal=True)
    
    if st.button("Rozpocznij Naukę", use_container_width=True):
        # Filtrowanie
        filtered = questions_data
        if selected_section != "Wszystkie":
            filtered = [q for q in questions_data if q["section"] == selected_section]
        
        if filtered:
            random.shuffle(filtered)
            if num_q != "Wszystkie":
                filtered = filtered[:int(num_q)]
            
            # Przygotowanie pytań do sesji (mieszanie odpowiedzi RAZ na początku)
            for item in filtered:
                random.shuffle(item["options"]) # Mieszamy kolejność a, b, c raz
            
            st.session_state.questions = filtered
            st.session_state.index = 0
            st.session_state.score = 0
            st.session_state.answered = False
            st.session_state.quiz_started = True
            st.session_state.answers_log = []
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ===== GŁÓWNY MODUŁ QUIZU (WIZUALNIE 1:1) =====
else:
    if st.session_state.index < len(st.session_state.questions):
        q = st.session_state.questions[st.session_state.index]
        
        # Sidebar ze statystykami
        st.sidebar.title("Postęp")
        st.sidebar.write(f"Użytkownik: **{st.session_state.user}**")
        st.sidebar.metric("Wynik", f"{st.session_state.score}")
        st.sidebar.write(f"Pytanie: {st.session_state.index + 1} / {len(st.session_state.questions)}")
        
        if st.sidebar.button("Zakończ i wróć"):
            st.session_state.quiz_started = False
            st.rerun()

        # Karta pytania
        st.markdown(f"""
        <div class="card">
            <div class="question-number">Pytanie źródłowe nr: {q['nr']}</div>
            <div class="question-text">{q['q']}</div>
            <div style="color: gray; font-size: 12px; margin-top: 10px;">Dział: {q['section']}</div>
        </div>
        """, unsafe_allow_html=True)

        if q['img']:
            st.image(q['img'], use_column_width=True)

        # Logika wyboru odpowiedzi
        # options_map łączy tekst z oryginalnym kluczem (a, b, lub c)
        options_map = {f"{opt[1]}": opt[0] for opt in q['options']}
        
        if not st.session_state.answered:
            # Używamy st.radio bez formularza, ale z przyciskiem "Zatwierdź", jak w oryginale
            choice_text = st.radio("Wybierz odpowiedź:", list(options_map.keys()), index=None)
            
            if st.button("Zatwierdź", type="primary"):
                if choice_text:
                    user_choice = options_map[choice_text]
                    st.session_state.last_choice = user_choice
                    st.session_state.answered = True
                    
                    is_correct = (user_choice == q['correct'])
                    if is_correct:
                        st.session_state.score += 1
                    
                    st.session_state.answers_log.append({
                        "nr": q['nr'],
                        "is_correct": is_correct
                    })
                    st.rerun()
                else:
                    st.warning("Proszę zaznaczyć odpowiedź!")
        else:
            # Widok po zatwierdzeniu - kolory 1:1 z Twoim stylem
            for opt_letter, opt_text in q['options']:
                cls = "answer"
                if opt_letter == q['correct']:
                    cls += " correct"
                elif opt_letter == st.session_state.last_choice:
                    cls += " wrong"
                
                st.markdown(f"<div class='{cls}'>{opt_text}</div>", unsafe_allow_html=True)

            if st.button("➡ Dalej"):
                st.session_state.index += 1
                st.session_state.answered = False
                st.rerun()

    else:
        # PODSUMOWANIE (WIZUALNIE 1:1)
        st.balloons()
        st.markdown("<div class='card' style='text-align:center;'>", unsafe_allow_html=True)
        st.title("Koniec Quizu!")
        st.header(f"Twój wynik: {st.session_state.score} / {len(st.session_state.questions)}")
        
        # Małe podsumowanie błędów
        wrongs = [str(a['nr']) for a in st.session_state.answers_log if not a['is_correct']]
        if wrongs:
            st.write(f"Pytania z błędami: {', '.join(wrongs)}")
            
        if st.button("Wróć do menu głównego"):
            st.session_state.quiz_started = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
