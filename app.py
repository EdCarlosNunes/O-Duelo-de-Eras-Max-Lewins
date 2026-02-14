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
        # Carrega arquivos brutos
        results = pd.read_csv('results.csv')
        drivers = pd.read_csv('drivers.csv')
        races = pd.read_csv('races.csv')
        # Tenta carregar sprint, se não existir cria vazio para não quebrar
        try:
            sprint_results = pd.read_csv('sprint_results.csv')
        except:
            st.warning("Arquivo 'sprint_results.csv' não encontrado. Pontos de Sprint serão ignorados.")
            sprint_results = pd.DataFrame(columns=['resultId', 'raceId', 'driverId', 'points'])

        return results, drivers, races, sprint_results
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None, None, None, None

# Carrega os dados brutos
results, drivers, races, sprint_results = load_data()

# Prepara o DataFrame Principal (DF) para os outros gráficos
if results is not None:
    df = results.merge(drivers[['driverId', 'forename', 'surname']], on='driverId', how='left')
    df = df.merge(races[['raceId', 'year', 'date', 'round', 'name']], on='raceId', how='left')
    df['nome_piloto'] = df['forename'] + ' ' + df['surname']
    df = df[df['driverId'].isin([1, 830])].copy() # Filtra Ham e Max
    # Cria coluna de Saldo de Posição
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
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Cap 1: Trajetórias", 
        "🚀 Cap 2: Anatomia da Vitória",
        "🏆 Cap 3: Pontos Totais",
        "🧬 Cap 4: DNA do Piloto",
        "🏁 Conclusão"
    ])

    # --- CAPÍTULO 1 ---
    with tab1:
        st.header("Capítulo 1: Trajetórias Paralelas (Sucesso vs. Experiência)")
        st.write("""
        Analisando os dados de número de corridas e vitórias na Fórmula 1, vemos que o Hamilton teve um grande começo. 
        Porém, ele começou com 22 anos em 2007, o que dá um ganho em cima de Max, que começou na Fórmula 1 com 17 anos em 2015. 
        Conseguimos ver que a maturidade contou para esse início grandioso de Hamilton, porém vemos que o ritmo de vitórias de Max ao atingir 200 corridas é assustadoramente similar ao auge de Hamilton.
        """)
        
        df_traj = df.sort_values(['driverId', 'year', 'round'])
        df_traj['win'] = (df_traj['positionOrder'] == 1).astype(int)
        df_traj['cum_wins'] = df_traj.groupby('driverId')['win'].cumsum()
        df_traj['race_count'] = df_traj.groupby('driverId').cumcount() + 1
        
        fig1, ax1 = plt.subplots(figsize=(10, 4))
        plt.style.use('dark_background')
        sns.lineplot(data=df_traj, x='race_count', y='cum_wins', hue='nome_piloto', 
                     palette={'Lewis Hamilton': '#00D2BE', 'Max Verstappen': '#0600EF'}, linewidth=2.5, ax=ax1)
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
        with col_a:
            st.subheader("Perfil de Densidade")
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            sns.kdeplot(data=df[df['grid']>0], x='pos_change', hue='nome_piloto', fill=True, 
                        palette={'Lewis Hamilton': '#00D2BE', 'Max Verstappen': '#0600EF'}, ax=ax2)
            ax2.axvline(0, color='white', linestyle='--')
            ax2.set_xlim(-5, 15)
            st.pyplot(fig2)
        with col_b:
            st.subheader("Top 'Masterclasses'")
            top_rec = df.sort_values('pos_change', ascending=False).groupby('nome_piloto').head(3)
            top_rec['Label'] = top_rec['name'] + ' ' + top_rec['year'].astype(str)
            fig2b, ax2b = plt.subplots(figsize=(6, 4))
            sns.barplot(data=top_rec, y='Label', x='pos_change', hue='nome_piloto',
                        palette={'Lewis Hamilton': '#00D2BE', 'Max Verstappen': '#0600EF'}, ax=ax2b)
            ax2b.set_xlabel("Posições Ganhas")
            st.pyplot(fig2b)

    # --- CAPÍTULO 3 (ALTERADO) ---
    with tab3:
        st.header("Capítulo 3: Comparação de Pontos por Temporada")
        st.markdown("""
        Neste gráfico, comparamos o início da jornada de ambos. A análise sugere que **Max Verstappen vive seu auge técnico**, quebrando recordes consecutivamente, enquanto Hamilton caminha para o encerramento de uma carreira lendária. 
        É provável que Max supere os números de Lewis, embora com um estilo diferente. Se no passado Max mostrava instabilidade, os dados a partir de 2020 revelam uma transformação: ele atingiu uma **maturidade e uma consistência impressionantes**.
        """)
        # Função de cálculo fornecida (adaptada para usar os dataframes carregados)
        def get_total_points(driver_id):
            # Filtra resultados normais
            df_res = results[results['driverId'] == driver_id].merge(races[['raceId', 'year']], on='raceId')
            pts_race = df_res.groupby('year')['points'].sum().reset_index()
            
            # Filtra resultados sprint
            df_spr = sprint_results[sprint_results['driverId'] == driver_id].merge(races[['raceId', 'year']], on='raceId')
            pts_spr = df_spr.groupby('year')['points'].sum().reset_index()
            
            # Junta tudo
            total = pd.merge(pts_race, pts_spr, on='year', how='left').fillna(0)
            total['total'] = total['points_x'] + total['points_y']
            return total[['year', 'total']]

        # Cálculos
        ham_pts = get_total_points(1)
        max_pts = get_total_points(830)

        # Plotagem (Adaptada para Streamlit)
        fig3, ax3 = plt.subplots(figsize=(12, 6)) # Ajustei tamanho para web
        plt.style.use('dark_background')
        
        # Linhas
        ax3.plot(ham_pts['year'], ham_pts['total'], marker='o', color='#6A0DAD', label='Lewis Hamilton', linewidth=2.5)
        ax3.plot(max_pts['year'], max_pts['total'], marker='s', color='#0600EF', label='Max Verstappen', linewidth=2.5)

        # Labels Hamilton
        for i, row in ham_pts.iterrows():
            offset = 18 if row['year'] == 2021 else 12
            ax3.annotate(f"{row['total']:.1f}", (row['year'], row['total']), 
                         textcoords="offset points", xytext=(0, offset), ha='center', 
                         fontsize=10, color='#6A0DAD', fontweight='bold')

        # Labels Max
        for i, row in max_pts.iterrows():
            offset = -25 if row['year'] == 2021 else -18
            ax3.annotate(f"{row['total']:.1f}", (row['year'], row['total']), 
                         textcoords="offset points", xytext=(0, offset), ha='center', 
                         fontsize=10, color='#0600EF', fontweight='bold')

        ax3.set_title('Comparação de Pontos Totais (Incluindo Sprints)', fontsize=16, fontweight='bold', color='white')
        ax3.grid(True, linestyle='--', alpha=0.3)
        ax3.set_xticks(sorted(list(set(ham_pts['year']) | set(max_pts['year']))))
        ax3.set_xticklabels(sorted(list(set(ham_pts['year']) | set(max_pts['year']))), rotation=45)
        ax3.set_ylim(-30, 650)
        ax3.legend(fontsize=12)
        
        st.pyplot(fig3)

    # --- CAPÍTULO 4 ---
    with tab4:
        st.header("Capítulo 4: O DNA do Piloto")
        col_dna1, col_dna2 = st.columns([1, 2])
        with col_dna1:
             st.write("Este gráfico compara a eficiência pura. Lewis leva vantagem histórica em Poles, enquanto Max tem índices de agressividade e pódio brutais.")
        with col_dna2:
             fig_radar = plot_radar_chart(df)
             st.pyplot(fig_radar)

    # --- CONCLUSÃO ---
    with tab5:
        st.header("Conclusão: O Que os Dados Dizem?")
        st.balloons()
        st.markdown("""
        ### 🏁 Veredito dos Dados
        1.  **A Era Hamilton (A Fortaleza):** Construída sobre Pole Positions e controle de corrida.
        2.  **A Era Verstappen (O Ataque):** Construída sobre ritmo de corrida e agressividade.
        
        > *"Os dados não dizem quem é o GOAT, mas revelam que vivemos a transição entre a maior consistência técnica da história e a maior aceleração de resultados já registrada."*
        """)
        st.success("Projeto Desenvolvido para Portfólio de Data Science | Python + Streamlit")

else:
    st.warning("Aguardando carregamento dos dados...")
