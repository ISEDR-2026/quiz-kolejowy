"""Tablica informacyjna zastępująca poprzednią aplikację Streamlit.

Obecne wdrożenie Streamlit uruchamia app.py: w repozytorium zapisz
ten plik jako app.py, zastępując jego dotychczasową zawartość.
"""

import streamlit as st


NEW_QUIZ_URL = "https://chmura.taild93bf7.ts.net:8443/"

st.set_page_config(
    page_title="Dyżurny — nowy adres quizu",
    page_icon="🚆",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
.stApp { background: #f3f6f8; }
.block-container { max-width: 760px; padding-top: 3.5rem; padding-bottom: 2rem; }
.move-card {
    background: #ffffff; color: #173346;
    border: 1px solid #dce6e9; border-top: 5px solid #087f75;
    border-radius: 20px; padding: 42px 36px;
    box-shadow: 0 12px 40px rgba(23, 51, 70, .06);
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.move-brand { color: #087f75; font-size: 13px; font-weight: 750; letter-spacing: .16em; }
.move-card h1 { color: #173346; font-size: clamp(28px, 5vw, 40px); line-height: 1.2; margin: 22px 0 18px; padding: 0; }
.move-card p { color: #526773; font-size: 17px; line-height: 1.65; margin: 0 0 22px; }
.move-password { background: #eaf6ef; color: #215d43; border: 1px solid #cfe7da; border-radius: 12px; padding: 16px 18px; margin: 26px 0; line-height: 1.5; }
.move-card a.move-button, .move-card a.move-button:visited {
    display: block; background: #08776e; color: #ffffff;
    text-align: center; text-decoration: none; font-size: 18px; font-weight: 700;
    border-radius: 10px; padding: 17px 20px; line-height: 1.4;
}
.move-card a.move-button:hover { background: #065e57; color: #ffffff; }
.move-card a:focus-visible { outline: 3px solid #db9e15; outline-offset: 4px; }
.move-card .move-address { margin: 16px 0 0; font-size: 13px; overflow-wrap: anywhere; text-align: center; }
.move-address a, .move-address a:visited { color: #526773; }
.move-card .move-hint { margin: 26px 0 0; font-size: 14px; text-align: center; }
.move-footer { margin: 22px 0 0; color: #667c88; font-size: 12px; text-align: center; }
@media (max-width: 480px) {
    .block-container { padding: 2rem 1rem; }
    .move-card { padding: 30px 22px; border-radius: 16px; }
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<section class="move-card" aria-labelledby="move-title">
    <div class="move-brand">DYŻURNY · TESTY KOLEJOWE</div>
    <h1 id="move-title">Quiz ma nowy adres.</h1>
    <p>Z powodów technicznych quiz dla dyżurnych ruchu został przeniesiony.
    Nauka i egzaminy próbne są teraz dostępne w nowej aplikacji.</p>
    <div class="move-password"><strong>Hasło główne pozostało bez zmian.</strong><br>
    Przy wejściu użyj dotychczasowego hasła dostępu.</div>
    <a class="move-button" href="{NEW_QUIZ_URL}" target="_blank" rel="noopener noreferrer">Przejdź do nowego quizu →</a>
    <p class="move-address"><a href="{NEW_QUIZ_URL}" target="_blank" rel="noopener noreferrer">{NEW_QUIZ_URL}</a></p>
    <p class="move-hint">Zapisz nowy adres w zakładkach, aby łatwo wrócić do nauki.</p>
</section>
<div class="move-footer">Administrator i twórca aplikacji: Adrian</div>
""",
    unsafe_allow_html=True,
)
