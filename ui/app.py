import os
import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("CIFAR_API_URL", "http://127.0.0.1:5000").rstrip("/")

st.set_page_config(
    page_title="Task 14 CIFAR-10",
    page_icon="🧠",
    layout="centered",
)
st.title("CIFAR-10 Image Classifier")
st.caption("Task 14 - Kubernetes Scaling and Rolling Updates")

uploaded = st.file_uploader(
    "Upload a color image",
    type=["png", "jpg", "jpeg"],
)

if uploaded:
    st.image(uploaded, caption="Uploaded Image", width=320)

    if st.button("Predict", type="primary"):
        try:
            response = requests.post(
                f"{API_URL}/predict",
                files={
                    "file": (
                        uploaded.name,
                        uploaded.getvalue(),
                        uploaded.type or "application/octet-stream",
                    )
                },
                timeout=60,
            )

            if response.ok:
                result = response.json()
                st.success(f"Predicted class: {result['predicted_class']}")
                st.metric("Confidence", f"{result['confidence_percent']:.2f}%")
                st.info(f"API version: {result['version']}")

                chart = pd.DataFrame(
                    {
                        "Class": list(result["probabilities"].keys()),
                        "Probability": list(result["probabilities"].values()),
                    }
                ).set_index("Class")
                st.bar_chart(chart)
            else:
                st.error(response.text)
        except requests.RequestException as exc:
            st.error(f"API connection failed: {exc}")
else:
    st.info("Upload an image to begin.")
