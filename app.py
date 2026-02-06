import streamlit as st
import pandas as pd
from datetime import datetime, date
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Desafio Enamed Duo", page_icon="🦉", layout="wide")

# --- INJEÇÃO DE CSS ESTILO DUOLINGO ---
def local_css():
    st.markdown("""
        <style>
        /* Importar fonte arredondada do Google */
        @import url('https://fonts.googleapis.com/css2?family=Varela+Round&display=swap');

        /* Aplicar fonte globalmente */
        html, body, [class*="css"] {
            font-family: 'Varela Round', sans-serif;
            color: #4b4b4b; /* Cinza escuro suave */
        }

        /* Cor de fundo principal */
        .stApp {
            background-color: #ffffff;
        }

        /* --- BOTÕES ESTILO DUOLINGO (Efeito 3D) --- */
        div.stButton > button {
            background-color: #58cc02 !important; /* Verde Duolingo */
            color: white !important;
            border: none !important;
            border-radius: 16px !important;
            padding: 12px 28px !important;
            font-size: 16px !important;
            font-weight: bold !important;
            border-bottom: 5px solid #45a300 !important; /* Sombra 3D verde escura */
            transition: all 0.1s ease-in-out;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
        }
        div.stButton > button:hover {
            transform: translateY(2px); /* Desce um pouco ao passar o mouse */
            border-bottom: 3px solid #45a300 !important;
        }
        div.stButton > button:active {
             transform: translateY(5px); /* Desce tudo ao clicar */
             border-bottom: none !important;
             box-shadow: none;
        }
        
        /* Botões secundários (Formulários) - Cor diferente */
        div[data-testid="stForm"] div.stButton > button {
            background-color: #1cb0f6 !important; /* Azul Duolingo */
            border-bottom: 5px solid #1899d6 !important;
        }

        /* --- CONTAINERS E EXPANDERS --- */
        /* Cabeçalho do Expander (O card da tarefa) */
        .streamlit-expanderHeader {
            background-color: #f7f7f7 !important;
            border-radius: 16px !important;
            border: 2px solid #e5e5e5 !important;
            color: #4b4b4b !important;
            font-weight: bold;
            padding: 15px !important;
        }
        /* Se a tarefa estiver feita (gambiarra visual) - Mudar cor da borda */
        /* Isso é difícil de fazer dinamicamente no Streamlit puro, mantendo simples */

        /* Conteúdo do Expander */
        div[data-testid="stExpanderDetails"] {
            border: 2px solid #e5e5e5;
            border-top: none;
            border-bottom-left-radius: 16px;
            border-bottom-right-radius: 16px;
            padding: 20px;
            background-color: #fff;
        }

        /* Inputs e Caixas de Seleção */
        .stTextInput > div > div > input, .stSelectbox > div > div > div, .stDateInput > div > div > input {
            border-radius: 12px !important;
            border: 2px solid #e5e5e5 !important;
            padding: 10px !important;
        }
        
        /* --- SIDEBAR --- */
        [data-testid="stSidebar"] {
            background-color: #f7f7f7;
            border-right: 2px solid #e5e5e5;
        }

        /* --- TABS (Abas) --- */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            border-radius: 12px 12px 0px 0px;
            gap: 2px;
            padding-top: 10px;
            padding-bottom: 10px;
            border: 2px solid #e5e5e5;
            border-bottom: none;
            background-color: #f7f7f7;
            font-weight: bold;
        }
        .stTabs [aria-selected="true"] {
            background-color: #ffffff !important;
            border-bottom: 3px solid #58cc02 !important; /* Verde na aba ativa */
             color: #58cc02 !important;
        }

        /* Títulos e Métricas */
        h1, h2, h3 {
            font-weight: 800 !important;
            color: #3c3c3c !important;
        }
        [data-testid="stMetricValue"] {
             color: #ffc800 !important; /* Amarelo Duolingo para números */
             font-weight: 900;
        }
        </style>
        """, unsafe_allow_html=True)

# Aplica o CSS
local_css()

# --- DADOS E CONEXÕES (MANTIDO DO CÓDIGO ANTERIOR) ---
SHEET_NAME = "Enamed_Database" 
USERS = ["Dr. Ana", "Dr. Bruno", "Dr. Carlos", "Dr. Daniel"]

def get_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client

