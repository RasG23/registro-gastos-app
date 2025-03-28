import streamlit as st
import pandas as pd
import os
from datetime import datetime
from zipfile import ZipFile

# ================= CONFIG ====================
st.set_page_config(page_title="Registro de Gastos", layout="centered")
st.markdown("## Registro de gastos")

# ============== DIRECTORIOS ==================
FOLDER_EXCEL = "registro-gastos-app/gastos_excel"
FOLDER_FOTOS = "registro-gastos-app/fotos_tickets"
os.makedirs(FOLDER_EXCEL, exist_ok=True)
os.makedirs(FOLDER_FOTOS, exist_ok=True)

# ============== FORMULARIO ===================
with st.form("form_gastos"):
    col1, col2 = st.columns(2)
    with col1:
        fecha_ticket = st.date_input("Fecha del ticket")
        tipo_ticket = st.selectbox("Tipo de gasto", ["Gasolina", "Gasoil", "Otro"])
        cliente_motivo = st.text_input("Cliente / Motivo")
    with col2:
        origen_destino = st.text_input("Origen - Destino")
        distancia_km = st.number_input("Distancia (KM)", min_value=0.0)
        importe_unitario = st.number_input("Importe Total (€)", min_value=0.0)

    foto_ticket = st.file_uploader("Sube la foto del ticket", type=["jpg", "jpeg", "png"])
    submitted = st.form_submit_button("Guardar gasto")

    if submitted:
        mes_actual = fecha_ticket.strftime("%m")
        anio_actual = fecha_ticket.strftime("%Y")
        nombre_excel = f"gastos_{mes_actual}_{anio_actual}.xlsx"
        ruta_excel = os.path.join(FOLDER_EXCEL, nombre_excel)

        # Leer o crear dataframe
        if os.path.exists(ruta_excel):
            df = pd.read_excel(ruta_excel)
        else:
            df = pd.DataFrame(columns=["REGISTRO", "FECHA Ticket", "TIPO Ticket", "CLIENTE/MOTIVO", "ORIGEN-DESTINO", "DISTANCIA (KM)", "IMPORTE (€)", "ARCHIVO FOTO"])

        numero_registro = len(df) + 1
        nombre_foto = ""

        if foto_ticket is not None:
            nombre_foto = f"ticket_{numero_registro}_{fecha_ticket.strftime('%d%m%Y')}.jpg"
            ruta_foto = os.path.join(FOLDER_FOTOS, nombre_foto)
            with open(ruta_foto, "wb") as f:
                f.write(foto_ticket.read())

        nueva_fila = {
            "REGISTRO": numero_registro,
            "FECHA Ticket": fecha_ticket,
            "TIPO Ticket": tipo_ticket,
            "CLIENTE/MOTIVO": cliente_motivo,
            "ORIGEN-DESTINO": origen_destino,
            "DISTANCIA (KM)": distancia_km,
            "IMPORTE (€)": importe_unitario,
            "ARCHIVO FOTO": nombre_foto
        }

        df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
        df.to_excel(ruta_excel, index=False)

        st.success("Gasto guardado correctamente.")
        if nombre_foto:
            st.info(f"📸 Foto guardada: `{ruta_foto}`")
        st.info(f"📁 Excel actualizado en: `{ruta_excel}`")

# ========== DESCARGAS ===================
st.markdown("## 📁 Descargar archivos")
col1, col2 = st.columns(2)

# === Selección de mes para Excel ===
with col1:
    fecha_excel = st.date_input("Selecciona mes para Excel")
    mes = fecha_excel.strftime("%m")
    anio = fecha_excel.strftime("%Y")
    archivo_excel = f"gastos_{mes}_{anio}.xlsx"
    ruta_excel = os.path.join(FOLDER_EXCEL, archivo_excel)
    if os.path.exists(ruta_excel):
        with open(ruta_excel, "rb") as f:
            st.download_button("Descargar Excel", f, file_name=archivo_excel, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.warning("No se encontró el archivo Excel para esa fecha.")

# === Selección de mes para Fotos ===
with col2:
    fecha_fotos = st.date_input("Selecciona mes para Fotos")
    mes_foto = fecha_fotos.strftime("%m")
    anio_foto = fecha_fotos.strftime("%Y")

    fotos_mes = [f for f in os.listdir(FOLDER_FOTOS) if f.endswith(('.jpg', '.jpeg', '.png')) and f"_{mes_foto}{anio_foto}" in f]

    if fotos_mes:
        zip_path = os.path.join(FOLDER_FOTOS, f"fotos_{mes_foto}_{anio_foto}.zip")
        with ZipFile(zip_path, "w") as zipf:
            for foto in fotos_mes:
                zipf.write(os.path.join(FOLDER_FOTOS, foto), arcname=foto)

        with open(zip_path, "rb") as f:
            st.download_button("🖼️ Descargar fotos ZIP", f, file_name=os.path.basename(zip_path), mime="application/zip")
    else:
        st.warning("No se encontraron fotos para ese mes.")
