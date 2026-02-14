Desafio aceito! Vamos transformar o seu projeto em um dashboard "Nível NASA" (Profissional Sênior). 🚀

Vou substituir a biblioteca gráfica antiga (matplotlib/seaborn) pela Plotly. A diferença é brutal: agora os gráficos serão interativos. O recrutador vai poder passar o mouse, dar zoom, filtrar clicando na legenda e ver detalhes de cada barra.

Também adicionei a Sidebar Profissional e o Rodapé de Contato.

⚠️ Importante: Atualize o requirements.txt
Antes de rodar o código novo, você precisa adicionar a biblioteca plotly no seu arquivo requirements.txt. Ele deve ficar assim:

Plaintext

streamlit
pandas
plotly
matplotlib
seaborn
Código Final app.py (Versão 2.0 - Interativa)
Copie e substitua TODO o conteúdo do seu arquivo app.py:

Python

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# CONFIGURAÇÃO VISUAL (DARK MODE F1)
# ==========================================
st.set_page_config(page_title="Duelo de Eras: Hamilton vs Verstappen", layout="wide", page_icon="🏎️")

# CSS Personalizado para ajustes finos
st.markdown("""
<style>
    .main { background-color: #0E1117; color: #FAFAFA; }
    h1 { color: #FF1E1E; font-family: 'Arial Black', sans-serif; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #262730; border-radius: 5px; color: white; }
    .stTabs [data-baseweb="tab"][aria-selected="true"] { background-color: #FF1E1E; }
    
    /* Estilo para links do rodapé e sidebar */
    a { text-decoration: none; color: #FF1E1E !important; font-weight: bold; }
    a:hover { text-decoration: underline; }
</style>
""", unsafe_allow_html=True)

# Paleta de Cores (Roxo Hamilton / Azul Max)
CORES = {'Lewis Hamilton': '#6A0DAD', 'Max Verstappen': '#0600EF', 
         'Hamilton': '#6A0DAD', 'Verstappen': '#0600EF'}

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
    df = df[df['driverId'].isin([1, 830])].copy()
    # Ganho de posição
    df['pos_change'] = df.apply(lambda x: x['grid'] - x['positionOrder'] if x['grid'] > 0 else 0, axis=1)

# ==========================================
# 2. BARRA LATERAL (SIDEBAR)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100) # Ícone genérico de perfil
    st.title("Analista de Dados")
    st.write("**Ed Carlos Nunes**")
    st.markdown("---")
    
    st.write("📍 **Sobre Mim:**")
    st.caption("Apaixonado por transformar dados complexos em histórias visuais. Especialista em Python, Pandas e Visualização de Dados.")
    
    st.write("🔗 **Conecte-se:**")
    st.markdown("[👔 LinkedIn](https://www.linkedin.com/in/edcarlosnunes)") # Substitua pelo seu link real
    st.markdown("[💻 GitHub](https://github.com/EdCarlosNunes)")
    
    st.markdown("---")
    st.write("🎛️ **Filtros Globais**")
    filtro_anos = st.slider("Período de Análise:", 2014, 2024, (2015, 2024))

# Aplica filtro de anos no DF global para os gráficos que usam tempo
df_filtrado = df[(df['year'] >= filtro_anos[0]) & (df['year'] <= filtro_anos[1])]

# ==========================================
# 3. INTERFACE PRINCIPAL
# ==========================================

st.title("🏎️ O Duelo de Eras")
st.markdown("**Uma Análise de Dados Interativa: Hamilton vs Verstappen**")

st.info("""
**Contexto:** A Fórmula 1 é definida por ciclos. O que acontece quando o maior vencedor de todos os tempos encontra o jovem prodígio mais veloz da história?
Este projeto compara as trajetórias para entender onde suas carreiras se cruzam.
*Passe o mouse sobre os gráficos para ver detalhes.*
""")

