import streamlit as st
from openpyxl import load_workbook
import random
import os

st.set_page_config(layout="wide")

# ===== STYLE =====
st.markdown("""
<style>
.card {background:#1c1f26;padding:20px;border-radius:15px;margin-bottom:20px;}
.question-number {font-size:14px;color:gray;margin-bottom:5px;}
.question-text {font-size:20px;font-weight:bold;}
div[role="radiogroup"] > label {font-size:18px !important;padding:10px !important;}
button[kind="secondary"], button[kind="primary"] {font-size:18px !important;padding:10px 20px !important;border-radius:10px !important;}

/* Poprawka stylu odpowiedzi, aby tekst był w pełni widoczny */
.answer {
    padding:12px;
    border-radius:10px;
    margin:8px 0;
    background:#2a2e38;
    line-height:1.4;
    height: auto !important;
    min-height: 40px;
    word-wrap: break-word;
}
.correct {background:#2ecc71 !important;color:white;}
.wrong {background:#e74c3c !important;color:white;}

.login-box {background:#1c1f26;padding:40px;border-radius:15px;width:400px;margin:auto;margin-top:10%;text-align:center;}
</style>
""", unsafe_allow_html=True)

HASLO = "szczecin26"
BIG_IMAGES = {1157,1158,1159,1160,1161,1162,1163,1164,1165,1166,1169,1170,1171}

def get_img_width(nr):
    base = 200
    if nr in BIG_IMAGES: return int(base * 2.5)
    return base

def norm(txt):
    if not txt: return ""
    return " ".join(str(txt).lower().strip().split())

IR1_FULL = norm("Ir - 1 Instrukcja o prowadzeniu ruchu pociągów")
IE1_FULL = norm("Ie - 1 Instrukcja sygnalizacji")

# ===== LOGOWANIE =====
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown('<div class="login-box"><h2>🔐 Dostęp</h2><p style="color:gray;">Baza pytań - Dyżurny Ruchu</p>', unsafe_allow_html=True)
    password = st.text_input("Hasło", type="password")
    if st.button("Wejdź"):
        if password == HASLO:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("❌ Niepoprawne hasło")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ===== WCZYTANIE (ZABEZPIECZONE CACHE) =====
@st.cache_data
def load_questions():
    excel_path = os.path.join(os.getcwd(), "quiz.xlsx")
    wb = load_workbook(excel_path, data_only=True)
    ws = wb.active
    qs = []
    for row in ws.iter_rows(min_row=5):
        if row[1].value and row[5].value:
            qs.append({
                "nr": int(row[0].value) if row[0].value else 0,
                "q": row[1].value,
                "answers": {"a": row[2].value, "b": row[3].value, "c": row[4].value},
                "correct": str(row[5].value).lower().strip(),
                "img": row[6].value if len(row) > 6 else None,
                "section": norm(row[7].value if len(row) > 7 else "")
            })
    return qs

all_questions = load_questions()

# ===== RESET SYSTEM =====
def hard_reset():
    for key in list(st.session_state.keys()):
        if key != "auth":
            del st.session_state[key]
    st.cache_data.clear()
    st.rerun()

# ===== INICJALIZACJA SESJI =====
if "started" not in st.session_state:
    st.session_state.update({
        "index": 0, "score": 0, "started": False, "selected": [], 
        "answers_log": [], "mode": "learn", "answered": False
    })

# ===== MENU GŁÓWNE =====
if not st.session_state.started:
    st.markdown("<h2 style='text-align:center;'>🚆 Baza pytań Dyżurny Ruchu</h2>", unsafe_allow_html=True)
    
    mode = st.radio("Tryb:", ["Nauka", "Egzamin"])
    
    if mode == "Nauka":
        option = st.selectbox("Ilość pytań:", ["10", "25", "Od pytania"])
        section_choice = st.radio("Dział:", ["Wszystkie", "Instrukcja Ir1", "Sygnalizacja", "Inne"])
        start_nr = st.number_input("Od pytania:", 1, 2000, 1) if option == "Od pytania" else 1

    if st.button("Start"):
        if mode == "Nauka":
            if section_choice == "Instrukcja Ir1": filtered = [q for q in all_questions if q["section"] == IR1_FULL]
            elif section_choice == "Sygnalizacja": filtered = [q for q in all_questions if q["section"] == IE1_FULL]
            elif section_choice == "Inne": filtered = [q for q in all_questions if q["section"] not in [IR1_FULL, IE1_FULL]]
            else: filtered = all_questions

            if option == "10": selected = random.sample(filtered, min(10, len(filtered)))
            elif option == "25": selected = random.sample(filtered, min(25, len(filtered)))
            else: selected = [q for q in filtered if q["nr"] >= start_nr]
        else:
            s_q = [q for q in all_questions if q["section"] == IE1_FULL]
            o_q = [q for q in all_questions if q["section"] != IE1_FULL]
            selected = random.sample(s_q, min(5, len(s_q))) + random.sample(o_q, min(25, len(o_q)))
            random.shuffle(selected)

        st.session_state.update({"selected": selected, "started": True, "index": 0, "score": 0, "mode": "learn" if mode == "Nauka" else "exam"})
        st.rerun()

