
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ==========================================
# CONFIGURAÇÃO DA PÁGINA (ESTILO F1)
# ==========================================
st.set_page_config(page_title="Duelo de Eras: Hamilton vs Verstappen", layout="wide", page_icon="🏎️")

# Estilo CSS para dar um ar profissional (Fundo escuro e fontes)
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    h1 {
        color: #FF1E1E; /* Vermelho F1 */
        font-family: 'Arial Black', sans-serif;
    }
    h2, h3 {
        color: #FAFAFA;
    }
    .stAlert {
        background-color: #262730;
        border: 1px solid #4B4B4B;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. CARREGAMENTO DOS DADOS
# ==========================================
@st.cache_data
def load_data():
    try:
        results = pd.read_csv('results.csv').drop_duplicates()
        drivers = pd.read_csv('drivers.csv').drop_duplicates()
        races = pd.read_csv('races.csv').drop_duplicates()
        
        # Merge para ter nome dos pilotos e ano das corridas
        df = results.merge(drivers[['driverId', 'forename', 'surname']], on='driverId', how='left')
        df = df.merge(races[['raceId', 'year', 'date', 'round']], on='raceId', how='left')
        df['nome_piloto'] = df['forename'] + ' ' + df['surname']
        
        # Filtra apenas Hamilton (1) e Verstappen (830) para otimizar
        df_duelo = df[df['driverId'].isin([1, 830])].copy()
        
        return df_duelo
    except Exception as e:
        st.error(f"Erro crítico ao carregar dados: {e}")
        return None

df = load_data()

# ==========================================
# 2. INTRODUÇÃO: O CONTEXTO
# ==========================================
st.title("🏎️ O Duelo de Eras")
st.subheader("Uma Análise de Dados sobre Lewis Hamilton e Max Verstappen")

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("""
    **A Fórmula 1 é definida por ciclos.** O que acontece quando o maior vencedor de todos os tempos encontra o jovem prodígio mais veloz da história?
    
    Este projeto utiliza **Python e Ciência de Dados** para comparar as trajetórias de **Lewis Hamilton** e **Max Verstappen**, não apenas contando vitórias, mas dissecando **como** elas acontecem.
    """)
with col2:
    st.info("""
    **Ferramentas Utilizadas:**
    - Python (Pandas)
    - Streamlit (Web App)
    - Seaborn/Matplotlib (Viz)
    """)

# ==========================================
# 3. NARRATIVA E GRÁFICOS
# ==========================================

# Criando as Abas para os Capítulos da História
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Cap 1: Trajetórias Paralelas", 
    "🚀 Cap 2: Perfil de Ultrapassagem",
    "🎻 Cap 3: Consistência (Violin)",
    "🧬 Conclusão: DNA do Piloto"
])

# --- CAPÍTULO 1: TRAJETÓRIAS ---
with tab1:
    st.header("Capítulo 1: Sucesso vs. Experiência")
    st.markdown("""
    > *"Não olhamos para os anos do calendário, mas para a quilometragem de cada um."*
    
    Lewis Hamilton teve um início explosivo na McLaren. Max Verstappen começou na Toro Rosso, mas seu ritmo de crescimento recente é o mais agressivo da história.
    O gráfico abaixo sincroniza as carreiras pelo **número de corridas disputadas**, ignorando os anos.
    """)
    
    if df is not None:
        # Preparando dados acumulados
        df_traj = df.sort_values(['driverId', 'year', 'round'])
        df_traj['win'] = (df_traj['positionOrder'] == 1).astype(int)
        
        # Cálculo acumulado por piloto
        df_traj['cum_wins'] = df_traj.groupby('driverId')['win'].cumsum()
        df_traj['race_count'] = df_traj.groupby('driverId').cumcount() + 1
        
        # Plot
        fig1, ax1 = plt.subplots(figsize=(12, 6))
        # Estilo Dark para o gráfico
        plt.style.use('dark_background')
        
        sns.lineplot(data=df_traj, x='race_count', y='cum_wins', hue='nome_piloto', 
                     palette={'Lewis Hamilton': '#00D2BE', 'Max Verstappen': '#0600EF'}, 
                     linewidth=2.5, ax=ax1)
        
        ax1.set_title("Evolução de Vitórias por Número de GPs Disputados", fontsize=14, color='white')
        ax1.set_xlabel("Número de Corridas na Carreira", color='white')
        ax1.set_ylabel("Vitórias Acumuladas", color='white')
        ax1.grid(color='#444444', linestyle='--', linewidth=0.5)
        ax1.legend(facecolor='#262730', edgecolor='white')
        
        st.pyplot(fig1)
        st.caption("Note como as linhas se cruzam ou se aproximam em momentos chave da carreira (aprox. corrida 150-200).")

