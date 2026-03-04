import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "0"

import streamlit as st
from ultralytics import YOLO
import numpy as np
import av
from streamlit_webrtc import webrtc_streamer

st.set_page_config(page_title="Pose Estimation — YOLO26", layout="wide")

st.title("Pose Estimation")
# st.subheader("Modifica i parametri del modello e osserva come cambia il risultato")

# ── Sidebar: parameters ───────────────────────────────────────────────────────
st.sidebar.header("Parametri del modello")

model_size = st.sidebar.radio(
    "Dimensione modello",
    ["yolo11n-pose", "yolo11s-pose", "yolo11m-pose"],
    captions=["Small — veloce, meno preciso", "Medium — bilanciato", "Big — lento, più preciso"],
)

conf = st.sidebar.slider(
    "Soglia di Confidenza - rilevamenti con confidenza sotto la soglia di confidenza vengono ignorati",
    min_value=0.10, max_value=0.95, value=0.50, step=0.05,
    # help="Sotto questa soglia un keypoint o una persona non vengono mostrati."
)

iou = st.sidebar.slider(
    "Soglia di Sovrapposizione - rilevamenti sovrapposti per più della percentuale vengono soppressi e considerati come unico",
    min_value=0.10, max_value=0.95, value=0.70, step=0.05,
    # help="Controlla quanto due rilevamenti devono sovrapporsi per essere considerati duplicati."
)

imgsz = st.sidebar.select_slider(
    "Risoluzione delle immagini - più alta = più dettagli, più lenta",
    options=[320, 480, 640, 1280],
    value=640,
    # help="Risoluzione a cui il modello elabora l'immagine. Più alta = più dettagli, più lenta."
)

max_det = st.sidebar.slider(
    "Numero persone — numero massimo di persone riconosciute dal modello",
    min_value=1, max_value=20, value=10, step=1,
    # help="Quante persone al massimo il modello può rilevare nell'immagine."
)

# ── Load model (cached by name) ───────────────────────────────────────────────
@st.cache_resource
def load_model(name):
    return YOLO(name)

model = load_model(model_size)

# ── WebRTC callback ───────────────────────────────────────────────────────────
def process_frame(frame):
    img = frame.to_ndarray(format="bgr24")
    results = model.predict(
        source=img,
        conf=conf,
        iou=iou,
        imgsz=imgsz,
        max_det=max_det,
        verbose=False,
    )
    return av.VideoFrame.from_ndarray(results[0].plot(), format="bgr24")

webrtc_streamer(
    key="pose",
    video_frame_callback=process_frame,
    media_stream_constraints={"video": True, "audio": False},
)

# ── Stats ─────────────────────────────────────────────────────────────────────
# st.divider()
# c1, c2, c3, c4 = st.columns(4)
# c1.metric("conf",    conf)
# c2.metric("iou",     iou)
# c3.metric("imgsz",   imgsz)
# c4.metric("max_det", max_det)
#
# # ── Explanation ───────────────────────────────────────────────────────────────
# st.divider()
# st.subheader("💡 Cosa sta succedendo?")
# st.markdown(f"""
# Il modello **{model_size}** elabora ogni frame della webcam in tempo reale.
#
# - **conf={conf}**: keypoint e persone con confidenza sotto {conf:.0%} vengono ignorati
# - **iou={iou}**: rilevamenti sovrapposti più del {iou:.0%} vengono considerati duplicati e soppressi
# - **imgsz={imgsz}**: ogni frame viene ridimensionato a {imgsz}×{imgsz}px prima dell'inferenza
# - **max_det={max_det}**: il modello si ferma alle {max_det} persone più confident per frame
# """)