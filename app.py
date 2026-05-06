import streamlit as st
from PIL import Image
import pandas as pd
import re
import io
import easyocr

# Inicializar lector OCR
reader = easyocr.Reader(['es'])

st.set_page_config(page_title="Vales Combustible", layout="centered")

st.title("⛽ Generador de Vales")
st.write("Sube fotos de los vales y descarga el Excel automáticamente")

def extraer_datos(texto):
    texto = texto.upper().replace("\n", " ")

    vale = re.search(r'NO\s*[:\-]?\s*(\d+)', texto)
    fecha = re.search(r'(\d{2}[-/]\d{2}[-/]\d{4})', texto)

    valores = re.findall(r'\d{2,3}[.,]?\d{3}', texto)
    valor = valores[-1] if valores else ""

    if "ACPM" in texto:
        combustible = "ACPM (Diesel)"
    else:
        combustible = "Gasolina Motor"

    placa_match = re.search(r'[A-Z]{3}\s?\d{3}', texto)
    placa = placa_match.group(0) if placa_match else "MAQUINARIA"

    if placa == "MAQUINARIA":
        destino = "Maquinaria"
        cantidad = 3
        obs = "Maquinaria GUADAÑA"
    else:
        destino = "Vehículo"
        cantidad = 1
        obs = ""

    return {
        "N° Vale": vale.group(1) if vale else "",
        "Fecha": fecha.group(1) if fecha else "",
        "Placa / Equipo": placa,
        "Tipo de Combustible": combustible,
        "Cantidad": cantidad,
        "Valor Total ($)": valor,
        "Destino": destino,
        "Observaciones": obs
    }

uploaded_files = st.file_uploader(
    "📸 Sube los vales",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

if uploaded_files:
    datos = []

    for file in uploaded_files:
        img = Image.open(file)

        # OCR con easyocr
        resultado = reader.readtext(img)
        texto = " ".join([res[1] for res in resultado])

        datos.append(extraer_datos(texto))

    df = pd.DataFrame(datos)

    df["Valor Total ($)"] = df["Valor Total ($)"].str.replace(".", "").astype(float)

    st.subheader("📊 Resultado")
    st.dataframe(df)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    buffer.seek(0)

    st.download_button(
        "📥 Descargar Excel",
        data=buffer,
        file_name="vales.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
