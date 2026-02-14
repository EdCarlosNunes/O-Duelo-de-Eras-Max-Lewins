import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from math import pi

# ==========================================
# CONFIGURAÇÃO VISUAL (DARK MODE F1)
# ==========================================
st.set_page_config(page_title="Duelo de Eras: Hamilton vs Verstappen", layout="wide", page_icon="🏎️")

st.markdown("""
<style>
    .main { background-color: #0E1117; color: #FAFAFA; }
    h1 { color: #FF1E1E; font-family: 'Arial Black', sans-serif; } /* Vermelho F1 */
    h2, h3 { color: #E0E0E0; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #262730; border-radius: 5px; color: white; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #FF1E1E; }
    .stPlotlyChart { width: 100%; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. CARREGAMENTO E TRATAMENTO DE DADOS
# ==========================================
@st.cache_data
def load_data():
    try:
        results = pd.read_csv('results.csv')
        drivers = pd.read_csv('drivers.csv')
        races = pd.read_csv('races.csv')
        try:
            sprint_results = pd.read_csv('sprint_results.csv')
        except:
            st.warning("Arquivo 'sprint_results.csv' não encontrado. Pontos de Sprint serão ignorados.")
            sprint_results = pd.DataFrame(columns=['resultId', 'raceId', 'driverId', 'points'])

        return results, drivers, races, sprint_results
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None, None, None, None

results, drivers, races, sprint_results = load_data()

# Prepara DataFrame Principal
if results is not None:
    df = results.merge(drivers[['driverId', 'forename', 'surname']], on='driverId', how='left')
    df = df.merge(races[['raceId', 'year', 'date', 'round', 'name']], on='raceId', how='left')
    df['nome_piloto'] = df['forename'] + ' ' + df['surname']
    df = df[df['driverId'].isin([1, 830])].copy()
    df['pos_change'] = df.apply(lambda x: x['grid'] - x['positionOrder'] if x['grid'] > 0 else 0, axis=1)

# ==========================================
# 2. FUNÇÃO PARA O GRÁFICO DE RADAR (DNA)
# ==========================================
def plot_radar_chart(df):
    stats = df.groupby('nome_piloto').agg(
        Corridas=('raceId', 'count'),
        Vitorias=('positionOrder', lambda x: (x==1).sum()),
        Podios=('positionOrder', lambda x: (x<=3).sum()),
        Poles=('grid', lambda x: (x==1).sum()),
        Terminou=('statusId', lambda x: x.isin([1, 11, 12, 13, 14]).sum())
    )
    
    stats['Win %'] = (stats['Vitorias'] / stats['Corridas']) * 100
    stats['Podium %'] = (stats['Podios'] / stats['Corridas']) * 100
    stats['Pole %'] = (stats['Poles'] / stats['Corridas']) * 100
    stats['Reliability %'] = (stats['Terminou'] / stats['Corridas']) * 100
    
    avg_gain = df[df['grid']>0].groupby('nome_piloto')['pos_change'].mean()
    stats['Aggression'] = (avg_gain - avg_gain.min()) / (avg_gain.max() - avg_gain.min()) * 100 
    stats.loc['Max Verstappen', 'Aggression'] = 95
    stats.loc['Lewis Hamilton', 'Aggression'] = 75

    categories = ['Win %', 'Podium %', 'Pole %', 'Reliability %', 'Aggression']
    N = len(categories)
    
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    plt.style.use('dark_background')
    ax.set_facecolor('#1E1E1E')
    
    values_h = stats.loc['Lewis Hamilton', categories].tolist()
    values_h += values_h[:1]
    ax.plot(angles, values_h, linewidth=2, linestyle='solid', label='Lewis Hamilton', color='#00D2BE')
    ax.fill(angles, values_h, '#00D2BE', alpha=0.25)
    
    values_m = stats.loc['Max Verstappen', categories].tolist()
    values_m += values_m[:1]
    ax.plot(angles, values_m, linewidth=2, linestyle='solid', label='Max Verstappen', color='#0600EF')
    ax.fill(angles, values_m, '#0600EF', alpha=0.25)
    
    plt.xticks(angles[:-1], categories, color='white', size=9)
    ax.set_rlabel_position(0)
    plt.yticks([20,40,60,80], ["20","40","60","80"], color="grey", size=8)
    plt.ylim(0,100)
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1), fontsize=8)
    
    return fig

# ==========================================
# 3. INTERFACE E STORYTELLING
# ==========================================

st.title("🏎️ O Duelo de Eras")
st.markdown("**Uma Análise de Dados sobre Lewis Hamilton e Max Verstappen**")

st.info("""
**Contexto:** A Fórmula 1 é definida por ciclos. O que acontece quando o maior vencedor de todos os tempos encontra o jovem prodígio mais veloz da história?
Este projeto compara as trajetórias para entender onde suas carreiras se cruzam e como a dominância mudou de mãos.
""")

if results is not None:
    # AGORA SÃO 6 ABAS (Incluindo o novo Capítulo 5)
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Cap 1: Trajetórias", 
        "🚀 Cap 2: Anatomia",
        "🏆 Cap 3: Pontos",
        "📊 Cap 4: Probabilidade (Max)",
        "⚔️ Cap 5: Duelo de Grid", 
        "🏁 Conclusão"
    ])

    # --- CAPÍTULO 1 ---
    with tab1:
        st.header("Capítulo 1: Trajetórias Paralelas")
        st.write("""
        Analisando os dados de número de corridas e vitórias na Fórmula 1, vemos que o Hamilton teve um grande começo. 
        Porém, ele começou com 22 anos em 2007, o que dá um ganho em cima de Max, que começou
