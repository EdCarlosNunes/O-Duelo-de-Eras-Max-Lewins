import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# CONFIGURAÇÃO VISUAL (GLASSMORPHISM LIGHT)
# ==========================================
st.set_page_config(page_title="Duelo de Eras: Hamilton vs Verstappen", layout="wide", page_icon="🏎️")

# CSS Personalizado Avançado (Glassmorphism + Navbar)
st.markdown("""
<style>
    /* Importando Fontes Modernas */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

    /* Fundo Geral */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgb(242, 246, 255) 0%, rgb(235, 248, 255) 50%, rgb(224, 230, 240) 100%);
        font-family: 'Inter', sans-serif;
        color: #000000;
    }

    /* Navbar Customizada */
    .navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.9);
        border-radius: 16px;
        padding: 12px 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
    }
    
    .navbar-title {
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E293B 0%, #334155 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .navbar-subtitle {
        font-size: 0.9rem;
        color: #64748B;
        font-weight: 500;
        margin: 0;
    }

    /* Container Glassmorphism AUTOMÁTICO para as Abas */
    div[data-baseweb="tab-panel"] {
        background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.8);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05);
        border-radius: 20px;
        padding: 24px;
        margin-top: 16px; 
    }
    
    /* Espaçamento interno dos elementos dentro da aba */
    div[data-baseweb="tab-panel"] > div {
        gap: 1.5rem;
    }

    /* Títulos */
    h1, h2, h3, h4 {
        color: #000000 !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }
    
    /* Texto Corrido */
    p, li {
        color: #1E293B;
        line-height: 1.6;
        font-size: 1rem;
        font-weight: 500;
    }

    /* Abas Modernas (Estilo iOS Segmented Control) */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(255, 255, 255, 0.5);
        padding: 6px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.6);
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 12px;
        color: #64748B;
        font-weight: 600;
        font-size: 14px;
        border: none;
        padding: 8px 16px;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255, 255, 255, 0.5);
        color: #334155;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #FFFFFF;
        color: #0F172A;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    /* Remove a barra vermelha padrão do Streamlit nas abas */
    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }

    /* Sidebar Glassmorphism */
    section[data-testid="stSidebar"] > div {
        background-color: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255,255,255,0.6);
    }
    
    /* Links */
    a { text-decoration: none; color: #2563EB !important; font-weight: 600; transition: color 0.2s; }
    a:hover { color: #1D4ED8 !important; }
    
    /* Classe Glass Container Manual (apenas para footer se precisar) */
    .glass-manual {
         background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.8);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05);
        border-radius: 20px;
        padding: 24px;
    }

</style>
""", unsafe_allow_html=True)

# Paleta de Cores Atualizada
CORES = {'Lewis Hamilton': '#7C3AED', 'Max Verstappen': '#2563EB', 
         'Hamilton': '#7C3AED', 'Verstappen': '#2563EB'}

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
    df['pos_change'] = df.apply(lambda x: x['grid'] - x['positionOrder'] if x['grid'] > 0 else 0, axis=1)

