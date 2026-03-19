import os
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "0"

import streamlit as st
from ultralytics import solutions

st.set_page_config(page_title="Pose Estimation — YOLO", layout="wide")

inf = solutions.Inference(model="yolo11n-pose.pt")
inf.inference()