# ===== QUIZ =====
else:
    q_list = st.session_state.selected
    idx = st.session_state.index
    
    if idx >= len(q_list):
        # PODSUMOWANIE (POPRAWIONE WYŚWIETLANIE)
        st.success(f"Koniec! Wynik: {st.session_state.score}/{len(q_list)}")
        if st.button("Zrestartuj aplikację (Pełny Reset)"):
            hard_reset()
            
        for log in st.session_state.answers_log:
            with st.expander(f"Pytanie {log['nr']} - {'✅ OK' if log['correct'] else '❌ BŁĄD'}"):
                st.markdown(f"**{log['q']}**")
                if log["img"] == "img":
                    img_p = os.path.join("image", f"{log['nr']}.png")
                    if os.path.exists(img_p): st.image(img_p, width=get_img_width(log['nr']))
                
                # Renderowanie odpowiedzi w podsumowaniu z poprawionym stylem
                for k, v in log['answers'].items():
                    c_class = "answer"
                    if k == log['correct_answer']: c_class += " correct"
                    elif k == log['selected'] and not log['correct']: c_class += " wrong"
                    
                    st.markdown(f"<div class='{c_class}'>{k}) {v}</div>", unsafe_allow_html=True)
    else:
        q = q_list[idx]
        st.progress(idx / len(q_list))
        st.markdown(f"<div class='card'><div class='question-number'>Pytanie {idx+1}/{len(q_list)} (nr {q['nr']})</div><div class='question-text'>{q['q']}</div></div>", unsafe_allow_html=True)

        if q["img"] == "img":
            img_p = os.path.join("image", f"{q['nr']}.png")
            if os.path.exists(img_p): st.image(img_p, width=get_img_width(q['nr']))

        if f"shuf_{idx}" not in st.session_state:
            items = list(q["answers"].items())
            random.shuffle(items)
            st.session_state[f"shuf_{idx}"] = items
        
        shuffled = st.session_state[f"shuf_{idx}"]
        
        choice = st.radio("Wybierz:", [item[0] for item in shuffled], format_func=lambda x: next(i[1] for i in shuffled if i[0] == x), key=f"r_{idx}")

        if st.session_state.mode == "learn":
            if not st.session_state.answered:
                if st.button("Zatwierdź"):
                    correct = choice == q["correct"]
                    if correct: st.session_state.score += 1
                    st.session_state.answers_log.append({"nr":q["nr"], "q":q["q"], "answers":q["answers"], "selected":choice, "correct_answer":q["correct"], "correct":correct, "img": q["img"]})
                    st.session_state.answered = True
                    st.session_state.last_choice = choice
                    st.rerun()
            else:
                for k, v in shuffled:
                    c = "answer"
                    if k == q["correct"]: c += " correct"
                    elif k == st.session_state.last_choice: c += " wrong"
                    st.markdown(f"<div class='{c}'>{v}</div>", unsafe_allow_html=True)
                if st.button("Dalej"):
                    st.session_state.index += 1
                    st.session_state.answered = False
                    st.rerun()
        else: # TRYB EGZAMIN
            if st.button("Zatwierdź odpowiedź"):
                correct = choice == q["correct"]
                if correct: st.session_state.score += 1
                st.session_state.answers_log.append({"nr":q["nr"], "q":q["q"], "answers":q["answers"], "selected":choice, "correct_answer":q["correct"], "correct":correct, "img": q["img"]})
                st.session_state.index += 1
                st.rerun()