# ==========================================
# 2. BARRA LATERAL (SIDEBAR)
# ==========================================
with st.sidebar:
    st.image("https://avatars.githubusercontent.com/u/93043407?v=4", width=80) 
    st.markdown('<div style="margin-top: -10px; margin-bottom: 20px;"><h2>Ed Carlos Nunes</h2><p style="color: #64748B;">Analista de Dados</p></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.caption("📍 **Sobre Mim**")
    st.info("Especialista em transformar dados complexos em experiências visuais. Foco em Python, Dashboards e Storytelling.")
    st.markdown("---")
    st.write("🎛️ **Filtros Globais**")
    filtro_anos = st.slider("Período de Análise:", 2014, 2024, (2015, 2024))
    st.markdown("---")
    st.markdown("🔗 [**LinkedIn**](https://www.linkedin.com/in/ed-carlos-nunes-almeida-418767125/)")
    st.markdown("🔗 [**GitHub**](https://github.com/EdCarlosNunes)")

# Aplica filtro de anos
df_filtrado = df[(df['year'] >= filtro_anos[0]) & (df['year'] <= filtro_anos[1])]

# ==========================================
# 3. INTERFACE PRINCIPAL
# ==========================================

# Navbar Compacta
st.markdown("""
<div class="navbar">
    <div style="display: flex; gap: 12px; align-items: center;">
        <span style="font-size: 1.8rem;">🏎️</span>
        <div>
            <h1 class="navbar-title">O Duelo de Eras</h1>
            <p class="navbar-subtitle">Lewis Hamilton vs Max Verstappen</p>
        </div>
    </div>
    <div style="display: flex; gap: 10px;">
        <span style="background: rgba(37, 99, 235, 0.1); color: #2563EB; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">v2.0 Glass</span>
    </div>
</div>
""", unsafe_allow_html=True)

if results is not None:
    # Abas com Ícones
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Trajetórias", 
        "🚀 Anatomia",
        "🏆 Pontos",
        "📊 Probabilidade",
        "⚔️ Duelo Grid", 
        "🏁 Veredito"
    ])

    # --- FUNÇÃO HELPER PARA LAYOUT DE GRÁFICO ---
    def update_chart_layout(fig):
        fig.update_layout(
            template="plotly_white", 
            hovermode="x unified",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter", color="#000000", size=14), # PRETO PURO
            title_font_color="#000000",
            legend_title_font_color="#000000",
            legend_font_color="#000000",
            legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0.5, xanchor="center")
        )
        fig.update_xaxes(
            showgrid=False, 
            color="#000000", 
            title_font_color="#000000", 
            tickfont_color="#000000"
        )
        fig.update_yaxes(
            showgrid=True, 
            gridcolor='rgba(0,0,0,0.1)', # Grade sutil escura
            color="#000000", 
            title_font_color="#000000", 
            tickfont_color="#000000"
        )
        return fig

    # --- CAPÍTULO 1: TRAJETÓRIAS ---
    with tab1:
        st.subheader("Capítulo 1: Trajetórias Paralelas")
        st.markdown("""
        Analisando os dados de número de corridas e vitórias na Fórmula 1, vemos que o Hamilton teve um grande começo. 
        Porém, ele começou com 22 anos em 2007, o que dá um ganho em cima de Max, que começou na Fórmula 1 com 17 anos em 2015. 
        Conseguimos ver que a maturidade contou para esse início grandioso de Hamilton, porém vemos que o ritmo de vitórias de Max ao atingir 200 corridas é assustadoramente similar ao auge de Hamilton.
        """)
        
        # Preparar dados
        df_traj = df.sort_values(['driverId', 'year', 'round'])
        df_traj['win'] = (df_traj['positionOrder'] == 1).astype(int)
        df_traj['cum_wins'] = df_traj.groupby('driverId')['win'].cumsum()
        df_traj['race_count'] = df_traj.groupby('driverId').cumcount() + 1
        
        fig1 = px.line(df_traj, x='race_count', y='cum_wins', color='nome_piloto',
                       color_discrete_map=CORES,
                       labels={'race_count': 'GPs Disputados', 'cum_wins': 'Vitórias Acumuladas'})
        
        fig1 = update_chart_layout(fig1)
        st.plotly_chart(fig1, use_container_width=True)

    # --- CAPÍTULO 2: ANATOMIA ---
    with tab2:
        st.subheader("Capítulo 2: A Anatomia da Vitória")
        st.markdown("""
        ### 📊 Análise Técnica: O "Sniper" vs. O "Rolo Compressor"
        
        Ao analisarmos a distribuição de *Ganho de Posições* (Grid - Chegada), os dados revelam dois comportamentos estatísticos distintos:
        
        1.  **Lewis Hamilton (O Pico da Precisão):**
            * Observe como a curva de Hamilton é **leptocúrtica** (pico alto e estreito) em torno do **Zero**.
            * **O que isso significa?** Hamilton vence "no sábado". Sua estratégia histórica baseia-se em conquistar a Pole Position e converter essa vantagem em vitória sem precisar escalar o pelotão. É um estilo de **controle e gestão de liderança**.
            
        2.  **Max Verstappen (A Cauda da Agressividade):**
            * A distribuição de Max apresenta uma **assimetria positiva** (cauda longa para a direita).
            * **O que isso significa?** Os dados mostram uma frequência anormal de corridas onde ele ganha +5, +10 ou +14 posições. Isso indica que Max não depende da posição de largada para vencer; ele possui o maior índice de **eficiência de ultrapassagem** da era moderna.
        """)
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            fig2 = px.histogram(df_filtrado[df_filtrado['grid']>0], x="pos_change", color="nome_piloto",
                                barmode="overlay", nbins=30, opacity=0.7,
                                color_discrete_map=CORES,
                                labels={'pos_change': 'Posições Ganhas/Perdidas'})
            fig2.add_vline(x=0, line_dash="dash", line_color="#000000")
            fig2 = update_chart_layout(fig2)
            st.plotly_chart(fig2, use_container_width=True)
            
        with col_b:
            top_rec = df.sort_values('pos_change', ascending=False).groupby('nome_piloto').head(5)
            top_rec['Rotulo'] = top_rec['name'] + ' ' + top_rec['year'].astype(str)
            
            fig2b = px.bar(top_rec, x='pos_change', y='Rotulo', color='nome_piloto',
                           orientation='h', color_discrete_map=CORES,
                           text='pos_change')
            
            fig2b = update_chart_layout(fig2b)
            fig2b.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
            fig2b.update_traces(textfont_color='#000000', textfont_weight='bold') # Texto nas barras
            st.plotly_chart(fig2b, use_container_width=True)

    # --- CAPÍTULO 3: PONTOS ---
    with tab3:
        st.subheader("Capítulo 3: Pontos Totais por Temporada")
        st.markdown("""
        Neste gráfico, comparamos o início da jornada de ambos. A análise sugere que **Max Verstappen vive seu auge técnico**, quebrando recordes consecutivamente, enquanto Hamilton caminha para o encerramento de uma carreira lendária. 
        É provável que Max supere os números de Lewis, embora com um estilo diferente. Se no passado Max mostrava instabilidade, os dados a partir de 2020 revelam uma transformação: ele atingiu uma **maturidade e uma consistência impressionantes**.
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
        
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=ham_pts['year'], y=ham_pts['total'], mode='lines+markers+text',
                                  name='Lewis Hamilton', line=dict(color='#7C3AED', width=3),
                                  text=ham_pts['total'], textposition="top center",
                                  textfont=dict(color='#000000', weight='bold')))
        
        fig3.add_trace(go.Scatter(x=max_pts['year'], y=max_pts['total'], mode='lines+markers+text',
                                  name='Max Verstappen', line=dict(color='#2563EB', width=3),
                                  text=max_pts['total'], textposition="top center",
                                  textfont=dict(color='#000000', weight='bold')))
        
        fig3 = update_chart_layout(fig3)
        st.plotly_chart(fig3, use_container_width=True)

    # --- CAPÍTULO 4: PROBABILIDADE ---
    with tab4:
        st.subheader("Capítulo 4: Probabilidade de Pódio (Max)")
        st.markdown("""
        Esta análise mede a **Taxa de Conversão** entre Posição de Largada e Pódios. Aqui identificamos o diferencial competitivo mais letal de Verstappen: a **independência do Grid**.
        Ao contrário da média histórica, os dados mostram que Max consegue atingir o pódio partindo de praticamente qualquer posição. Essa capacidade de anular desvantagens de largada é o fator chave que o projeta matematicamente para superar os recordes absolutos de Hamilton.
        """)
        
        max_id = 830
        max_results = results[results['driverId'] == max_id].copy()
        max_results['is_podium'] = (max_results['positionOrder'] <= 3).astype(int)
        grid_stats = max_results.groupby('grid').agg(total=('raceId', 'count'), podios=('is_podium', 'sum')).reset_index()
        grid_stats['chance'] = (grid_stats['podios'] / grid_stats['total']) * 100
        grid_stats = grid_stats[grid_stats['grid'] <= 20]
        
        fig4 = px.bar(grid_stats, x='grid', y='chance', 
                      color_discrete_sequence=['#2563EB'],
                      text=grid_stats.apply(lambda x: f"{x['chance']:.0f}%", axis=1),
                      labels={'grid': 'Posição de Largada', 'chance': 'Chance de Pódio (%)'})
        
        fig4 = update_chart_layout(fig4)
        fig4.update_traces(textfont_color='#000000', textfont_weight='bold')
        st.plotly_chart(fig4, use_container_width=True)

    # --- CAPÍTULO 5: DUELO DE GRID ---
    with tab5:
        st.subheader("Capítulo 5: Duelo de Resiliência")
        st.markdown("""
        ### ⚔️ O Veredito: Resiliência vs. Controle
        
        Este gráfico confirma sua hipótese: **Max Verstappen é estatisticamente mais resiliente a posições ruins de largada.**
        
        * **Max Verstappen (O Caçador):** As barras azuis mostram que ele sustenta uma chance de pódio altíssima (acima de 50-60%) mesmo largando do meio do pelotão (P6-P14). Para Max, o grid é apenas um obstáculo temporário.
        * **Lewis Hamilton (O Controlador):** As barras roxas mostram um domínio absoluto nas primeiras posições (P1-P3), mas uma queda acentuada ao largar de trás. O estilo de Hamilton é baseado na **perfeição da classificação**: ele vence evitando o tráfego, enquanto Max vence atacando o tráfego.
        """)
        
        df_chart5 = df.copy()
        df_chart5['is_podium'] = df_chart5['positionOrder'].apply(lambda x: 1 if x <= 3 else 0)
        
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
        
        fig5 = px.bar(stats5, x='grid', y='probabilidade', color='surname', barmode='group',
                      color_discrete_map=CORES,
                      text=stats5.apply(lambda x: f"{x['probabilidade']:.0f}%" if x['total_largadas']>0 else "", axis=1))
        
        fig5 = update_chart_layout(fig5)
        fig5.update_layout(xaxis=dict(tickmode='linear', range=[0, 16]))
        fig5.update_traces(textfont_color='#000000', textfont_weight='bold')
        
        st.plotly_chart(fig5, use_container_width=True)

    # --- CONCLUSÃO ---
    with tab6:
        # Aqui, como não é apenas um container simples, vou usar o 'glass-manual' para o container de veredito
        # se quiser manter o fundo. Mas com o CSS global de aba, não precisa.
        # Vou deixar o HTML puro para os cards internos.
        
        st.markdown('<h2 style="text-align: center; margin-bottom: 30px;">Veredito dos Dados</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 300px; background: rgba(124, 58, 237, 0.1); padding: 20px; border-radius: 15px; border-left: 5px solid #7C3AED;">
                <h4 style="color: #7C3AED;">A Era Hamilton (A Fortaleza)</h4>
                <p>Construída sobre Pole Positions e controle de corrida. Hamilton vence evitando o caos, dominando a classificação e gerenciando a liderança.</p>
            </div>
            <div style="flex: 1; min-width: 300px; background: rgba(37, 99, 235, 0.1); padding: 20px; border-radius: 15px; border-left: 5px solid #2563EB;">
                <h4 style="color: #2563EB;">A Era Verstappen (O Ataque)</h4>
                <p>Construída sobre ritmo de corrida e agressividade. Max vence atacando o tráfego, independente de onde larga.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="margin-top: 30px; text-align: center; font-style: italic; color: #1E293B;">
            "Os dados não dizem quem é o GOAT, mas revelam que vivemos a transição entre a maior consistência técnica da história e a maior aceleração de resultados já registrada."
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎉 Celebrar a Análise", use_container_width=True):
            st.balloons()

else:
    st.warning("Aguardando carregamento dos dados...")
