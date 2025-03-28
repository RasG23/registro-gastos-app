import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configurar título
st.title("Registro de Gastos de Empresa")

# Definir carpetas
EXCEL_FOLDER = os.path.abspath("gastos_excel")
FOTOS_FOLDER = os.path.abspath("fotos_tickets")

# Crear carpetas si no existen
os.makedirs(EXCEL_FOLDER, exist_ok=True)
os.makedirs(FOTOS_FOLDER, exist_ok=True)

# Formulario para ingreso de datos
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
        # Obtener mes y año
        mes_anio = fecha_ticket.strftime("%m_%Y")
        nombre_archivo_excel = os.path.join(EXCEL_FOLDER, f"gastos_{mes_anio}.xlsx")

        # Crear o cargar Excel existente
        if os.path.exists(nombre_archivo_excel):
            df = pd.read_excel(nombre_archivo_excel)
        else:
            df = pd.DataFrame(columns=["FECHA Ticket", "TIPO Ticket", "CLIENTE/MOTIVO", "ORIGEN-DESTINO", "DISTANCIA (KM)", "IMPORTE (un)", "IMPORTE TOTAL"])

        # Agregar fila
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

        # Guardar foto (único nombre para evitar sobrescribir)
        if foto_ticket is not None:
            timestamp = datetime.now().strftime("%H%M%S")
            nombre_foto = f"ticket_{fecha_ticket.strftime('%d%m%Y')}_{tipo_ticket}_{timestamp}.png"
            ruta_foto = os.path.join(FOTOS_FOLDER, nombre_foto)
            with open(ruta_foto, "wb") as f:
                f.write(foto_ticket.read())
            st.success(f"📸 Foto guardada: `{ruta_foto}`")

        # Mostrar confirmación con ruta del Excel
        st.success("✅ Gasto guardado correctamente.")
        st.info(f"📁 Excel guardado en: `{nombre_archivo_excel}`")
