import streamlit as st
from PIL import Image
import pandas as pd
import re
import io
import requests

st.set_page_config(page_title="Vales Combustible", layout="centered")

st.title("⛽ Generador de Vales")
st.write("Sube fotos de los vales y descarga el Excel automáticamente")

API_KEY = "helloworld"

# -------- OCR -------- #
def leer_texto(img):
    url = "https://api.ocr.space/parse/image"
    
    response = requests.post(
        url,
        files={"file": img},
        data={
            "apikey": API_KEY,
            "language": "spa",
            "OCREngine": 2
        }
    )

    result = response.json()

    if result.get("IsErroredOnProcessing"):
        return ""

    try:
        return result["ParsedResults"][0]["ParsedText"]
    except:
        return ""

# -------- EXTRACCIÓN -------- #
def extraer_datos(texto):
    texto = texto.upper().replace("\n", " ")

    # Vale
    vale_match = re.search(r'(NO|N°|N0)[\s.:]*(\d{3,})', texto)
    vale = vale_match.group(2) if vale_match else ""

    # Fecha
    fecha_match = re.search(r'(\d{2}[-/]\d{2}[-/]\d{4})', texto)
    fecha = fecha_match.group(1) if fecha_match else ""

    # Valor (elige el mayor)
    valores = re.findall(r'\d{2,3}[.,]?\d{3}', texto)
    valor = ""
    if valores:
        valor = max(valores, key=lambda x: int(x.replace(".", "").replace(",", "")))

    # Combustible
    if "ACPM" in texto:
        combustible = "ACPM (Diesel)"
    else:
        combustible = "Gasolina Motor"

    # Placa
    placa_match = re.findall(r'[A-Z]{3}\s?\d{3}', texto)

    if placa_match:
        placa = placa_match[0].replace(" ", "")
        destino = "Vehículo"
        cantidad = 1
        obs = ""
    else:
        placa = "MAQUINARIA"
        destino = "Maquinaria"
        cantidad = 3
        obs = "Maquinaria GUADAÑA"

    return {
        "N° Vale": vale,
        "Fecha": fecha,
        "Placa / Equipo": placa,
        "Tipo de Combustible": combustible,
        "Cantidad": cantidad,
        "Valor Total ($)": valor,
        "Destino": destino,
        "Observaciones": obs
    }

# -------- INTERFAZ -------- #
uploaded_files = st.file_uploader(
    "📸 Sube los vales",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

if uploaded_files:
    datos = []

    for file in uploaded_files:
        img = Image.open(file)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        texto = leer_texto(buf)

        # 🔍 MOSTRAR TEXTO DETECTADO (CLAVE)
        st.subheader("🔎 Texto detectado")
        st.text(texto)

        datos.append(extraer_datos(texto))

    df = pd.DataFrame(datos)

    if not df.empty:
        df["Valor Total ($)"] = df["Valor Total ($)"].astype(str).str.replace(".", "", regex=False)
        df["Valor Total ($)"] = pd.to_numeric(df["Valor Total ($)"], errors='coerce')

    st.subheader("📊 Resultado")
    st.dataframe(df)

    # Exportar Excel
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
