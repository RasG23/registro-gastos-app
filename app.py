import streamlit as st
import pandas as pd
import os
from datetime import datetime
import gspread
import json
import zipfile

from oauth2client.service_account import ServiceAccountCredentials

# Cargar credenciales desde Secrets de Streamlit
creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(credentials)

# Abrir hoja de cálculo y worksheet (asegúrate de tener una hoja con ese nombre)
sheet = client.open("registro_gastos").sheet1

# Crear carpetas si no existen
os.makedirs("fotos_tickets", exist_ok=True)

st.title("Registro de Gastos - Google Sheets")

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
        # Obtener el número de línea actual
        num_linea = len(sheet.get_all_values()) + 1
        registro_id = f"ID{num_linea:04}"

        # Guardar imagen con nombre único
        if foto_ticket:
            nombre_foto = f"fotos_tickets/ticket_{registro_id}.png"
            with open(nombre_foto, "wb") as f:
                f.write(foto_ticket.read())
            st.success(f"📸 Foto guardada: {nombre_foto}")

        # Formato de fila a insertar
        fila = [
            fecha_ticket.strftime("%d/%m/%Y"),
            tipo_ticket,
            cliente_motivo,
            origen_destino,
            distancia,
            "",
            f"{importe:.2f} €"
        ]
        sheet.append_row(fila)
        st.success("✅ Gasto guardado en Google Sheets correctamente.")

# Descargar fotos en ZIP
if st.button("📁 Descargar todas las fotos (ZIP)"):
    zip_path = "fotos_tickets.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for root, _, files in os.walk("fotos_tickets"):
            for file in files:
                zipf.write(os.path.join(root, file), arcname=file)

    with open(zip_path, "rb") as f:
        st.download_button("📥 Descargar ZIP", f, file_name="fotos_tickets.zip")
