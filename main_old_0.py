import streamlit as st
import os
import random
import json
import time
from pathlib import Path
from datetime import datetime

# ── Config ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Umano o AI?",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Paths ─────────────────────────────────────────────────────────────────--
AI_FOLDER = Path("images/ai")
REAL_FOLDER = Path("images/real")
LEADERBOARD_FILE = Path("leaderboard.json")

# ── Helpers ──────────────────────────────────────────────────────────────────
def load_leaderboard():
    if LEADERBOARD_FILE.exists():
        with open(LEADERBOARD_FILE) as f:
            return json.load(f)
    return []

def save_leaderboard(data):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_to_leaderboard(name: str, score: int, correct: int, total: int):
    lb = load_leaderboard()
    lb.append({
        "name": name,
        "score": score,
        "correct": correct,
        "total": total,
        "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
    })
    lb.sort(key=lambda x: x["score"], reverse=True)
    save_leaderboard(lb)

def load_images():
    """Load all images from both folders, shuffle, return list of (path, label)."""
    images = []
    if AI_FOLDER.exists():
        for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
            for p in AI_FOLDER.glob(ext):
                images.append((str(p), "ai"))
    if REAL_FOLDER.exists():
        for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
            for p in REAL_FOLDER.glob(ext):
                images.append((str(p), "real"))
    random.shuffle(images)
    return images

def calc_score(correct: bool, elapsed: float, confidence: int) -> int:
    """Score = base points * confidence multiplier * speed bonus."""
    if not correct:
        return 0
    base = 100
    speed_bonus = max(0, 1.0 - elapsed / 15.0)   # max 15 s per question
    conf_mult = {50: 0.5, 75: 1.0, 100: 1.5}[confidence]
    return int(base * conf_mult * (0.5 + 0.5 * speed_bonus))

