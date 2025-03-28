import streamlit as st
import pandas as pd
import os
from datetime import datetime
import zipfile

# ======== CONFIGURACIÓN =========
EXCEL_FOLDER = "gastos_excel"
FOTOS_FOLDER = "fotos_tickets"
os.makedirs(EXCEL_FOLDER, exist_ok=True)
os.makedirs(FOTOS_FOLDER, exist_ok=True)

st.set_page_config(page_title="Registro de Gastos", layout="centered")
st.title("📋 Registro de Gastos de Empresa")

# ========== FORMULARIO ==========
with st.form("registro_gasto"):
    fecha_ticket = st.date_input("📅 Fecha del ticket")
    tipo_ticket = st.selectbox("🧾 Tipo de ticket", ["Gasoil", "Comida", "Peajes", "Chat GPT", "Notion"])
    cliente_motivo = st.text_input("👤 Cliente / Motivo")
    origen_destino = st.text_input("🛣️ Origen - Destino")
    distancia = st.number_input("📏 Distancia (KM)", min_value=0.0)
    importe = st.number_input("💶 Importe Total (€)", min_value=0.0)
    foto_ticket = st.file_uploader("📷 Sube la foto del ticket", type=["jpg", "jpeg", "png"])
    enviado = st.form_submit_button("✅ Guardar gasto")

    if enviado:
        mes_anio = fecha_ticket.strftime("%m_%Y")
        nombre_archivo_excel = os.path.join(EXCEL_FOLDER, f"gastos_{mes_anio}.xlsx")

        # Leer o crear archivo Excel
        if os.path.exists(nombre_archivo_excel):
            df = pd.read_excel(nombre_archivo_excel)
        else:
            df = pd.DataFrame(columns=[
                "FECHA Ticket", "TIPO Ticket", "CLIENTE/MOTIVO", "ORIGEN-DESTINO",
                "DISTANCIA (KM)", "IMPORTE (un)", "IMPORTE TOTAL"
            ])

        # Agregar nueva fila
        nueva_fila = {
            "FECHA Ticket": fecha_ticket.strftime("%d/%m/%Y"),
            "TIPO Ticket": tipo_ticket,
            "CLIENTE/MOTIVO": cliente_motivo,
            "ORIGEN-DESTINO": origen_destino,
            "DISTANCIA (KM)": distancia,
            "IMPORTE (un)": "",
            "IMPORTE TOTAL": f"{importe:.2f} €"
        }
        df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)

        # Guardar Excel
        df.to_excel(nombre_archivo_excel, index=False)

        # Guardar imagen con nombre según la fila
        if foto_ticket is not None:
            linea = len(df)
            extension = os.path.splitext(foto_ticket.name)[-1].lower()
            nombre_foto = f"ticket_{mes_anio}_{linea}{extension}"
            ruta_foto = os.path.join(FOTOS_FOLDER, nombre_foto)
            with open(ruta_foto, "wb") as f:
                f.write(foto_ticket.read())
            st.success(f"📸 Foto guardada como: `{ruta_foto}`")

        st.success("✅ Gasto guardado correctamente.")
        st.info(f"📁 Excel guardado en: `{nombre_archivo_excel}`")

# ========== DESCARGA DE EXCEL ==========
st.markdown("---")
st.subheader("📤 Descargas")

# Descarga del Excel actual
mes_actual = datetime.now().strftime("%m_%Y")
excel_actual = os.path.join(EXCEL_FOLDER, f"gastos_{mes_actual}.xlsx")
if os.path.exists(excel_actual):
    with open(excel_actual, "rb") as f:
        st.download_button(
            label="📊 Descargar Excel actual",
            data=f,
            file_name=f"gastos_{mes_actual}.xlsx"
        )

# Descargar fotos en ZIP
zip_path = "fotos_tickets.zip"
with zipfile.ZipFile(zip_path, "w") as zipf:
    for root, _, files in os.walk(FOTOS_FOLDER):
        for file in files:
            zipf.write(os.path.join(root, file), arcname=file)

with open(zip_path, "rb") as f:
    st.download_button(
        label="📁 Descargar todas las fotos (ZIP)",
        data=f,
        file_name="fotos_tickets.zip"
    )
