import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests

# 1. Configuration et Style Business (Sobre)
st.set_page_config(page_title="Data Automation", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    div[data-testid="metric-container"] {
        background-color: white; border: 1px solid #E0E0E0;
        padding: 15px; border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Fonction Slack Sécurisée (Secrets Streamlit)
def send_slack(text):
    try:
        url = st.secrets["SLACK_WEBHOOK_URL"]
        requests.post(url, json={"text": text})
        return True
    except: return False

# 3. Chargement et Nettoyage de data.csv
@st.cache_data
def load_data():
    # Chargement du fichier maintenant renommé
    df = pd.read_csv('data.csv')
    
    # Nettoyage de la colonne prix (ex: "373,36 €" -> 373.36)
    df['prix_clean'] = df['prix'].str.replace(' €', '').str.replace(',', '.').astype(float)
    df['date_commande'] = pd.to_datetime(df['date_commande'], dayfirst=True)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Erreur : Le fichier 'data.csv' est introuvable ou mal formé. Erreur : {e}")
    st.stop()

# 4. Sidebar Automation
st.sidebar.title("🤖 Data Automation")
if st.sidebar.button("🚀 Envoyer Rapport Slack"):
    if send_slack("Dashboard RSA : Le rapport de performance a été consulté."):
        st.sidebar.success("Notification envoyée !")
    else:
        st.sidebar.warning("Lien Slack non configuré dans les Secrets.")

# 5. Calcul des 6 KPIs Stratégiques
ca = df['prix_clean'].sum()
nb_ventes = df['quantité'].sum()
panier_moyen = ca / len(df) if len(df) > 0 else 0
satisfaction = df['note_avis'].mean()
clients_uniques = df['identifiant_client'].nunique()
frequence = len(df) / clients_uniques if clients_uniques > 0 else 0

# --- AFFICHAGE DU DASHBOARD ---
st.title("Business Monitoring Dashboard")
st.caption("Système d'automatisation | Performance en temps réel")

# Ligne 1 : Les 6 KPIs
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Revenue Total", f"{ca/1000:.1f}k €")
c2.metric("Unités Vendues", nb_ventes)
c3.metric("Panier Moyen", f"{panier_moyen:.2f} €")
c4.metric("Satisfaction", f"{satisfaction:.1f}/5")
c5.metric("Clients Uniques", clients_uniques)
c6.metric("Fidélité", f"{frequence:.2f}")

st.divider()

# Ligne 2 : Jauges de Performance
st.subheader("Objectifs de Performance")
g1, g2, g3, g4 = st.columns(4)

def draw_gauge(title, value, target):
    return go.Figure(go.Indicator(
        mode="gauge+number", value=(value/target)*100,
        number={'suffix': "%", 'font': {'size': 20}},
        title={'text': title, 'font': {'size': 14}},
        gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#20B2AA"}, 'bgcolor': "white"}
    )).update_layout(height=180, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)')

# Objectifs arbitraires
g1.plotly_chart(draw_gauge("Objectif CA", ca, 500000), use_container_width=True)
g2.plotly_chart(draw_gauge("Objectif Volume", nb_ventes, 5000), use_container_width=True)
g3.plotly_chart(draw_gauge("Objectif Sat.", satisfaction, 5), use_container_width=True)
g4.plotly_chart(draw_gauge("Objectif Fidélité", frequence, 2.5), use_container_width=True)

# Ligne 3 : Graphiques Business
st.markdown("---")
col_l, col_r = st.columns([7, 3])

with col_l:
    trend = df.groupby('date_commande')['prix_clean'].sum().reset_index()
    fig_trend = px.area(trend, x='date_commande', y='prix_clean', title="Évolution des Ventes", color_discrete_sequence=['#20B2AA'])
    fig_trend.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_trend, use_container_width=True)

with col_r:
    cat_data = df.groupby('nom_catégorie')['prix_clean'].sum().reset_index()
    fig_bar = px.bar(cat_data, x='prix_clean', y='nom_catégorie', orientation='h', title="Ventes par Catégorie", color_discrete_sequence=['#7FB3D5'])
    st.plotly_chart(fig_bar, use_container_width=True)
