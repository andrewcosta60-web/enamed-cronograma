import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
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

# Avatares
AVATARS = [
    "👨‍⚕️", "👩‍⚕️", "🦉", "🧠", "🫀", "🧬", "🚑", "🏥", "💉", "💊", 
    "🦠", "🩸", "🎓", "🦁", "🦊", "🐼", "🐨", "🐯", "🦖", "🚀", "💡", "🔥"
]

# Tradução Dias
DIAS_PT = {0: "Seg", 1: "Ter", 2: "Qua", 3: "Qui", 4: "Sex", 5: "Sáb", 6: "Dom"}

# --- CRONOGRAMA COMPLETO ---
FULL_SCHEDULE = [
    ("Semana 01", "Pediatria - Imunizações", "Calendário Vacinal 2026, Vacinas vivas x inativadas."),
    ("Semana 01", "Preventiva - SUS", "Princípios Doutrinários e Organizativos, Lei 8080/90."),
    ("Semana 02", "Cirurgia - Trauma (ATLS)", "Avaliação Primária (ABCDE), Trauma Torácico e Abdominal."),
    ("Semana 02", "Ginecologia - Ciclo Menstrual", "Fisiologia, Hormônios e Amenorreias Primárias."),
    ("Semana 03", "Cardiologia - Hipertensão", "Diagnóstico, Estadiamento e Tratamento Farmacológico."),
    ("Semana 03", "Obstetrícia - Diagnóstico de Gravidez", "Sinais de Presunção, Probabilidade e Certeza. Modificações Maternas."),
    ("Semana 04", "Nefrologia - Distúrbios Ácido-Base", "Acidose/Alcalose Metabólica e Respiratória. Gasometria."),
    ("Semana 04", "Pediatria - Crescimento e Desenv.", "Marcos do desenvolvimento, Curvas de Crescimento (Z-score)."),
    ("Semana 05", "Gastroenterologia - DRGE e Dispepsia", "Diagnóstico diferencial, H. pylori, Tratamento clínico."),
    ("Semana 05", "Preventiva - Vigilância em Saúde", "Notificação Compulsória (Lista Nacional), Invest. de Surtos."),
    ("Semana 06", "Cirurgia - Hérnias da Parede Abd.", "Inguinais, Femorais, Umbilical. Classificação de Nyhus."),
    ("Semana 06", "Infectologia - HIV/AIDS", "Diagnóstico, Estadiamento, Tratamento Antirretroviral e IOs."),
    ("Semana 07", "Obstetrícia - Sangramentos 1ª Metade", "Abortamento, Gravidez Ectópica, Doença Trofoblástica."),
    ("Semana 07", "Pneumologia - Asma e DPOC", "Diferenciação, Espirometria, GOLD e GINA."),
    ("Semana 08", "Endocrinologia - Diabetes Mellitus", "Rastreio, Diagnóstico, Insulinas e Antidiabéticos Orais."),
    ("Semana 08", "Pediatria - Aleitamento Materno", "Fisiologia, Técnica, Contraindicações e Alimentação Comp."),
    ("Semana 09", "Reumatologia - Artrites", "Artrite Reumatoide vs Osteoartrite vs Gota."),
    ("Semana 09", "Ginecologia - Anticoncepção", "Métodos Comportamentais, Hormonais, DIU e LARC."),
    ("Semana 10", "Cirurgia - Coloproctologia", "Câncer Colorretal, Doença Diverticular, Hemorroidas."),
    ("Semana 10", "Psiquiatria - Transtornos de Humor", "Depressão Maior, TAB, Ansiedade Generalizada."),
    ("Semana 11", "Hematologia - Anemias", "Ferropriva, Megaloblástica, Hemolíticas e Talassemias."),
    ("Semana 11", "Preventiva - Estudos Epidemiológicos", "Coorte, Caso-Controle, Transversal, Ensaio Clínico."),
    ("Semana 12", "Obstetrícia - Sangramentos 2ª Metade", "Placenta Prévia, DPP, Rotura Uterina, Vasa Prévia."),
    ("Semana 12", "Pediatria - Doenças Exantemáticas", "Sarampo, Rubéola, Varicela, Eritema Infeccioso."),
    ("Semana 13", "Neurologia - AVC", "Isquêmico x Hemorrágico, Trombólise, Manejo Agudo."),
    ("Semana 13", "Cirurgia - Trauma Cranioencefálico", "Escala de Glasgow, Indicações de TC, HIC."),
    ("Semana 14", "Ginecologia - Climaterio", "Terapia de Reposição Hormonal, Osteoporose."),
    ("Semana 14", "Nefrologia - Glomerulopatias", "Síndrome Nefrítica x Nefrótica."),
    ("Semana 15", "Cardiologia - Insuficiência Cardíaca", "ICFER x ICFEP, Classificação NYHA e AHA."),
    ("Semana 15", "Preventiva - Medidas de Saúde", "Mortalidade Materna, Infantil, Swaroop-Uemura."),
    ("Semana 16", "Pediatria - Respiratório", "Pneumonias, Bronquiolite, Crupe, Epiglotite."),
    ("Semana 16", "Obstetrícia - Doença Hipertensiva", "Pré-eclâmpsia, Eclâmpsia, Síndrome HELLP."),
    ("Semana 17", "REVISÃO GERAL - CLÍNICA", "Top 5 temas de Clínica Médica + Questões."),
    ("Semana 18", "REVISÃO GERAL - CIRURGIA", "Top 5 temas de Cirurgia + Questões."),
    ("Semana 19", "REVISÃO GERAL - PEDIATRIA", "Top 5 temas de Pediatria + Questões."),
    ("Semana 20", "REVISÃO GERAL - G.O.", "Top 5 temas de Ginecologia e Obstetrícia + Questões.")
]

