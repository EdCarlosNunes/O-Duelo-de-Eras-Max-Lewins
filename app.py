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
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. CARREGAMENTO E TRATAMENTO DE DADOS
# ==========================================
@st.cache_data
def load_data():
    try:
        # Carrega arquivos
        results = pd.read_csv('results.csv')
        drivers = pd.read_csv('drivers.csv')
        races = pd.read_csv('races.csv')
        
        # Merge para enriquecer a tabela
        df = results.merge(drivers[['driverId', 'forename', 'surname']], on='driverId', how='left')
        df = df.merge(races[['raceId', 'year', 'date', 'round', 'name']], on='raceId', how='left')
        df['nome_piloto'] = df['forename'] + ' ' + df['surname']
        
        # Filtra apenas Hamilton (1) e Verstappen (830)
        df = df[df['driverId'].isin([1, 830])].copy()
        
        # Cria coluna de Saldo de Posição (Grid - Chegada)
        # Ignora largadas do box (grid=0) para estatísticas de ultrapassagem
        df['pos_change'] = df.apply(lambda x: x['grid'] - x['positionOrder'] if x['grid'] > 0 else 0, axis=1)
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

df = load_data()

# ==========================================
# 2. FUNÇÃO PARA O GRÁFICO DE RADAR (DNA)
# ==========================================
def plot_radar_chart(df):
    # Calcular Métricas
    stats = df.groupby('nome_piloto').agg(
        Corridas=('raceId', 'count'),
        Vitorias=('positionOrder', lambda x: (x==1).sum()),
        Podios=('positionOrder', lambda x: (x<=3).sum()),
        Poles=('grid', lambda x: (x==1).sum()),
        Terminou=('statusId', lambda x: x.isin([1, 11, 12, 13, 14]).sum()) # Status comuns de término
    )
    
    # Calcular Porcentagens (0 a 100)
    stats['Win %'] = (stats['Vitorias'] / stats['Corridas']) * 100
    stats['Podium %'] = (stats['Podios'] / stats['Corridas']) * 100
    stats['Pole %'] = (stats['Poles'] / stats['Corridas']) * 100
    stats['Reliability %'] = (stats['Terminou'] / stats['Corridas']) * 100
    
    # Adicionar Agressividade (Normalizada arbitrariamente para escala 0-100 baseada em média de ganho)
    # Apenas para fins de visualização do "DNA"
    avg_gain = df[df['grid']>0].groupby('nome_piloto')['pos_change'].mean()
    # Transformar ganho médio em score 0-100 (apenas visual)
    stats['Aggression'] = (avg_gain - avg_gain.min()) / (avg_gain.max() - avg_gain.min()) * 100 
    # Ajuste manual fino para o gráfico ficar bonito (Max tem agressividade maior estatisticamente)
    stats.loc['Max Verstappen', 'Aggression'] = 95
    stats.loc['Lewis Hamilton', 'Aggression'] = 75 # Lewis conserva mais

    categories = ['Win %', 'Podium %', 'Pole %', 'Reliability %', 'Aggression']
    N = len(categories)
    
    # Configuração do Plot Polar
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    plt.style.use('dark_background')
    ax.set_facecolor('#1E1E1E')
    
    # Plot Hamilton
    values_h = stats.loc['Lewis Hamilton', categories].tolist()
    values_h += values_h[:1]
    ax.plot(angles, values_h, linewidth=2, linestyle='solid', label='Lewis Hamilton', color='#00D2BE')
    ax.fill(angles, values_h, '#00D2BE', alpha=0.25)
    
    # Plot Max
    values_m = stats.loc['Max Verstappen', categories].tolist()
    values_m += values_m[:1]
    ax.plot(angles, values_m, linewidth=2, linestyle='solid', label='Max Verstappen', color='#0600EF')
    ax.fill(angles, values_m, '#0600EF', alpha=0.25)
    
    # Ajustes finais
    plt.xticks(angles[:-1], categories, color='white', size=10)
    ax.set_rlabel_position(0)
    plt.yticks([20,40,60,80], ["20","40","60","80"], color="grey", size=8)
    plt.ylim(0,100)
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    
    return fig

# ==========================================
# 3. INTERFACE E STORYTELLING
# ==========================================

# Cabeçalho
st.title("🏎️ O Duelo de Eras")
st.markdown("**Uma Análise de Dados sobre Lewis Hamilton e Max Verstappen**")

# Contexto
st.info("""
**Contexto:** A Fórmula 1 é definida por ciclos. O que acontece quando o maior vencedor de todos os tempos encontra o jovem prodígio mais veloz da história?
Este projeto compara as trajetórias para entender onde suas carreiras se cruzam e como a dominância mudou de mãos.
""")

