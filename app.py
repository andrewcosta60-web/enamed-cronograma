import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import html

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Enamed Game", page_icon="🦉", layout="centered")

# --- CSS GLOBAL ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Varela+Round&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Varela Round', sans-serif;
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
    
    /* Input de Texto */
    .stTextInput > div > div > input {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÕES ---
CSV_FILE = "enamed_data.csv"
DEFAULT_USERS = [] 

# Lista de Avatares Disponíveis
AVATARS = [
    "👨‍⚕️", "👩‍⚕️", "🦉", "🧠", "🫀", "🧬", "🚑", "🏥", "💉", "💊", 
    "🦠", "🩸", "🎓", "🦁", "🦊", "🐼", "🐨", "🐯", "🦖", "🚀", "💡", "🔥"
]

# --- FUNÇÕES ---

def get_users_from_df(df):
    """Descobre quem são os usuários olhando as colunas do arquivo"""
    users = []
    for col in df.columns:
        if col.endswith("_Status"):
            user_name = col.replace("_Status", "")
            users.append(user_name)
    return sorted(users)

def init_db():
    """Cria o arquivo CSV se não existir"""
    if not os.path.exists(CSV_FILE):
        cols = ["ID", "Semana", "Data_Alvo", "Tema", "Detalhes", "Link_Questões"]
        for user in DEFAULT_USERS:
            cols.extend([f"{user}_Status", f"{user}_Date"])
            
        df = pd.DataFrame(columns=cols)
        
        initial_data = []
        row1 = [1, "Semana 01", "2026-02-20", "Pediatria - Imunizações", "Foco: Calendário 0-15 meses.", ""]
        for _ in DEFAULT_USERS: row1.extend([False, None])
        initial_data.append(row1)
        
        row2 = [2, "Semana 01", "2026-02-21", "Preventiva - Vigilância", "Notificação Compulsória.", ""]
        for _ in DEFAULT_USERS: row2.extend([False, None])
        initial_data.append(row2)

        for r in initial_data:
            df.loc[len(df)] = r
            
        df.to_csv(CSV_FILE, index=False)

def load_data():
    if not os.path.exists(CSV_FILE): init_db()
    return pd.read_csv(CSV_FILE)

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def add_new_user(df, new_name):
    """Adiciona colunas para um novo usuário no DataFrame e Salva"""
    if f"{new_name}_Status" in df.columns:
        return df, False, "Esse nome já existe!"
    
    # Cria as colunas
    df[f"{new_name}_Status"] = False
    df[f"{new_name}_Date"] = None
    
    save_data(df)
    return df, True, "Usuário criado com sucesso!"

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
df = load_data()
ALL_USERS = get_users_from_df(df)

# --- TELA DE LOGIN ---
if "logged_user" not in st.session_state:
    qp = st.query_params
    if "user" in qp and qp["user"] in ALL_USERS:
        st.session_state["logged_user"] = qp["user"]
        st.rerun()
    
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 6, 1])
        with c2:
            # CORUJA GIGANTE NO LOGIN TAMBÉM
            st.markdown("<div style='text-align: center; font-size: 80px;'>🦉</div>", unsafe_allow_html=True)
            st.markdown("<h1 style='text-align: center;'>Desafio Enamed</h1>", unsafe_allow_html=True)
            
            tab_login, tab_register = st.tabs(["🔑 Entrar", "➕ Novo Participante"])
            
            # ABA DE LOGIN
            with tab_login:
                if not ALL_USERS:
                    st.info("Nenhum participante encontrado. Cadastre o primeiro na aba ao lado! 👉")
                else:
                    st.write("### Quem é você?")
                    user_input = st.selectbox("Selecione seu perfil:", ALL_USERS)
                    if st.button("🚀 ENTRAR", type="primary"):
                        if user_input:
                            st.session_state["logged_user"] = user_input
                            st.rerun()
                        else:
                            st.warning("Selecione um usuário.")

            # ABA DE CADASTRO (COM SELEÇÃO DE EMOJI)
            with tab_register:
                st.write("### Criar novo perfil")
                
                col_emoji, col_nome = st.columns([1, 3])
                
                with col_emoji:
                    selected_avatar = st.selectbox("Avatar", AVATARS)
                
                with col_nome:
                    input_name = st.text_input("Seu Nome (ex: Dr. João)")
                
                # Monta o nome final
                final_name = f"{selected_avatar} {input_name}" if input_name else ""
                
                if input_name:
                    st.caption(f"Como vai aparecer: **{final_name}**")
                
                if st.button("Salvar e Entrar"):
                    if input_name and len(input_name) > 2:
                        df, success, msg = add_new_user(df, final_name)
                        if success:
                            st.success(msg)
                            st.session_state["logged_user"] = final_name
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("Digite um nome válido.")
        
        st.stop()

