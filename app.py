import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# --- CONFIGURAÇÃO DA PÁGINA (ESTÉTICA) ---
st.set_page_config(page_title="Enamed Game", page_icon="🦉", layout="centered")

# --- CSS PARA VISUAL "DUOLINGO" (SEGURO) ---
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
        box-shadow: 0 4px 0 #e5e5e5; /* Sombra sólida estilo game */
    }
    
    /* Botão de Ação */
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
    
    /* Cores de Status */
    .status-gold { color: #ffc800; font-weight: bold; }
    .status-green { color: #58cc02; font-weight: bold; }
    .status-red { color: #ff4b4b; font-weight: bold; }
    
    </style>
""", unsafe_allow_html=True)

# --- DADOS E VARIÁVEIS ---
USERS = ["Dr. Ana", "Dr. Bruno", "Dr. Carlos", "Dr. Daniel"]
CSV_FILE = "enamed_data.csv"

# --- FUNÇÕES DE BANCO DE DADOS ---
def init_db():
    # Cria o arquivo se não existir
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=[
            "ID", "Semana", "Data_Alvo", "Tema", "Detalhes", "Link_Questões",
            "Dr. Ana_Status", "Dr. Ana_Date",
            "Dr. Bruno_Status", "Dr. Bruno_Date",
            "Dr. Carlos_Status", "Dr. Carlos_Date",
            "Dr. Daniel_Status", "Dr. Daniel_Date"
        ])
        # Dados de Exemplo
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
            return 100 # Pontuação Cheia (Verde)
        else:
            return 50  # Metade (Amarelo)
    except:
        return 0

# --- INICIALIZAÇÃO ---
st.title("🦉 Desafio Enamed")

# Carrega ou Cria Dados
df = load_data()

# --- BARRA LATERAL (SELEÇÃO DE PERFIL) ---
with st.sidebar:
    st.image("https://d35aaqx5ub95lt.cloudfront.net/images/leagues/0e3ed60b2999bed9b757e7eb22f300c1.svg", width=100)
    st.write("### Quem está estudando?")
    current_user = st.selectbox("Selecione seu perfil", USERS)
    
    st.divider()
    
    # Cálculo de XP Total
    total_xp = 0
    for idx, row in df.iterrows():
        total_xp += calculate_xp(row["Data_Alvo"], row[f"{current_user}_Date"])
    
    st.metric("💎 XP Total", f"{total_xp}")
    st.caption("Meta: 5000 XP")

# --- ABAS ---
tab_licoes, tab_rank, tab_admin = st.tabs(["📚 Lições do Dia", "🏆 Placar", "⚙️ Admin"])

# ==========================================================
# ABA 1: LIÇÕES (A CORREÇÃO PRINCIPAL ESTÁ AQUI)
# ==========================================================
with tab_licoes:
    
    # Filtro de Semana
    semanas = df["Semana"].unique()
    col_filter, _ = st.columns(2)
    with col_filter:
        sem_selecionada = st.selectbox("Escolha o Módulo:", semanas)

    # Filtra dados
    df_view = df[df["Semana"] == sem_selecionada]

    for index, row in df_view.iterrows():
        # Pega o índice real para salvar depois
        real_idx = df[df["ID"] == row["ID"]].index[0]
        
        # Status Atual
        is_done = row[f"{current_user}_Status"]
        done_date = row[f"{current_user}_Date"]
        target_date = row["Data_Alvo"]
        
        # --- DESENHO DO CARD (CAIXA) ---
        with st.container():
            # A moldura visual é feita com st.markdown simulando um container
            st.markdown(f"""
            <div class="task-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="flex:1; text-align:center; border-right: 2px solid #f0f0f0; padding-right:10px;">
                        <span style="font-size:12px; color:#888;">DATA</span><br>
                        <span style="font-size:16px; font-weight:bold;">{target_date[5:]}</span> </div>
                    <div style="flex:4; padding-left:15px;">
                        <span style="font-size:18px; font-weight:bold; color:#4b4b4b;">{row['Tema']}</span><br>
                        <span style="font-size:14px; color:#777;">{row['Detalhes'][:50]}...</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # --- LÓGICA DE BOTÕES E STATUS (ABAIXO DO VISUAL) ---
            c1, c2 = st.columns([3, 1])
            
            with c1:
                with st.expander("📖 Ver Detalhes e Link"):
                    st.write(f"**Foco:** {row['Detalhes']}")
                    if row['Link_Questões']:
                        st.markdown(f"🔗 [Clique para ir às Questões]({row['Link_Questões']})")
                    else:
                        new_link = st.text_input("Colar Link:", key=f"lk_{row['ID']}")
                        if st.button("Salvar", key=f"s_{row['ID']}"):
                            df.at[real_idx, "Link_Questões"] = new_link
                            save_data(df)
                            st.rerun()

            with c2:
                # SE JÁ FEZ: MOSTRA O RESULTADO COLORIDO
                if is_done:
                    # Calcula se foi pontuação cheia ou metade
                    pontos = calculate_xp(target_date, done_date)
                    
                    if pontos == 100:
                        st.success(f"✅ FEITO! \n(+100 XP)")
                    else:
                        st.warning(f"⚠️ ATRASADO \n(+50 XP)")
                        st.caption(f"Fez em: {done_date}")
                
                # SE NÃO FEZ: MOSTRA O BOTÃO
                else:
                    # Verifica se já está atrasado para mudar o aviso
                    hoje = str(date.today())
                    atrasado = hoje > target_date
                    
                    label_btn = "Concluir" if not atrasado else "Concluir com Atraso"
                    
                    if st.button(label_btn, key=f"chk_{row['ID']}", type="primary" if not atrasado else "secondary"):
                        df.at[real_idx, f"{current_user}_Status"] = True
                        df.at[real_idx, f"{current_user}_Date"] = str(date.today())
                        save_data(df)
                        st.balloons()
                        st.rerun()

# ==========================================================
# ABA 2: RANKING (CORRIGIDO)
# ==========================================================
with tab_rank:
    st.subheader("🏆 Liga dos Campeões")
    
    placar = []
    
    for u in USERS:
        pts = 0
        tarefas_feitas = 0
        for i, r in df.iterrows():
            if r[f"{u}_Status"]:
                pts += calculate_xp(r["Data_Alvo"], r[f"{u}_Date"])
                tarefas_feitas += 1
        placar.append({"Médico": u, "XP": pts, "Tarefas": tarefas_feitas})
        
    df_placar = pd.DataFrame(placar).sort_values("XP", ascending=False).reset_index(drop=True)
    
    # Exibe visualmente
    for i, linha in df_placar.iterrows():
        cor_fundo = "#fff5c2" if i == 0 else "#f9f9f9" # Dourado para o 1º
        emoji = ["🥇", "🥈", "🥉", "❄️"][i] if i < 4 else ""
        
        st.markdown(f"""
        <div style="background-color:{cor_fundo}; padding:15px; border-radius:12px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; border:2px solid #eee;">
            <div>
                <span style="font-size:24px;">{emoji}</span>
                <span style="font-size:18px; font-weight:bold; margin-left:10px;">{linha['Médico']}</span>
            </div>
            <div style="text-align:right;">
                <span style="font-size:20px; font-weight:bold; color:#ffc800;">{linha['XP']} XP</span><br>
                <span style="font-size:12px; color:#666;">{linha['Tarefas']} lições</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================================
# ABA 3: ADMIN (FUNCIONANDO)
# ==========================================================
with tab_admin:
    st.write("Adicionar Tarefa")
    with st.form("nova"):
        c1, c2 = st.columns(2)
        ns = c1.text_input("Semana (Ex: Semana 02)")
        nd = c2.date_input("Data Alvo")
        nt = st.text_input("Tema")
        nde = st.text_input("Detalhes")
        
        if st.form_submit_button("Criar"):
            new_id = df["ID"].max() + 1 if not df.empty else 1
            new_row = {
                "ID": new_id, "Semana": ns, "Data_Alvo": str(nd), 
                "Tema": nt, "Detalhes": nde, "Link_Questões": ""
            }
            # Adiciona colunas vazias para usuários
            for u in USERS:
                new_row[f"{u}_Status"] = False
                new_row[f"{u}_Date"] = None
                
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success("Adicionado!")
            st.rerun()
