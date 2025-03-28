import streamlit as st
import pandas as pd
import os
from datetime import datetime
from zipfile import ZipFile

# ================= CONFIG =================
st.set_page_config(page_title="Registro de Gastos", layout="centered")

# ================== RUTAS ==================
FOLDER_EXCEL = "registro-gastos-app/gastos_excel"
FOLDER_FOTOS = "registro-gastos-app/fotos_tickets"
os.makedirs(FOLDER_EXCEL, exist_ok=True)
os.makedirs(FOLDER_FOTOS, exist_ok=True)

# =============== FUNCIONES =================
def guardar_excel(df, fecha):
    mes = fecha.strftime("%m")
    anio = fecha.strftime("%Y")
    nombre_archivo = f"gastos_{mes}_{anio}.xlsx"
    ruta_archivo = os.path.join(FOLDER_EXCEL, nombre_archivo)
    df.to_excel(ruta_archivo, index=False)
    return nombre_archivo

def cargar_excel(fecha):
    mes = fecha.strftime("%m")
    anio = fecha.strftime("%Y")
    nombre_archivo = f"gastos_{mes}_{anio}.xlsx"
    ruta_archivo = os.path.join(FOLDER_EXCEL, nombre_archivo)
    if os.path.exists(ruta_archivo):
        return pd.read_excel(ruta_archivo)
    else:
        return pd.DataFrame(columns=[
            "REGISTRO Nº", "FECHA Ticket", "TIPO Ticket", "CLIENTE/MOTIVO",
            "ORIGEN-DESTINO", "DISTANCIA (KM)", "IMPORTE (un)", "IMPORTE TOTAL",
            "ARCHIVO FOTO"])

def zip_fotos_mes(fecha):
    mes = fecha.strftime("%m")
    anio = fecha.strftime("%Y")
    zip_filename = f"fotos_tickets_{mes}_{anio}.zip"
    zip_path = os.path.join(FOLDER_FOTOS, zip_filename)
    with ZipFile(zip_path, 'w') as zipf:
        for file in os.listdir(FOLDER_FOTOS):
            if file.endswith(f"_{mes}{anio}.jpg") or file.endswith(f"_{mes}{anio}.png"):
                zipf.write(os.path.join(FOLDER_FOTOS, file), arcname=file)
    return zip_path

# ================= UI =================
st.title("Registro de Gastos")

with st.form("registro_form"):
    col1, col2 = st.columns(2)
    with col1:
        fecha_ticket = st.date_input("Fecha del ticket", value=datetime.today())
        tipo_ticket = st.selectbox("Tipo de ticket", ["Gasoil", "Gasolina", "Otro"])
        cliente_motivo = st.text_input("Cliente / Motivo")
    with col2:
        origen_destino = st.text_input("Origen - Destino")
        distancia_km = st.number_input("Distancia (KM)", min_value=0.0, step=1.0, format="%.2f")
        importe_total = st.number_input("Importe Total (€)", min_value=0.0, step=1.0, format="%.2f")

    foto = st.file_uploader("Sube la foto del ticket", type=["jpg", "jpeg", "png"])
    st.form_submit_button("Guardar gasto")

    if st.session_state.get("registro_form"):
        df = cargar_excel(fecha_ticket)
        registro_num = len(df) + 1

        # Guardar la foto con nombre único
        fecha_str = fecha_ticket.strftime("%d%m%Y")
        foto_nombre = f"ticket_{registro_num}_{fecha_str}.jpg"
        ruta_foto = os.path.join(FOLDER_FOTOS, foto_nombre)

        if foto:
            with open(ruta_foto, "wb") as f:
                f.write(foto.read())
            st.success(f"\U0001F4F7 Foto guardada: {ruta_foto}")

        nuevo_registro = {
            "REGISTRO Nº": registro_num,
            "FECHA Ticket": fecha_ticket.strftime("%d/%m/%Y"),
            "TIPO Ticket": tipo_ticket,
            "CLIENTE/MOTIVO": cliente_motivo,
            "ORIGEN-DESTINO": origen_destino,
            "DISTANCIA (KM)": distancia_km,
            "IMPORTE (un)": "",
            "IMPORTE TOTAL": f"{importe_total:.2f} €",
            "ARCHIVO FOTO": foto_nombre if foto else ""
        }

        df.loc[len(df)] = nuevo_registro
        nombre_excel = guardar_excel(df, fecha_ticket)

        st.success("\u2705 Gasto guardado correctamente.")
        st.info(f"\U0001F4C4 Excel guardado en: {nombre_excel}")

# ================= DESCARGAS =================
st.markdown("---")
st.subheader("Descargar archivos")

col1, col2 = st.columns(2)
with col1:
    fecha_excel = st.date_input("Selecciona mes para Excel")
    excel_file = os.path.join(FOLDER_EXCEL, guardar_excel(cargar_excel(fecha_excel), fecha_excel))
    with open(excel_file, "rb") as f:
        st.download_button("\U0001F4C3 Descargar Excel", f, file_name=os.path.basename(excel_file))

with col2:
    fecha_fotos = st.date_input("Selecciona mes para Fotos")
    zip_file = zip_fotos_mes(fecha_fotos)
    with open(zip_file, "rb") as f:
        st.download_button("\U0001F4C4 Descargar fotos ZIP", f, file_name=os.path.basename(zip_file))