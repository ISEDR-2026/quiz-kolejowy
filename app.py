import streamlit as st
from openpyxl import load_workbook
import random
import time

HASLO = "316b"
CZAS_EGZAMIN = 30 * 60

# ===== LOGOWANIE =====
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Dostęp do quizu na dyżurnego ruchu")
    password = st.text_input("Podaj hasło:", type="password")

    if st.button("Wejdź"):
        if password == HASLO:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("❌ Niepoprawne hasło")
    st.stop()

# ===== DANE =====
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
    st.session_state.start_time = None
    st.session_state.answers_log = []

# ===== NAGŁÓWEK =====
st.markdown("""
<h2 style='text-align:center; color:red;'>
Baza pytań sprawdzających wiedzę na stanowisku Dyżurny Ruchu
</h2>
""", unsafe_allow_html=True)

# ===== START =====
if not st.session_state.started:

    mode = st.radio("Tryb:", ["Nauka", "Egzamin"])

    if mode == "Nauka":
        option = st.selectbox("Tryb pytań:", ["10", "25", "Od pytania"])

        start_q = 1
        if option == "Od pytania":
            start_q = st.number_input("Od którego pytania zacząć?", 1, len(questions), 1)

    else:
        st.info(f"Liczba pytań: 30 z {len(questions)} | Czas: 30 min")

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
            selected = random.sample(questions, min(30, len(questions)))
            st.session_state.start_time = time.time()

        st.session_state.selected = selected
        st.session_state.started = True
        st.session_state.mode = "learn" if mode == "Nauka" else "exam"
        st.session_state.index = 0
        st.session_state.score = 0
        st.session_state.answers_log = []
        st.rerun()

# ===== QUIZ =====
else:
    q_list = st.session_state.selected
    i = st.session_state.index

    # ===== TIMER (EGZAMIN) =====
    if st.session_state.mode == "exam":
        elapsed = int(time.time() - st.session_state.start_time)
        remaining = CZAS_EGZAMIN - elapsed

        if remaining <= 0:
            st.error("⏰ Czas minął!")
            st.session_state.index = len(q_list)

        mins = remaining // 60
        secs = remaining % 60

        st.markdown(
            f"<h3 style='text-align:center;'>⏳ {mins:02d}:{secs:02d} | Pytanie {i+1} z {len(q_list)}</h3>",
            unsafe_allow_html=True
        )

    # ===== KONIEC =====
    if i >= len(q_list):

        total = len(q_list)
        correct = st.session_state.score
        wrong = total - correct
        percent = int((correct / total) * 100)

        elapsed = int(time.time() - st.session_state.start_time) if st.session_state.start_time else 0
        mins = elapsed // 60
        secs = elapsed % 60

        st.markdown(f"""
        <div style='text-align:center; padding:20px; background:#111; border-radius:10px;'>
            <h2>Wynik: {correct} / {total} ({percent}%)</h2>
            <p>✔ Poprawne: {correct}</p>
            <p>❌ Błędne: {wrong}</p>
            <p>⏱ Czas: {mins} min {secs} s</p>
            <h3 style='color:{'lime' if percent>=80 else 'red'};'>
                {'ZALICZONE' if percent>=80 else 'NIEZALICZONE'}
            </h3>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("📊 Przegląd odpowiedzi")

        for item in st.session_state.answers_log:

            st.markdown(f"### Pytanie {item['nr']}")
            st.write(item["q"])

            for key, text in item["answers"].items():

                if key == item["correct_answer"]:
                    st.markdown(f"<div style='background:#1e7e34;color:white;padding:8px;border-radius:6px;'>{key}) {text}</div>", unsafe_allow_html=True)
                elif key == item["selected"]:
                    st.markdown(f"<div style='background:#c82333;color:white;padding:8px;border-radius:6px;'>{key}) {text}</div>", unsafe_allow_html=True)
                else:
                    st.write(f"{key}) {text}")

        if st.button("Restart"):
            st.session_state.clear()
            st.rerun()

    # ===== PYTANIE =====
    else:
        q = q_list[i]

        st.markdown(f"""
        <div style='text-align:center;'>
            <div style='font-size:18px;color:#aaa;'>Pytanie {q['nr']}</div>
            <div style='font-size:26px;font-weight:bold;margin-top:10px;'>{q['q']}</div>
        </div>
        """, unsafe_allow_html=True)

        choice = st.radio(
            "Wybierz odpowiedź:",
            list(q["answers"].keys()),
            format_func=lambda x: f"{x}) {q['answers'][x]}",
            key=f"q_{i}"
        )

        # ===== TRYB NAUKA (natychmiastowa odpowiedź) =====
        if st.session_state.mode == "learn":

            correct = q["correct"]

            for key, text in q["answers"].items():

                if key == correct:
                    st.markdown(f"<div style='background:#1e7e34;color:white;padding:8px;border-radius:6px;'>{key}) {text}</div>", unsafe_allow_html=True)

                elif key == choice:
                    st.markdown(f"<div style='background:#c82333;color:white;padding:8px;border-radius:6px;'>{key}) {text}</div>", unsafe_allow_html=True)

                else:
                    st.write(f"{key}) {text}")

            if st.button("Następne"):
                st.session_state.index += 1
                st.rerun()

        # ===== TRYB EGZAMIN =====
        else:
            if st.button("Zatwierdź"):

                is_correct = choice == q["correct"]

                if is_correct:
                    st.session_state.score += 1

                st.session_state.answers_log.append({
                    "nr": q["nr"],
                    "q": q["q"],
                    "answers": q["answers"],
                    "selected": choice,
                    "correct_answer": q["correct"],
                    "correct": is_correct
                })

                st.session_state.index += 1
                st.rerun()
