import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

results = pd.read_csv('results.csv')
drivers = pd.read_csv('drivers.csv')
races = pd.read_csv('races.csv')

# Configuração da Página
st.set_page_config(page_title="F1 Analytics: Hamilton vs Verstappen", layout="wide")

st.title("🏎️ F1 Data Insight: Hamilton vs Verstappen")
st.markdown("Uma análise profissional sobre a transição de dominância na Fórmula 1.")

# Função para carregar dados - Buscando direto na raiz do seu GitHub
@st.cache_data
def load_data():
    try:
        results = pd.read_csv('results.csv').drop_duplicates()
        drivers = pd.read_csv('drivers.csv').drop_duplicates()
        races = pd.read_csv('races.csv').drop_duplicates()
        return results, drivers, races
    except Exception as e:
        st.error(f"Erro ao ler CSVs: {e}")
        return None, None, None

results, drivers, races = load_data()

if results is not None:
    # Preparação dos Dados
    df = results.merge(drivers[['driverId', 'forename', 'surname']], on='driverId', how='left')
    df['nome_piloto'] = df['forename'] + ' ' + df['surname']
    
    # Barra Lateral
    st.sidebar.header("Filtros")
    st.sidebar.success("Dados carregados com sucesso!")

    # Abas
    tab1, tab2 = st.tabs(["🏆 Vitórias", "📊 Perfil de Ultrapassagem"])

    with tab1:
        st.subheader("Top 5 Vencedores da História")
        vitorias = df[df['positionOrder'] == 1]
        top_5 = vitorias['nome_piloto'].value_counts().head(5).reset_index()
        top_5.columns = ['Piloto', 'Vitorias']
        
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        sns.barplot(x='Vitorias', y='Piloto', data=top_5, palette='viridis', ax=ax1)
        st.pyplot(fig1)

    with tab2:
        st.subheader("Densidade de Ganho de Posições")
        ham_max = df[df['driverId'].isin([1, 830])].copy()
        ham_max['pos_change'] = ham_max['grid'] - ham_max['positionOrder']
        
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        sns.kdeplot(data=ham_max, x='pos_change', hue='nome_piloto', fill=True, 
                    palette={'Lewis Hamilton': '#00D2BE', 'Max Verstappen': '#0600EF'}, ax=ax2)
        plt.axvline(0, color='white', linestyle='--')
        st.pyplot(fig2)

        st.info("Valores positivos indicam ganho de posições durante a corrida.")
