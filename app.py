import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 1. Look Corporate & Sobre (Gris et Bleu pro)
st.set_page_config(page_title="Data Automation RSA", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    div[data-testid="metric-container"] {
        background-color: white; border: 1px solid #E0E0E0;
        padding: 15px; border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Chargement Ultra-Sécurisé
@st.cache_data
def load_data():
    # Chargement du fichier
    df = pd.read_csv('data.csv')

try:
    df = load_data()
except Exception as e:
    st.error(f"⚠️ Erreur : Le fichier 'data.csv' est introuvable sur GitHub. Vérifie le nom !")
    st.stop()

# 3. Calculs avec protection (si une colonne manque, l'app ne crash pas)
ca = df['prix_clean'].sum() if 'prix_clean' in df.columns else 0
qty = df['quantité'].sum() if 'quantité' in df.columns else 0
basket = ca / len(df) if len(df) > 0 else 0
# Sécurité pour note_avis (remplace les vides par 0)
sat = pd.to_numeric(df['note_avis'], errors='coerce').mean() if 'note_avis' in df.columns else 0
clients = df['identifiant_client'].nunique() if 'identifiant_client' in df.columns else 0

# 4. Affichage du Dashboard
st.title("📊 Business Automation Dashboard")
st.caption("Reporting Automatisé - Version Stable")

# Les 6 KPIs (Sobres)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Revenue", f"{ca/1000:.1f}k€")
c2.metric("Orders", int(qty))
c3.metric("Avg Basket", f"{basket:.1f}€")
c4.metric("Customer Sat.", f"{sat:.1f}/5")
c5.metric("Unique Clients", clients)

st.divider()

# Les Jauges (Gauges) - Style Executive
st.subheader("Performance vs Targets")
g1, g2, g3 = st.columns(3)

def draw_gauge(title, val, target, color="#2E4053"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=(val/target)*100 if target > 0 else 0,
        number={'suffix': "%", 'font': {'size': 20}},
        title={'text': title, 'font': {'size': 14}},
        gauge={'axis': {'range': [None, 100]}, 'bar': {'color': color}}
    ))
    fig.update_layout(height=180, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)')
    return fig

g1.plotly_chart(draw_gauge("Sales Goal", ca, 500000), use_container_width=True)
g2.plotly_chart(draw_gauge("Volume Goal", qty, 5000), use_container_width=True)
g3.plotly_chart(draw_gauge("Satisfaction Goal", sat, 5), use_container_width=True)

# Graphiques
st.markdown("---")
l, r = st.columns([7, 3])
with l:
    if 'date_commande' in df.columns:
        trend = df.groupby('date_commande')['prix_clean'].sum().reset_index()
        st.plotly_chart(px.area(trend, x='date_commande', y='prix_clean', title="Evolution des Ventes", color_discrete_sequence=['#2E4053']), use_container_width=True)
with r:
    if 'nom_catégorie' in df.columns:
        cat = df.groupby('nom_catégorie')['prix_clean'].sum().reset_index()
        st.plotly_chart(px.bar(cat, x='prix_clean', y='nom_catégorie', orientation='h', title="Top Catégories", color_discrete_sequence=['#5D6D7E']), use_container_width=True)