# --- APP PRINCIPAL ---
current_user = st.session_state["logged_user"]

# --- SIDEBAR (BARRA LATERAL) ---
with st.sidebar:
    # --- AQUI: AUMENTAMOS A CORUJA PARA 100PX ---
    st.markdown("<div style='text-align: center; font-size: 100px; margin-bottom: 20px;'>🦉</div>", unsafe_allow_html=True)
    
    st.markdown(f"### Olá, **{current_user}**! 👋")
    
    if st.button("Sair"):
        del st.session_state["logged_user"]
        st.query_params.clear()
        st.rerun()

    st.divider()
    total_xp = 0
    for idx, row in df.iterrows():
        if f"{current_user}_Date" in df.columns:
            total_xp += calculate_xp(row["Data_Alvo"], row[f"{current_user}_Date"])
    st.metric("💎 XP Total", f"{total_xp}")

st.title("🦉 Desafio Enamed")

# --- ABAS ---
tab1, tab2, tab3 = st.tabs(["📚 Lições", "🏆 Placar", "⚙️ Admin"])

# ==========================================================
# ABA 1: LIÇÕES
# ==========================================================
with tab1:
    semanas = df["Semana"].unique()
    sem = st.selectbox("Módulo:", semanas)
    df_view = df[df["Semana"] == sem]

    for index, row in df_view.iterrows():
        real_idx = df[df["ID"] == row["ID"]].index[0]
        
        if f"{current_user}_Status" not in df.columns:
            st.error("Erro no perfil. Tente relogar.")
            continue

        status = row[f"{current_user}_Status"]
        data_gravada = row[f"{current_user}_Date"]
        pontos_garantidos = calculate_xp(row["Data_Alvo"], data_gravada)
        
        hoje = date.today()
        try: data_alvo_dt = datetime.strptime(str(row["Data_Alvo"]), "%Y-%m-%d").date()
        except: data_alvo_dt = date.today()
        
        bg_tema = "#ffffff"
        border_tema = "#e5e5e5"
        
        if status:
            border_data = "#58cc02"
            bg_data = "#e6fffa" 
            text_data = "#58cc02"
            label = "FEITO"
            icone = "✅"
            border_tema = "#58cc02"
        elif hoje > data_alvo_dt:
            border_data = "#ffc800"
            bg_data = "#fff5d1"
            text_data = "#d4a000"
            label = "ATRASADO"
            icone = "⚠️"
            border_tema = "#ffc800"
        else:
            border_data = "#e5e5e5"
            bg_data = "#f7f7f7"
            text_data = "#afafaf"
            label = "PRAZO"
            icone = "📅"

        tema_txt = html.escape(str(row['Tema']))
        detalhes_txt = html.escape(str(row['Detalhes']))
        data_txt = str(row['Data_Alvo'])[5:]

        html_content = f"""
<div style="display: flex; gap: 15px; align-items: stretch; width: 100%; margin-bottom: 15px; font-family: 'Varela Round', sans-serif;">
<div style="flex: 0 0 100px; background-color: {bg_data}; border: 2px solid {border_data}; border-radius: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 10px; color: {text_data}; box-shadow: 0 4px 0 rgba(0,0,0,0.05);">
<div style="font-size: 10px; font-weight: bold; margin-bottom: 5px;">{label}</div>
<div style="font-size: 24px;">{icone}</div>
<div style="font-size: 14px; font-weight: bold; margin-top: 5px;">{data_txt}</div>
</div>
<div style="flex: 1; background-color: {bg_tema}; border: 2px solid {border_tema}; border-radius: 12px; padding: 15px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 4px 0 rgba(0,0,0,0.05);">
<div style="font-size: 17px; font-weight: bold; color: #4b4b4b; line-height: 1.2; margin-bottom: 5px;">{tema_txt}</div>
<div style="font-size: 13px; color: #888; line-height: 1.4;">{detalhes_txt}</div>
</div>
</div>
"""
        st.markdown(html_content, unsafe_allow_html=True)

        c1, c2 = st.columns([3, 1])
        with c1:
            with st.expander("📂 Acessar conteúdo extra"): 
                if row['Link_Questões']: st.markdown(f"🔗 [Abrir Questões]({row['Link_Questões']})")
                else: 
                    nl = st.text_input("Link:", key=f"l_{row['ID']}")
                    if st.button("Salvar", key=f"sl_{row['ID']}"):
                        df.at[real_idx, "Link_Questões"] = nl
                        save_data(df); st.rerun()
        
        with c2:
            if status:
                st.success(f"✅ FEITO! (+{pontos_garantidos})")
                if st.button("🔄 Refazer", key=f"re_{row['ID']}"):
                    df.at[real_idx, f"{current_user}_Status"] = False
                    save_data(df); st.rerun()
            else:
                if pontos_garantidos > 0:
                    if st.button("✅ Concluir", key=f"chk2_{row['ID']}"):
                        df.at[real_idx, f"{current_user}_Status"] = True
                        save_data(df); st.rerun()
                    st.markdown(f"<div style='text-align:center; font-size:11px; color:#999; font-family:Varela Round;'>↺ XP: {pontos_garantidos}</div>", unsafe_allow_html=True)
                else:
                    hoje_str = str(date.today())
                    atrasado = hoje > data_alvo_dt
                    lbl = "Concluir" if not atrasado else "Entregar"
                    btn_type = "primary" if not atrasado else "secondary"
                    if st.button(lbl, key=f"chk_{row['ID']}", type=btn_type):
                        df.at[real_idx, f"{current_user}_Status"] = True
                        df.at[real_idx, f"{current_user}_Date"] = hoje_str
                        save_data(df); st.balloons(); st.rerun()
        
        st.write("") 

