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
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 4px 0 #e5e5e5;
    }
    
    /* Botões */
    .stButton > button {
        border-radius: 12px;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 0 rgba(0,0,0,0.2);
        transition: margin-top 0.1s, box-shadow 0.1s;
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
        # Dados Iniciais
        initial_data = [
            [1, "Semana 01", "2026-02-20", "Pediatria - Imunizações", "Foco: Calendário 0-15 meses.", "", False, None, False, None, False, None, False, None],
            [2, "Semana 01", "2026-02-21", "Preventiva - Vigilância", "Notificação Compulsória.", "", False, None, False, None, False, None, False, None],
            [3, "Semana 01", "2026-02-23", "Obstetrícia - Pré-Natal", "Rotina e Exames.", "", False, None, False, None, False, None, False, None],
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
    # Regra Anti-Roubo: Se tem data, tem ponto. Não importa o status atual.
    if pd.isna(completed_at) or str(completed_at) == "None" or str(completed_at) == "":
        return 0
    try:
        t = datetime.strptime(str(target), "%Y-%m-%d").date()
        c = datetime.strptime(str(completed_at), "%Y-%m-%d").date()
        if c <= t:
            return 100
        else:
            return 50
    except:
        return 0

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
    
    # XP Total (Baseado nas datas gravadas, independente se está checkado ou não)
    total_xp = 0
    for idx, row in df.iterrows():
        total_xp += calculate_xp(row["Data_Alvo"], row[f"{current_user}_Date"])
    
    st.metric("💎 XP Total", f"{total_xp}")

# --- ABAS ---
tab1, tab2, tab3 = st.tabs(["📚 Lições", "🏆 Placar", "⚙️ Admin"])

# ==========================================================
# ABA 1: LIÇÕES (COM TRAVA DE PONTUAÇÃO)
# ==========================================================
with tab1:
    semanas = df["Semana"].unique()
    sem = st.selectbox("Módulo:", semanas)
    df_view = df[df["Semana"] == sem]

    for index, row in df_view.iterrows():
        real_idx = df[df["ID"] == row["ID"]].index[0]
        
        status = row[f"{current_user}_Status"] # O check visual (True/False)
        data_gravada = row[f"{current_user}_Date"] # A data oficial da pontuação
        
        # Se tem data gravada, a pontuação já existe
        pontos_garantidos = calculate_xp(row["Data_Alvo"], data_gravada)
        
        # Estilo do Card
        style = 'border-color: #58cc02; background-color: #f7fff7;' if status else ''
        
        with st.container():
            st.markdown(f"""
            <div class="task-card" style="{style}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="flex:1; text-align:center; border-right: 2px solid #eee;">
                        <span style="font-size:12px; color:#888;">PRAZO</span><br>
                        <b>{row['Data_Alvo'][5:]}</b>
                    </div>
                    <div style="flex:4; padding-left:15px;">
                        <span style="font-size:18px; font-weight:bold; color:#4b4b4b;">{row['Tema']}</span><br>
                        <span style="font-size:14px; color:#777;">{row['Detalhes']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns([3, 1])
            with c1:
                with st.expander("📖 Ver Link"):
                    if row['Link_Questões']: st.markdown(f"🔗 [Abrir Questões]({row['Link_Questões']})")
                    else: 
                        nl = st.text_input("Link:", key=f"l_{row['ID']}")
                        if st.button("Salvar", key=f"sl_{row['ID']}"):
                            df.at[real_idx, "Link_Questões"] = nl
                            save_data(df); st.rerun()
            
            with c2:
                # CENÁRIO 1: TAREFA JÁ CHECKADA
                if status:
                    st.success(f"✅ FEITO!\n(+{pontos_garantidos})")
                    # Botão Refazer: Apenas desmarca visualmente (Status=False), mas MANTÉM a Data
                    if st.button("🔄 Refazer", key=f"re_{row['ID']}", help="Praticar de novo. Seus pontos não mudam."):
                        df.at[real_idx, f"{current_user}_Status"] = False
                        # NÃO apagamos a data! df.at[..., Date] continua o mesmo.
                        save_data(df); st.rerun()

                # CENÁRIO 2: TAREFA ABERTA (CHECK VAZIO)
                else:
                    # Se já tem data gravada (foi feita antes), avisa que é REVISÃO
                    if pontos_garantidos > 0:
                        st.caption(f"Revisando... (XP já garantido: {pontos_garantidos})")
                        if st.button("✅ Concluir (De novo)", key=f"chk2_{row['ID']}"):
                            df.at[real_idx, f"{current_user}_Status"] = True
                            # NÃO atualizamos a data, mantemos a original para não perder pontos
                            save_data(df); st.rerun()
                    
                    # Se nunca foi feita (Data vazia)
                    else:
                        hoje = str(date.today())
                        atrasado = hoje > row["Data_Alvo"]
                        lbl = "Concluir" if not atrasado else "Entregar (Atrasado)"
                        btn_type = "primary" if not atrasado else "secondary"
                        
                        if st.button(lbl, key=f"chk_{row['ID']}", type=btn_type):
                            df.at[real_idx, f"{current_user}_Status"] = True
                            df.at[real_idx, f"{current_user}_Date"] = hoje # Grava data pela 1ª vez
                            save_data(df); st.balloons(); st.rerun()

# ==========================================================
# ABA 2: RANKING
# ==========================================================
with tab2:
    st.subheader("🏆 Classificação")
    placar = []
    for u in USERS:
        pts = 0
        tasks = 0
        for i, r in df.iterrows():
            # Conta pontos se tiver Data (independente do status checkado)
            p = calculate_xp(r["Data_Alvo"], r[f"{u}_Date"])
            if p > 0:
                pts += p
                tasks += 1
        placar.append({"Médico": u, "XP": pts, "Tarefas": tasks})
        
    df_p = pd.DataFrame(placar).sort_values("XP", ascending=False).reset_index(drop=True)
    
    for i, row in df_p.iterrows():
        medalha = ["🥇", "🥈", "🥉", ""][i] if i < 4 else ""
        bg = "#fff5c2" if i == 0 else "#f9f9f9"
        st.markdown(f"""
        <div style="background-color:{bg}; padding:10px; border-radius:10px; margin-bottom:5px; border:1px solid #ddd; display:flex; justify-content:space-between;">
            <div><span style="font-size:20px;">{medalha}</span> <b>{row['Médico']}</b></div>
            <div style="text-align:right;"><b>{row['XP']} XP</b><br><small>{row['Tarefas']} lições</small></div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================================
# ABA 3: ADMIN
# ==========================================================
with tab3:
    st.write("Adicionar Tarefa")
    with st.form("add"):
        s = st.text_input("Semana", value="Semana 02")
        d = st.date_input("Data")
        t = st.text_input("Tema")
        dt = st.text_input("Detalhes")
        if st.form_submit_button("Salvar"):
            nid = df["ID"].max() + 1 if not df.empty else 1
            nrow = {"ID": nid, "Semana": s, "Data_Alvo": str(d), "Tema": t, "Detalhes": dt, "Link_Questões": ""}
            for u in USERS:
                nrow[f"{u}_Status"] = False; nrow[f"{u}_Date"] = None
            df = pd.concat([df, pd.DataFrame([nrow])], ignore_index=True)
            save_data(df); st.success("Ok!"); st.rerun()
