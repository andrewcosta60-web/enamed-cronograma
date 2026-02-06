import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Enamed Game", page_icon="🦉", layout="centered")

# --- CSS VISUAL (ESTILO DUOLINGO / CLEAN) ---
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
    
    /* Ajustes Gerais */
    .status-done { background-color: #dff6dd; border-color: #58cc02; }
    
    </style>
""", unsafe_allow_html=True)

# --- DADOS E VARIÁVEIS ---
USERS = ["Dr. Ana", "Dr. Bruno", "Dr. Carlos", "Dr. Daniel"]
CSV_FILE = "enamed_data.csv"

# --- FUNÇÕES DE BANCO DE DADOS ---
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
            [3, "Semana 01", "2026-02-23", "Obstetrícia - Pré-Natal", "Rotina e Exames.", "", False, None, False, None, False, None, False, None],
        ]
        for row in initial_data:
            df.loc[len(df)] = row
        df.to_csv(CSV_FILE, index=False)

def load_data():
    if not os.path.exists(CSV_FILE):
        init_db()
    return pd.read_csv(CSV_FILE)

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def calculate_xp(target, completed_at):
    if pd.isna(completed_at) or str(completed_at) == "None":
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

# --- LÓGICA DE LOGIN PERSISTENTE (URL) ---
# Verifica se tem usuário na URL
query_params = st.query_params
default_idx = 0

if "user" in query_params:
    try:
        user_param = query_params["user"]
        if user_param in USERS:
            default_idx = USERS.index(user_param)
    except:
        pass

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://d35aaqx5ub95lt.cloudfront.net/images/leagues/0e3ed60b2999bed9b757e7eb22f300c1.svg", width=100)
    
    st.write("### Identificação")
    # O selectbox já começa com o índice pego da URL
    current_user = st.selectbox("Quem é você?", USERS, index=default_idx)
    
    # Atualiza a URL se mudar o usuário (Isso faz o login "fixar")
    if current_user != st.query_params.get("user"):
        st.query_params["user"] = current_user
    
    st.info(f"💡 **Dica:** Salve esta página nos favoritos. Como o seu nome está no link, você entrará direto como **{current_user}** da próxima vez!")
    
    st.divider()
    
    # XP Total
    total_xp = 0
    for idx, row in df.iterrows():
        total_xp += calculate_xp(row["Data_Alvo"], row[f"{current_user}_Date"])
    
    st.metric("💎 XP Total", f"{total_xp}")

# --- ABAS ---
tab_licoes, tab_rank, tab_admin = st.tabs(["📚 Lições do Dia", "🏆 Placar", "⚙️ Admin"])

# ==========================================================
# ABA 1: LIÇÕES (COM BOTÃO DE REINICIAR)
# ==========================================================
with tab_licoes:
    semanas = df["Semana"].unique()
    sem_selecionada = st.selectbox("Módulo:", semanas)
    df_view = df[df["Semana"] == sem_selecionada]

    for index, row in df_view.iterrows():
        real_idx = df[df["ID"] == row["ID"]].index[0]
        
        is_done = row[f"{current_user}_Status"]
        done_date = row[f"{current_user}_Date"]
        target_date = row["Data_Alvo"]
        
        # Estilo diferente se estiver feito
        card_style = 'border-color: #58cc02; background-color: #f7fff7;' if is_done else ''
        
        with st.container():
            st.markdown(f"""
            <div class="task-card" style="{card_style}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="flex:1; text-align:center; border-right: 2px solid #eee; padding-right:10px;">
                        <span style="font-size:12px; color:#888;">PRAZO</span><br>
                        <span style="font-size:16px; font-weight:bold;">{target_date[5:]}</span>
                    </div>
                    <div style="flex:4; padding-left:15px;">
                        <span style="font-size:18px; font-weight:bold; color:#4b4b4b;">{row['Tema']}</span><br>
                        <span style="font-size:14px; color:#777;">{row['Detalhes'][:60]}...</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns([3, 1])
            
            with c1:
                with st.expander("📖 Ver Link / Detalhes"):
                    st.write(f"**Foco:** {row['Detalhes']}")
                    
                    # Link sempre visível (mesmo se concluído, para revisão)
                    if row['Link_Questões']:
                        st.markdown(f"🔗 [**Abrir Banco de Questões**]({row['Link_Questões']})")
                    else:
                        new_link = st.text_input("Colar Link:", key=f"lk_{row['ID']}")
                        if st.button("Salvar Link", key=f"s_{row['ID']}"):
                            df.at[real_idx, "Link_Questões"] = new_link
                            save_data(df)
                            st.rerun()

            with c2:
                if is_done:
                    pontos = calculate_xp(target_date, done_date)
                    texto_pontos = "+100 XP" if pontos == 100 else "+50 XP"
                    st.success(f"✅ FEITO!\n({texto_pontos})")
                    
                    # --- BOTÃO DE REINICIAR (NOVA FUNCIONALIDADE) ---
                    # Usa uma chave única para não conflitar
                    if st.button("🔄 Refazer", key=f"redo_{row['ID']}", help="Reiniciar para praticar. A nota será recalculada quando terminar de novo."):
                        df.at[real_idx, f"{current_user}_Status"] = False
                        df.at[real_idx, f"{current_user}_Date"] = None
                        save_data(df)
                        st.rerun()
                
                else:
                    hoje = str(date.today())
                    atrasado = hoje > target_date
                    lbl = "Concluir" if not atrasado else "Entregar (Atrasado)"
                    tipo_btn = "primary" if not atrasado else "secondary"
                    
                    if st.button(lbl, key=f"chk_{row['ID']}", type=tipo_btn):
                        df.at[real_idx, f"{current_user}_Status"] = True
                        df.at[real_idx, f"{current_user}_Date"] = hoje
                        save_data(df)
                        st.balloons()
                        st.rerun()

# ==========================================================
# ABA 2: RANKING
# ==========================================================
with tab_rank:
    st.subheader("🏆 Classificação Geral")
    placar = []
    for u in USERS:
        pts = 0
        tarefas = 0
        for i, r in df.iterrows():
            if r[f"{u}_Status"]:
                pts += calculate_xp(r["Data_Alvo"], r[f"{u}_Date"])
                tarefas += 1
        placar.append({"Médico": u, "XP": pts, "Tarefas": tarefas})
        
    df_placar = pd.DataFrame(placar).sort_values("XP", ascending=False).reset_index(drop=True)
    
    for i, linha in df_placar.iterrows():
        cor = "#fff5c2" if i == 0 else "#f9f9f9"
        medalha = ["🥇", "🥈", "🥉", "❄️"][i] if i < 4 else ""
        st.markdown(f"""
        <div style="background-color:{cor}; padding:15px; border-radius:12px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; border:2px solid #eee;">
            <div><span style="font-size:24px;">{medalha}</span> <b>{linha['Médico']}</b></div>
            <div style="text-align:right;"><span style="color:#ffc800; font-weight:900; font-size:18px;">{linha['XP']} XP</span><br><small>{linha['Tarefas']} lições</small></div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================================
# ABA 3: ADMIN
# ==========================================================
with tab_admin:
    st.write("Adicionar Tarefa")
    with st.form("nova"):
        c1, c2 = st.columns(2)
        ns = c1.text_input("Semana", value="Semana 02")
        nd = c2.date_input("Data")
        nt = st.text_input("Tema")
        nde = st.text_input("Detalhes")
        if st.form_submit_button("Criar"):
            new_id = df["ID"].max() + 1 if not df.empty else 1
            new_row = {
                "ID": new_id, "Semana": ns, "Data_Alvo": str(nd), 
                "Tema": nt, "Detalhes": nde, "Link_Questões": ""
            }
            for u in USERS:
                new_row[f"{u}_Status"] = False
                new_row[f"{u}_Date"] = None
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success("Criado!")
            st.rerun()
