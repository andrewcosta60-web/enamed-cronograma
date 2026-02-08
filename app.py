import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json
import base64
import io
from PIL import Image

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Enamed Oficial", page_icon="🏥", layout="wide")

# --- CSS GLOBAL ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Varela+Round&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Varela Round', sans-serif;
    }
    
    /* === TRADUÇÃO UPLOAD === */
    [data-testid="stFileUploaderDropzoneInstructions"] > div > span { display: none; }
    [data-testid="stFileUploaderDropzoneInstructions"] > div::after {
        content: "Arraste sua foto aqui ou clique para buscar";
        font-size: 14px;
        color: #888;
        font-weight: bold;
        display: block;
        margin-top: -10px;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] > div > small { display: none; }
    
    /* === BOTÕES === */
    button[kind="primary"] {
        background-color: #58cc02 !important;
        border-color: #58cc02 !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: bold !important;
    }
    button[kind="secondary"] {
        border-radius: 12px !important;
        font-weight: bold !important;
    }

    /* === CHAT ESTILO === */
    .chat-msg-container {
        display: flex;
        gap: 10px;
        margin-bottom: 10px;
        align-items: flex-start;
        font-size: 13px;
    }
    .chat-avatar-img {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        object-fit: cover;
        border: 1px solid #ddd;
        flex-shrink: 0;
    }
    .chat-avatar-emoji {
        width: 30px;
        height: 30px;
        font-size: 20px;
        text-align: center;
        flex-shrink: 0;
    }
    .chat-bubble {
        background-color: #f0f2f6;
        padding: 8px 12px;
        border-radius: 10px;
        border-top-left-radius: 0px;
        flex-grow: 1;
        color: #333;
    }
    .chat-header {
        font-size: 11px;
        color: #888;
        margin-bottom: 2px;
        display: flex;
        justify-content: space-between;
    }
    .chat-header strong {
        color: #58cc02;
    }

    /* === PERFIL SIDEBAR === */
    .profile-pic-sidebar {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #58cc02;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        display: block;
        margin: 0 auto;
    }
    .profile-emoji-sidebar {
        font-size: 70px;
        text-align: center;
        display: block;
        margin: 0 auto;
    }
    .profile-name {
        text-align: center;
        font-weight: bold;
        font-size: 18px;
        margin-top: 10px;
        margin-bottom: 5px;
    }
    
    /* XP Box Compacta */
    .xp-box {
        background-color: #262730;
        border: 1px solid #444;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        margin-top: 5px;
        margin-bottom: 20px;
    }
    .xp-val {
        font-size: 24px;
        font-weight: bold;
        color: #58cc02;
    }
    
    /* Outros Estilos */
    .stProgress > div > div > div > div { background-color: #58cc02; }
    
    /* Dashboard e outros elementos mantidos... */
    .dash-card {
        background-color: #f0f2f6 !important;
        border-radius: 8px;
        padding: 8px 15px;
        text-align: center;
        border: 1px solid #dcdcdc;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .dash-label { font-size: 11px !important; font-weight: bold !important; color: #333 !important; text-transform: uppercase; }
    .dash-value { font-size: 16px !important; font-weight: 900 !important; color: #000 !important; }
    .custom-title { font-size: 40px; font-weight: bold; margin-bottom: 0px; padding-bottom: 0px; line-height: 1.2; }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÕES ---
CSV_FILE = "enamed_db_v4.csv"
LINK_FILE = "drive_link.txt" 
PROFILE_FILE = "profiles.json"
CHAT_FILE = "chat_db.json" # Novo arquivo para o chat
DEFAULT_USERS = [] 

# Avatares
AVATARS = [
    "👨‍⚕️", "👩‍⚕️", "🦁", "🦊", "🐼", "🐨", "🐯", "🦖", "🦄", "🐸", 
    "🦉", "🐙", "🦋", "🍄", "🔥", "🚀", "💡", "🧠", "🫀", "💊", 
    "💉", "🦠", "🧬", "🩺", "🚑", "🏥", "🐧", "🦈", "🦅", "🐺"
]

# --- DADOS CRONOGRAMA (Resumido para não ocupar espaço, o seu já está salvo no CSV) ---
# Se o arquivo CSV já existe, o código usa ele. Se não, cria com o RAW_SCHEDULE.
RAW_SCHEDULE = """Data,Dia,Semana_Estudo,Disciplina,Tema,Meta_Diaria
20/02/2026,Sex,1,Pediatria,Imunizações (Calendário),15 Questões + Eng. Reversa
21/02/2026,Sáb,1,Medicina Preventiva,Vigilância em Saúde,30 Questões + Sprint Semanal
""" 
# ... (Mantenha o RAW_SCHEDULE completo se for rodar pela primeira vez em um novo local)

# --- FUNÇÕES ---

def init_db():
    if not os.path.exists(CSV_FILE):
        # Criação inicial simplificada para garantir funcionamento
        cols = ["ID", "Semana", "Data_Alvo", "Dia_Semana", "Disciplina", "Tema", "Meta", "Link_Questões", "Links_Content"]
        for user in DEFAULT_USERS:
            cols.extend([f"{user}_Status", f"{user}_Date"])
        df = pd.DataFrame(columns=cols)
        
        # Tenta carregar o RAW_SCHEDULE completo se você colar ele aqui, 
        # senão cria um dummy para não quebrar
        try:
            f = io.StringIO(RAW_SCHEDULE)
            reader = csv.DictReader(f)
            initial_data = []
            for i, row_data in enumerate(reader):
                try:
                    dt_obj = datetime.strptime(row_data['Data'], "%d/%m/%Y").date()
                    formatted_date = str(dt_obj)
                except: formatted_date = str(date.today())
                row = [i+1, int(row_data['Semana_Estudo']), formatted_date, row_data['Dia'], row_data['Disciplina'], row_data['Tema'], row_data['Meta_Diaria'], "", "[]"]
                initial_data.append(row)
            for r in initial_data: df.loc[len(df)] = r
        except: pass
        df.to_csv(CSV_FILE, index=False)

def load_data():
    if not os.path.exists(CSV_FILE): init_db()
    return pd.read_csv(CSV_FILE)

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def get_users_from_df(df):
    users = []
    for col in df.columns:
        if col.endswith("_Status"):
            users.append(col.replace("_Status", ""))
    return sorted(users)

# --- PERFIL E IMAGEM ---
def load_profiles():
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_profile(username, image_data):
    profiles = load_profiles()
    profiles[username] = image_data
    with open(PROFILE_FILE, "w") as f: json.dump(profiles, f)

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def add_new_user(df, new_name):
    if f"{new_name}_Status" in df.columns:
        return df, False, "Esse nome já existe!"
    df[f"{new_name}_Status"] = False
    df[f"{new_name}_Date"] = None
    save_data(df)
    return df, True, "Usuário criado com sucesso!"

def calculate_xp(target, completed_at):
    if pd.isna(completed_at) or str(completed_at) == "None" or str(completed_at) == "": return 0
    try:
        t = datetime.strptime(str(target), "%Y-%m-%d").date()
        c = datetime.strptime(str(completed_at), "%Y-%m-%d").date()
        return 100 if c <= t else 50
    except: return 0

# --- LINK DRIVE ---
def get_saved_link():
    if os.path.exists(LINK_FILE):
        with open(LINK_FILE, "r") as f: return f.read().strip()
    return ""
def save_drive_link_file(new_link):
    with open(LINK_FILE, "w") as f: f.write(new_link)

# --- CHAT FUNÇÕES ---
def load_chat():
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, "r") as f: return json.load(f)
        except: return []
    return []

def save_chat_message(user, msg, avatar_data):
    messages = load_chat()
    new_msg = {
        "user": user,
        "msg": msg,
        "time": datetime.now().strftime("%d/%m %H:%M"),
        "avatar": avatar_data
    }
    messages.append(new_msg)
    # Manter apenas as últimas 50 mensagens para não pesar
    if len(messages) > 50: messages = messages[-50:]
    
    with open(CHAT_FILE, "w") as f:
        json.dump(messages, f)

# --- INICIALIZAÇÃO ---
df = load_data()
ALL_USERS = get_users_from_df(df)
profiles = load_profiles()

# --- LOGIN ---
if "logged_user" not in st.session_state:
    c1, c2, c3 = st.columns([1, 6, 1])
    with c2:
        st.markdown("<div style='text-align: center; font-size: 80px;'>🏥</div>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>Enamed Diário</h1>", unsafe_allow_html=True)
        
        tab_login, tab_register = st.tabs(["🔑 Entrar", "➕ Novo Participante"])
        
        with tab_login:
            if not ALL_USERS: st.info("Cadastre o primeiro participante!")
            else:
                st.write("### Quem é você?")
                col_sel, col_pic = st.columns([3, 1])
                with col_sel: user_input = st.selectbox("Selecione seu perfil:", ALL_USERS)
                with col_pic:
                    if user_input and user_input in profiles:
                        p_data = profiles[user_input]
                        if len(p_data) > 20:
                            st.markdown(f'<img src="data:image/png;base64,{p_data}" style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover;">', unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='font-size: 50px; text-align: center;'>{p_data}</div>", unsafe_allow_html=True)
                
                if st.button("🚀 ENTRAR", type="primary"):
                    if user_input:
                        st.session_state["logged_user"] = user_input
                        st.rerun()
        
        with tab_register:
            nm = st.text_input("Seu Nome")
            st.write("Escolha seu avatar:")
            avatar_choice = st.selectbox("Selecione um ícone:", AVATARS)
            st.markdown("**OU**")
            uploaded_file = st.file_uploader("Envie sua foto (Prioridade sobre o ícone)", type=['png', 'jpg', 'jpeg'])
            
            if st.button("Salvar e Entrar"):
                if nm and len(nm) > 2:
                    final_name = f"Dr(a). {nm}"
                    df, success, msg = add_new_user(df, final_name)
                    if success:
                        if uploaded_file:
                            try:
                                img = Image.open(uploaded_file)
                                img.thumbnail((150, 150))
                                save_profile(final_name, image_to_base64(img))
                            except: pass
                        else:
                            save_profile(final_name, avatar_choice)
                        st.session_state["logged_user"] = final_name
                        st.rerun()
                else: st.warning("Nome curto.")
    st.stop()

current_user = st.session_state["logged_user"]

# --- SIDEBAR (PERFIL + XP + CHAT) ---
with st.sidebar:
    # 1. PERFIL (NO TOPO)
    if current_user in profiles:
        p_data = profiles[current_user]
        if len(p_data) > 20:
            st.markdown(f'<img class="profile-pic-sidebar" src="data:image/png;base64,{p_data}">', unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='profile-emoji-sidebar'>{p_data}</div>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='profile-name'>{current_user}</div>", unsafe_allow_html=True)
    
    if st.button("Sair", use_container_width=True):
        del st.session_state["logged_user"]
        st.rerun()
    
    # 2. XP (LOGO ABAIXO)
    total_xp = 0
    for idx, row in df.iterrows():
        if f"{current_user}_Date" in df.columns:
            total_xp += calculate_xp(row["Data_Alvo"], row[f"{current_user}_Date"])
    
    st.markdown(f"""
    <div class="xp-box">
        <div style="font-size: 12px; color: #aaa;">💎 XP ACUMULADO</div>
        <div class="xp-val">{total_xp}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # 3. CHAT (CANTO INFERIOR)
    st.markdown("### 💬 Bate-papo Global")
    
    # Container para mensagens (com scroll se tiver muitas)
    chat_container = st.container(height=300)
    messages = load_chat()
    
    with chat_container:
        if not messages:
            st.caption("Nenhuma mensagem ainda. Diga oi! 👋")
        
        for m in messages:
            # Identificar Avatar do Remetente
            av_html = ""
            if len(m['avatar']) > 20:
                av_html = f'<img class="chat-avatar-img" src="data:image/png;base64,{m["avatar"]}">'
            else:
                av_html = f'<div class="chat-avatar-emoji">{m["avatar"]}</div>'
            
            st.markdown(f"""
            <div class="chat-msg-container">
                {av_html}
                <div class="chat-bubble">
                    <div class="chat-header">
                        <strong>{m['user']}</strong> <span>{m['time']}</span>
                    </div>
                    {m['msg']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    # Input do Chat (Fixo no fundo da sidebar nativamente pelo Streamlit)
    if prompt := st.chat_input("Digite sua mensagem...", key="sidebar_chat"):
        user_avatar = profiles.get(current_user, "👤")
        save_chat_message(current_user, prompt, user_avatar)
        st.rerun()
        
    if st.button("🔄 Atualizar Chat", use_container_width=True):
        st.rerun()

# --- MAIN PAGE (DASHBOARD) ---
today = date.today()
df['dt_obj'] = pd.to_datetime(df['Data_Alvo']).dt.date
future_tasks = df[df['dt_obj'] >= today]

if df['dt_obj'].min() > today: status_cronograma = "Pré-Edital"
elif future_tasks.empty: status_cronograma = "Concluído"
else:
    prox_semana = future_tasks.iloc[0]['Semana']
    status_cronograma = f"Semana {prox_semana:02d}"

total_tasks = len(df)
tasks_done = df[f"{current_user}_Status"].sum() if f"{current_user}_Status" in df.columns else 0
pct_completo = (tasks_done / total_tasks) * 100 if total_tasks > 0 else 0

c_title, c_dash = st.columns([1.5, 2.5])
with c_title: st.markdown("<div class='custom-title'>🏥 Desafio<br>Enamed</div>", unsafe_allow_html=True)
with c_dash:
    st.markdown(f"""
    <div style="display: flex; gap: 10px; height: 100%; align-items: center;">
        <div class="dash-card" style="flex: 1;"><div class="dash-label">📅 Hoje</div><div class="dash-value">{today.strftime("%d/%m")}</div></div>
        <div class="dash-card" style="flex: 1;"><div class="dash-label">📍 Cronograma</div><div class="dash-value">{status_cronograma}</div></div>
        <div class="dash-card" style="flex: 1;"><div class="dash-label">🚀 Concluído</div><div class="dash-value">{int(pct_completo)}%</div></div>
    </div>
    """, unsafe_allow_html=True)

st.progress(int(pct_completo) / 100)
st.divider()

# --- ABAS PRINCIPAIS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📚 Lições", "🏆 Placar", "📂 Material", "⚙️ Admin", "🔰 Tutorial"])

# ABA 1: LIÇÕES
with tab1:
    st.markdown("### 📅 Cronograma Diário")
    semanas = sorted(df["Semana"].unique())
    for sem in semanas:
        df_week = df[df["Semana"] == sem]
        xp_f, xp_t = 0, 0
        for _, r in df_week.iterrows():
            if f"{current_user}_Status" in df.columns:
                xp_t += 100
                if r[f"{current_user}_Status"]: xp_f += calculate_xp(r["Data_Alvo"], r[f"{current_user}_Date"])
        
        with st.expander(f"📍 Semana {sem:02d} — ({xp_f} / {xp_t} XP)", expanded=(sem==1)):
            for _, row in df_week.iterrows():
                idx = df[df["ID"] == row["ID"]].index[0]
                status = row[f"{current_user}_Status"]
                try: d_alvo = datetime.strptime(str(row["Data_Alvo"]), "%Y-%m-%d").date(); d_br = d_alvo.strftime("%d/%m")
                except: d_alvo, d_br = date.today(), "--/--"
                
                bg, border = ("#e6fffa", "#58cc02") if status else ("#fff5d1", "#ffc800") if today > d_alvo else ("#ffffff", "#e5e5e5")
                lbl, ico, clr = ("FEITO", "✅", "#58cc02") if status else ("ATRASADO", "⚠️", "#d4a000") if today > d_alvo else ("PRAZO", "📅", "#afafaf")
                
                st.markdown(f"""
                <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                    <div style="flex: 0 0 80px; border: 2px solid {clr}; border-radius: 12px; text-align: center; padding: 5px; color: {clr}; background-color: {bg};">
                        <div style="font-size: 9px; font-weight: bold;">{lbl}</div><div style="font-size: 18px;">{ico}</div>
                        <div style="font-size: 11px; font-weight: bold;">{row['Dia_Semana']}</div><div style="font-size: 12px; font-weight: bold;">{d_br}</div>
                    </div>
                    <div style="flex: 1; background-color: {bg}; border: 2px solid {border}; border-radius: 12px; padding: 10px;">
                        <div style="font-size: 11px; color: #888; font-weight: bold; text-transform: uppercase;">{row['Disciplina']}</div>
                        <div style="font-size: 15px; font-weight: bold; color: #444;">{row['Tema']}</div>
                        <div style="font-size: 12px; color: #666;">🎯 {row['Meta']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns([4, 1])
                with c1:
                    with st.expander("🔗 Recursos"):
                        try: links = json.loads(row['Links_Content'])
                        except: links = []
                        if links:
                            for i, l in enumerate(links):
                                cl, cd = st.columns([6, 1])
                                cl.markdown(f'<div class="saved-link-item"><a href="{l["url"]}" target="_blank">🔗 {l["desc"]}</a></div>', unsafe_allow_html=True)
                                if cd.button("🗑️", key=f"d{row['ID']}_{i}", type="secondary"):
                                    st.session_state[f"conf_del_{row['ID']}_{i}"] = True
                                    st.rerun()
                                if st.session_state.get(f"conf_del_{row['ID']}_{i}"):
                                    st.warning(f"Excluir '{l['desc']}'?")
                                    if st.button("Sim", key=f"y{row['ID']}_{i}"):
                                        links.pop(i); df.at[idx, "Links_Content"] = json.dumps(links); save_data(df); st.rerun()
                        
                        st.caption("Novo Link:")
                        nd = st.text_input("Nome:", key=f"dn{row['ID']}")
                        nu = st.text_input("URL:", key=f"du{row['ID']}")
                        if st.button("Adicionar", key=f"ba{row['ID']}", type="primary"):
                            if nd and nu:
                                links.append({"desc": nd, "url": nu})
                                df.at[idx, "Links_Content"] = json.dumps(links); save_data(df); st.success("Ok!"); st.rerun()
                with c2:
                    if status:
                        if st.button("Desfazer", key=f"r{row['ID']}"):
                            df.at[idx, f"{current_user}_Status"] = False; save_data(df); st.rerun()
                    else:
                        btn_t = "secondary" if today > d_alvo else "primary"
                        lbl_b = "Entregar" if today > d_alvo else "Concluir"
                        if st.button(lbl_b, key=f"c{row['ID']}", type=btn_t):
                            df.at[idx, f"{current_user}_Status"] = True
                            df.at[idx, f"{current_user}_Date"] = str(date.today())
                            save_data(df); st.rerun()
                st.divider()

# ABA 2: PLACAR
with tab2:
    st.subheader("🏆 Classificação Geral")
    placar = []
    for u in ALL_USERS:
        pts, tks = 0, 0
        for _, r in df.iterrows():
            if f"{u}_Date" in df.columns:
                p = calculate_xp(r["Data_Alvo"], r[f"{u}_Date"])
                if p > 0: pts += p; tks += 1
        placar.append({"User": u, "XP": pts, "Tasks": tks})
    
    df_p = pd.DataFrame(placar).sort_values("XP", ascending=False).reset_index(drop=True)
    for i, r in df_p.iterrows():
        av_html = ""
        if r['User'] in profiles:
            pd_img = profiles[r['User']]
            if len(pd_img) > 20: av_html = f'<img src="data:image/png;base64,{pd_img}" style="width: 30px; height: 30px; border-radius: 50%; margin-right: 10px; vertical-align: middle;">'
            else: av_html = f'<span style="font-size: 24px; margin-right: 10px;">{pd_img}</span>'
        
        medal = ["🥇", "🥈", "🥉", ""][i] if i < 4 else ""
        bg = "#fff5c2" if i == 0 else "#f9f9f9"
        st.markdown(f"""
        <div style="background-color:{bg}; padding:10px; border-radius:10px; margin-bottom:5px; border:1px solid #ddd; display:flex; justify-content:space-between; align-items: center; color: black;">
            <div style="display: flex; align-items: center;">
                <span style="font-size:20px; margin-right: 10px;">{medal}</span>{av_html}<b>{r['User']}</b>
            </div>
            <div style="text-align:right;"><b>{r['XP']} XP</b><br><small>{r['Tasks']} lições</small></div>
        </div>""", unsafe_allow_html=True)

# ABA 3: MATERIAL
with tab3:
    st.markdown("## 📂 Repositório de Aulas")
    st.markdown("Acesse abaixo o Google Drive contendo os PDFs, Vídeos e Resumos.")
    cur_link = get_saved_link()
    if cur_link: st.link_button("🚀 ACESSAR DRIVE DE ESTUDOS", cur_link, type="primary", use_container_width=True)
    else: st.warning("⚠️ Nenhum link configurado.")
    st.divider()
    with st.expander("⚙️ Configurar Link"):
        if "d_unlock" not in st.session_state: st.session_state["d_unlock"] = False
        if not st.session_state["d_unlock"]:
            pwd = st.text_input("Senha:", type="password")
            if st.button("Desbloquear"):
                if pwd == "UNIARP": st.session_state["d_unlock"] = True; st.rerun()
                else: st.error("Senha incorreta.")
        else:
            nl = st.text_input("Novo Link:", value=cur_link)
            if st.button("Salvar", type="primary"):
                save_drive_link_file(nl); st.success("Salvo!"); st.rerun()

# ABA 4: ADMIN
with tab4:
    st.header("⚙️ Administração")
    if "admin_unlocked" not in st.session_state: st.session_state["admin_unlocked"] = False
    if not st.session_state["admin_unlocked"]:
        senha = st.text_input("Senha Admin:", type="password")
        if senha == "UNIARP": st.session_state["admin_unlocked"] = True; st.rerun()
    else:
        st.success("🔓 Liberado")
        if st.button("🗑️ RESETAR TUDO", type="primary"):
            if os.path.exists(CSV_FILE): os.remove(CSV_FILE)
            if os.path.exists(PROFILE_FILE): os.remove(PROFILE_FILE)
            if os.path.exists(CHAT_FILE): os.remove(CHAT_FILE)
            st.rerun()
        if st.button("🔒 Sair"): st.session_state["admin_unlocked"] = False; st.rerun()

# ABA 5: TUTORIAL
with tab5:
    st.markdown("## 📚 Manual do Usuário")
    st.markdown("""<div class="warning-box"><strong>⚠️ PRÉ-REQUISITO</strong><br>Acesse o material na aba <strong>📂 MATERIAL</strong> ou siga pelo Tema do Dia.</div>""", unsafe_allow_html=True)
    st.markdown("### 🧠 Metodologia")
    st.markdown("1. **Sprint Teórico (20%)**\n2. **Questões (80%)**\n3. **Engenharia Reversa**")
