import streamlit as st
import os
import random
import json
from pathlib import Path
from datetime import datetime

# ── Config ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Umano o AI?",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
[data-testid="stImage"] img {
    max-height: 400px;
    object-fit: contain;
}
</style>
""", unsafe_allow_html=True)

# ── Paths ────────────────────────────────────────────────────────────────────
AI_FOLDER        = Path("images/ai")
REAL_FOLDER      = Path("images/real")
LEADERBOARD_FILE = Path("leaderboard.json")

# ── Per-image reveal text ─────────────────────────────────────────────────────
# For images NOT listed here, fallback text is used automatically.
IMAGE_REVEALS = {
    "ai1": {
        "prompt":  "Magari ci mettiamo il prompt che ha generato l'immagine",
        "caption": "Possibile testo che spiega qualche dettaglio interessante dell'immagine",
    },
    "ai2": {
        "prompt":  "Magari ci mettiamo il prompt che ha generato l'immagine",
        "caption": "Possibile testo che spiega qualche dettaglio interessante dell'immagine",
    },
    "ai3": {
        "prompt":  "Magari ci mettiamo il prompt che ha generato l'immagine",
        "caption": "Possibile testo che spiega qualche dettaglio interessante dell'immagine",
    },
    "ai4": {
        "prompt":  "Magari ci mettiamo il prompt che ha generato l'immagine",
        "caption": "Possibile testo che spiega qualche dettaglio interessante dell'immagine",
    },
    "ai5": {
        "prompt":  "Magari ci mettiamo il prompt che ha generato l'immagine",
        "caption": "Possibile testo che spiega qualche dettaglio interessante dell'immagine",
    },

    "real1": {
        "caption": "Possibile testo che spiega qualche dettaglio interessante dell'immagine",
    },
    "real2": {
        "caption": "Possibile testo che spiega qualche dettaglio interessante dell'immagine",
    },
    "real3": {
        "caption": "Possibile testo che spiega qualche dettaglio interessante dell'immagine",
    },
    "real4": {
        "caption": "Possibile testo che spiega qualche dettaglio interessante dell'immagine",
    },
    "real5": {
        "caption": "Possibile testo che spiega qualche dettaglio interessante dell'immagine",
    },

}

FALLBACK_REVEAL = {
    "ai": {
        "correct": "Corretto!",
        "wrong":   "Sbagliato",
    },
    "real": {
        "correct": "Corretto!",
        "wrong":   "Sbagliato",
    },
}

# ── Leaderboard helpers ───────────────────────────────────────────────────────
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
        "name":    name,
        "score":   score,
        "correct": correct,
        "total":   total,
        "date":    datetime.now().strftime("%d/%m/%Y %H:%M"),
    })
    lb.sort(key=lambda x: x["score"], reverse=True)
    save_leaderboard(lb)

# ── Image loader ──────────────────────────────────────────────────────────────
def load_images(max_images_to_load = 6):
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
    return images[:max_images_to_load + 1]

POINTS_PER_CORRECT = 100

# ── Session state ─────────────────────────────────────────────────────────────
defaults = {
    "page":           "home",
    "player_name":    "",
    "images":         [],
    "current_idx":    0,
    "score":          0,
    "correct":        0,
    "answered":       False,
    "answer_correct": None,
    "last_label":     None,
    "last_img_stem":  None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Navigation ────────────────────────────────────────────────────────────────
def go(page):
    st.session_state["page"] = page

def start_game():
    imgs = load_images()
    if not imgs:
        st.error("Nessuna immagine trovata. Crea le cartelle `images/ai` e `images/real` e aggiungici delle immagini.")
        return
    st.session_state.update({
        "images":      imgs,
        "current_idx": 0,
        "score":       0,
        "correct":     0,
        "answered":    False,
        "page":        "game",
    })

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state["page"] == "home":
    st.title("Umano o AI?")
    st.subheader("Riesci a distinguere le immagini reali da quelle generate dall'AI?")
    st.divider()

    name = st.text_input(
        "Il tuo nome per la classifica",
        value=st.session_state["player_name"],
        placeholder="es. Mario Rossi",
        max_chars=30,
    )
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

    lb = load_leaderboard()
    if lb:
        st.divider()
        st.subheader("🏆 Top 5")
        cols = st.columns([0.5, 3, 1.5, 1.5])
        cols[0].markdown("**#**")
        cols[1].markdown("**Nome**")
        cols[2].markdown("**Punti**")
        cols[3].markdown("**Corrette**")
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        for i, entry in enumerate(lb[:5]):
            cols = st.columns([0.5, 3, 1.5, 1.5])
            cols[0].markdown(medals[i])
            cols[1].markdown(entry["name"])
            cols[2].markdown(f"**{entry['score']}**")
            cols[3].markdown(f"{entry['correct']}/{entry['total']}")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: GAME
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state["page"] == "game":
    imgs  = st.session_state["images"]
    idx   = st.session_state["current_idx"]
    total = len(imgs)

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
    img_stem = Path(img_path).stem

    # So the image and the buttons can stay on the same page without
    # needing to scroll the page each time.
    #
    # col1, col2, col3 = st.columns(3)
    # col1.metric("👤 Giocatore", st.session_state["player_name"])
    # col2.metric("📸 Immagine",  f"{idx + 1} / {total}")
    # col3.metric("⭐ Punteggio", st.session_state["score"])
    st.progress(idx / total)

    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True)
    else:
        st.warning(f"Immagine non trovata: {img_path}")

    if not st.session_state["answered"]:
        st.subheader("Questa immagine è reale o generata dall'AI?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🤖 Generata dall'AI", use_container_width=True):
                correct = (label == "ai")
                st.session_state["score"]         += POINTS_PER_CORRECT if correct else 0
                st.session_state["correct"]       += int(correct)
                st.session_state["answered"]       = True
                st.session_state["answer_correct"] = correct
                st.session_state["last_label"]     = label
                st.session_state["last_img_stem"]  = img_stem
                st.rerun()
        with col2:
            if st.button("📷 Foto reale", use_container_width=True):
                correct = (label == "real")
                st.session_state["score"]         += POINTS_PER_CORRECT if correct else 0
                st.session_state["correct"]       += int(correct)
                st.session_state["answered"]       = True
                st.session_state["answer_correct"] = correct
                st.session_state["last_label"]     = label
                st.session_state["last_img_stem"]  = img_stem
                st.rerun()

    else:
        correct  = st.session_state["answer_correct"]
        lbl      = st.session_state["last_label"]
        stem     = st.session_state["last_img_stem"]
        img_data = IMAGE_REVEALS.get(stem, {})

        fallback = FALLBACK_REVEAL[lbl]["correct" if correct else "wrong"]
        caption  = img_data.get("caption", fallback)
        prompt   = img_data.get("prompt")

        label_str = "generata dall'AI" if lbl == "ai" else "una foto reale"

        if correct:
            reveal_text = f"**Esatto! Era {label_str}.** \n\n{caption}"
            if lbl == "ai" and prompt:
                reveal_text += f"\n\n **Prompt usato:** *{prompt}*"
            st.success(reveal_text)
        else:
            reveal_text = f"**Sbagliato! Era {label_str}.\n\n{caption}"
            if lbl == "ai" and prompt:
                reveal_text += f"\n\n️ **Prompt usato:** *{prompt}*"
            st.warning(reveal_text)

        next_label = "🏁 Vedi risultato finale" if idx + 1 >= total else "➡️ Prossima immagine"
        if st.button(next_label, use_container_width=True):
            st.session_state["current_idx"] += 1
            st.session_state["answered"]     = False
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: RESULT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state["page"] == "result":
    score   = st.session_state["score"]
    correct = st.session_state["correct"]
    total   = len(st.session_state["images"])
    pct     = int(correct / total * 100) if total else 0

    st.title("🎉 Risultato finale")
    st.subheader(f"{st.session_state['player_name']}, ecco come te la sei cavata!")

    c1, c2, c3 = st.columns(3)
    c1.metric("⭐ Punteggio",   score)
    c2.metric("✅ Corrette",    f"{correct}/{total}")
    # c3.metric("🎯 Accuratezza", f"{pct}%")
    st.divider()

    lb   = load_leaderboard()
    rank = next((i + 1 for i, e in enumerate(lb)
                 if e["name"] == st.session_state["player_name"] and e["score"] == score), None)
    if rank:
        st.subheader(f"🏆 Sei in posizione #{rank} in classifica!")

    st.divider()
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

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: LEADERBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state["page"] == "leaderboard":
    st.title("🏆 Classifica")
    st.subheader("Chi riesce a distinguere meglio umani e macchine?")

    lb     = load_leaderboard()
    medals = ["🥇", "🥈", "🥉"]

    if not lb:
        st.info("Nessun giocatore ancora. Sii il primo!")
    else:
        cols = st.columns([0.5, 3, 1.5, 1.5, 2])
        cols[0].markdown("**#**")
        cols[1].markdown("**Nome**")
        cols[2].markdown("**Punti**")
        cols[3].markdown("**Corrette**")
        cols[4].markdown("**Data**")
        st.divider()

        for i, entry in enumerate(lb):
            rank_str = medals[i] if i < 3 else str(i + 1)
            is_me    = entry["name"] == st.session_state["player_name"]
            cols     = st.columns([0.5, 3, 1.5, 1.5, 2])
            cols[0].markdown(rank_str)
            cols[1].markdown(f"**{entry['name']}**" if is_me else entry["name"])
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