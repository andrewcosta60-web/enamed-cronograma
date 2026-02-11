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
import pytz
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURAÇÃO DE FUSO HORÁRIO ---
def get_brazil_time():
    return datetime.utcnow() - timedelta(hours=3)

def get_brazil_date():
    return get_brazil_time().date()

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Enamed Oficial", page_icon="🏥", layout="wide") 

# --- CONEXÃO GOOGLE SHEETS ---
def get_db_connection():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    if "gcp_service_account" not in st.secrets:
        st.error("⚠️ Configuração de Segredos (Secrets) não encontrada.")
        st.stop()
        
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # Tenta abrir a planilha pelo nome EXATO que vimos na sua imagem
    try:
        return client.open("enamed_db_v4.csv").sheet1
    except:
        try:
            return client.open("enamed_db_v4").sheet1
        except:
            st.error("❌ Não encontrei a planilha 'enamed_db_v4.csv'. Verifique o nome no Google Drive.")
            st.stop()

# --- FUNÇÕES DE CARREGAMENTO E SALVAMENTO ---

def init_db_online(sheet):
    # Gera o cronograma padrão
    f = io.StringIO(RAW_SCHEDULE)
    reader = csv.DictReader(f)
    
    rows = []
    for i, row_data in enumerate(reader):
        try:
            dt_obj = datetime.strptime(row_data['Data'], "%d/%m/%Y").date()
            formatted_date = str(dt_obj)
        except:
            formatted_date = str(get_brazil_date())

        row_dict = {
            "ID": i + 1,
            "Semana": int(row_data['Semana_Estudo']),
            "Data_Alvo": formatted_date,
            "Dia_Semana": row_data['Dia'],
            "Disciplina": row_data['Disciplina'],
            "Tema": row_data['Tema'],
            "Meta": row_data['Meta_Diaria'],
            "Link_Questões": "",
            "Links_Content": "[]"
        }
        for user in DEFAULT_USERS:
            row_dict[f"{user}_Status"] = False
            row_dict[f"{user}_Date"] = None
            
        rows.append(row_dict)
    
    df = pd.DataFrame(rows)
    
    # FORÇA a escrita na planilha (Limpa tudo antes)
    try:
        sheet.clear()
        data_to_upload = [df.columns.values.tolist()] + df.values.tolist()
        sheet.update(range_name='A1', values=data_to_upload)
        return df
    except Exception as e:
        st.error(f"Erro ao inicializar planilha: {e}")
        return df

def load_data():
    try:
        sheet = get_db_connection()
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        # --- CORREÇÃO DO ERRO (AUTO-REPARO) ---
        # Verifica se a planilha tem as colunas certas. 
        # Se estiver vazia OU com colunas erradas (seu caso atual), recria tudo.
        required_cols = ["ID", "Semana", "Disciplina"]
        
        if df.empty or not all(col in df.columns for col in required_cols):
            with st.spinner("⚠️ Planilha incorreta detectada. Reparando banco de dados..."):
                return init_db_online(sheet)
            
        return df
    except Exception as e:
        # Em caso de erro de conexão, retorna vazio para não travar o app
        # st.error(f"Erro ao carregar: {e}") 
        return pd.DataFrame()

def save_data(df):
    try:
        sheet = get_db_connection()
        sheet.clear()
        data_to_upload = [df.columns.values.tolist()] + df.values.tolist()
        sheet.update(range_name='A1', values=data_to_upload)
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")

# --- ARQUIVOS LOCAIS ---
PROFILE_FILE = "profiles.json"
CHAT_FILE = "chat_db.json"
DEFAULT_USERS = [] 

AVATARS = [
    "👨‍⚕️", "👩‍⚕️", "🦁", "🦊", "🐼", "🐨", "🐯", "🦖", "🦄", "🐸", 
    "🦉", "🐙", "🦋", "🍄", "🔥", "🚀", "💡", "🧠", "🫀", "💊", 
    "💉", "🦠", "🧬", "🩺", "🚑", "🏥", "🐧", "🦈", "🦅", "🐺"
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
29/06/2026,Seg,19,Ginecologia,Câncer de Mama
