import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import html
import io
import csv

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Enamed Oficial", page_icon="🦉", layout="centered")

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
CSV_FILE = "enamed_cronograma_final.csv" # Nome novo para garantir atualização
DEFAULT_USERS = [] 

# Avatares
AVATARS = [
    "👨‍⚕️", "👩‍⚕️", "🦉", "🧠", "🫀", "🧬", "🚑", "🏥", "💉", "💊", 
    "🦠", "🩸", "🎓", "🦁", "🦊", "🐼", "🐨", "🐯", "🦖", "🚀", "💡", "🔥"
]

# Tradução Dias
DIAS_PT = {0: "Seg", 1: "Ter", 2: "Qua", 3: "Qui", 4: "Sex", 5: "Sáb", 6: "Dom"}

# --- DADOS DO CRONOGRAMA (RAW CSV) ---
RAW_SCHEDULE = """Semana,Data_Inicio,Data_Fim,Foco_Principal,Tarefas_Chave_Enamed (Prioridade Alta)
01,20/02/2026,26/02/2026,Preventiva & Pediatria,"1. Imunizações: Calendário < 1 ano e Gestante | 2. Vigilância em Saúde: Notificação Compulsória e Investigação de Óbitos | 3. Revisão Flash: Vacinas"
02,27/02/2026,05/03/2026,Obstetrícia & Infecto,"1. Pré-Natal: Rotina, Exames e Suplementação | 2. Arboviroses: Dengue (Manejo A-D), Zika e Chikungunya | 3. Cirurgia Pediátrica: Hérnias e Fimose"
03,06/03/2026,12/03/2026,Gineco & Pediatria,"1. ISTs: Úlceras Genitais (Sífilis, Cancro, Herpes) | 2. Doenças Exantemáticas: Sarampo e Varicela | 3. Sistemas de Informação em Saúde (SIM/SINAN)"
04,13/03/2026,19/03/2026,Clínica & Preventiva,"1. Hipertensão (HAS): Diagnóstico e Drogas 1ª Linha | 2. Medidas de Saúde Coletiva: Coeficientes e Indicadores | 3. Pneumologia: Pneumonia Adquirida na Comunidade (PAC)"
05,20/03/2026,26/03/2026,Obstetrícia & Pediatria,"1. DHEG: Pré-eclâmpsia (Diagnóstico e Sulfato de Magnésio) | 2. Icterícia Neonatal: Zonas de Kramer e Incompatibilidade | 3. Sepse Neonatal: Fatores de Risco"
06,27/03/2026,02/04/2026,Cirurgia & Infecto,"1. Trauma (ATLS): Avaliação Primária (ABCDE) | 2. HIV/AIDS: Diagnóstico e Infecções Oportunistas | 3. Cirurgia do Trauma: Trauma Abdominal Fechado vs Penetrante"
07,03/04/2026,09/04/2026,Gineco & Clínica,"1. Rastreamento (Screening): CA Colo Utero e Mama (Diretrizes MS) | 2. Diabetes Mellitus: Rastreio e Metas Terapêuticas | 3. Climatério: Terapia de Reposição Hormonal"
08,10/04/2026,16/04/2026,Preventiva & Gastro,"1. Estudos Epidemiológicos: Coorte vs Caso-Controle vs Transversal | 2. Dispepsia e DRGE: Diagnóstico e IBP | 3. Medicina Baseada em Evidências: Sensibilidade e Especificidade"
09,17/04/2026,23/04/2026,Obstetrícia & Pediatria,"1. Sangramentos 1ª Metade: Aborto, Mola e Ectópica | 2. Aleitamento Materno: Pega correta e Contraindicações (HIV/HTLV) | 3. Crescimento: Curvas da OMS (Escore Z)"
10,24/04/2026,30/04/2026,Cirurgia & Nefro,"1. Abdome Agudo: Inflamatório (Apendicite/Colecistite) | 2. Litíase Urinária: Cólica Nefrética e Tratamento | 3. Hérnias da Parede Abdominal: Inguinais e Femorais"
11,01/05/2026,07/05/2026,Clínica & Infecto,"1. Tuberculose: Diagnóstico (TRM/Bacilo) e Tratamento (RIPE) | 2. Asma: Classificação e Manejo da Crise | 3. DPOC: Classificação GOLD"
12,08/05/2026,14/05/2026,REVISÃO GERAL,"SEMANA BUFFER: Recuperar atrasos e focar EXCLUSIVAMENTE no Caderno de Erros das semanas 1-11."
13,15/05/2026,21/05/2026,Preventiva & Gineco,"1. SUS: Princípios Doutrinários (Universalidade, Integralidade, Equidade) | 2. Sangramento Uterino Anormal (SUA): PALM-COEIN | 3. Amenorreia: Primária vs Secundária"
14,22/05/2026,28/05/2026,Pediatria & Cardio,"1. IVAS na Infância: Otite, Sinusite e Faringite | 2. Insuficiência Cardíaca: Classificação NYHA e Drogas que mudam mortalidade | 3. Pneumonias na Infância: Quando internar?"
15,29/05/2026,04/06/2026,Obstetrícia & Cirurgia,"1. Sangramentos 3ª Metade: Placenta Prévia e DPP (Diagnóstico Diferencial) | 2. Pré-Operatório: Risco Cirúrgico e Jejum | 3. Complicações Pós-Op: Febre e Deiscência"
16,05/06/2026,11/06/2026,Infecto & Gastro,"1. Hepatites Virais: Sorologia da Hepatite B (HBsAg, Anti-HBs) | 2. Diarreia Aguda: Planos de Hidratação (A, B, C) | 3. Parasitoses Intestinais: Tratamento Empírico"
17,12/06/2026,18/06/2026,Preventiva & Psiquiatria,"1. Atenção Primária: Política Nacional (PNAB) e Atributos | 2. Transtornos de Ansiedade e Depressão: Critérios DSM-5 e ISRS | 3. Ética Médica: Sigilo e Código de Ética"
18,19/06/2026,25/06/2026,Gineco & Pediatria,"1. SOP e Infertilidade: Critérios de Rotterdam | 2. Puberdade: Precoce vs Atrasada (Estadiamento de Tanner) | 3. Anticoncepção: Critérios de Elegibilidade da OMS"
19,26/06/2026,02/07/2026,Clínica & Neuro,"1. AVC: Isquêmico vs Hemorrágico (Janela de Trombólise) | 2. Cefaleias: Migrânea vs Tensional vs Em Salvas | 3. Delirium vs Demência"
20,03/07/2026,09/07/2026,Cirurgia & Ortopedia,"1. Queimaduras: Regra dos 9 e Fórmula de Parkland | 2. Fraturas Expostas: Classificação de Gustilo | 3. Trauma Torácico: Pneumotórax e Tamponamento"
21,10/07/2026,16/07/2026,Obstetrícia & Infecto,"1. Parto Prematuro: Tocólise e Corticoide | 2. Ruptura Prematura de Membros (RPMO) | 3. Infecções Congênitas: Toxoplasmose e Sífilis"
22,17/07/2026,23/07/2026,Preventiva & Reumato,"1. Saúde do Trabalhador: LER/DORT e Pneumoconioses | 2. Artrites: Reumatoide vs Osteoartrose vs Gota | 3. Notificação em Saúde do Trabalhador"
23,24/07/2026,30/07/2026,Pediatria & Gastro,"1. Síndromes Disabsortivas: Doença Celíaca | 2. Constipação Intestinal na Infância | 3. Desidratação: Avaliação e Manejo"
24,31/07/2026,06/08/2026,Clínica & Hemato,"1. Anemias Carenciais: Ferropriva e Megaloblástica | 2. Leucemias Agudas e Crônicas (Diferenciação básica) | 3. Distúrbios da Coagulação"
25,07/08/2026,13/08/2026,REVISÃO MEIO DE ANO,"SEMANA DE SIMULADO GERAL: Fazer prova na íntegra (100 questões) e corrigir cada erro."
26,14/08/2026,20/08/2026,Cirurgia & Urologia,"1. Câncer de Próstata: Rastreamento e Tratamento | 2. Nefrolitíase: Tratamento Cirúrgico | 3. Escroto Agudo: Torção Testicular"
27,21/08/2026,27/08/2026,Gineco & Mastologia,"1. Nódulos Mamários: BIRADS e Conduta | 2. Câncer de Mama: Tipos Histológicos e Tratamento | 3. Incontinência Urinária: Esforço vs Urgência"
28,28/08/2026,03/09/2026,Preventiva & Clínica,"1. Financiamento do SUS: Blocos de Financiamento | 2. Emergências Hipertensivas e Crise Convulsiva | 3. Intoxicações Exógenas (Carvão Ativado?)"
29,04/09/2026,10/09/2026,Obstetrícia & Pediatria,"1. Sofrimento Fetal Agudo: Cardiotocografia (DIPs) | 2. Reanimação Neonatal: O Fluxograma de Ouro (Atualizado 2022/23) | 3. Mecanismo de Parto"
30,11/09/2026,17/09/2026,Clínica & Nefro,"1. Injúria Renal Aguda (IRA): Pré-renal vs NTA | 2. Doença Renal Crônica: Estadiamento e Complicações | 3. Distúrbios Hidroeletrolíticos (Sódio e Potássio)"
31,18/09/2026,24/09/2026,Especialidades I,"1. Dermatologia: Hanseníase e Câncer de Pele | 2. Otorrino: Vertigens e Rinites | 3. Oftalmo: Olho Vermelho (Diferencial Básico)"
32,25/09/2026,01/10/2026,Cirurgia & Vias Biliares,"1. Icterícia Obstrutiva: Coledocolitíase e Tumores Periampulares | 2. Pancreatite Aguda: Critérios de Ranson/Atlanta | 3. Trauma Pediátrico"
33,02/10/2026,08/10/2026,Gineco & Oncologia,"1. Câncer de Colo Uterino: Estadiamento e Tratamento | 2. Câncer de Endométrio e Ovário | 3. Vulvovaginites (Revisão Prática)"
34,09/10/2026,15/10/2026,Preventiva & Geriatria,"1. Geriatria: Síndromes Geriátricas (Quedas, Demência, Iatrogenia) | 2. Violência Interpessoal: Notificação | 3. Humanização e PNH"
35,16/10/2026,22/10/2026,Pediatria & Emergência,"1. Emergências Pediátricas: Cetoacidose, Crise Asmática Grave | 2. Infecções do Trato Urinário na Criança | 3. Meningites (Líquor)"
36,23/10/2026,29/10/2026,Clínica & Cardio,"1. Síndrome Coronariana Aguda: Com e Sem Supra (Conduta no PS) | 2. Arritmias: Fibrilação Atrial (Anticoagular?) | 3. Valvopatias"
37,30/10/2026,05/11/2026,Cirurgia & Vascular,"1. Doença Arterial Obstrutiva Periférica (DAOP) | 2. Insuficiência Venosa Crônica (Varizes) | 3. Aneurismas de Aorta"
38,06/11/2026,12/11/2026,SPRINT FINAL I,"FOCAR APENAS NOS ERROS: Refazer todas as questões erradas de PREVENTIVA e PEDIATRIA das últimas 37 semanas."
39,13/11/2026,19/11/2026,SPRINT FINAL II,"FOCAR APENAS NOS ERROS: Refazer todas as questões erradas de CLÍNICA e CIRURGIA das últimas 37 semanas."
40,20/11/2026,26/11/2026,SPRINT FINAL III,"FOCAR APENAS NOS ERROS: Refazer todas as questões erradas de GINECOLOGIA e OBSTETRÍCIA."
41,27/11/2026,03/12/2026,SIMULADOS FINAIS,"Realizar 2 Provas do Enamed/Enare anteriores na íntegra (tempo real) + Correção detalhada."
42,04/12/2026,10/12/2026,SEMANA PRÉ-PROVA,"1. Revisão de Decorebas (Tabelas do Caderno de Erros) | 2. Higiene do Sono | 3. NADA DE QUESTÕES NOVAS DIFÍCEIS."
"""

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
        
        # Parse do CSV Raw
        f = io.StringIO(RAW_SCHEDULE)
        reader = csv.DictReader(f)
        
        initial_data = []
        for i, row_data in enumerate(reader):
            # Converte data DD/MM/YYYY para YYYY-MM-DD
            try:
                date_str = row_data['Data_Fim']
                dt_obj = datetime.strptime(date_str, "%d/%m/%Y").date()
                formatted_date = str(dt_obj)
            except:
                formatted_date = str(date.today())

            row = [
                i + 1, 
                f"Semana {row_data['Semana']}", 
                formatted_date, 
                row_data['Foco_Principal'], 
                row_data['Tarefas_Chave_Enamed (Prioridade Alta)'], 
                ""
            ]
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
            st.markdown("<h1 style='text-align: center;'>Enamed Oficial</h1>", unsafe_allow_html=True)
            st.caption("<div style='text-align: center;'>Cronograma 2026 • 42 Semanas</div>", unsafe_allow_html=True)
            
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
            with st.expander("📂 Conteúdo Extra / Contribuir ➕"):
                current_link = row['Link_Questões']
                if current_link:
                    st.markdown(f"🔗 **Link:** [{current_link}]({current_link})")
                else:
                    st.info("Nenhum material ainda.")

                new_link = st.text_input("Colar Link:", key=f"l_{row['ID']}")
                if st.button("💾 Salvar", key=f"s_{row['ID']}"):
                    if new_link:
                        df.at[real_idx, "Link_Questões"] = new_link
                        save_data(df); st.success("Atualizado!"); st.rerun()
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
    st.subheader("🏆 Classificação Anual")
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
    if st.button("🗑️ ZERAR BANCO DE DADOS (Carregar Cronograma)", type="primary"):
        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.warning("Banco reiniciado para o Cronograma Oficial! Atualize a página."); st.rerun()
