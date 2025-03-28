import streamlit as st
import pandas as pd
import os
from datetime import datetime
import zipfile

# Carpetas
EXCEL_FOLDER = "gastos_excel"
FOTOS_FOLDER = "fotos_tickets"

# Crear carpetas si no existen
os.makedirs(EXCEL_FOLDER, exist_ok=True)
os.makedirs(FOTOS_FOLDER, exist_ok=True)

# Título
st.title("Registro de Gastos de Empresa")

# Formulario
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
        mes_anio = fecha_ticket.strftime("%m_%Y")
        nombre_archivo_excel = os.path.join(EXCEL_FOLDER, f"gastos_{mes_anio}.xlsx")

        # Cargar o crear DataFrame
        if os.path.exists(nombre_archivo_excel):
            df = pd.read_excel(nombre_archivo_excel)
        else:
            df = pd.DataFrame(columns=["Nº Registro", "FECHA Ticket", "TIPO Ticket", "CLIENTE/MOTIVO", "ORIGEN-DESTINO", "DISTANCIA (KM)", "IMPORTE (un)", "IMPORTE TOTAL", "FOTO"])

        # Número de línea
        num_registro = len(df) + 1

        # Nombre foto
        nombre_foto = f"ticket_{num_registro:03d}.png"
        ruta_foto = os.path.join(FOTOS_FOLDER, nombre_foto)

        # Guardar foto
        if foto_ticket is not None:
            with open(ruta_foto, "wb") as f:
                f.write(foto_ticket.read())

        # Nueva fila
        nueva_fila = {
            "Nº Registro": num_registro,
            "FECHA Ticket": fecha_ticket.strftime("%d/%m/%Y"),
            "TIPO Ticket": tipo_ticket,
            "CLIENTE/MOTIVO": cliente_motivo,
            "ORIGEN-DESTINO": origen_destino,
            "DISTANCIA (KM)": distancia,
            "IMPORTE (un)": "",
            "IMPORTE TOTAL": f"{importe:.2f} €",
            "FOTO": nombre_foto
        }

        df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)

        # Guardar Excel
        df.to_excel(nombre_archivo_excel, index=False)

        # Confirmación
        st.success("✅ Gasto guardado correctamente.")
        st.info(f"📁 Excel guardado en: {nombre_archivo_excel}")
        st.success(f"📷 Foto guardada como: {nombre_foto}")

        # Botón descarga Excel
        with open(nombre_archivo_excel, "rb") as f:
            st.download_button("📥 Descargar Excel", f, file_name=os.path.basename(nombre_archivo_excel))

# Botón para descargar carpeta de fotos como ZIP
if os.listdir(FOTOS_FOLDER):
    zip_path = "fotos_tickets.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for filename in os.listdir(FOTOS_FOLDER):
            filepath = os.path.join(FOTOS_FOLDER, filename)
            zipf.write(filepath, arcname=filename)

    with open(zip_path, "rb") as fzip:
        st.download_button("🗂️ Descargar todas las fotos (ZIP)", fzip, file_name="fotos_tickets.zip")