REVEAL_TEXT = {
    ("ai",   True):  ("✅ Esatto! Era generata dall'AI.",           "🤖 Hai un occhio allenato! Le AI migliorano ogni giorno ma ci sono ancora dettagli che le tradiscono: bordi sfumati, texture innaturali, simmetrie strane."),
    ("ai",   False): ("❌ Era AI, non ti ha convinto!",             "😅 Questa immagine è stata generata da un modello di diffusione. Guarda bene i dettagli: spesso le mani, i capelli ai bordi o le scritte rivelano l'AI."),
    ("real", True):  ("✅ Esatto! Era una foto reale.",             "📷 Bravo! Le foto reali hanno imperfezioni naturali, luci casuali e una certa 'rumorosità' che le AI faticano ancora a replicare perfettamente."),
    ("real", False): ("❌ Era reale, sembrava AI!",                 "🌍 Questa è una foto vera! A volte la realtà è così strana da sembrare generata. È il bello di questo gioco — il confine si sta assottigliando."),
}

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { max-width: 700px; margin: auto; }
    .big-title { font-size: 3rem; font-weight: 900; text-align: center; margin-bottom: 0; }
    .subtitle  { font-size: 1.1rem; text-align: center; color: #888; margin-top: 0; margin-bottom: 2rem; }
    .score-box { background: #1a1a2e; border-radius: 12px; padding: 1rem 1.5rem;
                 display: flex; justify-content: space-between; align-items: center;
                 margin-bottom: 1rem; border: 1px solid #333; }
    .reveal-box { border-radius: 12px; padding: 1rem 1.5rem; margin-top: 1rem; }
    .reveal-correct { background: #0d3b26; border: 1px solid #1a7a45; }
    .reveal-wrong   { background: #3b0d0d; border: 1px solid #7a1a1a; }
    .lb-row { display: flex; justify-content: space-between; padding: 0.5rem 0;
              border-bottom: 1px solid #222; }
    .lb-medal { font-size: 1.4rem; margin-right: 0.5rem; }
    div[data-testid="stButton"] button {
        width: 100%;
        font-size: 1.1rem;
        font-weight: 700;
        padding: 0.7rem;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
defaults = {
    "page": "home",          # home | game | leaderboard | result
    "player_name": "",
    "images": [],
    "current_idx": 0,
    "score": 0,
    "correct": 0,
    "question_start": None,
    "answered": False,
    "answer_correct": None,
    "confidence": 75,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Navigation helpers ────────────────────────────────────────────────────────
def go(page):
    st.session_state["page"] = page

def start_game():
    imgs = load_images()
    if not imgs:
        st.error("⚠️ Nessuna immagine trovata. Assicurati di avere le cartelle `images/ai` e `images/real`.")
        return
    st.session_state.update({
        "images": imgs,
        "current_idx": 0,
        "score": 0,
        "correct": 0,
        "answered": False,
        "question_start": time.time(),
        "page": "game",
    })

# ════════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ════════════════════════════════════════════════════════════════════════════════
if st.session_state["page"] == "home":
    st.markdown('<p class="big-title">🤖 Umano o AI?</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Riesci a distinguere le immagini reali da quelle generate dall\'intelligenza artificiale?</p>', unsafe_allow_html=True)

    name = st.text_input("Il tuo nome per la classifica 👇", value=st.session_state["player_name"],
                         placeholder="es. Mario Rossi", max_chars=30)
    st.session_state["player_name"] = name.strip()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Inizia a giocare", use_container_width=True):
            if not st.session_state["player_name"]:
                st.warning("Inserisci il tuo nome prima di iniziare!")
            else:
                start_game()
                st.rerun()
    with col2:
        if st.button("🏆 Classifica", use_container_width=True):
            go("leaderboard")
            st.rerun()

    # Mini leaderboard preview
    lb = load_leaderboard()
    if lb:
        st.divider()
        st.markdown("#### 🏆 Top 5 giocatori")
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        for i, entry in enumerate(lb[:5]):
            st.markdown(
                f'<div class="lb-row"><span><span class="lb-medal">{medals[i]}</span>{entry["name"]}</span>'
                f'<span><b>{entry["score"]} pt</b> &nbsp;·&nbsp; {entry["correct"]}/{entry["total"]}</span></div>',
                unsafe_allow_html=True
            )

# ════════════════════════════════════════════════════════════════════════════════
# PAGE: GAME
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state["page"] == "game":
    imgs = st.session_state["images"]
    idx  = st.session_state["current_idx"]
    total = len(imgs)

    # Game over check
    if idx >= total:
        add_to_leaderboard(
            st.session_state["player_name"],
            st.session_state["score"],
            st.session_state["correct"],
            total,
        )
        go("result")
        st.rerun()

    img_path, label = imgs[idx]

    # ── Header bar ──
    st.markdown(
        f'<div class="score-box">'
        f'<span>👤 {st.session_state["player_name"]}</span>'
        f'<span>📸 {idx + 1} / {total}</span>'
        f'<span>⭐ {st.session_state["score"]} pt</span>'
        f'</div>',
        unsafe_allow_html=True
    )

    # Progress bar
    st.progress((idx) / total)

    # Image
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True)
    else:
        st.warning(f"Immagine non trovata: {img_path}")

    if not st.session_state["answered"]:
        # Confidence selector
        st.markdown("**Quanto sei sicuro/a?**")
        confidence = st.select_slider(
            "confidenza",
            options=[50, 75, 100],
            value=75,
            format_func=lambda x: {50: "50% — Mah...", 75: "75% — Abbastanza", 100: "100% — Certo!"}[x],
            label_visibility="collapsed"
        )
        st.session_state["confidence"] = confidence

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🤖 Generata dall'AI", use_container_width=True):
                elapsed = time.time() - st.session_state["question_start"]
                correct = (label == "ai")
                pts = calc_score(correct, elapsed, st.session_state["confidence"])
                st.session_state["score"]   += pts
                st.session_state["correct"] += int(correct)
                st.session_state["answered"] = True
                st.session_state["answer_correct"] = correct
                st.session_state["last_label"] = label
                st.session_state["last_pts"]  = pts
                st.rerun()
        with col2:
            if st.button("📷 Foto reale", use_container_width=True):
                elapsed = time.time() - st.session_state["question_start"]
                correct = (label == "real")
                pts = calc_score(correct, elapsed, st.session_state["confidence"])
                st.session_state["score"]   += pts
                st.session_state["correct"] += int(correct)
                st.session_state["answered"] = True
                st.session_state["answer_correct"] = correct
                st.session_state["last_label"] = label
                st.session_state["last_pts"]  = pts
                st.rerun()

    else:
        # ── Reveal ──
        correct = st.session_state["answer_correct"]
        lbl     = st.session_state["last_label"]
        pts     = st.session_state["last_pts"]
        title, body = REVEAL_TEXT[(lbl, correct)]
        css_class = "reveal-correct" if correct else "reveal-wrong"

        st.markdown(
            f'<div class="reveal-box {css_class}"><b>{title}</b><br><br>{body}'
            f'{"<br><br>🎯 <b>+" + str(pts) + " punti!</b>" if pts > 0 else "<br><br>💔 0 punti questa volta."}'
            f'</div>',
            unsafe_allow_html=True
        )

        next_label = "🏁 Vedi risultato" if idx + 1 >= total else "➡️ Prossima immagine"
        if st.button(next_label, use_container_width=True):
            st.session_state["current_idx"] += 1
            st.session_state["answered"] = False
            st.session_state["question_start"] = time.time()
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════════
# PAGE: RESULT
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state["page"] == "result":
    score   = st.session_state["score"]
    correct = st.session_state["correct"]
    total   = len(st.session_state["images"])
    pct     = int(correct / total * 100) if total else 0

    st.markdown('<p class="big-title">🎉 Risultato</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{st.session_state["player_name"]}, ecco come sei andato/a!</p>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("⭐ Punteggio", score)
    c2.metric("✅ Corrette", f"{correct}/{total}")
    c3.metric("🎯 Accuratezza", f"{pct}%")

    if pct >= 80:
        st.success("🔥 Impressionante! Hai un occhio da esperto di AI.")
    elif pct >= 60:
        st.info("👍 Bel risultato! Con un po' di pratica diventerai imbattibile.")
    else:
        st.warning("😅 Le AI ci stanno ingannando sempre di più — non sei solo/a!")

    # Rank
    lb = load_leaderboard()
    rank = next((i+1 for i, e in enumerate(lb) if e["name"] == st.session_state["player_name"] and e["score"] == score), None)
    if rank:
        st.markdown(f"### 🏆 Sei in posizione **#{rank}** in classifica!")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Gioca ancora", use_container_width=True):
            start_game()
            st.rerun()
    with col2:
        if st.button("🏆 Classifica", use_container_width=True):
            go("leaderboard")
            st.rerun()
    with col3:
        if st.button("🏠 Home", use_container_width=True):
            go("home")
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════════
# PAGE: LEADERBOARD
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state["page"] == "leaderboard":
    st.markdown('<p class="big-title">🏆 Classifica</p>', unsafe_allow_html=True)

    lb = load_leaderboard()
    medals = ["🥇", "🥈", "🥉"]

    if not lb:
        st.info("Nessun giocatore ancora. Sii il primo!")
    else:
        # Header
        cols = st.columns([0.5, 3, 1.5, 1.5, 2])
        cols[0].markdown("**#**")
        cols[1].markdown("**Nome**")
        cols[2].markdown("**Punti**")
        cols[3].markdown("**Corrette**")
        cols[4].markdown("**Data**")
        st.divider()

        for i, entry in enumerate(lb):
            rank_str = medals[i] if i < 3 else str(i + 1)
            cols = st.columns([0.5, 3, 1.5, 1.5, 2])
            cols[0].markdown(rank_str)
            name_str = f"**{entry['name']}**" if entry["name"] == st.session_state["player_name"] else entry["name"]
            cols[1].markdown(name_str)
            cols[2].markdown(f"**{entry['score']}**")
            cols[3].markdown(f"{entry['correct']}/{entry['total']}")
            cols[4].markdown(entry.get("date", "—"))

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Gioca", use_container_width=True):
            if st.session_state["player_name"]:
                start_game()
            else:
                go("home")
            st.rerun()
    with col2:
        if st.button("🏠 Home", use_container_width=True):
            go("home")
            st.rerun()