# --- CAPÍTULO 2: RACER INDEX ---
with tab2:
    st.header("Capítulo 2: A Anatomia da Vitória")
    st.markdown("""
    > *"Como cada um se comporta no domingo? Quem é o caçador e quem é a caça?"*
    
    - **Lewis Hamilton (O Mestre da Precisão):** O pico no zero indica que ele larga na frente e mantém a ponta.
    - **Max Verstappen (O Mestre da Recuperação):** A curva mais larga para a direita mostra sua tendência a escalar o pelotão.
    """)
    
    if df is not None:
        # Cálculo de ganho de posição
        df_k = df.copy()
        df_k = df_k[df_k['grid'] > 0] # Remove largadas do box/erros
        df_k['pos_change'] = df_k['grid'] - df_k['positionOrder']
        
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        plt.style.use('dark_background')
        
        sns.kdeplot(data=df_k, x='pos_change', hue='nome_piloto', fill=True, 
                    palette={'Lewis Hamilton': '#00D2BE', 'Max Verstappen': '#0600EF'}, 
                    alpha=0.3, linewidth=2, ax=ax2)
        
        ax2.axvline(0, color='white', linestyle='--', alpha=0.6, label='Mantém Posição')
        ax2.set_title("Densidade de Ganho de Posições (KDE)", fontsize=14, color='white')
        ax2.set_xlabel("Saldo de Posições (Direita = Ganhou | Esquerda = Perdeu)", color='white')
        ax2.set_xlim(-5, 10)
        ax2.legend()
        
        st.pyplot(fig2)

# --- CAPÍTULO 3: VIOLIN PLOTS ---
with tab3:
    st.header("Capítulo 3: Consistência e Domínio")
    st.markdown("""
    Os **Violin Plots** mostram a distribuição de resultados em uma temporada. 
    - Um violino "gordo" embaixo significa muitos pódios/vitórias.
    - Um violino "esticado" significa resultados inconstantes.
    """)
    
    if df is not None:
        anos = st.slider("Selecione o intervalo de anos:", 2014, 2024, (2021, 2024))
        df_v = df[(df['year'] >= anos[0]) & (df['year'] <= anos[1])]
        
        fig3, ax3 = plt.subplots(figsize=(12, 6))
        plt.style.use('dark_background')
        
        sns.violinplot(x='year', y='positionOrder', hue='nome_piloto', data=df_v,
                       split=True, inner='quart', 
                       palette={'Lewis Hamilton': '#00D2BE', 'Max Verstappen': '#0600EF'}, ax=ax3)
        
        ax3.set_ylim(0, 20) # Foca nas primeiras 20 posições
        ax3.invert_yaxis() # 1º lugar no topo
        ax3.set_title(f"Distribuição de Resultados ({anos[0]}-{anos[1]})", fontsize=14, color='white')
        
        st.pyplot(fig3)
        st.markdown("**Insight:** Observe como o violino de Max em 2023 é quase uma linha reta no topo (1º lugar), indicando uma das temporadas mais dominantes da história.")

# --- CAPÍTULO 4: CONCLUSÃO ---
with tab4:
    st.header("Conclusão: O Que os Dados Dizem?")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.success("Lewis Hamilton")
        st.write("Representa a **Consistência Técnica**. Maior número de poles e vitórias absolutas, construídas com precisão cirúrgica e gestão de pneus.")
    with col_c2:
        st.warning("Max Verstappen")
        st.write("Representa a **Aceleração Pura**. Maior taxa de vitórias por temporada recente e capacidade inigualável de recuperação de posições.")
    
    st.markdown("---")
    st.markdown("""
    ### 🧠 Visão do Analista
    Os dados não apontam um "melhor" definitivo, mas mostram uma transição de estilos. A era Hamilton foi marcada pela **estratégia e resistência**. A era Verstappen é marcada pela **agressividade e ritmo puro**.
    
    *Projeto desenvolvido por [Seu Nome] para Portfólio de Data Science.*
    """)

# Rodapé
st.markdown("---")
st.markdown("Dados fornecidos pela Ergast API (1950-2024) | Processados via Pandas")
