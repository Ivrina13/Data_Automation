import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import json

# --- CONFIG & STYLE ---
st.set_page_config(page_title="Data Automation", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    div[data-testid="metric-container"] {
        background-color: white; border: 1px solid #E0E0E0;
        padding: 15px; border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FONCTION SLACK SÉCURISÉE ---
def send_slack_alert(text):
    try:
        url = st.secrets["SLACK_WEBHOOK_URL"]
        requests.post(url, json={"text": text})
        return True
    except: return False

# --- CHARGEMENT ---
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv') 
    df['date_commande'] = pd.to_datetime(df['date_commande'])
    return df

df = load_data()

# --- SIDEBAR AUTOMATION ---
st.sidebar.title("🤖 Data Automation")
if st.sidebar.button("🚀 Trigger Slack Report"):
    if send_slack_alert("Rapport généré par un utilisateur externe."):
        st.sidebar.success("Notification envoyée !")
    else:
        st.sidebar.warning("Secret non configuré.")

# --- DASHBOARD ---
st.title("Business Intelligence Dashboard")
st.caption("Pipeline automatisé • Données sécurisées")

# Calculs
ca = df['prix'].sum()
qty = df['quantité'].sum()
basket = ca / len(df)
sat = df['note_avis'].mean()
clients = df['identifiant_client'].nunique()
loyalty = len(df) / clients

# LIGNE 1 : 6 KPIs
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Revenue", f"{ca/1000:.1f}K€")
c2.metric("Orders", qty)
c3.metric("Avg Basket", f"{basket:.1f}€")
c4.metric("Customer Sat", f"{sat:.1f}/5")
c5.metric("Unique ID", clients)
c6.metric("Retention", f"{loyalty:.1f}")

st.divider()

# LIGNE 2 : LES JAUGES (Targets)
st.subheader("Target Progress")
g1, g2, g3 = st.columns(3)

def create_gauge(name, val, target):
    return go.Figure(go.Indicator(
        mode="gauge+number", value=val,
        title={'text': name, 'font': {'size': 18}},
        gauge={'axis': {'range': [None, target]}, 'bar': {'color': "#20B2AA"}}
    )).update_layout(height=220, margin=dict(l=20, r=20, t=40, b=20))

g1.plotly_chart(create_gauge("Sales vs Goal", ca, 100000), use_container_width=True)
g2.plotly_chart(create_gauge("Volume vs Goal", qty, 5000), use_container_width=True)
g3.plotly_chart(create_gauge("Sat vs Goal", sat, 5), use_container_width=True)

# LIGNE 3 : TRENDS
st.markdown("---")
col_l, col_r = st.columns([7, 3])
with col_l:
    trend = df.groupby('date_commande')['prix'].sum().reset_index()
    st.plotly_chart(px.area(trend, x='date_commande', y='prix', title="Revenue Stream", color_discrete_sequence=['#7FB3D5']), use_container_width=True)
with col_r:
    st.plotly_chart(px.pie(df, values='prix', names='nom_catégorie', hole=0.5, title="Category Mix"), use_container_width=True)
