import streamlit as st
import pandas as pd
import os
from datetime import datetime
import zipfile
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ======================== CONFIGURACIÓN GOOGLE SHEETS ========================

# Leer credenciales desde los secretos de Streamlit
creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(credentials)

# Abrir hoja por ID (asegúrate de compartir el documento con el correo de servicio)
sheet = client.open_by_key("T1HpVxewZ3HoqeppZmKycNV8SyYqhRJHmVULKMmoa-JoA").sheet1  # <-- Reemplaza con tu ID

# ======================== INTERFAZ ========================
st.set_page_config(page_title="Registro de Gastos", layout="centered")
st.title("Registro de Gastos de Empresa")

# Crear carpetas locales si no existen
os.makedirs("fotos_tickets", exist_ok=True)

# ======================== FORMULARIO ========================
with st.form("registro_gasto"):
    fecha_ticket = st.date_input("Fecha del ticket")
    tipo_ticket = st.selectbox("Tipo de ticket", ["Gasoil", "Comida", "Peajes", "Chat GPT", "Notion"])
    cliente_motivo = st.text_input("Cliente / Motivo")
    origen_destino = st.text_input("Origen - Destino")
    distancia = st.number_input("Distancia (KM)", min_value=0.0)
    importe = st.number_input("Importe Total (€)", min_value=0.0)
    foto_ticket = st.file_uploader("Sube la foto del ticket", type=["jpg", "jpeg", "png"])
    enviado = st.form_submit_button("Guardar gasto")

    if enviado:
        # Obtener la siguiente línea (registro)
        existing_records = sheet.get_all_values()
        registro = len(existing_records)

        # Nueva fila para Google Sheets
        nueva_fila = [
            fecha_ticket.strftime("%d/%m/%Y"),
            tipo_ticket,
            cliente_motivo,
            origen_destino,
            distancia,
            "",
            f"{importe:.2f} €"
        ]
        sheet.append_row(nueva_fila)

        # Guardar foto
        if foto_ticket is not None:
            nombre_foto = f"foto_{registro}.png"
            ruta_foto = os.path.join("fotos_tickets", nombre_foto)
            with open(ruta_foto, "wb") as f:
                f.write(foto_ticket.read())
            st.success(f"📷 Foto guardada: {ruta_foto}")

        st.success("✅ Gasto guardado correctamente.")

# ======================== DESCARGAR FOTOS ========================
if st.button("📁 Descargar todas las fotos (ZIP)"):
    zip_filename = "fotos_tickets.zip"
    with zipfile.ZipFile(zip_filename, "w") as zipf:
        for root, dirs, files in os.walk("fotos_tickets"):
            for file in files:
                zipf.write(os.path.join(root, file), arcname=file)
    with open(zip_filename, "rb") as f:
        st.download_button("Descargar ZIP", f, file_name=zip_filename)

# ======================== DESCARGAR GOOGLE SHEET ========================
if st.button("📄 Descargar Excel (Google Sheets)"):
    data = sheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    excel_filename = "registro_gastos.xlsx"
    df.to_excel(excel_filename, index=False)
    with open(excel_filename, "rb") as f:
        st.download_button("Descargar Excel", f, file_name=excel_filename)
