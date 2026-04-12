import streamlit as st
from openpyxl import load_workbook
import random

# ===== HASŁO =====
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

dzial = ws["C3"].value

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
        "nr": nr,
        "q": q,
        "answers": {"a": a, "b": b, "c": c},
        "correct": correct.lower()
    })

# ===== SESSION =====
if "index" not in st.session_state:
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.started = False
    st.session_state.mode = "learn"
    st.session_state.selected = []
    st.session_state.answered = False
    st.session_state.last_choice = None

# ===== START =====
st.title("🚂 Quiz kolejowy")

if not st.session_state.started:

    st.subheader(f"Dział: {dzial}")

    mode = st.radio("Tryb:", ["Nauka", "Egzamin"])

    if mode == "Nauka":
        count = st.selectbox("Liczba pytań:", [10, 25, "Wszystkie"])
    else:
        st.info(f"Liczba pytań: {len(questions)} | Czas: 30 min")
        count = "Wszystkie"

    if st.button("Start"):
        random.shuffle(questions)

        if count == "Wszystkie":
            st.session_state.selected = questions
        else:
            st.session_state.selected = questions[:int(count)]

        st.session_state.mode = "learn" if mode == "Nauka" else "exam"
        st.session_state.started = True
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

        if percent >= 80:
            st.success("ZALICZONE ✅")
        else:
            st.error("NIEZALICZONE ❌")

        if st.button("Restart"):
            st.session_state.clear()
            st.rerun()

    else:
        q = q_list[i]

        st.markdown(f"### Pytanie {q['nr']}")
        st.markdown(f"**{q['q']}**")

        # ===== WYBÓR =====
        choice = st.radio(
            "Wybierz odpowiedź:",
            list(q["answers"].keys()),
            format_func=lambda x: f"{x}) {q['answers'][x]}",
            key=f"q_{i}"
        )

        # ===== ZATWIERDZENIE =====
        if not st.session_state.answered:
            if st.button("Zatwierdź"):
                st.session_state.answered = True
                st.session_state.last_choice = choice

                if choice == q["correct"]:
                    st.session_state.score += 1

                st.rerun()

        # ===== WYNIK + PODŚWIETLENIE =====
        else:
            correct = q["correct"]
            selected = st.session_state.last_choice

            if st.session_state.mode == "learn":

                st.write("### Wynik:")

                for key, text in q["answers"].items():

                    if key == correct:
                        st.markdown(
                            f"<div style='background-color:#1e7e34;padding:10px;border-radius:8px;color:white;margin-bottom:5px;'>"
                            f"{key}) {text}</div>",
                            unsafe_allow_html=True
                        )

                    elif key == selected:
                        st.markdown(
                            f"<div style='background-color:#c82333;padding:10px;border-radius:8px;color:white;margin-bottom:5px;'>"
                            f"{key}) {text}</div>",
                            unsafe_allow_html=True
                        )

                    else:
                        st.markdown(
                            f"<div style='background-color:#333;padding:10px;border-radius:8px;color:white;margin-bottom:5px;'>"
                            f"{key}) {text}</div>",
                            unsafe_allow_html=True
                        )

                if selected == correct:
                    st.success("✔ Dobra odpowiedź")
                else:
                    st.error("❌ Zła odpowiedź")

            # ===== NASTĘPNE =====
            if st.button("Następne pytanie"):
                st.session_state.index += 1
                st.session_state.answered = False
                st.rerun()
