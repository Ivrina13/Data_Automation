import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests

# 1. Look Pro & Sobres
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

# 2. Sécurité Slack
def send_slack(text):
    try:
        url = st.secrets["SLACK_WEBHOOK_URL"]
        requests.post(url, json={"text": text})
        return True
    except: return False

# 3. Chargement avec sécurité sur les noms de colonnes
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv')
    # On nettoie le prix (enlève le € et gère la virgule)
    if 'prix' in df.columns:
        df['prix_clean'] = df['prix'].astype(str).str.replace(' €', '').str.replace(',', '.').astype(float)
    else:
        df['prix_clean'] = 0
    
    # On force la date
    df['date_commande'] = pd.to_datetime(df['date_commande'], dayfirst=True, errors='coerce')
    
    # On remplace les avis vides par 0 pour éviter le crash
    if 'note_avis' in df.columns:
        df['note_avis'] = pd.to_numeric(df['note_avis'], errors='coerce').fillna(0)
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Erreur de lecture du fichier : {e}")
    st.stop()

# 4. Calculs avec sécurités (pour éviter les divisions par zéro)
ca = df['prix_clean'].sum()
qty = df['quantité'].sum() if 'quantité' in df.columns else 0
basket = ca / len(df) if len(df) > 0 else 0
sat = df['note_avis'].mean() if 'note_avis' in df.columns else 0
clients = df['identifiant_client'].nunique() if 'identifiant_client' in df.columns else 0
loyalty = len(df) / clients if clients > 0 else 0

# 5. Dashboard
st.title("📊 Business Automation Dashboard")
st.caption("RSA Monitoring - Version Sécurisée")

# Les 6 KPIs
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Revenue", f"{ca/1000:.1f}k€")
c2.metric("Orders", int(qty))
c3.metric("Avg Basket", f"{basket:.1f}€")
c4.metric("Sat.", f"{sat:.1f}/5")
c5.metric("Clients", clients)
c6.metric("Loyalty", f"{loyalty:.1f}")

st.divider()

# Les Jauges (Gauges)
st.subheader("Performance vs Targets")
g1, g2, g3, g4 = st.columns(4)

def draw_gauge(title, val, target):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=(val/target)*100 if target > 0 else 0,
        number={'suffix': "%", 'font': {'size': 20}},
        title={'text': title, 'font': {'size': 14}},
        gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#20B2AA"}}
    ))
    fig.update_layout(height=180, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)')
    return fig

g1.plotly_chart(draw_gauge("Sales Goal", ca, 500000), use_container_width=True)
g2.plotly_chart(draw_gauge("Units Goal", qty, 5000), use_container_width=True)
g3.plotly_chart(draw_gauge("Sat. Goal", sat, 5), use_container_width=True)
g4.plotly_chart(draw_gauge("Loyalty Goal", loyalty, 2.5), use_container_width=True)

# Graphs
st.markdown("---")
l, r = st.columns([7, 3])
with l:
    trend = df.groupby('date_commande')['prix_clean'].sum().reset_index()
    st.plotly_chart(px.area(trend, x='date_commande', y='prix_clean', title="Sales Trend", color_discrete_sequence=['#20B2AA']), use_container_width=True)
with r:
    if 'nom_catégorie' in df.columns:
        cat = df.groupby('nom_catégorie')['prix_clean'].sum().reset_index()
        st.plotly_chart(px.bar(cat, x='prix_clean', y='nom_catégorie', orientation='h', title="By Category", color_discrete_sequence=['#7FB3D5']), use_container_width=True)

# Bouton Slack dans la Sidebar
if st.sidebar.button("🚀 Push to Slack"):
    if send_slack("Rapport généré avec succès."):
        st.sidebar.success("OK !")
    else: st.sidebar.warning("Webhook non configuré.")
