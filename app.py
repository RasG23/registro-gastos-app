import streamlit as st
import pandas as pd
import os
from datetime import datetime
from zipfile import ZipFile

# ============================
# Configuración de página
# ============================
st.set_page_config(page_title="Registro de Gastos", layout="wide")
st.title("🧾 Registro de Gastos")

# ============================
# Crear carpetas necesarias
# ============================
ruta_base = "registro-gastos-app"
ruta_fotos = os.path.join(ruta_base, "fotos_tickets")
ruta_excel = os.path.join(ruta_base, "gastos_excel")
os.makedirs(ruta_fotos, exist_ok=True)
os.makedirs(ruta_excel, exist_ok=True)

# ============================
# Formulario de ingreso
# ============================
with st.form("gasto_form"):
    st.subheader("Registrar nuevo gasto")
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha del ticket", value=datetime.today())
        tipo = st.selectbox("Tipo de gasto", ["Gasolina", "Gasoil", "Otro"])
        cliente = st.text_input("Cliente / Motivo")
        distancia = st.number_input("Distancia (KM)", min_value=0.0, step=1.0)
    with col2:
        origen_destino = st.text_input("Origen - Destino")
        importe_unitario = st.number_input("Importe Unitario (€)", min_value=0.0, step=1.0)
        importe_total = st.number_input("Importe Total (€)", min_value=0.0, step=1.0)

    st.markdown("---")
    st.subheader("Sube la foto del ticket")
    foto = st.file_uploader("Foto del ticket", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

    boton_guardar = st.form_submit_button("Guardar gasto")

    if boton_guardar:
        mes = fecha.strftime("%m")
        anio = fecha.strftime("%Y")
        nombre_excel = f"gastos_{mes}_{anio}.xlsx"
        ruta_excel_mes = os.path.join(ruta_excel, nombre_excel)

        # Leer o crear DataFrame
        if os.path.exists(ruta_excel_mes):
            df = pd.read_excel(ruta_excel_mes)
        else:
            df = pd.DataFrame(columns=["REGISTRO", "FECHA Ticket", "TIPO Ticket", "CLIENTE/MOTIVO", "ORIGEN-DESTINO", "DISTANCIA (KM)", "IMPORTE (unit)", "IMPORTE TOTAL", "ARCHIVO FOTO"])

        # Nuevo registro
        registro = len(df) + 1
        nombre_foto = ""

        if foto:
            extension = os.path.splitext(foto.name)[1]
            nombre_foto = f"ticket_{registro}_{fecha.strftime('%d%m%Y')}{extension}"
            ruta_foto = os.path.join(ruta_fotos, nombre_foto)
            with open(ruta_foto, "wb") as f:
                f.write(foto.read())

        nuevo = {
            "REGISTRO": registro,
            "FECHA Ticket": fecha,
            "TIPO Ticket": tipo,
            "CLIENTE/MOTIVO": cliente,
            "ORIGEN-DESTINO": origen_destino,
            "DISTANCIA (KM)": distancia,
            "IMPORTE (unit)": importe_unitario,
            "IMPORTE TOTAL": importe_total,
            "ARCHIVO FOTO": nombre_foto
        }

        df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
        df.to_excel(ruta_excel_mes, index=False)

        st.success("Gasto guardado correctamente.")
        if nombre_foto:
            st.info(f"📸 Foto guardada: {ruta_foto}")
        st.info(f"📁 Excel guardado en: {ruta_excel_mes}")

# ============================
# Sección de descargas
# ============================
st.markdown("---")
st.header("📁 Descargar archivos")

col1, col2 = st.columns(2)

with col1:
    st.write("Selecciona mes para Excel")
    fecha_excel = st.date_input("", value=datetime.today(), key="excel")
    mes_excel = fecha_excel.strftime("%m")
    anio_excel = fecha_excel.strftime("%Y")
    nombre_excel = f"gastos_{mes_excel}_{anio_excel}.xlsx"
    ruta_excel_mes = os.path.join(ruta_excel, nombre_excel)

    if os.path.exists(ruta_excel_mes):
        with open(ruta_excel_mes, "rb") as f:
            st.download_button("Descargar Excel", f, file_name=nombre_excel)

with col2:
    st.write("Selecciona mes para Fotos")
    fecha_foto = st.date_input("", value=datetime.today(), key="fotos")
    mes_foto = fecha_foto.strftime("%m")
    anio_foto = fecha_foto.strftime("%Y")

    fotos_mes = [f for f in os.listdir(ruta_fotos) if f.endswith(('.jpg', '.png', '.jpeg')) and f"_{mes_foto}{anio_foto}" in f.replace("ticket_", "").replace(".jpg", "").replace(".png", "").replace(".jpeg", "")]

    if fotos_mes:
        nombre_zip = f"fotos_tickets_{mes_foto}_{anio_foto}.zip"
        ruta_zip = os.path.join(ruta_base, nombre_zip)
        with ZipFile(ruta_zip, "w") as zipf:
            for foto in fotos_mes:
                zipf.write(os.path.join(ruta_fotos, foto), arcname=foto)

        with open(ruta_zip, "rb") as f:
            st.download_button("Descargar fotos ZIP", f, file_name=nombre_zip)
