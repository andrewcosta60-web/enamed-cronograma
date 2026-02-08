import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os
import html
import io
import csv
import json
import base64
import uuid
from PIL import Image

# --- CONFIGURAÇÃO DE FUSO HORÁRIO (FORÇADA UTC-3) ---
def get_brazil_time():
    # Pega o horário universal (UTC) e subtrai 3 horas para chegar em Brasília
    # Isso funciona em qualquer servidor (EUA, Europa, etc) sem precisar de configurar máquina
    return datetime.utcnow() - timedelta(hours=3)

def get_brazil_date():
    return get_brazil_time().date()

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Enamed Oficial", page_icon="🏥", layout="wide") 

# --- CSS GLOBAL (ESTILO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Varela+Round&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Varela Round', sans-serif;
    }
    
    /* === TRADUÇÃO UPLOAD (PORTUGUÊS) === */
    [data-testid="stFileUploaderDropzoneInstructions"] > div > span { display: none; }
    [data-testid="stFileUploaderDropzoneInstructions"] > div::after {
        content: "Arraste sua foto aqui ou clique para buscar";
        font-size: 14px; color: #888; font-weight: bold; display: block; margin-top: -10px;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] > div > small { display: none; }
    
    /* === BOTÕES VERDES (PRIMÁRIOS) === */
    button[kind="primary"] {
        background-color: #58cc02 !important;
        border-color: #58cc02 !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 0 rgba(0,0,0,0.1);
        transition: all 0.1s;
    }
    button[kind="primary"]:active {
        box-shadow: none;
        transform: translateY(2px);
    }

    /* === BOTÕES SECUNDÁRIOS (PADRÃO) === */
    button[kind="secondary"] {
        border-radius: 12px !important;
        font-weight: bold !important;
        border: 1px solid #e0e0e0 !important;
    }

    /* === LIXEIRA INVISÍVEL NO CHAT (SIDEBAR) === */
    /* Remove fundo e borda APENAS dos botões secundários da barra lateral (Lixeira) */
    /* Nota: O botão de Sair e Atualizar devem ser Primários para não sumirem */
    section[data-testid="stSidebar"] button[kind="secondary"] {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0px !important;
        color: #bbb !important; /* Cinza claro */
        margin-top: 5px !important;
    }
    section[data-testid="stSidebar"] button[kind="secondary"]:hover {
        color: #ff4b4b !important; /* Vermelho ao passar o mouse */
        background: transparent !important;
    }

    /* === CHAT VISUAL === */
    .chat-msg-container {
        display: flex;
        gap: 8px;
        align-items: center; /* Alinha foto, texto e botão no centro vertical */
        font-size: 12px;
        width: 100%;
        margin-bottom: 2px;
    }
    .chat-avatar-img {
        width: 28px; height: 28px; border-radius: 50%; object-fit: cover; border: 1px solid #ddd; flex-shrink: 0;
    }
    .chat-avatar-emoji {
        width: 28px; height: 28px; font-size: 18px; text-align: center; flex-shrink: 0;
    }
    .chat-bubble {
        background-color: #f0f2f6;
        padding: 8px 12px;
        border-radius: 12px;
        border-top-left-radius: 0px;
        flex-grow: 1;
        color: #333;
        line-height: 1.4;
    }
    .chat-header {
        font-size: 10px; color: #888; margin-bottom: 2px; display: flex; justify-content: space-between;
    }
    .chat-header strong { color: #58cc02; }

   /* === PERFIL SIDEBAR (TAMANHO GRANDE FORÇADO V15) === */
    
    /* Estilo para FOTO (Upload) */
    .profile-pic-sidebar {
        width: 160px !important;  /* Força o tamanho GRANDE (160px) */
        height: 160px !important; /* Força a altura igual */
        border-radius: 50%;
        object-fit: cover;
        border: 5px solid #58cc02; /* Borda verde mais grossa */
        box-shadow: 0 5px 15px rgba(0,0,0,0.3); /* Sombra para destacar */
        display: block;
        margin: 10px auto; /* Centraliza */
    }

    /* Estilo para EMOJI (Caso não tenha foto) */
    .profile-emoji-sidebar {
        font-size: 130px !important; /* Força o emoji GRANDE */
        text-align: center;
        display: block;
        margin: 0 auto;
        line-height: 1.1; /* Ajusta altura da linha do emoji */
    }
    
    /* Ajuste do Nome abaixo da foto */
    .profile-name {
        text-align: center;
        font-weight: 900;
        font-size: 22px !important; /* Nome maior e forçado */
        margin-top: 15px;
        margin-bottom: 15px;
        color: white !important; /* Nome branco */
    }
    
    /* === OUTROS === */
    .stProgress > div > div > div > div { background-color: #58cc02; }
    .dash-card {
        background-color: #f0f2f6 !important; border-radius: 8px; padding: 8px 15px;
        text-align: center; border: 1px solid #dcdcdc; height: 100%;
        display: flex; flex-direction: column; justify-content: center;
    }
    .dash-label { font-size: 11px !important; font-weight: bold !important; color: #333 !important; text-transform: uppercase; }
    .dash-value { font-size: 16px !important; font-weight: 900 !important; color: #000 !important; }
    .custom-title { font-size: 40px; font-weight: bold; margin-bottom: 0px; padding-bottom: 0px; line-height: 1.2; }
    .saved-link-item { background-color: #ffffff; border: 1px solid #e0e0e0; padding: 10px; border-radius: 10px; margin-bottom: 0px; display: flex; align-items: center; gap: 10px; }
    .saved-link-item a { text-decoration: none; color: #0068c9; font-weight: bold; }
    .delete-confirm-box { background-color: #ffe6e6; border: 1px solid #ffcccc; padding: 5px; border-radius: 5px; text-align: center; font-size: 12px; margin-bottom: 5px;}
    .warning-box { background-color: #fff3e0; border-left: 5px solid #ff9800; padding: 15px; border-radius: 5px; margin-bottom: 10px; color: black; }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÕES ---
CSV_FILE = "enamed_db_v4.csv"
LINK_FILE = "drive_link.txt" 
PROFILE_FILE = "profiles.json"
CHAT_FILE = "chat_db.json"
DEFAULT_USERS = [] 

# Avatares
AVATARS = [
    "👨‍⚕️", "👩‍⚕️", "🦁", "🦊", "🐼", "🐨", "🐯", "🦖", "🦄", "🐸", 
    "🦉", "🐙", "🦋", "🍄", "🔥", "🚀", "💡", "🧠", "🫀", "💊", 
    "💉", "🦠", "🧬", "🩺", "🚑", "🏥", "🐧", "🦈", "🦅", "🐺"
]

# --- DADOS DO CRONOGRAMA (COMPLETO) ---
RAW_SCHEDULE = """Data,Dia,Semana_Estudo,Disciplina,Tema,Meta_Diaria
20/02/2026,Sex,1,Pediatria,Imunizações (Calendário),15 Questões + Eng. Reversa
21/02/2026,Sáb,1,Medicina Preventiva,Vigilância em Saúde,30 Questões + Sprint Semanal
23/02/2026,Seg,1,Ginecologia,Planejamento Familiar,15 Questões + Eng. Reversa
24/02/2026,Ter,1,Obstetrícia,Pré-Natal (Rotina),15 Questões + Eng. Reversa
25/02/2026,Qua,1,Infectologia,Arboviroses (Dengue/Zika),15 Questões + Eng. Reversa
26/02/2026,Qui,1,Cirurgia,Cirurgia Infantil I (Hérnias),15 Questões + Eng. Reversa
27/02/2026,Sex,2,Pediatria,Imunizações (Vacinas Especiais),15 Questões + Eng. Reversa
28/02/2026,Sáb,2,Medicina Preventiva,Sistemas de Informação (SIM/SINAN),30 Questões + Sprint Semanal
02/03/2026,Seg,2,Obstetrícia,Pré-Natal (Exames),15 Questões + Eng. Reversa
03/03/2026,Ter,2,Infectologia,Arboviroses (Manejo Clínico),15 Questões + Eng. Reversa
04/03/2026,Qua,2,Cirurgia,Cirurgia Infantil II,15 Questões + Eng. Reversa
05/03/2026,Qui,2,Ginecologia,Planejamento Familiar (Métodos),15 Questões + Eng. Reversa
06/03/2026,Sex,3,Pediatria,Doenças Exantemáticas,15 Questões + Eng. Reversa
07/03/2026,Sáb,3,Medicina Preventiva,Sistemas de Informação,30 Questões + Sprint Semanal
09/03/2026,Seg,3,Medicina Preventiva,Vigilância em Saúde,15 Questões + Eng. Reversa
10/03/2026,Ter,3,Ginecologia,Úlceras Genitais (ISTs),15 Questões + Eng. Reversa
11/03/2026,Qua,3,Infectologia,Arboviroses (Revisão),15 Questões + Eng. Reversa
12/03/2026,Qui,3,Cirurgia,Cirurgia Infantil II,15 Questões + Eng. Reversa
13/03/2026,Sex,4,Medicina Preventiva,Medidas de Saúde Coletiva,15 Questões + Eng. Reversa
14/03/2026,Sáb,4,Obstetrícia,Distúrbios Hipertensivos (DHEG),30 Questões + Sprint Semanal
16/03/2026,Seg,4,Pediatria,Doenças Exantemáticas II,15 Questões + Eng. Reversa
17/03/2026,Ter,4,Cirurgia,Cirurgia Infantil III,15 Questões + Eng. Reversa
18/03/2026,Qua,4,Ginecologia,Úlceras Genitais,15 Questões + Eng. Reversa
19/03/2026,Qui,4,Pneumologia,Pneumologia Intensiva,15 Questões + Eng. Reversa
20/03/2026,Sex,5,Medicina Preventiva,Medidas de Saúde Coletiva II,15 Questões + Eng. Reversa
21/03/2026,Sáb,5,Pediatria,Icterícia e Sepse Neonatal,30 Questões + Sprint Semanal
23/03/2026,Seg,5,Ginecologia,Rastreamento de Câncer (Colo),15 Questões + Eng. Reversa
24/03/2026,Ter,5,Obstetrícia,Doença Hipertensiva (Crônica),15 Questões + Eng. Reversa
25/03/2026,Qua,5,Infectologia,HIV (Diagnóstico),15 Questões + Eng. Reversa
26/03/2026,Qui,5,Cirurgia,Cirurgia Infantil III,15 Questões + Eng. Reversa
27/03/2026,Sex,6,Medicina Preventiva,Indicadores de Saúde,15 Questões + Eng. Reversa
28/03/2026,Sáb,6,Pediatria,Emergências Pediátricas,30 Questões + Sprint Semanal
30/03/2026,Seg,6,Ginecologia,Rastreamento de Câncer (Mama),15 Questões + Eng. Reversa
31/03/2026,Ter,6,Obstetrícia,Doença Hipertensiva (Pré-eclâmpsia),15 Questões + Eng. Reversa
01/04/2026,Qua,6,Pediatria,Icterícia e Sepse Neonatal,15 Questões + Eng. Reversa
02/04/2026,Qui,6,Cirurgia,Trauma - Avaliação Inicial (ABCDE),15 Questões + Eng. Reversa
03/04/2026,Sex,7,Pediatria,Emergências Pediátricas II,15 Questões + Eng. Reversa
04/04/2026,Sáb,7,Medicina Preventiva,Estudos Epidemiológicos,30 Questões + Sprint Semanal
06/04/2026,Seg,7,Ginecologia,Rastreamento de Câncer,15 Questões + Eng. Reversa
07/04/2026,Ter,7,Obstetrícia,Doença Hipertensiva (Eclampsia),15 Questões + Eng. Reversa
08/04/2026,Qua,7,Infectologia,HIV (Tratamento),15 Questões + Eng. Reversa
09/04/2026,Qui,7,Cirurgia,Trauma - Vias Aéreas,15 Questões + Eng. Reversa
10/04/2026,Sex,8,Medicina Preventiva,Estudos Epidemiológicos (Tipos),15 Questões + Eng. Reversa
11/04/2026,Sáb,8,Pediatria,Imunizações (Revisão Geral),30 Questões + Sprint Semanal
13/04/2026,Seg,8,Ginecologia,Climatério e Terapia Hormonal,15 Questões + Eng. Reversa
14/04/2026,Ter,8,Obstetrícia,Sífilis na Gestação,15 Questões + Eng. Reversa
15/04/2026,Qua,8,Infectologia,HIV (Oportunistas),15 Questões + Eng. Reversa
16/04/2026,Qui,8,Pediatria,Emergências Pediátricas,15 Questões + Eng. Reversa
17/04/2026,Sex,9,Pediatria,Cardiopatias Congênitas,15 Questões + Eng. Reversa
18/04/2026,Sáb,9,Medicina Preventiva,Epidemiologia (Cálculos),30 Questões + Sprint Semanal
20/04/2026,Seg,9,Ginecologia,Climatério (Sintomas),15 Questões + Eng. Reversa
21/04/2026,Ter,9,Obstetrícia,Sífilis Congênita,15 Questões + Eng. Reversa
22/04/2026,Qua,9,Ginecologia,Doenças Benignas da Mama,15 Questões + Eng. Reversa
23/04/2026,Qui,9,Ginecologia,Planejamento Familiar (DIU/Hormônios),15 Questões + Eng. Reversa
24/04/2026,Sex,10,Medicina Preventiva,Saúde do Trabalhador,15 Questões + Eng. Reversa
25/04/2026,Sáb,10,Pediatria,Cuidados Neonatais,30 Questões + Sprint Semanal
27/04/2026,Seg,10,Ginecologia,Doenças Benignas (Ovário),15 Questões + Eng. Reversa
28/04/2026,Ter,10,Obstetrícia,Infecções na Gestação,15 Questões + Eng. Reversa
29/04/2026,Qua,10,Obstetrícia,Sangramento da 1ª Metade (Aborto),15 Questões + Eng. Reversa
30/04/2026,Qui,10,Infectologia,Tuberculose (Diagnóstico),15 Questões + Eng. Reversa
01/05/2026,Sex,11,Pediatria,Cuidados Neonatais (Sala de Parto),15 Questões + Eng. Reversa
02/05/2026,Sáb,11,Medicina Preventiva,Saúde do Trabalhador (Doenças),30 Questões + Sprint Semanal
04/05/2026,Seg,11,Obstetrícia,Sangramento 1ª Metade (Ectópica),15 Questões + Eng. Reversa
05/05/2026,Ter,11,Infectologia,Tuberculose (Tratamento),15 Questões + Eng. Reversa
06/05/2026,Qua,11,Cirurgia,Trauma Abdominal,15 Questões + Eng. Reversa
07/05/2026,Qui,11,Ginecologia,Doenças Benignas da Mama,15 Questões + Eng. Reversa
08/05/2026,Sex,12,Pediatria,Asma na Infância,15 Questões + Eng. Reversa
09/05/2026,Sáb,12,Medicina Preventiva,Vigilância Sanitária,30 Questões + Sprint Semanal
11/05/2026,Seg,12,Ginecologia,Vulvovaginites (Candidíase/Vaginose),15 Questões + Eng. Reversa
12/05/2026,Ter,12,Obstetrícia,Sangramento 1ª Metade (Mola),15 Questões + Eng. Reversa
13/05/2026,Qua,12,Cirurgia,Trauma Pélvico,15 Questões + Eng. Reversa
14/05/2026,Qui,12,Pneumologia,Pneumonia Adquirida na Comunidade,15 Questões + Eng. Reversa
15/05/2026,Sex,13,Pediatria,Asma (Crise Aguda),15 Questões + Eng. Reversa
16/05/2026,Sáb,13,Medicina Preventiva,Ética Médica,30 Questões + Sprint Semanal
18/05/2026,Seg,13,Ginecologia,Vulvovaginites (ISTs),15 Questões + Eng. Reversa
19/05/2026,Ter,13,Obstetrícia,Sangramento 1ª Metade (Revisão),15 Questões + Eng. Reversa
20/05/2026,Qua,13,Obstetrícia,Pré-Natal (Alto Risco),15 Questões + Eng. Reversa
21/05/2026,Qui,13,Cirurgia,Trauma Abdominal (Baço/Fígado),15 Questões + Eng. Reversa
22/05/2026,Sex,14,Medicina Preventiva,Processo Saúde-Doença,15 Questões + Eng. Reversa
23/05/2026,Sáb,14,Medicina Preventiva,Medidas de Saúde Coletiva,30 Questões + Sprint Semanal
25/05/2026,Seg,14,Pediatria,Aleitamento Materno,15 Questões + Eng. Reversa
26/05/2026,Ter,14,Obstetrícia,Assistência ao Parto (Fases),15 Questões + Eng. Reversa
27/05/2026,Qua,14,Pediatria,Asma (Manutenção),15 Questões + Eng. Reversa
28/05/2026,Qui,14,Infectologia,Meningites,15 Questões + Eng. Reversa
29/05/2026,Sex,15,Medicina Preventiva,História Natural da Doença,15 Questões + Eng. Reversa
30/05/2026,Sáb,15,Pediatria,Aleitamento (Dificuldades),30 Questões + Sprint Semanal
01/06/2026,Seg,15,Ginecologia,Endometriose,15 Questões + Eng. Reversa
02/06/2026,Ter,15,Obstetrícia,Assistência ao Parto (Humanização),15 Questões + Eng. Reversa
03/06/2026,Qua,15,Pediatria,Cardiopatias Congênitas,15 Questões + Eng. Reversa
04/06/2026,Qui,15,Infectologia,Meningites (Líquor),15 Questões + Eng. Reversa
05/06/2026,Sex,16,Pediatria,Diarreia Aguda e Desidratação,15 Questões + Eng. Reversa
06/06/2026,Sáb,16,Medicina Preventiva,Medicina de Família (Ferramentas),30 Questões + Sprint Semanal
08/06/2026,Seg,16,Ginecologia,Endometriose (Tratamento),15 Questões + Eng. Reversa
09/06/2026,Ter,16,Obstetrícia,Assistência ao Parto,15 Questões + Eng. Reversa
10/06/2026,Qua,16,Cirurgia,Abdome Agudo (Apendicite),15 Questões + Eng. Reversa
11/06/2026,Qui,16,Nefrologia,Lesão Renal Aguda (IRA),15 Questões + Eng. Reversa
12/06/2026,Sex,17,Pediatria,Diarreia (Planos A-B-C),15 Questões + Eng. Reversa
13/06/2026,Sáb,17,Medicina Preventiva,Saúde do Idoso,30 Questões + Sprint Semanal
15/06/2026,Seg,17,Ginecologia,Câncer de Mama (Tipos),15 Questões + Eng. Reversa
16/06/2026,Ter,17,Infectologia,Meningites,15 Questões + Eng. Reversa
17/06/2026,Qua,17,Infectologia,Arboviroses (Febre Amarela),15 Questões + Eng. Reversa
18/06/2026,Qui,17,Cirurgia,Abdome Agudo Inflamatório,15 Questões + Eng. Reversa
19/06/2026,Sex,18,Pediatria,Pneumonias na Infância,15 Questões + Eng. Reversa
20/06/2026,Sáb,18,Medicina Preventiva,Saúde do Idoso (Fragilidade),30 Questões + Sprint Semanal
22/06/2026,Seg,18,Medicina Preventiva,Processo Saúde-Doença,15 Questões + Eng. Reversa
23/06/2026,Ter,18,Ginecologia,Câncer de Mama (Cirurgia),15 Questões + Eng. Reversa
24/06/2026,Qua,18,Obstetrícia,Vitalidade Fetal (Cardio),15 Questões + Eng. Reversa
25/06/2026,Qui,18,Infectologia,Micoses Sistêmicas,15 Questões + Eng. Reversa
26/06/2026,Sex,19,Medicina Preventiva,Princípios do SUS (Lei 8080),15 Questões + Eng. Reversa
27/06/2026,Sáb,19,Pediatria,Choque em Pediatria,30 Questões + Sprint Semanal
29/06/2026,Seg,19,Ginecologia,Câncer de Mama (Adjuvância),15 Questões + Eng. Reversa
30/06/2026,Ter,19,Obstetrícia,Vitalidade Fetal (Perfil Biofísico),15 Questões + Eng. Reversa
01/07/2026,Qua,19,Infectologia,Sepse (qSOFA/SOFA),15 Questões + Eng. Reversa
02/07/2026,Qui,19,Pediatria,Pneumonias (Complicações),15 Questões + Eng. Reversa
03/07/2026,Sex,20,Pediatria,Choque (Séptico/Hipovolêmico),15 Questões + Eng. Reversa
04/07/2026,Sáb,20,Infectologia,Sepse (Manejo 1h),30 Questões + Sprint Semanal
06/07/2026,Seg,20,Ginecologia,Doenças Benignas da Mama,15 Questões + Eng. Reversa
07/07/2026,Ter,20,Cirurgia,Cirurgia Vascular (DAOP),15 Questões + Eng. Reversa
08/07/2026,Qua,20,Ginecologia,Câncer de Mama (Revisão),15 Questões + Eng. Reversa
09/07/2026,Qui,20,Obstetrícia,Vitalidade Fetal,15 Questões + Eng. Reversa
10/07/2026,Sex,21,Pediatria,Choque em Pediatria,15 Questões + Eng. Reversa
11/07/2026,Sáb,21,Infectologia,Sepse,30 Questões + Sprint Semanal
13/07/2026,Seg,21,Ginecologia,Doenças Benignas da Mama,15 Questões + Eng. Reversa
14/07/2026,Ter,21,Cirurgia,Cirurgia Vascular (Varizes),15 Questões + Eng. Reversa
15/07/2026,Qua,21,Ginecologia,Câncer de Mama,15 Questões + Eng. Reversa
16/07/2026,Qui,21,Obstetrícia,Vitalidade Fetal,15 Questões + Eng. Reversa
17/07/2026,Sex,22,Pediatria,Reanimação Neonatal (Golden Minute),15 Questões + Eng. Reversa
18/07/2026,Sáb,22,Pediatria,Diarreia Crônica,30 Questões + Sprint Semanal
20/07/2026,Seg,22,Ginecologia,Sangramento Uterino Anormal (SUA),15 Questões + Eng. Reversa
21/07/2026,Ter,22,Obstetrícia,Diabetes Gestacional,15 Questões + Eng. Reversa
22/07/2026,Qua,22,Infectologia,Parasitoses Intestinais,15 Questões + Eng. Reversa
23/07/2026,Qui,22,Obstetrícia,Mecanismo de Parto,15 Questões + Eng. Reversa
24/07/2026,Sex,23,Pediatria,Crescimento (Curvas),15 Questões + Eng. Reversa
25/07/2026,Sáb,23,Pediatria,Constipação Intestinal,30 Questões + Sprint Semanal
27/07/2026,Seg,23,Ginecologia,Sangramento Uterino (PALM-COEIN),15 Questões + Eng. Reversa
28/07/2026,Ter,23,Obstetrícia,Sangramento da 2ª Metade (Placenta Prévia),15 Questões + Eng. Reversa
29/07/2026,Qua,23,Infectologia,Parasitoses,15 Questões + Eng. Reversa
30/07/2026,Qui,23,Pediatria,Reanimação Neonatal,15 Questões + Eng. Reversa
31/07/2026,Sex,24,Pediatria,Doença Celíaca,15 Questões + Eng. Reversa
01/08/2026,Sáb,24,Ginecologia,Tumores Anexiais (Cistos),30 Questões + Sprint Semanal
03/08/2026,Seg,24,Obstetrícia,Sangramento da 2ª Metade (DPP),15 Questões + Eng. Reversa
04/08/2026,Ter,24,Pediatria,Crescimento (Puberdade),15 Questões + Eng. Reversa
05/08/2026,Qua,24,Cirurgia,Urologia (Litíase),15 Questões + Eng. Reversa
06/08/2026,Qui,24,Cardiologia,Insuficiência Cardíaca,15 Questões + Eng. Reversa
07/08/2026,Sex,25,Pediatria,Tópicos em Pediatria,15 Questões + Eng. Reversa
08/08/2026,Sáb,25,Pediatria,Reanimação neonatal (Avançado),30 Questões + Sprint Semanal
10/08/2026,Seg,25,Ginecologia,Tumores Anexiais,15 Questões + Eng. Reversa
11/08/2026,Ter,25,Obstetrícia,Sangramento da 2ª Metade (Rotura),15 Questões + Eng. Reversa
12/08/2026,Qua,25,Cirurgia,Urgências Abdominais (Obstrução),15 Questões + Eng. Reversa
13/08/2026,Qui,25,Infectologia,Parasitoses,15 Questões + Eng. Reversa
14/08/2026,Sex,26,Medicina Preventiva,Princípios do SUS,15 Questões + Eng. Reversa
15/08/2026,Sáb,26,Pediatria,Diagnóstico Nutricional,30 Questões + Sprint Semanal
17/08/2026,Seg,26,Pediatria,Vitaminas e Carências,15 Questões + Eng. Reversa
18/08/2026,Ter,26,Medicina Preventiva,Financiamento do SUS,15 Questões + Eng. Reversa
19/08/2026,Qua,26,Ginecologia,Prolapsos Genitais,15 Questões + Eng. Reversa
20/08/2026,Qui,26,Obstetrícia,Sangramento 2ª Metade (Vasa Previa),15 Questões + Eng. Reversa
21/08/2026,Sex,27,Medicina Preventiva,Estatística (Testes Diagnósticos),15 Questões + Eng. Reversa
22/08/2026,Sáb,27,Pediatria,Desnutrição na Infância,30 Questões + Sprint Semanal
24/08/2026,Seg,27,Pediatria,Febre Sem Sinais Localizatórios,15 Questões + Eng. Reversa
25/08/2026,Ter,27,Ginecologia,Prolapsos,15 Questões + Eng. Reversa
26/08/2026,Qua,27,Obstetrícia,Sangramento 2ª Metade,15 Questões + Eng. Reversa
27/08/2026,Qui,27,Infectologia,Infecções Hospitalares (IRAS),15 Questões + Eng. Reversa
28/08/2026,Sex,28,Medicina Preventiva,Estatística Médica,15 Questões + Eng. Reversa
29/08/2026,Sáb,28,Ginecologia,Câncer de Colo Uterino (HPV),30 Questões + Sprint Semanal
31/08/2026,Seg,28,Obstetrícia,Sangramento 2ª Metade,15 Questões + Eng. Reversa
01/09/2026,Ter,28,Obstetrícia,Assistência ao Parto,15 Questões + Eng. Reversa
02/09/2026,Qua,28,Pediatria,Desnutrição,15 Questões + Eng. Reversa
03/09/2026,Qui,28,Infectologia,Infecções Hospitalares,15 Questões + Eng. Reversa
04/09/2026,Sex,29,Pediatria,Obesidade Infantil,15 Questões + Eng. Reversa
05/09/2026,Sáb,29,Obstetrícia,Partograma e Distocia,30 Questões + Sprint Semanal
07/09/2026,Seg,29,Infectologia,Pneumonias Bacterianas,15 Questões + Eng. Reversa
08/09/2026,Ter,29,Ginecologia,Sangramento Uterino,15 Questões + Eng. Reversa
09/09/2026,Qua,29,Ginecologia,Câncer de Colo Uterino (Tratamento),15 Questões + Eng. Reversa
10/09/2026,Qui,29,Cirurgia,Cirurgia Vascular,15 Questões + Eng. Reversa
11/09/2026,Sex,30,Pediatria,Obesidade Infantil,15 Questões + Eng. Reversa
12/09/2026,Sáb,30,Obstetrícia,Partograma e Distocia (Tipos),30 Questões + Sprint Semanal
14/09/2026,Seg,30,Pediatria,Infecção Urinária (ITU),15 Questões + Eng. Reversa
15/09/2026,Ter,30,Pediatria,Diagnóstico Nutricional,15 Questões + Eng. Reversa
16/09/2026,Qua,30,Ginecologia,Incontinência Urinária (Esforço/Urgência),15 Questões + Eng. Reversa
17/09/2026,Qui,30,Cirurgia,Abdome Agudo Obstrutivo,15 Questões + Eng. Reversa
18/09/2026,Sex,31,Medicina Preventiva,Normas Regulamentadoras (Trabalho),15 Questões + Eng. Reversa
19/09/2026,Sáb,31,Pediatria,ITU na Infância,30 Questões + Sprint Semanal
21/09/2026,Seg,31,Pediatria,Bronquiolite Viral Aguda,15 Questões + Eng. Reversa
22/09/2026,Ter,31,Infectologia,Pneumonias,15 Questões + Eng. Reversa
23/09/2026,Qua,31,Ginecologia,Anatomia e Embriologia,15 Questões + Eng. Reversa
24/09/2026,Qui,31,Obstetrícia,Infecções Congênitas (TORCH),15 Questões + Eng. Reversa
25/09/2026,Sex,32,Medicina Preventiva,Marcos Legais do SUS,15 Questões + Eng. Reversa
26/09/2026,Sáb,32,Ginecologia,Câncer de Endométrio,30 Questões + Sprint Semanal
28/09/2026,Seg,32,Obstetrícia,Gestação Múltipla,15 Questões + Eng. Reversa
29/09/2026,Ter,32,Pediatria,Bronquiolite,15 Questões + Eng. Reversa
30/09/2026,Qua,32,Infectologia,Pneumonias,15 Questões + Eng. Reversa
01/10/2026,Qui,32,Cirurgia,Abdome Agudo,15 Questões + Eng. Reversa
02/10/2026,Sex,33,Medicina Preventiva,Leis Orgânicas da Saúde,15 Questões + Eng. Reversa
03/10/2026,Sáb,33,Pediatria,Alergias (Anafilaxia),30 Questões + Sprint Semanal
05/10/2026,Seg,33,Ginecologia,Câncer do Corpo do Útero,15 Questões + Eng. Reversa
06/10/2026,Ter,33,Infectologia,Pneumonias,15 Questões + Eng. Reversa
07/10/2026,Qua,33,Ginecologia,Adenomiose,15 Questões + Eng. Reversa
08/10/2026,Qui,33,Obstetrícia,Infecção Puerperal,15 Questões + Eng. Reversa
09/10/2026,Sex,34,Ginecologia,Amenorreia (Primária/Secundária),15 Questões + Eng. Reversa
10/10/2026,Sáb,34,Obstetrícia,Hemorragia Pós-Parto (4 Ts),30 Questões + Sprint Semanal
12/10/2026,Seg,34,Pediatria,Puberdade (Precoce/Atrasada),15 Questões + Eng. Reversa
13/10/2026,Ter,34,Infectologia,Pneumonias,15 Questões + Eng. Reversa
14/10/2026,Qua,34,Pediatria,Urticária,15 Questões + Eng. Reversa
15/10/2026,Qui,34,Cirurgia,Complicações Pós-Operatórias,15 Questões + Eng. Reversa
16/10/2026,Sex,35,Ginecologia,Amenorreia,15 Questões + Eng. Reversa
17/10/2026,Sáb,35,Obstetrícia,Hemorragia Pós-Parto,30 Questões + Sprint Semanal
19/10/2026,Seg,35,Pediatria,Doença de Kawasaki,15 Questões + Eng. Reversa
20/10/2026,Ter,35,Pediatria,ITU (Profilaxia),15 Questões + Eng. Reversa
21/10/2026,Qua,35,Pediatria,Puberdade,15 Questões + Eng. Reversa
22/10/2026,Qui,35,Infectologia,Sepse,15 Questões + Eng. Reversa
23/10/2026,Sex,36,Medicina Preventiva,Atenção Primária (PNAB),15 Questões + Eng. Reversa
24/10/2026,Sáb,36,Medicina Preventiva,Estatística Médica,30 Questões + Sprint Semanal
26/10/2026,Seg,36,Obstetrícia,Bacia Obstétrica,15 Questões + Eng. Reversa
27/10/2026,Ter,36,Ginecologia,Ciclo Menstrual (Fisiologia),15 Questões + Eng. Reversa
28/10/2026,Qua,36,Pediatria,Doença de Kawasaki,15 Questões + Eng. Reversa
29/10/2026,Qui,36,Cirurgia,Vesícula e Vias Biliares,15 Questões + Eng. Reversa
30/10/2026,Sex,37,Medicina Preventiva,Saúde da Família,15 Questões + Eng. Reversa
31/10/2026,Sáb,37,Pediatria,Distúrbios Metabólicos,30 Questões + Sprint Semanal
02/11/2026,Seg,37,Ginecologia,Infertilidade Conjugal,15 Questões + Eng. Reversa
03/11/2026,Ter,37,Obstetrícia,Estática Fetal,15 Questões + Eng. Reversa
04/11/2026,Qua,37,Cirurgia,Colecistite/Coledocolitíase,15 Questões + Eng. Reversa
05/11/2026,Qui,37,Infectologia,COVID-19,15 Questões + Eng. Reversa
06/11/2026,Sex,38,Medicina Preventiva,Políticas de Saúde,15 Questões + Eng. Reversa
07/11/2026,Sáb,38,Pediatria,Distúrbios Metabólicos,30 Questões + Sprint Semanal
09/11/2026,Seg,38,Ginecologia,Infertilidade (Investigação),15 Questões + Eng. Reversa
10/11/2026,Ter,38,Pediatria,Síndromes Genéticas (Down/Turner),15 Questões + Eng. Reversa
11/11/2026,Qua,38,Obstetrícia,Bacia Obstétrica,15 Questões + Eng. Reversa
12/11/2026,Qui,38,Obstetrícia,Partograma,15 Questões + Eng. Reversa
13/11/2026,Sex,39,Medicina Preventiva,Redes de Atenção à Saúde,15 Questões + Eng. Reversa
14/11/2026,Sáb,39,Pediatria,Síndromes Genéticas,30 Questões + Sprint Semanal
16/11/2026,Seg,39,Medicina Preventiva,Políticas de Saúde,15 Questões + Eng. Reversa
17/11/2026,Ter,39,Obstetrícia,TPP - Trabalho de Parto Prematuro,15 Questões + Eng. Reversa
18/11/2026,Qua,39,Ginecologia,Incontinência Urinária,15 Questões + Eng. Reversa
19/11/2026,Qui,39,Cirurgia,Cirurgia Plástica (Queimaduras),15 Questões + Eng. Reversa
20/11/2026,Sex,40,Medicina Preventiva,Regionalização do SUS,15 Questões + Eng. Reversa
21/11/2026,Sáb,40,Medicina Preventiva,Descentralização,30 Questões + Sprint Semanal
23/11/2026,Seg,40,Medicina Preventiva,Bases do SUS,15 Questões + Eng. Reversa
24/11/2026,Ter,40,Pediatria,Erros Inatos do Metabolismo,15 Questões + Eng. Reversa
25/11/2026,Qua,40,Ginecologia,Miomatose Uterina,15 Questões + Eng. Reversa
26/11/2026,Qui,40,Obstetrícia,Prematuridade,15 Questões + Eng. Reversa
27/11/2026,Sex,41,Pediatria,Tuberculose na Infância,15 Questões + Eng. Reversa
28/11/2026,Sáb,41,Medicina Preventiva,Pesquisa Epidemiológica,30 Questões + Sprint Semanal
30/11/2026,Seg,41,Ginecologia,Miomatose,15 Questões + Eng. Reversa
01/12/2026,Ter,41,Obstetrícia,RPMO (Bolsa Rota),15 Questões + Eng. Reversa
02/12/2026,Qua,41,Infectologia,Endocardite Bacteriana,15 Questões + Eng. Reversa
03/12/2026,Qui,41,Cirurgia,Queimaduras,15 Questões + Eng. Reversa
04/12/2026,Sex,42,Medicina Preventiva,Pesquisa Qualitativa,15 Questões + Eng. Reversa
05/12/2026,Sáb,42,Pediatria,Distúrbios Respiratórios,30 Questões + Sprint Semanal
07/12/2026,Seg,42,Pediatria,Revisão Geral (Kawasaki/Exantemáticas),15 Questões + Eng. Reversa
08/12/2026,Ter,42,Ginecologia,Rastreamento (Revisão Final),15 Questões + Eng. Reversa
09/12/2026,Qua,42,Obstetrícia,RPMO,15 Questões + Eng. Reversa
10/12/2026,Qui,42,Pediatria,Tuberculose,15 Questões + Eng. Reversa
11/12/2026,Sex,43,Pediatria,Distúrbios Respiratórios,15 Questões + Eng. Reversa
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
        cols = ["ID", "Semana", "Data_Alvo", "Dia_Semana", "Disciplina", "Tema", "Meta", "Links_Content"]
        for user in DEFAULT_USERS:
            cols.extend([f"{user}_Status", f"{user}_Date"])
            
        df = pd.DataFrame(columns=cols)
        
        # Parse do CSV Raw (FULL)
        f = io.StringIO(RAW_SCHEDULE)
        reader = csv.DictReader(f)
        
        initial_data = []
        for i, row_data in enumerate(reader):
            try:
                date_str = row_data['Data']
                dt_obj = datetime.strptime(date_str, "%d/%m/%Y").date()
                formatted_date = str(dt_obj)
            except:
                formatted_date = str(get_brazil_date()) 

            row = [
                i + 1, 
                int(row_data['Semana_Estudo']), 
                formatted_date, 
                row_data['Dia'],
                row_data['Disciplina'],
                row_data['Tema'],
                row_data['Meta_Diaria'],
                "[]" # Lista vazia em JSON
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

# FUNÇÕES PERSISTÊNCIA LINK DO DRIVE
def get_saved_link():
    if os.path.exists(LINK_FILE):
        with open(LINK_FILE, "r") as f:
            return f.read().strip()
    return ""

def save_drive_link_file(new_link):
    with open(LINK_FILE, "w") as f:
        f.write(new_link)

# --- FUNÇÕES PARA PERFIL (FOTO/EMOJI) ---
def load_profiles():
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def save_profile(username, image_data):
    profiles = load_profiles()
    profiles[username] = image_data
    with open(PROFILE_FILE, "w") as f:
        json.dump(profiles, f)

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
    if pd.isna(completed_at) or str(completed_at) == "None" or str(completed_at) == "":
        return 0
    try:
        t = datetime.strptime(str(target), "%Y-%m-%d").date()
        c = datetime.strptime(str(completed_at), "%Y-%m-%d").date()
        if c <= t: return 100
        else: return 50
    except: return 0

# --- FUNÇÕES DE CHAT ---
def load_chat():
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, "r") as f: return json.load(f)
        except: return []
    return []

def save_chat_message(user, msg, avatar_data):
    messages = load_chat()
    new_msg = {
        "id": str(uuid.uuid4()), 
        "user": user,
        "msg": msg,
        "time": get_brazil_time().strftime("%d/%m %H:%M"), 
        "avatar": avatar_data
    }
    messages.append(new_msg)
    if len(messages) > 50: messages = messages[-50:] 
    with open(CHAT_FILE, "w") as f:
        json.dump(messages, f)

def delete_chat_message(msg_id):
    messages = load_chat()
    new_messages = [m for m in messages if m.get("id") != msg_id]
    with open(CHAT_FILE, "w") as f:
        json.dump(new_messages, f)

# --- INICIALIZAÇÃO ---
df = load_data()
ALL_USERS = get_users_from_df(df)
profiles = load_profiles()

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
            st.markdown("<div style='text-align: center; font-size: 80px;'>🏥</div>", unsafe_allow_html=True)
            st.markdown("<h1 style='text-align: center;'>Enamed Diário</h1>", unsafe_allow_html=True)
            st.caption("<div style='text-align: center;'>Controle Dia a Dia • 2026</div>", unsafe_allow_html=True)
            
            tab_login, tab_register = st.tabs(["🔑 Entrar", "➕ Novo Participante"])
            
            with tab_login:
                if not ALL_USERS:
                    st.info("Nenhum participante. Cadastre o primeiro na aba ao lado! 👉")
                else:
                    st.write("### Quem é você?")
                    col_sel, col_pic = st.columns([3, 1])
                    with col_sel:
                        user_input = st.selectbox("Selecione seu perfil:", ALL_USERS)
                    with col_pic:
                        if user_input and user_input in profiles:
                            profile_data = profiles[user_input]
                            if len(profile_data) > 20:
                                st.markdown(f"""<img src="data:image/png;base64,{profile_data}" style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover; border: 2px solid #58cc02;">""", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div style='font-size: 50px; text-align: center;'>{profile_data}</div>", unsafe_allow_html=True)
                    
                    if st.button("🚀 ENTRAR", type="primary"):
                        if user_input:
                            st.session_state["logged_user"] = user_input
                            st.rerun()
            
            with tab_register:
                st.write("### Criar novo perfil")
                nm = st.text_input("Seu Nome")
                st.write("Escolha seu avatar:")
                avatar_choice = st.selectbox("Selecione um bichinho/ícone:", AVATARS)
                st.markdown("**OU**")
                uploaded_file = st.file_uploader("Envie sua foto (Prioridade sobre o ícone)", type=['png', 'jpg', 'jpeg'])
                
                if st.button("Salvar e Entrar"):
                    if nm and len(nm) > 2:
                        final_name = f"Dr(a). {nm}"
                        df, success, msg = add_new_user(df, final_name)
                        if success:
                            if uploaded_file is not None:
                                try:
                                    img = Image.open(uploaded_file)
                                    img.thumbnail((150, 150)) 
                                    b64_str = image_to_base64(img)
                                    save_profile(final_name, b64_str)
                                except: pass
                            else:
                                save_profile(final_name, avatar_choice)
                            st.session_state["logged_user"] = final_name
                            st.rerun()
                        else: st.error(msg)
                    else: st.warning("Nome muito curto.")
        st.stop()

current_user = st.session_state["logged_user"]

# --- SIDEBAR (PERFIL + XP + CHAT) ---
with st.sidebar:
    # 1. PERFIL
    if current_user in profiles:
        profile_data = profiles[current_user]
        if len(profile_data) > 20: 
            st.markdown(f"""<div class="profile-pic-container"><img class="profile-pic" src="data:image/png;base64,{profile_data}"></div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='profile-emoji'>{profile_data}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align: center; font-size: 100px; margin-bottom: 20px;'>🏥</div>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='profile-name'>{current_user}</div>", unsafe_allow_html=True)
    
    # Botão Sair deve ser primário para não ser afetado pelo CSS "invisível"
    if st.button("Sair", type="primary", use_container_width=True):
        del st.session_state["logged_user"]
        st.rerun()
    
    # 2. XP
    total_xp = 0
    for idx, row in df.iterrows():
        if f"{current_user}_Date" in df.columns:
            total_xp += calculate_xp(row["Data_Alvo"], row[f"{current_user}_Date"])
    
    st.markdown(f"""<div class="xp-box"><div style="font-size: 14px; color: #aaa;">💎 XP Total</div><div class="xp-val">{total_xp}</div></div>""", unsafe_allow_html=True)
    st.divider()

    # 3. CHAT (FIXO NO FIM - CORRIGIDO ALINHAMENTO E LIXEIRA)
    st.markdown("### 💬 Chat da Turma")
    chat_container = st.container(height=250)
    messages = load_chat()
    
    with chat_container:
        if not messages: st.caption("Nenhuma mensagem ainda.")
        for i, m in enumerate(messages):
            # Layout: Coluna 0.85 (Texto) | Coluna 0.15 (Botão)
            # vertical_alignment="center" garante o alinhamento
            cols_chat = st.columns([0.85, 0.15], gap="small", vertical_alignment="center")
            
            with cols_chat[0]:
                av_html = ""
                if len(m['avatar']) > 20: 
                    av_html = f'<img class="chat-avatar-img" src="data:image/png;base64,{m["avatar"]}">'
                else: 
                    av_html = f'<div class="chat-avatar-emoji">{m["avatar"]}</div>'
                
                st.markdown(f"""
                <div class="chat-msg-container">
                    {av_html}
                    <div class="chat-bubble">
                        <div class="chat-header"><strong>{m['user']}</strong> <span>{m['time']}</span></div>
                        {m['msg']}
                    </div>
                </div>""", unsafe_allow_html=True)
            
            with cols_chat[1]:
                if m['user'] == current_user:
                    msg_id = m.get("id", "legacy")
                    # Botão secundário (invisível por CSS)
                    if st.button("🗑️", key=f"del_{i}_{msg_id}", type="secondary", help="Excluir"):
                        if msg_id == "legacy":
                            messages.pop(i)
                            with open(CHAT_FILE, "w") as f: json.dump(messages, f)
                        else:
                            delete_chat_message(msg_id)
                        st.rerun()
            
    if prompt := st.chat_input("Mensagem...", key="sidebar_chat"):
        u_av = profiles.get(current_user, "👤")
        save_chat_message(current_user, prompt, u_av)
        st.rerun()
        
    # Botão de atualizar deve ser primário para não ser invisível
    if st.button("🔄 Atualizar Chat", type="primary", use_container_width=True): st.rerun()

# --- DASHBOARD ---
today = get_brazil_date() 
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
    </div>""", unsafe_allow_html=True)

st.progress(int(pct_completo) / 100)
st.caption(f"Você completou **{tasks_done}** de **{total_tasks}** atividades previstas no ano.")
st.divider()

# --- ABAS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📚 Lições", "🏆 Placar", "📂 Material", "⚙️ Admin", "🔰 Tutorial"])

# ABA 1
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
                except: d_alvo, d_br = get_brazil_date(), "--/--"
                
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
                </div>""", unsafe_allow_html=True)
                
                c1, c2 = st.columns([4, 1])
                with c1:
                    with st.expander("🔗 Recursos / Links"):
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
                                    cc1, cc2 = st.columns(2)
                                    if cc1.button("Sim", key=f"y{row['ID']}_{i}"):
                                        links.pop(i); df.at[idx, "Links_Content"] = json.dumps(links); save_data(df); st.rerun()
                                    if cc2.button("Não", key=f"n{row['ID']}_{i}"):
                                        del st.session_state[f"conf_del_{row['ID']}_{i}"]; st.rerun()
                        
                        st.caption("Adicionar Novo:")
                        nd = st.text_input("Nome:", key=f"dn{row['ID']}")
                        nu = st.text_input("URL:", key=f"du{row['ID']}")
                        if st.button("Adicionar", key=f"ba{row['ID']}", type="primary"):
                            if nd and nu:
                                links.append({"desc": nd, "url": nu})
                                df.at[idx, "Links_Content"] = json.dumps(links); save_data(df); st.success("Adicionado!"); st.rerun()
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
    st.markdown("Acesse abaixo o Google Drive contendo os PDFs, Vídeos e Resumos do Estratégia MED.")
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
    st.markdown("## 📚 Manual do Usuário Enamed")
    
    st.markdown("""
    <div class="warning-box">
    <strong>⚠️ PRÉ-REQUISITO OBRIGATÓRIO</strong><br>
    Este aplicativo é um <strong>GUIA DE ESTUDOS</strong>. Ele não contém os vídeos/PDFs hospedados aqui.<br><br>
    Para estudar, acesse o link do Drive do Estratégia MED disponível na aba <strong>📂 MATERIAL</strong>.<br>
    Se você usa outro cursinho, sem problemas! Basta se guiar pelo <strong>Tema do Dia</strong> descrito no cronograma.
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### 🧠 Metodologia de Estudo")
    st.markdown("""
    Nossa abordagem é baseada em **Engenharia Reversa** e **Estudo Ativo**. Esqueça assistir 4 horas de aula passivamente!
    
    1.  **⚡ Sprint Teórico (20% do tempo):** Leia o resumo ou mapa mental do tema do dia no Drive. Entenda o básico.
    2.  **📝 Questões (80% do tempo):** Vá para o banco de questões e faça a meta do dia (ex: 15 questões).
    3.  **🔄 Engenharia Reversa:** O mais importante! Para cada questão que você errar (ou chutar), leia o comentário detalhado e entenda *por que* errou. Anote o conceito chave.
    """)

    st.divider()

    st.markdown("### 📱 Fluxo de Uso do App")
    st.markdown("""
    1.  **Abra o App:** Faça login com seu Avatar.
    2.  **Verifique a Meta:** Vá na aba "Lições", abra a Semana atual e veja a tarefa do dia (ex: *Pediatria - Imunizações*).
    3.  **Estude:** Vá até o seu Drive/Material, encontre a aula correspondente e estude seguindo a metodologia acima.
    4.  **Registre o Link (Opcional):** Se achar um resumo top ou o link direto da pasta, clique em *🔗 Adicionar Link* no app e cole lá para facilitar seu acesso futuro (e dos colegas).
    5.  **Conclua:** Volte ao app e clique em **✅ Concluir**. Pronto! Seus 100 XP estão garantidos.
    """)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("📅 **Prazo:** Tente cumprir a meta no dia correto para ganhar pontuação máxima (Verde).")
    with col2:
        st.warning("🐢 **Atrasos:** Se fizer depois do prazo, a tarefa fica Amarela e vale metade dos pontos.")
