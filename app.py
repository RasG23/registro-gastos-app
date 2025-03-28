import streamlit as st
import pandas as pd
import os
from datetime import datetime
import zipfile

# Configuración de carpetas
EXCEL_FOLDER = "gastos_excel"
FOTOS_FOLDER = "fotos_tickets"
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
        nombre_excel = f"gastos_{mes_anio}.xlsx"
        ruta_excel = os.path.join(EXCEL_FOLDER, nombre_excel)

        # Cargar o crear Excel
        if os.path.exists(ruta_excel):
            df = pd.read_excel(ruta_excel)
        else:
            df = pd.DataFrame(columns=["Nº Registro", "FECHA Ticket", "TIPO Ticket", "CLIENTE/MOTIVO", "ORIGEN-DESTINO", "DISTANCIA (KM)", "IMPORTE (un)", "IMPORTE TOTAL", "FOTO"])

        nuevo_registro = len(df) + 1

        nombre_foto = ""
        if foto_ticket is not None:
            nombre_foto = f"ticket_{nuevo_registro:03d}_{fecha_ticket.strftime('%d%m%Y')}_{tipo_ticket}.png"
            ruta_foto = os.path.join(FOTOS_FOLDER, nombre_foto)
            with open(ruta_foto, "wb") as f:
                f.write(foto_ticket.read())

        nueva_fila = {
            "Nº Registro": nuevo_registro,
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
        df.to_excel(ruta_excel, index=False)

        st.success("✅ Gasto guardado correctamente.")
        if nombre_foto:
            st.success(f"📸 Foto guardada: {ruta_foto}")
        st.info(f"📁 Excel guardado en: {ruta_excel}")

# Descargar Excel por mes
st.markdown("### 📥 Descargar Excel")

archivos_excel = sorted([f for f in os.listdir(EXCEL_FOLDER) if f.endswith(".xlsx")])
if archivos_excel:
    archivo_seleccionado = st.selectbox("Selecciona archivo Excel", archivos_excel)
    ruta_excel = os.path.join(EXCEL_FOLDER, archivo_seleccionado)
    with open(ruta_excel, "rb") as f:
        st.download_button(
            label="📄 Descargar Excel",
            data=f,
            file_name=archivo_seleccionado,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("No hay archivos Excel para descargar.")

# Descargar ZIP de fotos
st.markdown("### 🗂️ Descargar fotos")

if st.button("📦 Descargar todas las fotos (ZIP)"):
    zip_path = "fotos_tickets.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for filename in os.listdir(FOTOS_FOLDER):
            ruta = os.path.join(FOTOS_FOLDER, filename)
            zipf.write(ruta, arcname=filename)
    with open(zip_path, "rb") as f:
        st.download_button("⬇️ Descargar ZIP", f, file_name="fotos_tickets.zip", mime="application/zip")
