import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import os
from zipfile import ZipFile

# === CONFIGURACIÓN INICIAL ===
st.set_page_config(page_title="Registro de Gastos", layout="centered")
st.title("📑 Registro de Gastos")

# === RUTAS ===
EXCEL_DIR = Path("registro-gastos-app/gastos_excel")
FOTOS_DIR = Path("registro-gastos-app/fotos_tickets")
EXCEL_DIR.mkdir(parents=True, exist_ok=True)
FOTOS_DIR.mkdir(parents=True, exist_ok=True)

# === FORMULARIO ===
with st.form("formulario_gastos"):
    fecha_ticket = st.date_input("Fecha del ticket", value=datetime.today())
    tipo_ticket = st.selectbox("Tipo de gasto", ["Gasoil", "Gasolina", "Peajes", "Comida", "Otros"])
    cliente = st.text_input("Cliente / Motivo")
    origen_destino = st.text_input("Origen - Destino")
    distancia_km = st.number_input("Distancia (KM)", min_value=0.0, format="%.2f")
    importe_unitario = st.number_input("Importe Total (€)", min_value=0.0, format="%.2f")
    imagen = st.file_uploader("Sube la foto del ticket", type=["jpg", "jpeg", "png"])
    submitted = st.form_submit_button("Guardar gasto")

# === GUARDAR DATOS ===
if submitted:
    mes = fecha_ticket.strftime("%m")
    año = fecha_ticket.strftime("%Y")
    excel_filename = f"gastos_{mes}_{año}.xlsx"
    excel_path = EXCEL_DIR / excel_filename

    # Leer o crear Excel
    if excel_path.exists():
        df = pd.read_excel(excel_path)
    else:
        df = pd.DataFrame(columns=[
            "REGISTRO", "FECHA Ticket", "TIPO Ticket", "CLIENTE/MOTIVO", "ORIGEN-DESTINO",
            "DISTANCIA (KM)", "IMPORTE (€)", "ARCHIVO FOTO"
        ])

    # Calcular número de registro
    nuevo_registro = len(df) + 1

    # Guardar imagen con nombre personalizado
    nombre_imagen = ""
    if imagen:
        nombre_imagen = f"ticket_{nuevo_registro}_{fecha_ticket.strftime('%d%m%Y')}.jpg"
        imagen_path = FOTOS_DIR / nombre_imagen
        with open(imagen_path, "wb") as f:
            f.write(imagen.read())

    # Agregar fila
    nueva_fila = {
        "REGISTRO": nuevo_registro,
        "FECHA Ticket": fecha_ticket,
        "TIPO Ticket": tipo_ticket,
        "CLIENTE/MOTIVO": cliente,
        "ORIGEN-DESTINO": origen_destino,
        "DISTANCIA (KM)": distancia_km,
        "IMPORTE (€)": importe_unitario,
        "ARCHIVO FOTO": nombre_imagen
    }
    df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
    df.to_excel(excel_path, index=False)

    # === MENSAJE CONFIRMACIÓN ===
    st.success("✅ Gasto guardado correctamente.")
    if nombre_imagen:
        st.info(f"📸 Foto guardada como: {nombre_imagen}")
    st.info(f"📁 Excel actualizado: {excel_filename}")

# === DESCARGA DE ARCHIVOS ===
st.markdown("---")
st.header("📂 Descargar archivos")

col1, col2 = st.columns(2)

with col1:
    fecha_excel = st.date_input("Selecciona mes para Excel", value=datetime.today(), key="fecha_excel")
    excel_mes = fecha_excel.strftime("%m")
    excel_año = fecha_excel.strftime("%Y")
    excel_a_descargar = EXCEL_DIR / f"gastos_{excel_mes}_{excel_año}.xlsx"
    if excel_a_descargar.exists():
        with open(excel_a_descargar, "rb") as f:
            st.download_button("📄 Descargar Excel", f, file_name=excel_a_descargar.name)
    else:
        st.warning("No hay archivo Excel para ese mes.")

with col2:
    fecha_fotos = st.date_input("Selecciona mes para Fotos", value=datetime.today(), key="fecha_fotos")
    mes_fotos = fecha_fotos.strftime("%m")
    año_fotos = fecha_fotos.strftime("%Y")

    fotos_zip = FOTOS_DIR / f"fotos_tickets_{mes_fotos}_{año_fotos}.zip"
    with ZipFile(fotos_zip, "w") as zipf:
        for file in FOTOS_DIR.glob(f"ticket_*_{mes_fotos}{año_fotos}.jpg"):
            zipf.write(file, arcname=file.name)

    if fotos_zip.exists():
        with open(fotos_zip, "rb") as f:
            st.download_button("🖼️ Descargar fotos ZIP", f, file_name=fotos_zip.name)
    else:
        st.warning("No hay fotos para ese mes.")