def init_db():
    client = get_connection()
    try:
        sh = client.open(SHEET_NAME)
        worksheet = sh.sheet1
        if not worksheet.get_all_values():
            headers = ["ID", "Semana", "Data_Alvo", "Tema", "Detalhes", "Link_Questões",
                       "Dr. Ana_Status", "Dr. Ana_Date",
                       "Dr. Bruno_Status", "Dr. Bruno_Date",
                       "Dr. Carlos_Status", "Dr. Carlos_Date",
                       "Dr. Daniel_Status", "Dr. Daniel_Date"]
            worksheet.append_row(headers)
    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"Erro: Planilha '{SHEET_NAME}' não encontrada.")

def load_data():
    client = get_connection()
    sh = client.open(SHEET_NAME)
    worksheet = sh.sheet1
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    for col in df.columns:
        if "_Status" in col:
            df[col] = df[col].apply(lambda x: True if str(x).upper() == "TRUE" else False)
    return df

def update_row(row_id, col_name, new_value):
    client = get_connection()
    sh = client.open(SHEET_NAME)
    worksheet = sh.sheet1
    cell = worksheet.find(str(row_id))
    if cell:
        headers = worksheet.row_values(1)
        col_index = headers.index(col_name) + 1
        worksheet.update_cell(cell.row, col_index, str(new_value))

def calculate_score(target_date_str, completion_date_str):
    if not completion_date_str or str(completion_date_str).strip() == "":
        return 0
    try:
        target = datetime.strptime(str(target_date_str), "%Y-%m-%d").date()
        completion = datetime.strptime(str(completion_date_str), "%Y-%m-%d").date()
        if completion <= target:
            return 100 
        else:
            return 50
    except:
        return 0

# --- APP PRINCIPAL ---

# Cabeçalho Gamificado
c1, c2 = st.columns([3,1])
with c1:
    st.title("🦉 Desafio Enamed")
with c2:
    # Simulação de "Gemas" ou "Fogo"
    st.markdown("""
        <div style="text-align: right; font-size: 24px; font-weight: bold; color: #ffc800; background-color: #fff5d1; padding: 10px; border-radius: 16px; display: inline-block;">
        🔥 4 Dias Seguidos!
        </div>
    """, unsafe_allow_html=True)

try:
    df = load_data()
    if df.empty: init_db(); df = load_data()
except:
    init_db(); df = load_data()

# --- SIDEBAR COM VISUAL NOVO ---
with st.sidebar:
    st.image("https://d35aaqx5ub95lt.cloudfront.net/images/owl-yay.svg", width=120)
    st.write("### Quem vai estudar hoje?")
    current_user = st.selectbox("", USERS, label_visibility="collapsed")
    
    st.write("---")
    
    # Métricas Gamificadas
    prova_enamed = date(2026, 12, 11)
    dias = (prova_enamed - date.today()).days
    
    m1, m2 = st.columns(2)
    with m1:
        st.metric("💎 XP Total", "1250") # Exemplo estático
    with m2:
        st.metric("📅 Dias Restantes", f"{dias}")
        
    st.write("")
    if st.button("🔄 Sincronizar Dados"):
        st.rerun()

# --- ABAS REDESENHADAS ---
st.write("") # Espaço
tab1, tab2, tab3 = st.tabs(["📚 Lições", "🏆 Liga de Ouro", "⚙️ Adicionar"])

