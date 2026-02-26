import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np

st.set_page_config(page_title="Pose Estimation — YOLO26", layout="wide")

st.title("Pose Estimation")
st.subheader("Modifica i parametri del modello e osserva come cambia il risultato")

# ── Sidebar: parameters ───────────────────────────────────────────────────────
st.sidebar.header("⚙️ Parametri del modello")

model_size = st.sidebar.radio(
    "Dimensione modello",
    ["yolo11n-pose", "yolo11s-pose", "yolo11m-pose"],
    captions=["Nano — veloce, meno preciso", "Small — bilanciato", "Medium — lento, più preciso"],
)

conf = st.sidebar.slider(
    "conf — soglia di confidenza",
    min_value=0.10, max_value=0.95, value=0.50, step=0.05,
    help="Sotto questa soglia un keypoint o una persona non vengono mostrati."
)

iou = st.sidebar.slider(
    "iou — soglia di sovrapposizione (NMS)",
    min_value=0.10, max_value=0.95, value=0.70, step=0.05,
    help="Controlla quanto due rilevamenti devono sovrapporsi per essere considerati duplicati."
)

imgsz = st.sidebar.select_slider(
    "imgsz — risoluzione di inferenza",
    options=[320, 480, 640, 1280],
    value=640,
    help="Risoluzione a cui il modello elabora l'immagine. Più alta = più dettagli, più lenta."
)

max_det = st.sidebar.slider(
    "max_det — numero massimo di persone",
    min_value=1, max_value=20, value=10, step=1,
    help="Quante persone al massimo il modello può rilevare nell'immagine."
)

# ── Image input ───────────────────────────────────────────────────────────────
st.sidebar.divider()
uploaded = st.sidebar.file_uploader(
    "Carica un'immagine (opzionale)",
    type=["jpg", "jpeg", "png"],
    help="Se non carichi nulla, viene usata l'immagine di esempio."
)

# ── Load model (cached) ───────────────────────────────────────────────────────
@st.cache_resource
def load_model(name):
    return YOLO(name)   # downloads weights automatically on first run

# ── Run inference ─────────────────────────────────────────────────────────────
col_img, col_result = st.columns(2)

if uploaded:
    image = Image.open(uploaded).convert("RGB")
else:
    # Use a bundled sample image or download one from COCO
    import urllib.request, os
    sample_path = "sample_people.jpg"
    if not os.path.exists(sample_path):
        url = "https://ultralytics.com/images/bus.jpg"
        urllib.request.urlretrieve(url, sample_path)
    image = Image.open(sample_path).convert("RGB")

with col_img:
    st.subheader("Immagine originale")
    st.image(image, use_container_width=True)

with col_result:
    st.subheader("Risultato inferenza")
    with st.spinner(f"Eseguo inferenza con {model_size}..."):
        model  = load_model(model_size)
        results = model.predict(
            source=np.array(image),
            conf=conf,
            iou=iou,
            imgsz=imgsz,
            max_det=max_det,
            verbose=False,
        )
        annotated = results[0].plot()   # returns BGR numpy array
        annotated_rgb = annotated[:, :, ::-1]  # BGR → RGB
    st.image(annotated_rgb, use_container_width=True)

# ── Stats ─────────────────────────────────────────────────────────────────────
st.divider()
n_people = len(results[0].boxes) if results[0].boxes is not None else 0
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Persone rilevate", n_people)
c2.metric("conf",   conf)
c3.metric("iou",    iou)
c4.metric("imgsz",  imgsz)
c5.metric("max_det", max_det)

# ── Explanation ───────────────────────────────────────────────────────────────
st.divider()
st.subheader("💡 Cosa sta succedendo?")
st.markdown(f"""
Il modello **{model_size}** ha analizzato l'immagine a risoluzione **{imgsz}px** e trovato **{n_people} persone**.

- **conf={conf}**: keypoint e persone con confidenza sotto {conf:.0%} sono stati ignorati
- **iou={iou}**: rilevamenti che si sovrappongono più del {iou:.0%} vengono considerati duplicati e soppressi
- **imgsz={imgsz}**: immagine ridimensionata a {imgsz}×{imgsz}px prima dell'inferenza
- **max_det={max_det}**: anche se ci fossero più persone, il modello si ferma a {max_det}
""")