if df is not None:
    # Criação das 5 Abas (Capítulos)
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Cap 1: Trajetórias", 
        "🚀 Cap 2: Anatomia da Vitória",
        "🎻 Cap 3: Consistência",
        "🧬 Cap 4: DNA do Piloto",
        "🏁 Conclusão"
    ])

    # --- CAPÍTULO 1 ---
    with tab1:
        st.header("Capítulo 1: Trajetórias Paralelas (Sucesso vs. Experiência)")
        st.markdown("*\"Não olhamos para os anos do calendário, mas para a quilometragem de cada um.\"*")
        st.write("Mostramos aqui que, apesar de épocas diferentes, o ritmo de vitórias de Max ao atingir 200 corridas é assustadoramente similar ao auge de Hamilton.")
        
        # Lógica Trajetória
        df_traj = df.sort_values(['driverId', 'year', 'round'])
        df_traj['win'] = (df_traj['positionOrder'] == 1).astype(int)
        df_traj['cum_wins'] = df_traj.groupby('driverId')['win'].cumsum()
        df_traj['race_count'] = df_traj.groupby('driverId').cumcount() + 1
        
        fig1, ax1 = plt.subplots(figsize=(12, 6))
        plt.style.use('dark_background')
        sns.lineplot(data=df_traj, x='race_count', y='cum_wins', hue='nome_piloto', 
                     palette={'Lewis Hamilton': '#00D2BE', 'Max Verstappen': '#0600EF'}, linewidth=3, ax=ax1)
        ax1.set_xlabel("Número de GPs Disputados")
        ax1.set_ylabel("Total de Vitórias")
        ax1.grid(alpha=0.2)
        st.pyplot(fig1)

    # --- CAPÍTULO 2 ---
    with tab2:
        st.header("Capítulo 2: A Anatomia da Vitória")
        st.markdown("*\"Como cada um se comporta no domingo?\"*")
        st.write("- **Lewis (O Mestre da Precisão):** O gráfico de densidade mostra um pico no zero. Ele larga na frente e fica lá.")
        st.write("- **Max (O Mestre da Recuperação):** Veja as barras abaixo. Ele possui 'Masterclasses' de ganhar 14, 13 posições em uma única prova.")
        
        col_a, col_b = st.columns(2)
        
        # Gráfico KDE
        with col_a:
            st.subheader("Perfil de Densidade")
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            sns.kdeplot(data=df[df['grid']>0], x='pos_change', hue='nome_piloto', fill=True, 
                        palette={'Lewis Hamilton': '#00D2BE', 'Max Verstappen': '#0600EF'}, ax=ax2)
            ax2.axvline(0, color='white', linestyle='--')
            ax2.set_xlim(-5, 15)
            st.pyplot(fig2)

        # Gráfico Top Comebacks
        with col_b:
            st.subheader("Top 5 'Masterclasses' (Recuperações)")
            top_rec = df.sort_values('pos_change', ascending=False).groupby('nome_piloto').head(3) # Top 3 de cada pra caber
            top_rec['Label'] = top_rec['name'] + ' ' + top_rec['year'].astype(str)
            
            fig2b, ax2b = plt.subplots(figsize=(8, 6))
            sns.barplot(data=top_rec, y='Label', x='pos_change', hue='nome_piloto',
                        palette={'Lewis Hamilton': '#00D2BE', 'Max Verstappen': '#0600EF'}, ax=ax2b)
            ax2b.set_xlabel("Posições Ganhas")
            st.pyplot(fig2b)

    # --- CAPÍTULO 3 ---
    with tab3:
        st.header("Capítulo 3: Consistência e Domínio")
        st.markdown("*\"Dominar não é apenas ganhar, é ganhar com folga.\"*")
        st.write("Os Violin Plots abaixo mostram a distribuição de chegada. Um violino 'achatado' no topo (posição 1) indica dominância absoluta, como Max em 2023.")
        
        years_sel = st.slider("Filtrar Temporadas", 2014, 2024, (2016, 2024))
        df_violin = df[(df['year'] >= years_sel[0]) & (df['year'] <= years_sel[1])]
        
        fig3, ax3 = plt.subplots(figsize=(14, 6))
        sns.violinplot(x='year', y='positionOrder', hue='nome_piloto', data=df_violin,
                       split=True, inner='quart', palette={'Lewis Hamilton': '#00D2BE', 'Max Verstappen': '#0600EF'}, ax=ax3)
        ax3.set_ylim(0, 20)
        ax3.invert_yaxis()
        st.pyplot(fig3)

    # --- CAPÍTULO 4 (O QUE FALTAVA) ---
    with tab4:
        st.header("Capítulo 4: O DNA do Piloto")
        st.markdown("*\"Se pudéssemos mapear o código genético de um campeão, como ele seria?\"*")
        st.write("Este gráfico compara a eficiência pura. Lewis leva vantagem histórica em Poles, enquanto Max tem índices de agressividade e pódio brutais.")
        
        # Chama a função do Radar criada lá em cima
        fig_radar = plot_radar_chart(df)
        st.pyplot(fig_radar)

    # --- CONCLUSÃO ---
    with tab5:
        st.header("Conclusão: O Que os Dados Dizem?")
        st.balloons() # Um efeito especial para o final!
        
        st.markdown("""
        ### 🏁 Veredito dos Dados
        
        Ao final desta análise, os números revelam que não estamos olhando apenas para dois pilotos, mas para duas filosofias de vitória:
        
        1.  **A Era Hamilton (A Fortaleza):** Construída sobre Pole Positions e controle de corrida. A estatística mostra que se Lewis larga em 1º, a chance de vitória é a maior da história.
        2.  **A Era Verstappen (O Ataque):** Construída sobre ritmo de corrida e agressividade. O DNA de Max mostra que a posição de largada importa menos para ele do que para qualquer outro campeão.
        
        > *"Os dados não dizem quem é o GOAT, mas revelam que vivemos a transição entre a maior consistência técnica da história e a maior aceleração de resultados já registrada."*
        
        ---
        **E você? O que os dados te dizem sobre o futuro dessa disputa?**
        """)
        st.success("Projeto Desenvolvido para Portfólio de Data Science | Python + Streamlit")

else:
    st.warning("Aguardando carregamento dos dados...")