# ABA 1: TAREFAS (ESTILO LIÇÕES)
with tab1:
    semanas = df["Semana"].unique()
    filtro_semana = st.selectbox("Escolha seu módulo:", semanas)
    df_view = df[df["Semana"] == filtro_semana]

    st.write("") # Espaço
    
    for index, row in df_view.iterrows():
        feito = row[f"{current_user}_Status"]
        
        # Ícones diferentes dependendo do estado
        if feito:
            icone = "🌟 COMPLETO!"
            # Tentar mudar a cor do cabeçalho via markdown (limitado no expander)
            prefixo_estilo = "✅"
        else:
            data_alvo = datetime.strptime(str(row["Data_Alvo"]), "%Y-%m-%d").date()
            if date.today() > data_alvo:
                 icone = "⏰ ATRASADO"
                 prefixo_estilo = "⚠️"
            else:
                 icone = "🎯 A FAZER"
                 prefixo_estilo = "📘"

        # Usando emojis para dar cor ao título do Expander
        with st.expander(f"{prefixo_estilo} {row['Tema']} | Prazo: {row['Data_Alvo']}"):
            st.info(f"**Status:** {icone}")
            
            c_det, c_action = st.columns([2, 1])
            
            with c_det:
                st.markdown(f"**Foco da Lição:**\n\n{row['Detalhes']}")
                
                link_existente = row['Link_Questões']
                if link_existente and len(str(link_existente)) > 5:
                    st.markdown(f"""
                        <a href="{link_existente}" target="_blank" style="text-decoration: none;">
                            <div style="background-color: #1cb0f6; color: white; padding: 10px 20px; border-radius: 12px; border-bottom: 4px solid #1899d6; text-align: center; font-weight: bold; margin-top: 10px; display: inline-block;">
                            🔗 ABRIR QUESTÕES
                            </div>
                        </a>
                    """, unsafe_allow_html=True)
                else:
                    novo_link = st.text_input(f"Colar Link:", key=f"lnk_{row['ID']}", placeholder="https://...")
                    if st.button("Salvar Link", key=f"btn_lnk_{row['ID']}"):
                        update_row(row['ID'], 'Link_Questões', novo_link)
                        st.success("Link salvo!")

            with c_action:
                st.write("---")
                if not feito:
                    # Botão verde "suculento"
                    if st.button(f"✅ MARCAR COMO FEITO", key=f"done_{row['ID']}"):
                        hoje = str(date.today())
                        update_row(row['ID'], f"{current_user}_Status", "TRUE")
                        update_row(row['ID'], f"{current_user}_Date", hoje)
                        st.balloons()
                        st.rerun()
                else:
                    st.markdown(f"""
                        <div style="background-color: #e5e5e5; color: #4b4b4b; padding: 10px; border-radius: 12px; text-align: center; font-weight: bold;">
                        🎉 Concluído em {row[f'{current_user}_Date']}
                        </div>
                    """, unsafe_allow_html=True)

# ABA 2: PLACAR
with tab2:
    st.subheader("Liga de Ouro 🏆")
    scores = {u: 0 for u in USERS}
    for user in USERS:
        for idx, row in df.iterrows():
            scores[user] += calculate_score(row["Data_Alvo"], row[f"{user}_Date"])
    
    ranking = pd.DataFrame(list(scores.items()), columns=["Médico", "XP Total"]).sort_values("XP Total", ascending=False)
    
    # Usando HTML para um ranking mais bonito
    for i, row in ranking.iterrows():
        medalha = ["🥇", "🥈", "🥉", "💩"][i] if i < 4 else str(i+1)
        cor_fundo = "#fff5d1" if i == 0 else "#f7f7f7" # Dourado para o primeiro
        st.markdown(f"""
            <div style="background-color: {cor_fundo}; padding: 15px; border-radius: 16px; border: 2px solid #e5e5e5; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                <div style="font-size: 20px; font-weight: bold;">
                    <span style="font-size: 30px;">{medalha}</span> {row['Médico']}
                </div>
                 <div style="font-size: 24px; font-weight: 900; color: #ffc800;">
                    {row['XP Total']} XP
                </div>
            </div>
        """, unsafe_allow_html=True)

# ABA 3: ADMIN
with tab3:
    st.markdown("### Adicionar Nova Lição 📘")
    with st.form("add_task"):
        c1, c2 = st.columns(2)
        n_sem = c1.text_input("Módulo (Ex: Semana 02)")
        n_date = c2.date_input("Data Alvo")
        n_tema = st.text_input("Título da Lição")
        n_det = st.text_area("Detalhes do estudo")
        if st.form_submit_button("Criar Lição"):
            new_id = df["ID"].max() + 1 if not df.empty else 1
            new_row = {
                "ID": new_id, "Semana": n_sem, "Data_Alvo": str(n_date), 
                "Tema": n_tema, "Detalhes": n_det, "Link_Questões": "",
                "Dr. Ana_Status": "FALSE", "Dr. Ana_Date": "",
                "Dr. Bruno_Status": "FALSE", "Dr. Bruno_Date": "",
                "Dr. Carlos_Status": "FALSE", "Dr. Carlos_Date": "",
                "Dr. Daniel_Status": "FALSE", "Dr. Daniel_Date": ""
            }
            # Adiciona no Google Sheets
            client = get_connection()
            sh = client.open(SHEET_NAME)
            worksheet = sh.sheet1
            worksheet.append_row(list(new_row.values()))
            st.success("Lição criada com sucesso!")
            st.rerun()
