import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Enamed Game", page_icon="🦉", layout="centered")

# --- CSS (ESTÉTICA) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Varela+Round&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Varela Round', sans-serif;
    }
    
    /* Card da Tarefa */
    .task-card {
        background-color: #ffffff;
        border: 2px solid #e5e5e5;
        border-radius: 16px;
        padding: 0px; 
        margin-bottom: 15px;
        box-shadow: 0 4px 0 #e5e5e5;
        overflow: hidden; 
    }
    
    /* Botões */
    .stButton > button {
        border-radius: 12px;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 0 rgba(0,0,0,0.2);
        transition: margin-top 0.1s, box-shadow 0.1s;
        width: 100%;
    }
    .stButton > button:active {
        margin-top: 4px;
        box-shadow: none;
    }
    </style>
""", unsafe_allow_html=True)

# --- DADOS E VARIÁVEIS ---
USERS = ["Dr. Ana", "Dr. Bruno", "Dr. Carlos", "Dr. Daniel"]
CSV_FILE = "enamed_data.csv"

# --- FUNÇÕES ---
def init_db():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=[
            "ID", "Semana", "Data_Alvo", "Tema", "Detalhes", "Link_Questões",
            "Dr. Ana_Status", "Dr. Ana_Date",
            "Dr. Bruno_Status", "Dr. Bruno_Date",
            "Dr. Carlos_Status", "Dr. Carlos_Date",
            "Dr. Daniel_Status", "Dr. Daniel_Date"
        ])
        initial_data = [
            [1, "Semana 01", "2026-02-20", "Pediatria - Imunizações", "Foco: Calendário 0-15 meses.", "", False, None, False, None, False, None, False, None],
            [2, "Semana 01", "2026-02-21", "Preventiva - Vigilância", "Notificação Compulsória.", "", False, None, False, None, False, None, False, None],
        ]
        for row in initial_data:
            df.loc[len(df)] = row
        df.to_csv(CSV_FILE, index=False)

def load_data():
    if not os.path.exists(CSV_FILE): init_db()
    return pd.read_csv(CSV_FILE)

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def calculate_xp(target, completed_at):
    if pd.isna(completed_at) or str(completed_at) == "None" or str(completed_at) == "":
        return 0
    try:
        t = datetime.strptime(str(target), "%Y-%m-%d").date()
        c = datetime.strptime(str(completed_at), "%Y-%m-%d").date()
        if c <= t: return 100
        else: return 50
    except: return 0

# --- INICIALIZAÇÃO ---
st.title("🦉 Desafio Enamed")
df = load_data()

# Login Fixo
qp = st.query_params
default_idx = 0
if "user" in qp:
    try:
        if qp["user"] in USERS: default_idx = USERS.index(qp["user"])
    except: pass

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://d35aaqx5ub95lt.cloudfront.net/images/leagues/0e3ed60b2999bed9b757e7eb22f300c1.svg", width=100)
    current_user = st.selectbox("Quem é você?", USERS, index=default_idx)
    if current_user != st.query_params.get("user"): st.query_params["user"] = current_user
    st.divider()
    total_xp = 0
    for idx, row in df.iterrows():
        total_xp += calculate_xp(row["Data_Alvo"], row[f"{current_user}_Date"])
    st.metric("💎 XP Total", f"{total_xp}")

# --- ABAS ---
tab1, tab2, tab3 = st.tabs(["📚 Lições", "🏆 Placar", "⚙️ Admin"])

# ==========================================================
# ABA 1: LIÇÕES (VISUAL CORRIGIDO)
# ==========================================================
with tab1:
    semanas = df["Semana"].unique()
    sem = st.selectbox("Módulo:", semanas)
    df_view = df[df["Semana"] == sem]

    for index, row in df_view.iterrows():
        real_idx = df[df["ID"] == row["ID"]].index[0]
        status = row[f"{current_user}_Status"]
        data_gravada = row[f"{current_user}_Date"]
        pontos_garantidos = calculate_xp(row["Data_Alvo"], data_gravada)
        
        # Cores e Estilos
        hoje = date.today()
        data_alvo_dt = datetime.strptime(row["Data_Alvo"], "%Y-%m-%d").date()
        
        if status:
            cor_fundo_card = "#f7fff7"
            cor_borda = "#58cc02"
            cor_box_data = "transparent"
            cor_texto_data = "#58cc02"
            label_data = "FEITO"
            icone_data = "✅"
        elif hoje > data_alvo_dt:
            cor_fundo_card = "#ffffff"
            cor_borda = "#e5e5e5"
            cor_box_data = "#fff3cd"
            cor_texto_data = "#856404"
            label_data = "ATRASADO"
            icone_data = "⚠️"
        else:
            cor_fundo_card = "#ffffff"
            cor_borda = "#e5e5e5"
            cor_box_data = "#f8f9fa" # Cinza leve
            cor_texto_data = "#888888"
            label_data = "PRAZO"
            icone_data = "📅"

        # HTML DO CARD (AJUSTADO PARA NÃO BUGAR TEXTO)
        st.markdown(f"""
        <div style="
            background-color: {cor_fundo_card}; 
            border: 2px solid {cor_borda}; 
            border-radius: 16px; 
            margin-bottom: 10px; 
            box-shadow: 0 4px 0 #e5e5e5;
            display: flex;
            align-items: stretch;
            min-height: 80px; /* Garante altura mínima */
        ">
            <div style="
                width: 100px;
                min-width: 100px; /* Largura fixa para a data */
                background-color: {cor_box_data}; 
                color: {cor_texto_data};
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                border-right: 1px solid #eee;
                padding: 5px;
            ">
                <div style="font-size: 10px; font-weight: bold; margin-bottom: 2px; letter-spacing: 1px;">{label_data}</div>
                <div style="font-size: 20px;">{icone_data}</div>
                <div style="font-size: 14px; font-weight: bold; margin-top: 2px;">{row['Data_Alvo'][5:]}</div>