# --- FUNÇÕES ---

def get_users_from_df(df):
    users = []
    for col in df.columns:
        if col.endswith("_Status"):
            user_name = col.replace("_Status", "")
            users.append(user_name)
    return sorted(users)

def init_db():
    if not os.path.exists(CSV_FILE):
        cols = ["ID", "Semana", "Data_Alvo", "Tema", "Detalhes", "Link_Questões"]
        for user in DEFAULT_USERS:
            cols.extend([f"{user}_Status", f"{user}_Date"])
            
        df = pd.DataFrame(columns=cols)
        start_date = date.today()
        
        initial_data = []
        for i, item in enumerate(FULL_SCHEDULE):
            semana_label, tema, detalhes = item
            week_num = i // 2
            days_add = (week_num * 7) + (0 if i % 2 == 0 else 3) 
            task_date = start_date + timedelta(days=days_add)
            
            row = [i + 1, semana_label, str(task_date), tema, detalhes, ""]
            for _ in DEFAULT_USERS: row.extend([False, None])
            initial_data.append(row)

        for r in initial_data:
            df.loc[len(df)] = r
            
        df.to_csv(CSV_FILE, index=False)

def load_data():
    if not os.path.exists(CSV_FILE): init_db()
    return pd.read_csv(CSV_FILE)

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def add_new_user(df, new_name):
    if f"{new_name}_Status" in df.columns:
        return df, False, "Esse nome já existe!"
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

# --- LOGIN ---
if "logged_user" not in st.session_state:
    qp = st.query_params
    if "user" in qp and qp["user"] in ALL_USERS:
        st.session_state["logged_user"] = qp["user"]
        st.rerun()
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 6, 1])
        with c2:
            st.markdown("<div style='text-align: center; font-size: 80px;'>🦉</div>", unsafe_allow_html=True)
            st.markdown("<h1 style='text-align: center;'>Desafio Enamed</h1>", unsafe_allow_html=True)
            
            tab_login, tab_register = st.tabs(["🔑 Entrar", "➕ Novo Participante"])
            
            with tab_login:
                if not ALL_USERS:
                    st.info("Nenhum participante. Cadastre o primeiro na aba ao lado! 👉")
                else:
                    st.write("### Quem é você?")
                    user_input = st.selectbox("Selecione seu perfil:", ALL_USERS)
                    if st.button("🚀 ENTRAR", type="primary"):
                        if user_input:
                            st.session_state["logged_user"] = user_input
                            st.rerun()
            
            with tab_register:
                st.write("### Criar novo perfil")
                ce, cn = st.columns([1, 3])
                with ce: av = st.selectbox("Avatar", AVATARS)
                with cn: nm = st.text_input("Seu Nome")
                final_name = f"{av} {nm}" if nm else ""
                if nm: st.caption(f"Será: **{final_name}**")
                
                if st.button("Salvar e Entrar"):
                    if nm and len(nm) > 2:
                        df, success, msg = add_new_user(df, final_name)
                        if success:
                            st.session_state["logged_user"] = final_name
                            st.rerun()
                        else: st.error(msg)
                    else: st.warning("Nome muito curto.")
        st.stop()

