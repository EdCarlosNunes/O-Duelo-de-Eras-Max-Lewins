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
    # Filtra apenas Hamilton e Verstappen
    df = df[df['driverId'].isin([1, 830])].copy()
    # Ganho de posição
    df['pos_change'] = df.apply(lambda x: x['grid'] - x['positionOrder'] if x['grid'] > 0 else 0, axis=1)

# ==========================================
# 2. INTERFACE E STORYTELLING
# ==========================================

st.title("🏎️ O Duelo de Eras")
st.markdown("**Uma Análise de Dados sobre Lewis Hamilton e Max Verstappen**")

st.info("""
**Contexto:** A Fórmula 1 é definida por ciclos. O que acontece quando o maior vencedor de todos os tempos encontra o jovem prodígio mais veloz da história?
Este projeto compara as trajetórias para entender onde suas carreiras se cruzam e como a dominância mudou de mãos.
""")

if results is not None:
    # DEFINIÇÃO DAS 6 ABAS
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

    # --- CAPÍTULO 3 ---
    with tab3:
        st.header("Capítulo 3: Comparação de Pontos por Temporada")
        st.markdown("""
        Esta análise sugere que **Max Verstappen vive seu auge técnico**. A partir de 2020, os dados revelam uma transformação: ele atingiu uma maturidade e consistência impressionantes.
        """)

        def get_total_points(driver_id):
            df_res = results[results['driverId'] == driver_id].merge(races[['raceId', 'year']], on='raceId')
            pts_race = df_res.groupby('year')['points'].sum().reset_index()
            df_spr = sprint_results[sprint_results['driverId'] == driver_id].merge(races[['raceId', 'year']], on='raceId')
            pts_spr = df_spr.groupby('year')['points'].sum().reset_index()
            total = pd.merge(pts_race, pts_spr, on='year', how='left').fillna(0)
            total['total'] = total['points_x'] + total['points_y']
            return total[['year', 'total']]

        ham_pts = get_total_points(1)
        max_pts = get_total_points(830)

        fig3, ax3 = plt.subplots(figsize=(12, 6))
        plt.style.use('dark_background')
        ax3.plot(ham_pts['year'], ham_pts['total'], marker='o', color='#6A0DAD', label='Lewis Hamilton', linewidth=2.5)
        ax3.plot(max_pts['year'], max_pts['total'], marker='s', color='#0600EF', label='Max Verstappen', linewidth=2.5)

        for i, row in ham_pts.iterrows():
            offset = 18 if row['year'] == 2021 else 12
            ax3.annotate(f"{row['total']:.1f}", (row['year'], row['total']), textcoords="offset points", xytext=(0, offset), ha='center', fontsize=10, color='#6A0DAD', fontweight='bold')

        for i, row in max_pts.iterrows():
            offset = -25 if row['year'] == 2021 else -18
            ax3.annotate(f"{row['total']:.1f}", (row['year'], row['total']), textcoords="offset points", xytext=(0, offset), ha='center', fontsize=10, color='#0600EF', fontweight='bold')

        ax3.set_title('Comparação de Pontos Totais', fontsize=16, fontweight='bold', color='white')
        ax3.grid(True, linestyle='--', alpha=0.3)
        ax3.set_xticks(sorted(list(set(ham_pts['year']) | set(max_pts['year']))))
        ax3.set_xticklabels(sorted(list(set(ham_pts['year']) | set(max_pts['year']))), rotation=45)
        ax3.set_ylim(-30, 650)
        ax3.legend(fontsize=12)
        st.pyplot(fig3)

    # --- CAPÍTULO 4 ---
    with tab4:
        st.header("Capítulo 4: Probabilidade de Pódio (Foco Max)")
        st.markdown("""
        Esta análise mede a **Taxa de Conversão** entre Posição de Largada e Pódios. Aqui identificamos o diferencial competitivo de Verstappen: a **independência do Grid**.
        """)
        
        max_id = 830
        max_results = results[results['driverId'] == max_id].copy()
        max_results['is_podium'] = (max_results['positionOrder'] <= 3).astype(int)

        grid_stats = max_results.groupby('grid').agg(
            total_largadas=('raceId', 'count'),
            total_podios=('is_podium', 'sum')
        ).reset_index()

        grid_stats['chance_podio'] = (grid_stats['total_podios'] / grid_stats['total_largadas']) * 100
        grid_stats = grid_stats.sort_values('grid')
        grid_stats = grid_stats[grid_stats['grid'] <= 20]

        fig4, ax4 = plt.subplots(figsize=(12, 6))
        plt.style.use('dark_background')
        
        bars = ax4.bar(grid_stats['grid'].astype(str), grid_stats['chance_podio'], color='#0600EF', alpha=0.8)

        for i, bar in enumerate(bars):
            yval = bar.get_height()
            total = grid_stats.iloc[i]['total_largadas']
            podios = grid_stats.iloc[i]['total_podios']
            ax4.text(bar.get_x() + bar.get_width()/2, yval + 1, 
                     f"{yval:.0f}%\n({int(podios)}/{int(total)})", 
                     ha='center', va='bottom', fontsize=8, color='white', fontweight='bold')

        ax4.set_title('Probabilidade de Pódio de Max Verstappen', fontsize=14, fontweight='bold', color='white')
        ax4.set_xlabel('Grid', fontsize=12, color='white')
        ax4.set_ylabel('Chance (%)', fontsize=12, color='white')
        ax4.set_ylim(0, 115)
        ax4.grid(axis='y', linestyle='--', alpha=0.3)
        st.pyplot(fig4)

    # --- CAPÍTULO 5 (NOVO E CORRIGIDO) ---
    with tab5:
        st.header("Capítulo 5: Duelo de Probabilidades (Grid vs Pódio)")
        st.markdown("""
        ### ⚔️ O Veredito: Resiliência vs. Controle
        
        Este gráfico confirma sua hipótese: **Max Verstappen é estatisticamente mais resiliente a posições ruins de largada.**
        
        * **Max Verstappen (O Caçador):** As barras azuis mostram que ele sustenta uma chance de pódio altíssima (acima de 50-60%) mesmo largando do meio do pelotão (P6-P14). Para Max, o grid é apenas um obstáculo temporário.
        * **Lewis Hamilton (O Controlador):** As barras roxas mostram um domínio absoluto nas primeiras posições (P1-P3), mas uma queda acentuada ao largar de trás. O estilo de Hamilton é baseado na **perfeição da classificação**: ele vence evitando o tráfego, enquanto Max vence atacando o tráfego.
        """)

        # 1. Preparar Dados Básicos
        df_chart5 = df.copy()
        df_chart5['is_podium'] = df_chart5['positionOrder'].apply(lambda x: 1 if x <= 3 else 0)
        
        # 2. Criar um "Esqueleto" com todas as combinações de Piloto e Grid (1 a 20)
        # Isso força o gráfico a mostrar posições onde um piloto não tem dados
        grids_all = pd.DataFrame({'grid': range(1, 21)})
        pilotos_all = pd.DataFrame({'surname': ['Hamilton', 'Verstappen']})
        # Produto cartesiano para ter todas as combinações
        template_df = pd.merge(pilotos_all.assign(key=1), grids_all.assign(key=1), on='key').drop('key', axis=1)

        # 3. Calcular Estatísticas Reais
        stats_real = df_chart5.groupby(['surname', 'grid']).agg(
            total_largadas=('raceId', 'count'),
            total_podios=('is_podium', 'sum')
        ).reset_index()

        # 4. Juntar Estatísticas no Esqueleto (Preencher vazios com 0)
        stats5 = pd.merge(template_df, stats_real, on=['surname', 'grid'], how='left').fillna(0)

        # 5. Calcular Porcentagem (cuidado com divisão por zero)
        stats5['probabilidade'] = np.where(stats5['total_largadas'] > 0, 
                                           (stats5['total_podios'] / stats5['total_largadas']) * 100, 
                                           0)

        # 6. Plotar Gráfico Robusto (1 a 20)
        fig5, ax5 = plt.subplots(figsize=(16, 8)) # Mais largo para caber 20 barras duplas
        plt.style.use('dark_background')
        sns.set_style("darkgrid")

        custom_palette = {'Hamilton': '#6A0DAD', 'Verstappen': '#0600EF'}
        
        sns.barplot(data=stats5, x='grid', y='probabilidade', hue='surname',
                    palette=custom_palette, ax=ax5)

        ax5.set_title('Probabilidade de Pódio por Posição de Largada (1-20)', fontsize=16, fontweight='bold', color='white')
        ax5.set_xlabel('Posição de Largada (Grid)', fontsize=12, color='white')
        ax5.set_ylabel('Chance de Pódio (%)', fontsize=12, color='white')
        ax5.set_ylim(0, 115)
        ax5.legend(title='Piloto', facecolor='#262730', edgecolor='white', labelcolor='white')
        
        # 7. Adicionar Labels Inteligentes (ignora zeros para não poluir)
        for container in ax5.containers:
            # Pega o nome do piloto deste container (para filtrar os dados correspondentes)
            # O seaborn não dá o nome direto no container, mas a ordem segue o 'hue'.
            # Como temos Hamilton e Verstappen, assumimos a ordem alfabética ou a ordem do dataframe
            # Método mais seguro: iterar pelas barras e buscar o valor no dataframe 'stats5'
            
            # Vamos iterar barra por barra deste container
            for i, bar in enumerate(container):
                height = bar.get_height()
                if height > 0: # Só escreve se tiver probabilidade > 0
                    # Precisamos achar os dados brutos (Nº Podios / Nº Largadas)
                    # Como o gráfico está ordenado por grid (0..19)
                    grid_pos = i + 1
                    # Descobre qual piloto é esse container (pela cor ou ordem)
                    # Container 0 = 1º do Hue (Hamilton), Container 1 = 2º do Hue (Verstappen)
                    # A ordem do hue é alfabética por padrão se não especificar 'hue_order', 
                    # mas definimos a palette. O seaborn segue a ordem dos dados ou alfabética. 
                    # 'Hamilton' vem antes de 'Verstappen'.
                    
                    piloto_atual = 'Hamilton' if container == ax5.containers[0] else 'Verstappen'
                    
                    # Busca os dados exatos na tabela stats5
                    row = stats5[(stats5['grid'] == grid_pos) & (stats5['surname'] == piloto_atual)].iloc[0]
                    podios = int(row['total_podios'])
                    largadas = int(row['total_largadas'])
                    
                    ax5.text(bar.get_x() + bar.get_width()/2, height + 2, 
                             f"{height:.0f}%\n({podios}/{largadas})", 
                             ha='center', va='bottom', fontsize=8, color='white', fontweight='bold')

        st.pyplot(fig5)
        st.info("Barras vazias indicam que o piloto nunca largou daquela posição ou nunca obteve pódio partindo dela.")

    # --- CONCLUSÃO ---
    with tab6:
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

