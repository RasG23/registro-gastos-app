import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configurar título
st.title("Registro de Gastos de Empresa")

# Crear carpetas si no existen
os.makedirs("gastos_excel", exist_ok=True)
os.makedirs("fotos_tickets", exist_ok=True)

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
        nombre_archivo_excel = f"gastos_excel/gastos_{mes_anio}.xlsx"

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

        # Guardar foto
        if foto_ticket is not None:
            nombre_foto = f"fotos_tickets/ticket_{fecha_ticket.strftime('%d%m%Y')}_{tipo_ticket}.png"
            with open(nombre_foto, "wb") as f:
                f.write(foto_ticket.read())

        st.success("✅ Gasto guardado correctamente.")
