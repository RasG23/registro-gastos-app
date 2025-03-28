import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO
import zipfile

# ========================
# CONFIGURACIÓN DE PÁGINA
# ========================
st.set_page_config(page_title="Registro de Gastos", layout="centered")

# ================
# RUTAS DIRECTORIOS
# ================
EXCEL_DIR = "gastos_excel"
FOTOS_DIR = "fotos_tickets"
os.makedirs(EXCEL_DIR, exist_ok=True)
os.makedirs(FOTOS_DIR, exist_ok=True)

# =====================
# FORMULARIO DE INGRESO
# =====================
st.title("💸 Registro de Gastos")

with st.form("gastos_formulario"):
    fecha_ticket = st.date_input("Fecha del ticket", value=datetime.today())
    tipo_ticket = st.selectbox("Tipo de gasto", ["Gasolina", "Peaje", "Otro"])
    cliente_motivo = st.text_input("Cliente o motivo")
    origen_destino = st.text_input("Origen - Destino")
    distancia_km = st.number_input("Distancia (KM)", min_value=0.0, step=1.0)
    importe_total = st.number_input("Importe Total (€)", min_value=0.0, step=0.01)
    archivo_ticket = st.file_uploader("Sube la foto del ticket", type=["jpg", "jpeg", "png"])

    enviar = st.form_submit_button("Guardar gasto")

    if enviar:
        # ------------------
        # Archivo Excel del mes
        # ------------------
        mes_ano = fecha_ticket.strftime("%m_%Y")
        archivo_excel = os.path.join(EXCEL_DIR, f"gastos_{mes_ano}.xlsx")

        # ------------------
        # Cargar datos existentes o crear nuevo
        # ------------------
        if os.path.exists(archivo_excel):
            df = pd.read_excel(archivo_excel)
        else:
            df = pd.DataFrame(columns=["FECHA Ticket", "TIPO Ticket", "CLIENTE/MOTIVO", "ORIGEN-DESTINO", "DISTANCIA (KM)", "IMPORTE TOTAL", "ARCHIVO FOTO"])

        # ------------------
        # Crear nuevo registro
        # ------------------
        nuevo_id = len(df) + 1
        nombre_foto = ""
        if archivo_ticket is not None:
            nombre_foto = f"ticket_{nuevo_id}_{fecha_ticket.strftime('%d%m%Y')}.jpg"
            ruta_foto = os.path.join(FOTOS_DIR, nombre_foto)
            with open(ruta_foto, "wb") as f:
                f.write(archivo_ticket.read())

        # ------------------
        # Añadir fila
        # ------------------
        nueva_fila = {
            "FECHA Ticket": fecha_ticket.strftime("%Y-%m-%d"),
            "TIPO Ticket": tipo_ticket,
            "CLIENTE/MOTIVO": cliente_motivo,
            "ORIGEN-DESTINO": origen_destino,
            "DISTANCIA (KM)": distancia_km,
            "IMPORTE TOTAL": importe_total,
            "ARCHIVO FOTO": nombre_foto
        }

        df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
        df.to_excel(archivo_excel, index=False)

        st.success("✅ Gasto guardado correctamente.")
        if nombre_foto:
            st.info(f"📸 Foto guardada: `{ruta_foto}`")
        st.info(f"🧾 Excel actualizado: `{archivo_excel}`")

# ====================================
# SECCIÓN DE DESCARGAS DE EXCEL Y FOTOS
# ====================================
st.markdown("---")
st.header("⬇️ Descargas")

# Obtener meses disponibles
meses_excel = sorted([f for f in os.listdir(EXCEL_DIR) if f.endswith(".xlsx")])
meses_fotos = sorted(set(
    "_".join(nombre.split("_")[2:4]).replace(".jpg", "") for nombre in os.listdir(FOTOS_DIR) if nombre.startswith("ticket")
))

# -----------------------
# DESCARGAR ARCHIVO EXCEL
# -----------------------
st.subheader("📊 Descargar Excel")
if meses_excel:
    mes_elegido_excel = st.selectbox("Selecciona el mes", meses_excel, key="excel")
    with open(os.path.join(EXCEL_DIR, mes_elegido_excel), "rb") as f:
        st.download_button("📥 Descargar Excel", data=f, file_name=mes_elegido_excel, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.info("No hay archivos Excel para descargar.")

# ---------------------
# DESCARGAR FOTOS ZIP
# ---------------------
st.subheader("🖼️ Descargar todas las fotos (ZIP)")
if meses_fotos:
    mes_elegido_foto = st.selectbox("Selecciona el mes", meses_fotos, key="fotos")

    # Filtrar fotos de ese mes
    fotos_mes = [f for f in os.listdir(FOTOS_DIR) if mes_elegido_foto in f]

    if fotos_mes:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for foto in fotos_mes:
                ruta = os.path.join(FOTOS_DIR, foto)
                zipf.write(ruta, arcname=foto)
        zip_buffer.seek(0)
        st.download_button("📥 Descargar ZIP con fotos", data=zip_buffer, file_name=f"fotos_{mes_elegido_foto}.zip", mime="application/zip")
    else:
        st.warning("No se encontraron fotos para ese mes.")
else:
    st.info("No hay fotos disponibles aún.")
