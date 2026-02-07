import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import html
import io
import csv

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Enamed Oficial", page_icon="🏥", layout="wide") 
# Mudei layout para "wide" para caber o título e as caixas lado a lado

# --- CSS GLOBAL (CORRIGIDO PARA CONTRASTE E TAMANHO) ---
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
    
    /* Barra de Progresso */
    .stProgress > div > div > div > div {
        background-color: #58cc02;
    }
    
    /* === CORREÇÃO DAS CAIXAS DE MÉTRICAS (DASHBOARD) === */
    .dash-card {
        background-color: #f0f2f6; /* Fundo Cinza Claro */
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        border: 1px solid #dcdcdc;
        height: 100%;
    }
    .dash-label {
        font-size: 12px !important;
        font-weight: bold !important;
        color: #555555 !important; /* Texto Cinza Escuro (Sempre visível) */
        margin-bottom: 2px;
        text-transform: uppercase;
    }
    .dash-value {
        font-size: 18px !important;
        font-weight: 800 !important;
        color: #000000 !important; /* Texto Preto (Sempre visível) */
    }
    
    /* Título Personalizado para alinhar com as caixas */
    .custom-title {
        font-size: 40px;
        font-weight: bold;
        margin-bottom: 0px;
        padding-bottom: 0px;
        line-height: 1.2;
    }
    
    /* Caixa de XP na Sidebar */
    .xp-box {
        background-color: #262730;
        border: 1px solid #444;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin-top: 10px;
    }
    .xp-val {
        font-size: 32px;
        font-weight: bold;
        color: #58cc02;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÕES ---
CSV_FILE = "enamed_daily_db.csv"
DEFAULT_USERS = [] 

# Avatares
AVATARS = [
    "👨‍⚕️", "👩‍⚕️", "🏥", "🧠", "🫀", "🧬", "🚑", "🩺", "💉", "💊", 
    "🦠", "🩸", "🎓", "🦁", "🦊", "🐼", "🐨", "🐯", "🦖", "🚀", "💡", "🔥"
]

# --- DADOS DO CRONOGRAMA ---
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
        cols = ["ID", "Semana", "Data_Alvo", "Dia_Semana", "Disciplina", "Tema", "Meta", "Link_Questões"]
        for user in DEFAULT_USERS:
            cols.extend([f"{user}_Status", f"{user}_Date"])
            
        df = pd.DataFrame(columns=cols)
        
        # Parse do CSV Raw
        f = io.StringIO(RAW_SCHEDULE)
        reader = csv.DictReader(f)
        
        initial_data = []
        for i, row_data in enumerate(reader):
            try:
                date_str = row_data['Data']
                dt_obj = datetime.strptime(date_str, "%d/%m/%Y").date()
                formatted_date = str(dt_obj)
            except:
                formatted_date = str(date.today())

            row = [
                i + 1, 
                int(row_data['Semana_Estudo']), 
                formatted_date, 
                row_data['Dia'],
                row_data['Disciplina'],
                row_data['Tema'],
                row_data['Meta_Diaria'],
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
            st.markdown("<div style='text-align: center; font-size: 80px;'>🏥</div>", unsafe_allow_html=True)
            st.markdown("<h1 style='text-align: center;'>Enamed Diário</h1>", unsafe_allow_html=True)
            st.caption("<div style='text-align: center;'>Controle Dia a Dia • 2026</div>", unsafe_allow_html=True)
            
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
    st.markdown("<div style='text-align: center; font-size: 100px; margin-bottom: 20px;'>🏥</div>", unsafe_allow_html=True)
    st.markdown(f"### Olá, **{current_user}**! 👋")
    if st.button("Sair"):
        del st.session_state["logged_user"]
        st.query_params.clear()
        st.rerun()
    
    st.divider()
    
    # Cálculo de XP
    total_xp = 0
    for idx, row in df.iterrows():
        if f"{current_user}_Date" in df.columns:
            total_xp += calculate_xp(row["Data_Alvo"], row[f"{current_user}_Date"])
    
    # Caixa XP Personalizada (Visível no Dark Mode)
    st.markdown(f"""
    <div class="xp-box">
        <div style="font-size: 14px; color: #aaa;">💎 XP Total</div>
        <div class="xp-val">{total_xp}</div>
    </div>
    """, unsafe_allow_html=True)

# --- LAYOUT DO TOPO (TÍTULO + DASHBOARD) ---
# Cálculo de Métricas
today = date.today()
df['dt_obj'] = pd.to_datetime(df['Data_Alvo']).dt.date

# 1. Identificar Semana
future_tasks = df[df['dt_obj'] >= today]
if df['dt_obj'].min() > today:
    status_cronograma = "Pré-Edital"
elif future_tasks.empty:
    status_cronograma = "Concluído"
else:
    prox_semana = future_tasks.iloc[0]['Semana']
    status_cronograma = f"Semana {prox_semana:02d}"

# 2. Calcular Progresso
total_tasks = len(df)
tasks_done = 0
if f"{current_user}_Status" in df.columns:
    tasks_done = df[f"{current_user}_Status"].sum()
pct_completo = (tasks_done / total_tasks) * 100 if total_tasks > 0 else 0

# 3. Renderizar (Grid 2 colunas: Título | Dashboard)
c_title, c_dash = st.columns([1.5, 2.5])

with c_title:
    st.markdown("<div class='custom-title'>🏥 Desafio<br>Enamed</div>", unsafe_allow_html=True)

with c_dash:
    # Pequenas cartas HTML lado a lado
    st.markdown(f"""
    <div style="display: flex; gap: 10px; height: 100%; align-items: center;">
        <div class="dash-card" style="flex: 1;">
            <div class="dash-label">📅 Hoje</div>
            <div class="dash-value">{today.strftime("%d/%m")}</div>
        </div>
        <div class="dash-card" style="flex: 1;">
            <div class="dash-label">📍 Cronograma</div>
            <div class="dash-value">{status_cronograma}</div>
        </div>
        <div class="dash-card" style="flex: 1;">
            <div class="dash-label">🚀 Concluído</div>
            <div class="dash-value">{int(pct_completo)}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.progress(int(pct_completo) / 100)
st.caption(f"Você completou **{tasks_done}** de **{total_tasks}** atividades previstas no ano.")
st.divider()

# --- ABAS ---
tab1, tab2, tab3, tab4 = st.tabs(["📚 Lições", "🏆 Placar", "⚙️ Admin", "🔰 Tutorial"])

# --- ABA 1: LIÇÕES ---
with tab1:
    st.markdown("### 📅 Cronograma Diário")
    semanas = sorted(df["Semana"].unique())
    for sem in semanas:
        df_week = df[df["Semana"] == sem]
        xp_feito = 0
        xp_total = 0
        for idx, row in df_week.iterrows():
            if f"{current_user}_Status" in df.columns:
                xp_total += 100
                if row[f"{current_user}_Status"]:
                    xp_feito += calculate_xp(row["Data_Alvo"], row[f"{current_user}_Date"])
        
        start_open = (sem == 1)
        with st.expander(f"📍 Semana {sem:02d} — ({xp_feito} / {xp_total} XP)", expanded=start_open):
            for index, row in df_week.iterrows():
                real_idx = df[df["ID"] == row["ID"]].index[0]
                if f"{current_user}_Status" not in df.columns: st.rerun()

                status = row[f"{current_user}_Status"]
                hoje = date.today()
                try: 
                    d_alvo = datetime.strptime(str(row["Data_Alvo"]), "%Y-%m-%d").date()
                    d_br = d_alvo.strftime("%d/%m")
                except: d_alvo = date.today(); d_br = "--/--"
                
                bg_tema, border_tema = "#ffffff", "#e5e5e5"
                if status:
                    b_data, bg_data, t_data, lbl, ico, border_tema = "#58cc02", "#e6fffa", "#58cc02", "FEITO", "✅", "#58cc02"
                elif hoje > d_alvo:
                    b_data, bg_data, t_data, lbl, ico, border_tema = "#ffc800", "#fff5d1", "#d4a000", "ATRASADO", "⚠️", "#ffc800"
                else:
                    b_data, bg_data, t_data, lbl, ico = "#e5e5e5", "#f7f7f7", "#afafaf", "PRAZO", "📅"

                disc_esc = html.escape(str(row['Disciplina']))
                tema_esc = html.escape(str(row['Tema']))
                meta_esc = html.escape(str(row['Meta']))

                st.markdown(f"""
                <div style="display: flex; gap: 10px; align-items: stretch; width: 100%; margin-bottom: 10px; font-family: 'Varela Round', sans-serif;">
                    <div style="flex: 0 0 80px; background-color: {bg_data}; border: 2px solid {b_data}; border-radius: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 5px; color: {t_data};">
                        <div style="font-size: 9px; font-weight: bold;">{lbl}</div>
                        <div style="font-size: 18px;">{ico}</div>
                        <div style="font-size: 11px; font-weight: bold;">{row['Dia_Semana']}</div>
                        <div style="font-size: 12px; font-weight: bold;">{d_br}</div>
                    </div>
                    <div style="flex: 1; background-color: {bg_tema}; border: 2px solid {border_tema}; border-radius: 12px; padding: 10px; display: flex; flex-direction: column; justify-content: center;">
                        <div style="font-size: 11px; color: #888; text-transform: uppercase; font-weight: bold;">{disc_esc}</div>
                        <div style="font-size: 15px; font-weight: bold; color: #4b4b4b; line-height: 1.2; margin-bottom: 3px;">{tema_esc}</div>
                        <div style="font-size: 12px; color: #666;">🎯 {meta_esc}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                c1, c2 = st.columns([4, 1])
                with c1:
                    with st.expander("🔗 Adicionar Link"):
                        cur_link = row['Link_Questões']
                        if cur_link: st.markdown(f"**Link:** [{cur_link}]({cur_link})")
                        nl = st.text_input("Novo Link:", key=f"l_{row['ID']}")
                        if st.button("Salvar", key=f"s_{row['ID']}"):
                            df.at[real_idx, "Link_Questões"] = nl
                            save_data(df); st.success("Salvo!"); st.rerun()
                with c2:
                    if status:
                        if st.button("Desfazer", key=f"r_{row['ID']}"):
                            df.at[real_idx, f"{current_user}_Status"] = False; save_data(df); st.rerun()
                    else:
                        lbl_btn = "Entregar" if hoje > d_alvo else "Concluir"
                        t_btn = "secondary" if hoje > d_alvo else "primary"
                        if st.button(lbl_btn, key=f"c_{row['ID']}", type=t_btn):
                            df.at[real_idx, f"{current_user}_Status"] = True
                            df.at[real_idx, f"{current_user}_Date"] = str(date.today())
                            save_data(df); st.rerun()
                st.divider()

# --- ABA 2: PLACAR ---
with tab2:
    st.subheader("🏆 Classificação Geral")
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
    st.header("⚙️ Administração")
    if "admin_unlocked" not in st.session_state: st.session_state["admin_unlocked"] = False
    if not st.session_state["admin_unlocked"]:
        senha = st.text_input("Senha:", type="password")
        if senha == "UNIARP":
            st.session_state["admin_unlocked"] = True; st.rerun()
        elif senha: st.error("Senha incorreta!")
    
    if st.session_state["admin_unlocked"]:
        st.success("🔓 Liberado")
        if st.button("🗑️ RESETAR TUDO", type="primary"):
            if os.path.exists(CSV_FILE):
                os.remove(CSV_FILE)
                for k in list(st.session_state.keys()): del st.session_state[k]
                st.rerun()
        if st.button("🔒 Sair"):
            st.session_state["admin_unlocked"] = False; st.rerun()

# --- ABA 4: TUTORIAL ---
with tab4:
    st.markdown("## 📚 Manual do Usuário Enamed")
    
    st.markdown("""
    <div class="warning-box">
    <strong>⚠️ PRÉ-REQUISITO OBRIGATÓRIO</strong><br>
    Este aplicativo é um <strong>GUIA DE ESTUDOS</strong> e <strong>TRACKER DE METAS</strong>. Ele não contém as aulas em si.<br><br>
    Para estudar, você deve ter acesso ao <strong>Drive do Estratégia MED</strong> (ou seu material de preferência) contendo os PDFs e Vídeos das aulas citadas no cronograma.
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

streamlit run app.py

