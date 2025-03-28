import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import zipfile

# ========== Configuración de directorios ==========
BASE_DIR = Path(__file__).resolve().parent
excel_dir = BASE_DIR / "gastos_excel"
fotos_dir = BASE_DIR / "fotos_tickets"

excel_dir.mkdir(exist_ok=True)
fotos_dir.mkdir(exist_ok=True)

# ========== Título ==========
st.set_page_config(page_title="Registro de Gastos", layout="centered")
st.title("🧾 Registro de Gastos")

# ========== Formulario de registro ==========
st.subheader("Registrar nuevo gasto")

col1, col2 = st.columns(2)
with col1:
    fecha_ticket = st.date_input("Fecha del ticket", value=datetime.today())
    tipo_ticket = st.selectbox("Tipo de ticket", ["Gasolina", "Gasoil"])
    cliente_motivo = st.text_input("Cliente / Motivo del gasto")
    origen_destino = st.text_input("Origen - Destino")
with col2:
    distancia = st.number_input("Distancia (KM)", min_value=0.0, step=1.0)
    importe = st.number_input("Importe Total (€)", min_value=0.0, step=1.0)

foto_ticket = st.file_uploader("Sube la foto del ticket", type=["jpg", "jpeg", "png"])
st.markdown("---")

# ========== Guardar gasto ==========
if st.button("Guardar gasto"):
    mes = fecha_ticket.strftime("%m")
    anio = fecha_ticket.strftime("%Y")
    nombre_excel = f"gastos_{mes}_{anio}.xlsx"
    ruta_excel = excel_dir / nombre_excel

    # Cargar o crear DataFrame
    if ruta_excel.exists():
        df = pd.read_excel(ruta_excel)
    else:
        df = pd.DataFrame(columns=[
            "REGISTRO", "FECHA Ticket", "TIPO Ticket", "CLIENTE/MOTIVO",
            "ORIGEN-DESTINO", "DISTANCIA (KM)", "IMPORTE (€)", "ARCHIVO FOTO"])

    nuevo_registro = len(df) + 1
    nombre_foto = ""

    if foto_ticket:
        extension = Path(foto_ticket.name).suffix
        nombre_foto = f"ticket_{nuevo_registro}_{fecha_ticket.strftime('%d%m%Y')}{extension}"
        ruta_foto = fotos_dir / nombre_foto
        with open(ruta_foto, "wb") as f:
            f.write(foto_ticket.getbuffer())
        st.success("📸 Foto guardada: " + str(ruta_foto))

    # Agregar fila
    fila = {
        "REGISTRO": nuevo_registro,
        "FECHA Ticket": fecha_ticket,
        "TIPO Ticket": tipo_ticket,
        "CLIENTE/MOTIVO": cliente_motivo,
        "ORIGEN-DESTINO": origen_destino,
        "DISTANCIA (KM)": distancia,
        "IMPORTE (€)": importe,
        "ARCHIVO FOTO": nombre_foto
    }
    df = pd.concat([df, pd.DataFrame([fila])], ignore_index=True)
    df.to_excel(ruta_excel, index=False)

    st.success("✅ Gasto guardado correctamente.")
    st.info("📁 Excel actualizado en: " + str(ruta_excel))

# ========== Descarga de archivos ==========
st.markdown("---")
st.title("📁 Descargar archivos")

col1, col2 = st.columns(2)
with col1:
    fecha_excel = st.date_input("Selecciona mes para Excel", value=datetime.today())
    mes_excel = fecha_excel.strftime("%m")
    anio_excel = fecha_excel.strftime("%Y")
    archivo_excel = excel_dir / f"gastos_{mes_excel}_{anio_excel}.xlsx"

    if archivo_excel.exists():
        with open(archivo_excel, "rb") as f:
            st.download_button("Descargar Excel", f, file_name=archivo_excel.name)
    else:
        st.warning("No se encontró el archivo para ese mes.")

with col2:
    fecha_fotos = st.date_input("Selecciona mes para Fotos", value=datetime.today())
    mes_fotos = fecha_fotos.strftime("%m")
    anio_fotos = fecha_fotos.strftime("%Y")

    fotos_mes = list(fotos_dir.glob(f"ticket_*_{mes_fotos}{anio_fotos}.*"))

    if fotos_mes:
        zip_path = fotos_dir / f"fotos_{mes_fotos}_{anio_fotos}.zip"
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for foto in fotos_mes:
                zipf.write(foto, arcname=foto.name)
        with open(zip_path, "rb") as f:
            st.download_button("Descargar fotos ZIP", f, file_name=zip_path.name)
    else:
        st.warning("No se encontraron fotos para ese mes.")