if results is not None:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Cap 1: Trajetórias", 
        "🚀 Cap 2: Anatomia",
        "🏆 Cap 3: Pontos",
        "📊 Cap 4: Probabilidade (Max)",
        "⚔️ Cap 5: Duelo de Grid", 
        "🏁 Conclusão"
    ])

    # --- CAPÍTULO 1: TRAJETÓRIAS (PLOTLY) ---
    with tab1:
        st.header("Capítulo 1: Trajetórias Paralelas")
        st.write("Ritmo de vitórias acumuladas por número de GPs disputados.")
        
        # Preparar dados
        df_traj = df.sort_values(['driverId', 'year', 'round'])
        df_traj['win'] = (df_traj['positionOrder'] == 1).astype(int)
        df_traj['cum_wins'] = df_traj.groupby('driverId')['win'].cumsum()
        df_traj['race_count'] = df_traj.groupby('driverId').cumcount() + 1
        
        # Gráfico Interativo
        fig1 = px.line(df_traj, x='race_count', y='cum_wins', color='nome_piloto',
                       color_discrete_map=CORES,
                       labels={'race_count': 'GPs Disputados', 'cum_wins': 'Vitórias Acumuladas', 'nome_piloto': 'Piloto'},
                       hover_data=['year', 'name'])
        
        fig1.update_layout(template="plotly_dark", hovermode="x unified")
        st.plotly_chart(fig1, use_container_width=True)

    # --- CAPÍTULO 2: ANATOMIA (PLOTLY) ---
    with tab2:
        st.header("Capítulo 2: A Anatomia da Vitória")
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.subheader("Distribuição de Ganho de Posição")
            # Histograma como alternativa ao KDE para interatividade
            fig2 = px.histogram(df_filtrado[df_filtrado['grid']>0], x="pos_change", color="nome_piloto",
                                barmode="overlay", nbins=30, opacity=0.7,
                                color_discrete_map=CORES,
                                labels={'pos_change': 'Posições Ganhas/Perdidas'})
            fig2.add_vline(x=0, line_dash="dash", line_color="white")
            fig2.update_layout(template="plotly_dark", xaxis_title="Saldo de Posições (Direita = Ganhou)")
            st.plotly_chart(fig2, use_container_width=True)
            
        with col_b:
            st.subheader("Top 'Masterclasses' (Recuperações)")
            top_rec = df.sort_values('pos_change', ascending=False).groupby('nome_piloto').head(5)
            top_rec['Rotulo'] = top_rec['name'] + ' ' + top_rec['year'].astype(str)
            
            fig2b = px.bar(top_rec, x='pos_change', y='Rotulo', color='nome_piloto',
                           orientation='h', color_discrete_map=CORES,
                           text='pos_change')
            fig2b.update_layout(template="plotly_dark", yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig2b, use_container_width=True)

    # --- CAPÍTULO 3: PONTOS (PLOTLY) ---
    with tab3:
        st.header("Capítulo 3: Pontos Totais por Temporada")
        st.markdown("Comparativo absoluto de pontos (incluindo Sprints).")

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
        
        # Criando Figura Manualmente com Go
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=ham_pts['year'], y=ham_pts['total'], mode='lines+markers+text',
                                  name='Lewis Hamilton', line=dict(color='#6A0DAD', width=3),
                                  text=ham_pts['total'], textposition="top center"))
        
        fig3.add_trace(go.Scatter(x=max_pts['year'], y=max_pts['total'], mode='lines+markers+text',
                                  name='Max Verstappen', line=dict(color='#0600EF', width=3),
                                  text=max_pts['total'], textposition="top center"))
        
        fig3.update_layout(template="plotly_dark", xaxis_title="Temporada", yaxis_title="Pontos Totais",
                           hovermode="x unified")
        st.plotly_chart(fig3, use_container_width=True)

    # --- CAPÍTULO 4: PROBABILIDADE MAX (PLOTLY) ---
    with tab4:
        st.header("Capítulo 4: Probabilidade de Pódio (Max)")
        
        max_id = 830
        max_results = results[results['driverId'] == max_id].copy()
        max_results['is_podium'] = (max_results['positionOrder'] <= 3).astype(int)
        grid_stats = max_results.groupby('grid').agg(total=('raceId', 'count'), podios=('is_podium', 'sum')).reset_index()
        grid_stats['chance'] = (grid_stats['podios'] / grid_stats['total']) * 100
        grid_stats = grid_stats[grid_stats['grid'] <= 20]
        
        fig4 = px.bar(grid_stats, x='grid', y='chance', 
                      color_discrete_sequence=['#0600EF'],
                      text=grid_stats.apply(lambda x: f"{x['chance']:.0f}% ({int(x['podios'])}/{int(x['total'])})", axis=1),
                      labels={'grid': 'Posição de Largada', 'chance': 'Chance de Pódio (%)'})
        
        fig4.update_layout(template="plotly_dark", xaxis=dict(tickmode='linear'))
        st.plotly_chart(fig4, use_container_width=True)

    # --- CAPÍTULO 5: DUELO DE GRID (PLOTLY) ---
    with tab5:
        st.header("Capítulo 5: Duelo de Resiliência")
        st.markdown("### ⚔️ Resiliência (Max) vs Controle (Lewis)")
        
        # Preparação dos dados completa
        df_chart5 = df.copy()
        df_chart5['is_podium'] = df_chart5['positionOrder'].apply(lambda x: 1 if x <= 3 else 0)
        
        # Esqueleto 1-20
        grids_all = pd.DataFrame({'grid': range(1, 21)})
        pilotos_all = pd.DataFrame({'surname': ['Hamilton', 'Verstappen']})
        template_df = pd.merge(pilotos_all.assign(key=1), grids_all.assign(key=1), on='key').drop('key', axis=1)
        
        stats_real = df_chart5.groupby(['surname', 'grid']).agg(
            total_largadas=('raceId', 'count'),
            total_podios=('is_podium', 'sum')
        ).reset_index()
        
        stats5 = pd.merge(template_df, stats_real, on=['surname', 'grid'], how='left').fillna(0)
        stats5['probabilidade'] = np.where(stats5['total_largadas'] > 0, 
                                           (stats5['total_podios'] / stats5['total_largadas']) * 100, 0)
        
        # Gráfico Plotly Grouped Bar
        fig5 = px.bar(stats5, x='grid', y='probabilidade', color='surname', barmode='group',
                      color_discrete_map=CORES,
                      hover_data=['total_podios', 'total_largadas'],
                      labels={'probabilidade': 'Chance de Pódio (%)', 'grid': 'Posição de Largada'},
                      text=stats5.apply(lambda x: f"{x['probabilidade']:.0f}%" if x['total_largadas']>0 else "", axis=1))
        
        fig5.update_layout(template="plotly_dark", xaxis=dict(tickmode='linear', range=[0, 21]),
                           legend_title_text='Piloto')
        
        st.plotly_chart(fig5, use_container_width=True)

    # --- CONCLUSÃO E CONTATO ---
    with tab6:
        st.header("Conclusão & Contato")
        st.balloons()
        
        col_c1, col_c2 = st.columns([2, 1])
        
        with col_c1:
            st.markdown("""
            ### 🏁 Veredito dos Dados
            1.  **A Era Hamilton (A Fortaleza):** Construída sobre Pole Positions e controle de corrida.
            2.  **A Era Verstappen (O Ataque):** Construída sobre ritmo de corrida e agressividade.
            
            > *"Os dados não dizem quem é o GOAT, mas revelam que vivemos a transição entre a maior consistência técnica da história e a maior aceleração de resultados já registrada."*
            """)
            
        with col_c2:
            st.markdown("### 📬 Vamos Conversar?")
            st.write("Gostou da análise? Estou disponível para projetos de Data Science.")
            
            st.link_button("👔 Me chame no LinkedIn", "https://www.linkedin.com/in/edcarlosnunes") # Ajuste o link
            st.link_button("📧 Enviar E-mail", "mailto:seuemail@exemplo.com")
            st.link_button("💻 Ver Código no GitHub", "https://github.com/EdCarlosNunes")

else:
    st.warning("Aguardando carregamento dos dados...")
