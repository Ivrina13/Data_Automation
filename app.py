import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration pour un look moderne
st.set_page_config(page_title="Data Automation", layout="wide", initial_sidebar_state="expanded")

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data
def load_data():
    # Remplace par ton nom de fichier
    df = pd.read_csv('ton_fichier.csv') 
    df['date_commande'] = pd.to_datetime(df['date_commande'])
    return df

try:
    df = load_data()
except:
    st.error("⚠️ Fichier CSV introuvable !")
    st.stop()

# --- STYLE CSS PERSONNALISÉ (Pour sortir du look standard) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border-left: 5px solid #7000FF; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRE LATÉRALE ---
st.sidebar.title("🤖 Data Automation")
st.sidebar.caption("Pipeline & Monitoring")
page = st.sidebar.radio("Menu Principal", ["Performance Business", "Audit & Intelligence"])

st.sidebar.divider()
selected_cat = st.sidebar.multiselect("Filtrer par Catégorie", options=df['nom_catégorie'].unique(), default=df['nom_catégorie'].unique())

# Filtrage
df_selection = df[df['nom_catégorie'].isin(selected_cat)]

# --- COULEURS PERSONNALISÉES ---
# On part sur du Violet (#7000FF), du Rose/Fuchsia et du Safran (#FFD700)
tech_colors = ['#7000FF', '#FF00E4', '#FFD700', '#00D4FF', '#FF4B4B']

# --- PAGE 1 : PERFORMANCE ---
if page == "📈 Performance Business":
    st.title("⚡ Data Automation Dashboard")
    st.write("Analyse des flux de revenus et volumes transactionnels.")
    
    # KPIs
    ca_total = df_selection['prix'].sum()
    ventes = df_selection['quantité'].sum()
    panier_moyen = ca_total / len(df_selection) if len(df_selection) > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Revenue Total", f"{ca_total:,.2f} €")
    col2.metric("Transactions", f"{ventes}")
    col3.metric("Average Basket", f"{panier_moyen:.2f} €")

    st.markdown("---")

    c1, c2 = st.columns([4, 6])

    # Donut avec couleurs Tech
    fig_cat = px.pie(df_selection, values='prix', names='nom_catégorie', hole=0.7, 
                     title="Segmentation du Chiffre d'Affaires",
                     color_discrete_sequence=tech_colors)
    fig_cat.update_layout(showlegend=False) # Plus propre sans légende
    c1.plotly_chart(fig_cat, use_container_width=True)

    # Courbe d'évolution - Ligne épaisse et colorée
    sales_line = df_selection.groupby('date_commande')['prix'].sum().reset_index()
    fig_line = px.line(sales_line, x='date_commande', y='prix', title="Trend des Ventes (Temps Réel)")
    fig_line.update_traces(line=dict(color='#7000FF', width=4))
    c2.plotly_chart(fig_line, use_container_width=True)

# --- PAGE 2 : AUDIT ---
else:
    st.title("Audit & Customer Intelligence")
    
    col_a, col_b = st.columns(2)

    # Top produits - Barres horizontales Safran
    top_prod = df_selection.groupby('nom_produit')['quantité'].sum().sort_values(ascending=True).tail(10).reset_index()
    fig_prod = px.bar(top_prod, x='quantité', y='nom_produit', orientation='h', 
                      title="Analyse de la Demande Produits",
                      color_discrete_sequence=['#FFD700'])
    col_a.plotly_chart(fig_prod, use_container_width=True)

    # Répartition par âge - Style Histogramme Tech
    fig_age = px.histogram(df_selection, x="age", nbins=12, title="Analyse Démographique", 
                           color_discrete_sequence=['#FF00E4'])
    col_b.plotly_chart(fig_age, use_container_width=True)

    st.markdown("---")
    st.subheader("📑 Data Registry (Raw Data)")
    st.dataframe(df_selection, use_container_width=True)

# Footer signature
st.sidebar.markdown("---")
st.sidebar.write("✅ **Status: Automated**")
