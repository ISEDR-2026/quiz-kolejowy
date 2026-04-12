import streamlit as st
from openpyxl import load_workbook
import random

HASLO = "316b"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Dostęp do quizu")
    password = st.text_input("Podaj hasło:", type="password")

    if st.button("Wejdź"):
        if password == HASLO:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("❌ Niepoprawne hasło")

    st.stop()

# ===== Wczytanie danych =====
wb = load_workbook("quiz.xlsx")
ws = wb.active

questions = []

for row in ws.iter_rows(min_row=5):
    nr = row[0].value
    q = row[1].value
    a = row[2].value
    b = row[3].value
    c = row[4].value
    correct = row[5].value

    if not q or not correct:
        continue

    questions.append({
        "nr": int(nr),
        "q": q,
        "answers": {"a": a, "b": b, "c": c},
        "correct": correct.lower()
    })

# ===== SESSION =====
if "index" not in st.session_state:
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.started = False
    st.session_state.selected = []
    st.session_state.mode = "learn"
    st.session_state.answered = False
    st.session_state.last_choice = None

# ===== 🔥 NOWY NAGŁÓWEK =====
st.markdown("""
<h1 style='text-align:center; color:red;'>
Baza pytań sprawdzających wiedzę na stanowisku
</h1>
<h2 style='text-align:center; color:red;'>
Dyżurny Ruchu
</h2>
<h4 style='text-align:center; color:#1f77b4; margin-top:20px;'>
Warszawa 2025 r.
</h4>
""", unsafe_allow_html=True)

# ===== START =====
if not st.session_state.started:

    mode = st.radio("Tryb:", ["Nauka", "Egzamin"])

    if mode == "Nauka":

        option = st.selectbox(
            "Tryb pytań:",
            ["10", "25", "Od pytania"]
        )

        start_q = 1

        if option == "Od pytania":
            start_q = st.number_input(
                "Od którego pytania zacząć?",
                min_value=1,
                max_value=len(questions),
                value=1
            )

    else:
        st.info(f"Liczba pytań: {len(questions)} | Czas: 30 min")

    if st.button("Start"):

        if mode == "Nauka":

            if option == "10":
                random.shuffle(questions)
                selected = questions[:10]

            elif option == "25":
                random.shuffle(questions)
                selected = questions[:25]

            elif option == "Od pytania":
                selected = [q for q in questions if q["nr"] >= start_q]

        else:
            random.shuffle(questions)
            selected = questions

        st.session_state.selected = selected
        st.session_state.started = True
        st.session_state.mode = "learn" if mode == "Nauka" else "exam"
        st.session_state.index = 0
        st.session_state.score = 0
        st.session_state.answered = False
        st.rerun()

# ===== QUIZ =====
else:
    q_list = st.session_state.selected
    i = st.session_state.index

    if i >= len(q_list):

        percent = int((st.session_state.score / len(q_list)) * 100)

        st.success(f"Wynik: {st.session_state.score}/{len(q_list)} ({percent}%)")

        if st.button("Restart"):
            st.session_state.clear()
            st.rerun()

    else:
        q = q_list[i]

        st.markdown(
            f"""
            <div style='text-align:center;'>
                <div style='font-size:18px;color:#aaa;'>Pytanie {q['nr']}</div>
                <div style='font-size:28px;font-weight:bold;margin-top:10px;'>
                    {q['q']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        choice = st.radio(
            "Wybierz odpowiedź:",
            list(q["answers"].keys()),
            format_func=lambda x: f"{x}) {q['answers'][x]}",
            key=f"q_{i}"
        )

        if not st.session_state.answered:
            if st.button("Zatwierdź"):
                st.session_state.answered = True
                st.session_state.last_choice = choice

                if choice == q["correct"]:
                    st.session_state.score += 1

                st.rerun()

        else:
            correct = q["correct"]
            selected = st.session_state.last_choice

            if st.session_state.mode == "learn":

                for key, text in q["answers"].items():

                    if key == correct:
                        st.markdown(f"<div style='background:#1e7e34;padding:10px;border-radius:8px;color:white;margin-bottom:5px;'>{key}) {text}</div>", unsafe_allow_html=True)

                    elif key == selected:
                        st.markdown(f"<div style='background:#c82333;padding:10px;border-radius:8px;color:white;margin-bottom:5px;'>{key}) {text}</div>", unsafe_allow_html=True)

                    else:
                        st.markdown(f"<div style='background:#333;padding:10px;border-radius:8px;color:white;margin-bottom:5px;'>{key}) {text}</div>", unsafe_allow_html=True)

            if st.button("Następne"):
                st.session_state.index += 1
                st.session_state.answered = False
                st.rerun()
