import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Desafio Enamed 4x4", page_icon="🩺", layout="wide")

# --- ARQUIVO DE DADOS ---
# ATENÇÃO: No Streamlit Cloud gratuito, arquivos CSV resetam quando o app reinicia.
# Para persistência real, seria necessário conectar ao Google Sheets.
# Este código usa persistência em memória/disco local temporário.
DATA_FILE = "cronograma_enamed.csv"

# Usuários do Grupo
USERS = ["Dr. Ana", "Dr. Bruno", "Dr. Carlos", "Dr. Daniel"]

# --- FUNÇÕES ---
def init_db():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=[
            "ID", "Semana", "Data_Alvo", "Tema", "Detalhes", "Link_Questões",
            "Dr. Ana_Status", "Dr. Ana_Date",
            "Dr. Bruno_Status", "Dr. Bruno_Date",
            "Dr. Carlos_Status", "Dr. Carlos_Date",
            "Dr. Daniel_Status", "Dr. Daniel_Date"
        ])
        # Dados Iniciais (Exemplo Semana 01)
        initial_data = [
            [1, "Semana 01", "2026-02-20", "Pediatria - Imunizações", "Foco: Calendário 0-15 meses. Vacinas 2, 4, 6 meses.", "", False, None, False, None, False, None, False, None],
            [2, "Semana 01", "2026-02-21", "Preventiva - Vigilância", "Foco: Notificação Compulsória (Imediata vs Semanal).", "", False, None, False, None, False, None, False, None],
            [3, "Semana 01", "2026-02-23", "Obstetrícia - Pré-Natal", "Foco: Exames por trimestre e regras do MS.", "", False, None, False, None, False, None, False, None],
            [4, "Semana 01", "2026-02-24", "Infecto - Arboviroses", "Foco: Dengue (Classificação A, B, C, D) e Hidratação.", "", False, None, False, None, False, None, False, None],
            [5, "Semana 01", "2026-02-25", "Cirurgia - Pediatria", "Foco: Hérnias e Estenose de Piloro.", "", False, None, False, None, False, None, False, None],
        ]
        for row in initial_data:
            df.loc[len(df)] = row
        df.to_csv(DATA_FILE, index=False)

def load_data():
    if not os.path.exists(DATA_FILE):
        init_db()
    return pd.read_csv(DATA_FILE)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def calculate_score(target_date_str, completion_date_str):
    if pd.isna(completion_date_str) or str(completion_date_str) == "nan" or completion_date_str is None:
        return 0
    try:
        target = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        completion = datetime.strptime(str(completion_date_str).split(' ')[0], "%Y-%m-%d").date() # Ajuste para garantir formato
        if completion <= target:
            return 100 
        else:
            return 50
    except:
        return 0

# --- INÍCIO DO APP ---
st.title("🩺 Desafio Enamed - Rumo à Residência")

# Verifica se o arquivo existe, se não, cria
if 'first_run' not in st.session_state:
    init_db()
    st.session_state['first_run'] = True

try:
    df = load_data()
except:
    init_db()
    df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.header("Painel do Médico")
    current_user = st.selectbox("Quem é você?", USERS)
    
    st.divider()
    prova_enamed = date(2026, 12, 11)
    hoje = date.today()
    dias_restantes = (prova_enamed - hoje).days
    st.metric("Dias até o Enamed", f"{dias_restantes}", "Foco total!")

# --- ABAS ---
tab1, tab2, tab3 = st.tabs(["📅 Tarefas", "🏆 Placar", "⚙️ Admin"])

# ABA 1: TAREFAS
with tab1:
    semanas = df["Semana"].unique()
    filtro_semana = st.selectbox("Selecione a Semana:", semanas)
    df_view = df[df["Semana"] == filtro_semana]

    for index, row in df_view.iterrows():
        # Status visual
        feito = row[f"{current_user}_Status"]
        cor_card = "green" if feito else "blue"
        icone = "✅" if feito else "⬜"
        
        with st.expander(f"{icone} {row['Data_Alvo']} | {row['Tema']}"):
            st.write(f"**Detalhes:** {row['Detalhes']}")
            
            # Link
            link_existente = row['Link_Questões']
            if pd.notna(link_existente) and len(str(link_existente)) > 5:
                st.markdown(f"🔗 [Clique aqui para fazer as Questões]({link_existente})")
            else:
                novo_link = st.text_input(f"Colar link (ID {row['ID']}):", key=f"lnk_{row['ID']}")
                if st.button("Salvar Link", key=f"btn_lnk_{row['ID']}"):
                    df.at[index, 'Link_Questões'] = novo_link
                    save_data(df)
                    st.success("Salvo! Recarregue a página.")

            # Checkbox de conclusão
            if not feito:
                if st.button(f"Marcar como FEITO", key=f"done_{row['ID']}"):
                    df.at[index, f"{current_user}_Status"] = True
                    df.at[index, f"{current_user}_Date"] = str(date.today())
                    save_data(df)
                    st.balloons()
                    st.rerun()
            else:
                st.info(f"Concluído em: {row[f'{current_user}_Date']}")

# ABA 2: PLACAR
with tab2:
    st.subheader("Ranking Geral")
    scores = {}
    
    for user in USERS:
        total_pontos = 0
        for idx, row in df.iterrows():
            total_pontos += calculate_score(row["Data_Alvo"], row[f"{user}_Date"])
        scores[user] = total_pontos
    
    ranking = pd.DataFrame(list(scores.items()), columns=["Médico", "Pontos"]).sort_values("Pontos", ascending=False)
    st.bar_chart(ranking, x="Médico", y="Pontos")
    st.dataframe(ranking, hide_index=True)

# ABA 3: ADMIN
with tab3:
    st.write("Adicionar nova tarefa para todos:")
    with st.form("add_task"):
        n_sem = st.text_input("Semana (Ex: Semana 02)")
        n_date = st.date_input("Data Alvo")
        n_tema = st.text_input("Tema")
        n_det = st.text_input("Detalhes")
        if st.form_submit_button("Criar"):
            new_row = {"ID": df["ID"].max()+1, "Semana": n_sem, "Data_Alvo": str(n_date), "Tema": n_tema, "Detalhes": n_det, "Link_Questões": ""}
            for u in USERS:
                new_row[f"{u}_Status"] = False
                new_row[f"{u}_Date"] = None
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success("Adicionado!")
            st.rerun()
