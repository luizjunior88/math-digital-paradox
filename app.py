import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- CONFIGURAÇÃO E DADOS ---
st.set_page_config(page_title="Math 5.0 | PISA Insights", page_icon="📐", layout="wide")

@st.cache_data
def generate_data():
    np.random.seed(42)
    n = 2000
    # Criação do DataFrame com alinhamento correto
    df = pd.DataFrame({
        'Uso_Digital': np.random.normal(4, 1.5, n).clip(0, 10),
        'Ansiedade': np.random.randint(1, 11, n),
        'Infra': np.random.choice(['Alta/High', 'Média/Avg', 'Baixa/Low'], n, p=[0.3, 0.5, 0.2])
    })
    
    # Tipo de Uso
    tipos = ['Passivo (Vídeo/Social)', 'Ativo (Code/Logic)', 'Misto/Mixed']
    df['Tipo_Uso'] = np.random.choice(tipos, n, p=[0.5, 0.2, 0.3])

    # Função interna para cálculo da nota
    def calc_nota(row):
        base = 480
        # Curva U invertida
        fator_horas = -2.5 * (row['Uso_Digital'] - 3)**2 + 20
        # Bônus Ativo
        bonus = 45 if 'Ativo' in row['Tipo_Uso'] else -15 if 'Passivo' in row['Tipo_Uso'] else 0
        # Penalidade Ansiedade
        penalidade = -4 * row['Ansiedade']
        return base + fator_horas + bonus + penalidade + np.random.normal(0, 35)

    df['Nota'] = df.apply(calc_nota, axis=1).clip(200, 800)
    return df

df = generate_data()

# --- DICIONÁRIO DE TRADUÇÃO ---
texts = {
    'PT': {
        'title': "📐 O Paradoxo Digital no Ensino",
        'subtitle': "Como a tecnologia impacta realmente o desempenho em Matemática?",
        'sidebar_title': "👨‍🏫 Prof. & Data Analyst",
        'sidebar_info': "Análise baseada nas tendências do relatório **PISA 2022 (OCDE)**.\n\n*Dados simulados estatisticamente.*",
        'filter_label': "Filtrar por Tipo de Uso:",
        'kpi_avg': "Média Matemática",
        'kpi_time': "Tempo Ecrã/Dia",
        'kpi_corr': "Correlação (Tempo x Nota)",
        'kpi_anx': "Alunos 'Nomofóbicos'",
        'chart1_title': "📉 A Curva de Desempenho Digital",
        'chart1_x': "Horas Online/Dia",
        'chart1_y': "Pontuação PISA",
        'chart2_title': "🧠 O Fator Ansiedade",
        'chart2_x': "Nível de Ansiedade (1-10)",
        'chart3_title': "💡 Qualidade > Quantidade",
        'insight': "**Conclusão Pedagógica:** O problema não é a tela, é a passividade. Alunos que usam tecnologia para **criar** superam os que apenas **consomem**."
    },
    'EN': {
        'title': "📐 The Digital Paradox in Education",
        'subtitle': "How does technology actually impact Math performance?",
        'sidebar_title': "👨‍🏫 Teacher & Data Analyst",
        'sidebar_info': "Analysis based on **PISA 2022 (OECD)** report trends.\n\n*Statistically simulated data.*",
        'filter_label': "Filter by Usage Type:",
        'kpi_avg': "Math Average",
        'kpi_time': "Screen Time/Day",
        'kpi_corr': "Correlation (Time vs Score)",
        'kpi_anx': "High Anxiety Students",
        'chart1_title': "📉 The Digital Performance Curve",
        'chart1_x': "Online Hours/Day",
        'chart1_y': "PISA Score",
        'chart2_title': "🧠 The Anxiety Factor",
        'chart2_x': "Anxiety Level (1-10)",
        'chart3_title': "💡 Quality > Quantity",
        'insight': "**Pedagogical Insight:** The screen isn't the enemy; passivity is. Students who use tech to **create** outperform those who only **consume**."
    }
}

# --- BARRA LATERAL ---
st.sidebar.header("Language / Idioma")
lang = st.sidebar.radio("", ["Português", "English"], horizontal=True)
L = 'PT' if lang == "Português" else 'EN'

st.sidebar.title(texts[L]['sidebar_title'])
st.sidebar.info(texts[L]['sidebar_info'])
st.sidebar.markdown("---")

filtro = st.sidebar.multiselect(texts[L]['filter_label'], df['Tipo_Uso'].unique(), default=df['Tipo_Uso'].unique())
# Filtro de segurança: se nada for selecionado, mostrar tudo
if not filtro:
    df_filtered = df
else:
    df_filtered = df[df['Tipo_Uso'].isin(filtro)]

# --- LAYOUT PRINCIPAL ---
st.title(texts[L]['title'])
st.markdown(f"### *{texts[L]['subtitle']}*")

c1, c2, c3, c4 = st.columns(4)
c1.metric(texts[L]['kpi_avg'], f"{df_filtered['Nota'].mean():.0f}")
c2.metric(texts[L]['kpi_time'], f"{df_filtered['Uso_Digital'].mean():.1f} h")
c3.metric(texts[L]['kpi_corr'], f"{df_filtered['Nota'].corr(df_filtered['Uso_Digital']):.2f}")
c4.metric(texts[L]['kpi_anx'], f"{len(df_filtered[df_filtered['Ansiedade'] >= 8])}")

st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(texts[L]['chart1_title'])
    fig1 = px.scatter(
        df_filtered, x="Uso_Digital", y="Nota", color="Tipo_Uso",
        trendline="lowess", trendline_color_override="black", opacity=0.5,
        labels={"Uso_Digital": texts[L]['chart1_x'], "Nota": texts[L]['chart1_y']}
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader(texts[L]['chart2_title'])
    df_anx = df_filtered.groupby('Ansiedade')['Nota'].mean().reset_index()
    fig2 = px.bar(
        df_anx, x='Ansiedade', y='Nota', color='Nota', color_continuous_scale='rdbu',
        range_y=[350, 550], labels={'Ansiedade': texts[L]['chart2_x']}
    )
    st.plotly_chart(fig2, use_container_width=True)

st.subheader(texts[L]['chart3_title'])
fig3 = px.box(
    df, x="Tipo_Uso", y="Nota", color="Tipo_Uso",
    color_discrete_map={'Passivo (Vídeo/Social)': '#EF553B', 'Misto/Mixed': '#FFA15A', 'Ativo (Code/Logic)': '#00CC96'}
)
st.plotly_chart(fig3, use_container_width=True)

st.success(texts[L]['insight'])
