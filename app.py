import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO
from zipfile import ZipFile

# === Config ===
FOLDER_EXCEL = "registro-gastos-app/gastos_excel"
FOLDER_FOTOS = "registro-gastos-app/fotos_tickets"
os.makedirs(FOLDER_EXCEL, exist_ok=True)
os.makedirs(FOLDER_FOTOS, exist_ok=True)

# === Título principal ===
st.set_page_config(page_title="Registro de Gastos", layout="wide")
st.title("💳 Registro de Gastos")

# === Formulario de gasto ===
st.subheader("Nuevo gasto")
col1, col2 = st.columns(2)

with col1:
    fecha_ticket = st.date_input("Fecha del ticket", format="DD/MM/YYYY")
    tipo_ticket = st.selectbox("Tipo de gasto", ["Gasolina", "Gasoil", "Otro"])
    cliente_motivo = st.text_input("Cliente o motivo")
    origen_destino = st.text_input("Origen - Destino")

with col2:
    distancia_km = st.number_input("Distancia (KM)", min_value=0.0, step=1.0)
    importe_unitario = st.number_input("Importe Total (€)", min_value=0.0, step=0.5)
    foto_ticket = st.file_uploader("Sube la foto del ticket", type=["jpg", "jpeg", "png"])

if st.button("Guardar gasto"):
    fecha_str = fecha_ticket.strftime("%d/%m/%Y")
    mes_excel = fecha_ticket.strftime("%m_%Y")
    archivo_excel = os.path.join(FOLDER_EXCEL, f"gastos_{mes_excel}.xlsx")

    # Cargar datos existentes o crear nuevo DataFrame
    columnas = ["REGISTRO", "FECHA Ticket", "TIPO Ticket", "CLIENTE/MOTIVO", "ORIGEN-DESTINO", "DISTANCIA (KM)", "IMPORTE (€)", "ARCHIVO FOTO"]
    if os.path.exists(archivo_excel):
        df = pd.read_excel(archivo_excel)
    else:
        df = pd.DataFrame(columns=columnas)

    # Crear nuevo registro
    nuevo_registro = len(df) + 1
    nombre_foto = f"ticket_{nuevo_registro}_{fecha_ticket.strftime('%d%m%Y')}.jpg" if foto_ticket else ""

    nueva_fila = pd.DataFrame({
        "REGISTRO": [nuevo_registro],
        "FECHA Ticket": [fecha_str],
        "TIPO Ticket": [tipo_ticket],
        "CLIENTE/MOTIVO": [cliente_motivo],
        "ORIGEN-DESTINO": [origen_destino],
        "DISTANCIA (KM)": [distancia_km],
        "IMPORTE (€)": [importe_unitario],
        "ARCHIVO FOTO": [nombre_foto]
    })

    df = pd.concat([df, nueva_fila], ignore_index=True)
    df.to_excel(archivo_excel, index=False)
    st.success("Gasto guardado correctamente.")

    # Guardar foto
    if foto_ticket:
        ruta_foto = os.path.join(FOLDER_FOTOS, nombre_foto)
        with open(ruta_foto, "wb") as f:
            f.write(foto_ticket.read())
        st.info(f"📸 Foto guardada: `{ruta_foto}`")

    st.info(f"📂 Excel actualizado en: `{archivo_excel}`")

# === Descarga de archivos ===
st.markdown("""
---
### 📁 Descargar archivos
""")

col_excel, col_fotos = st.columns(2)

with col_excel:
    st.write("Selecciona mes para Excel")
    fecha_excel = st.date_input("", key="excel")
    mes_excel = fecha_excel.strftime("%m_%Y")
    archivo_excel = os.path.join(FOLDER_EXCEL, f"gastos_{mes_excel}.xlsx")
    if os.path.exists(archivo_excel):
        with open(archivo_excel, "rb") as f:
            st.download_button("📄 Descargar Excel", f, file_name=os.path.basename(archivo_excel))
    else:
        st.warning("No se encontró el archivo Excel para ese mes.")

with col_fotos:
    st.write("Selecciona mes para Fotos")
    fecha_fotos = st.date_input("", key="fotos")
    mes_fotos = fecha_fotos.strftime("%m_%Y")

    fotos_mes = [f for f in os.listdir(FOLDER_FOTOS) if f.endswith(".jpg") and f"_{fecha_fotos.strftime('%d%m%Y')}" in f]

    if fotos_mes:
        buffer = BytesIO()
        with ZipFile(buffer, "w") as zip_file:
            for foto in fotos_mes:
                ruta = os.path.join(FOLDER_FOTOS, foto)
                zip_file.write(ruta, arcname=foto)
        buffer.seek(0)
        st.download_button("📸 Descargar fotos ZIP", buffer, file_name=f"fotos_{mes_fotos}.zip")
    else:
        st.warning("No se encontraron fotos para ese mes.")