# ==========================================================
# ABA 2: RANKING (CORRIGIDO PARA TEXTO PRETO)
# ==========================================================
with tab2:
    st.subheader("🏆 Classificação")
    placar = []
    
    for u in ALL_USERS:
        pts = 0
        tasks = 0
        for i, r in df.iterrows():
            if f"{u}_Date" in df.columns:
                p = calculate_xp(r["Data_Alvo"], r[f"{u}_Date"])
                if p > 0:
                    pts += p
                    tasks += 1
        placar.append({"Médico": u, "XP": pts, "Tarefas": tasks})
        
    df_p = pd.DataFrame(placar).sort_values("XP", ascending=False).reset_index(drop=True)
    
    for i, row in df_p.iterrows():
        medalha = ["🥇", "🥈", "🥉", ""][i] if i < 4 else ""
        bg = "#fff5c2" if i == 0 else "#f9f9f9"
        
        # Adicionei 'color: black' no estilo do div principal
        st.markdown(f"""
        <div style="background-color:{bg}; padding:10px; border-radius:10px; margin-bottom:5px; border:1px solid #ddd; display:flex; justify-content:space-between; font-family: 'Varela Round', sans-serif; color: black;">
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
        c1, c2 = st.columns(2)
        s = c1.text_input("Semana", value="Semana 02")
        d = c2.date_input("Data")
        t = st.text_input("Tema")
        dt = st.text_input("Detalhes")
        if st.form_submit_button("Salvar"):
            nid = df["ID"].max() + 1 if not df.empty else 1
            nrow = {"ID": nid, "Semana": s, "Data_Alvo": str(d), "Tema": t, "Detalhes": dt, "Link_Questões": ""}
            for u in ALL_USERS:
                nrow[f"{u}_Status"] = False
                nrow[f"{u}_Date"] = None
            
            df = pd.concat([df, pd.DataFrame([nrow])], ignore_index=True)
            save_data(df); st.success("Ok!"); st.rerun()

    st.divider()
    st.write("### 🚨 Zona de Perigo")
    
    if st.button("🗑️ ZERAR BANCO DE DADOS (Limpar Tudo)", type="primary"):
        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.warning("Banco de dados apagado! Por favor, atualize a página (F5).")
        else:
            st.info("O banco de dados já está limpo.")
