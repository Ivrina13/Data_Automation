import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests

# 1. Config & Look Pro
st.set_page_config(page_title="Data Automation", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F4F7F6; }
    div[data-testid="metric-container"] {
        background-color: white; border: 1px solid #E0E0E0;
        padding: 15px; border-radius: 8px; box-shadow: 0px 2px 4px rgba(0,0,0,0.02);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Sécurité Slack (Secrets)
def send_slack(text):
    try:
        url = st.secrets["SLACK_WEBHOOK_URL"]
        requests.post(url, json={"text": text})
        return True
    except: return False

# 3. Chargement & Nettoyage (Spécifique à ton fichier)
@st.cache_data
def load_data():
    # Remplace par le nom EXACT de ton fichier sur GitHub
    df = pd.read_csv('data.csv')
    
    # Nettoyage de la colonne Prix (Enlever € et remplacer la virgule par un point)
    df['prix_clean'] = df['prix'].str.replace(' €', '').str.replace(',', '.').astype(float)
    df['date_commande'] = pd.to_datetime(df['date_commande'], dayfirst=True)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Erreur : Vérifie que le fichier est bien nommé 'Business_Monitoring - donnée brute.csv' sur GitHub.")
    st.stop()

# 4. Sidebar Automation
st.sidebar.title("🤖 Automation")
if st.sidebar.button("🔔 Send Status to Slack"):
    if send_slack("Dashboard RSA consulté."):
        st.sidebar.success("Alerte envoyée !")
    else: st.sidebar.warning("Webhook non configuré dans les Secrets.")

# 5. Calculs des KPIs
ca_total = df['prix_clean'].sum()
nb_ventes = df['quantité'].sum()
panier_moyen = ca_total / len(df)
satisfaction = df['note_avis'].mean()
clients_uniques = df['identifiant_client'].nunique()
frequence = len(df) / clients_uniques

# --- AFFICHAGE ---
st.title("Business Performance Dashboard")
st.caption("Data Source: Business Monitoring System | RSA Style")

# Ligne 1 : 6 KPIs Sobres
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total Revenue", f"{ca_total/1000:.1f}k €")
c2.metric("Total Units", nb_ventes)
c3.metric("Avg Basket", f"{panier_moyen:.2f} €")
c4.metric("Cust. Sat", f"{satisfaction:.1f}/5")
c5.metric("Unique Clients", clients_uniques)
c6.metric("Loyalty Score", f"{frequence:.2f}")

st.divider()

# Ligne 2 : Jauges de Performance (Teal & Grey)
st.subheader("Target Progress")
g1, g2, g3, g4 = st.columns(4)

def draw_gauge(title, value, target):
    return go.Figure(go.Indicator(
        mode="gauge+number", value=(value/target)*100,
        number={'suffix': "%", 'font': {'size': 20}},
        title={'text': title, 'font': {'size': 15}},
        gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#20B2AA"}, 'bgcolor': "white", 'borderwidth': 1}
    )).update_layout(height=180, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)')

g1.plotly_chart(draw_gauge("Sales vs Goal", ca_total, 500000), use_container_width=True)
g2.plotly_chart(draw_gauge("Units vs Goal", nb_ventes, 5000), use_container_width=True)
g3.plotly_chart(draw_gauge("Satisfaction", satisfaction, 5), use_container_width=True)
g4.plotly_chart(draw_gauge("Loyalty Goal", frequence, 2), use_container_width=True)

# Ligne 3 : Graphiques
st.markdown("---")
left, right = st.columns([7, 3])

with left:
    trend = df.groupby('date_commande')['prix_clean'].sum().reset_index()
    fig_trend = px.area(trend, x='date_commande', y='prix_clean', title="Sales Trend by Week", color_discrete_sequence=['#7FB3D5'])
    fig_trend.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_trend, use_container_width=True)

with right:
    cat_data = df.groupby('nom_catégorie')['prix_clean'].sum().reset_index()
    fig_bar = px.bar(cat_data, x='prix_clean', y='nom_catégorie', orientation='h', title="Revenue by Category", color_discrete_sequence=['#20B2AA'])
    st.plotly_chart(fig_bar, use_container_width=True)