current_user = st.session_state["logged_user"]

# --- SIDEBAR ---
with st.sidebar:
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

tab1, tab2, tab3 = st.tabs(["📚 Lições", "🏆 Placar", "⚙️ Admin"])

# --- ABA 1: LIÇÕES ---
with tab1:
    semanas = df["Semana"].unique()
    sem = st.selectbox("Módulo:", semanas)
    df_view = df[df["Semana"] == sem]

    for index, row in df_view.iterrows():
        real_idx = df[df["ID"] == row["ID"]].index[0]
        if f"{current_user}_Status" not in df.columns: st.rerun()

        status = row[f"{current_user}_Status"]
        data_gravada = row[f"{current_user}_Date"]
        pontos = calculate_xp(row["Data_Alvo"], data_gravada)
        
        hoje = date.today()
        try: 
            d_alvo = datetime.strptime(str(row["Data_Alvo"]), "%Y-%m-%d").date()
            d_br = d_alvo.strftime("%d/%m")
            d_sem = DIAS_PT[d_alvo.weekday()]
        except: 
            d_alvo = date.today(); d_br = "--/--"; d_sem = "---"
        
        bg_tema, border_tema = "#ffffff", "#e5e5e5"
        
        if status:
            b_data, bg_data, t_data, lbl, ico, border_tema = "#58cc02", "#e6fffa", "#58cc02", "FEITO", "✅", "#58cc02"
        elif hoje > d_alvo:
            b_data, bg_data, t_data, lbl, ico, border_tema = "#ffc800", "#fff5d1", "#d4a000", "ATRASADO", "⚠️", "#ffc800"
        else:
            b_data, bg_data, t_data, lbl, ico = "#e5e5e5", "#f7f7f7", "#afafaf", "PRAZO", "📅"

        tema_esc = html.escape(str(row['Tema']))
        det_esc = html.escape(str(row['Detalhes']))

        st.markdown(f"""
        <div style="display: flex; gap: 15px; align-items: stretch; width: 100%; margin-bottom: 15px; font-family: 'Varela Round', sans-serif;">
            <div style="flex: 0 0 100px; background-color: {bg_data}; border: 2px solid {b_data}; border-radius: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 10px; color: {t_data}; box-shadow: 0 4px 0 rgba(0,0,0,0.05);">
                <div style="font-size: 10px; font-weight: bold; margin-bottom: 2px;">{lbl}</div>
                <div style="font-size: 24px; margin-bottom: 2px;">{ico}</div>
                <div style="font-size: 12px; font-weight: bold;">{d_sem}</div>
                <div style="font-size: 14px; font-weight: bold;">{d_br}</div>
            </div>
            <div style="flex: 1; background-color: {bg_tema}; border: 2px solid {border_tema}; border-radius: 12px; padding: 15px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 4px 0 rgba(0,0,0,0.05);">
                <div style="font-size: 17px; font-weight: bold; color: #4b4b4b; line-height: 1.2; margin-bottom: 5px;">{tema_esc}</div>
                <div style="font-size: 13px; color: #888; line-height: 1.4;">{det_esc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns([3, 1])
        with c1:
            # === AQUI ESTÁ A ALTERAÇÃO PARA CONTRIBUIÇÃO ===
            # Icone de "+" adicionado no título
            with st.expander("📂 Conteúdo Extra / Contribuir ➕"):
                current_link = row['Link_Questões']
                
                # Se existe link, mostra ele bonitinho
                if current_link:
                    st.markdown(f"🔗 **Link Atual:** [{current_link}]({current_link})")
                    st.caption("Deseja alterar o link? Cole o novo abaixo.")
                else:
                    st.info("Nenhum material adicionado ainda. Seja o primeiro!")

                # Campo para QUALQUER UM adicionar/editar
                new_link = st.text_input("Colar Link do Drive/Questões:", key=f"l_{row['ID']}")
                if st.button("💾 Salvar Link", key=f"s_{row['ID']}"):
                    if new_link:
                        df.at[real_idx, "Link_Questões"] = new_link
                        save_data(df)
                        st.success("Link atualizado com sucesso!")
                        st.rerun()
                    else:
                        st.warning("Cole um link válido.")

        with c2:
            if status:
                st.success(f"✅ FEITO! (+{pontos})")
                if st.button("Refazer", key=f"r_{row['ID']}"):
                    df.at[real_idx, f"{current_user}_Status"] = False; save_data(df); st.rerun()
            else:
                l_btn = "Entregar" if hoje > d_alvo else "Concluir"
                t_btn = "secondary" if hoje > d_alvo else "primary"
                if st.button(l_btn, key=f"c_{row['ID']}", type=t_btn):
                    df.at[real_idx, f"{current_user}_Status"] = True
                    df.at[real_idx, f"{current_user}_Date"] = str(date.today())
                    save_data(df); st.balloons(); st.rerun()
        st.write("")

# --- ABA 2: PLACAR ---
with tab2:
    st.subheader("🏆 Classificação")
    placar = []
    for u in ALL_USERS:
        pts, tasks = 0, 0
        for i, r in df.iterrows():
            if f"{u}_Date" in df.columns:
                p = calculate_xp(r["Data_Alvo"], r[f"{u}_Date"])
                if p > 0: pts += p; tasks += 1
        placar.append({"Médico": u, "XP": pts, "Tarefas": tasks})
        
    df_p = pd.DataFrame(placar).sort_values("XP", ascending=False).reset_index(drop=True)
    
    for i, row in df_p.iterrows():
        med, bg = ["🥇", "🥈", "🥉", ""][i] if i < 4 else "", "#fff5c2" if i == 0 else "#f9f9f9"
        st.markdown(f"""
        <div style="background-color:{bg}; padding:10px; border-radius:10px; margin-bottom:5px; border:1px solid #ddd; display:flex; justify-content:space-between; font-family: 'Varela Round', sans-serif; color: black;">
            <div><span style="font-size:20px;">{med}</span> <b>{row['Médico']}</b></div>
            <div style="text-align:right;"><b>{row['XP']} XP</b><br><small>{row['Tarefas']} lições</small></div>
        </div>
        """, unsafe_allow_html=True)

# --- ABA 3: ADMIN ---
with tab3:
    st.write("Adicionar Tarefa Extra")
    with st.form("add"):
        c1, c2 = st.columns(2)
        s, d = c1.text_input("Semana"), c2.date_input("Data")
        t, dt = st.text_input("Tema"), st.text_input("Detalhes")
        if st.form_submit_button("Salvar"):
            nid = df["ID"].max() + 1 if not df.empty else 1
            nrow = {"ID": nid, "Semana": s, "Data_Alvo": str(d), "Tema": t, "Detalhes": dt, "Link_Questões": ""}
            for u in ALL_USERS: nrow[f"{u}_Status"], nrow[f"{u}_Date"] = False, None
            df = pd.concat([df, pd.DataFrame([nrow])], ignore_index=True)
            save_data(df); st.success("Ok!"); st.rerun()

    st.divider()
    if st.button("🗑️ ZERAR BANCO DE DADOS (Limpar Tudo)", type="primary"):
        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.warning("Banco apagado! Atualize a página."); st.rerun()
