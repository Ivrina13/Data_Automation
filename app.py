import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Business Monitoring Dashboard",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
.stApp { background-color: #F4F6F8; }
div[data-testid="metric-container"] {
    background-color: white;
    border: 1px solid #DDE1E7;
    border-radius: 16px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    min-width: 0;
}
div[data-testid="metric-container"] > div {
    overflow: visible !important;
    white-space: nowrap;
}
div[data-testid="stMetricValue"] {
    font-size: 1.3rem !important;
    overflow: visible !important;
    white-space: nowrap !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 0.85rem !important;
    white-space: nowrap !important;
}
</style>
""", unsafe_allow_html=True)

# ── Chargement ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")

    # Nettoyage prix : "373,36 €" → 373.36
    df["prix_clean"] = (
        df["prix"]
        .astype(str)
        .str.replace(" €", "", regex=False)
        .str.replace("\u202f", "", regex=False)  # espace insécable
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    # Dates
    df["date_commande"] = pd.to_datetime(df["date_commande"], dayfirst=True, errors="coerce")
    df["mois"] = df["date_commande"].dt.to_period("M").astype(str)

    # Notes
    df["note_avis"] = pd.to_numeric(df["note_avis"], errors="coerce")

    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ Fichier `data.csv` introuvable. Vérifie qu'il est dans le repo GitHub avec ce nom exact.")
    st.stop()

# ── Sidebar Filtres ───────────────────────────────────────────────────────────
st.sidebar.header("🔍 Filtres")

cats = ["Toutes"] + sorted(df["nom_catégorie"].dropna().unique().tolist())
sel_cat = st.sidebar.selectbox("Catégorie", cats)

pays = ["Tous"] + sorted(df["mode de paiement"].dropna().unique().tolist())
sel_pay = st.sidebar.selectbox("Mode de paiement", pays)

date_min = df["date_commande"].min().date()
date_max = df["date_commande"].max().date()
date_range = st.sidebar.date_input("Période", value=(date_min, date_max), min_value=date_min, max_value=date_max)

# Application filtres
dff = df.copy()
if sel_cat != "Toutes":
    dff = dff[dff["nom_catégorie"] == sel_cat]
if sel_pay != "Tous":
    dff = dff[dff["mode de paiement"] == sel_pay]
if len(date_range) == 2:
    dff = dff[
        (dff["date_commande"].dt.date >= date_range[0]) &
        (dff["date_commande"].dt.date <= date_range[1])
    ]
    
# ── Bouton Slack ──────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
if st.sidebar.button("💬 Rejoindre notre Slack"):
    st.sidebar.markdown("""
    <div style="
        background-color: white;
        border: 1px solid #DDE1E7;
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        margin-top: 8px;
    ">
        <div style="font-size: 32px; margin-bottom: 8px;">🔒</div>
        <p style="font-size: 14px; font-weight: 600; color: #111827; margin: 0 0 6px;">Accès refusé</p>
        <p style="font-size: 12px; color: #6B7280; margin: 0; line-height: 1.6;">
            Ce Slack est privé.<br>Privé... mais si tu recrutes, on peut en parler. 😉
        </p>
    </div>
    """, unsafe_allow_html=True)
    
# ── KPIs ──────────────────────────────────────────────────────────────────────
ca      = dff["prix_clean"].sum()
orders  = len(dff)
basket  = ca / orders if orders > 0 else 0
sat     = dff["note_avis"].mean()
clients = dff["identifiant_client"].nunique()
loyalty = orders / clients if clients > 0 else 0

st.title("📊 Business Monitoring Dashboard")
st.subheader("Vue d'ensemble")

st.markdown("🔗 [Voir mon GitHub](https://github.com/Ivrina13)")

kpis = [
    ("💰", "Chiffre d'affaires", f"{ca:,.0f} €"),
    ("🛒", "Commandes",          f"{orders:,}"),
    ("⭐", "Satisfaction",       f"{sat:.2f} / 5" if not pd.isna(sat) else "—"),
    ("🧾", "Panier moyen",       f"{basket:,.0f} €"),
    ("👥", "Clients uniques",    f"{clients:,}"),
]

cols = st.columns(len(kpis))
for col, (icon, label, value) in zip(cols, kpis):
    col.markdown(f"""
    <div style="
        background-color: white;
        border: 1px solid #DDE1E7;
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    ">
        <div style="font-size:12px; color:#6B7280; margin-bottom:6px;">{icon} {label}</div>
        <div style="font-size:22px; font-weight:600; color:#111827;">{value}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── Jauges objectifs ──────────────────────────────────────────────────────────
st.subheader("🎯 Objectifs")

def gauge(title, val, target):
    pct = min((val / target) * 100, 100) if target else 0
    color = "#27AE60" if pct >= 80 else "#E67E22" if pct >= 50 else "#E74C3C"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct,
        number={"suffix": "%", "font": {"size": 22, "color": color}},
        title={"text": title, "font": {"size": 13}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 50],   "color": "#FADBD8"},
                {"range": [50, 80],  "color": "#FAE5D3"},
                {"range": [80, 100], "color": "#D5F5E3"},
            ],
        },
    ))
    fig.update_layout(height=180, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="rgba(0,0,0,0)")
    return fig

g1, g2, g3 = st.columns(3)
g1.plotly_chart(gauge("CA (objectif 500k€)", ca, 500_000), use_container_width=True)
g2.plotly_chart(gauge("Commandes (objectif 1000)", orders, 1_000), use_container_width=True)
g3.plotly_chart(gauge("Satisfaction (objectif 5)", sat if not pd.isna(sat) else 0, 5), use_container_width=True)

st.divider()

# ── Graphiques ────────────────────────────────────────────────────────────────
l, r = st.columns([7, 3])

with l:
    trend = dff.groupby("mois")["prix_clean"].sum().reset_index().sort_values("mois")
    fig_trend = px.area(
        trend, x="mois", y="prix_clean",
        title="📈 Évolution du CA par mois",
        labels={"mois": "Mois", "prix_clean": "CA (€)"},
        color_discrete_sequence=["#2E4053"]
    )
    fig_trend.update_layout(paper_bgcolor="white", plot_bgcolor="white")
    st.plotly_chart(fig_trend, use_container_width=True)

with r:
    cat = dff.groupby("nom_catégorie")["prix_clean"].sum().reset_index().sort_values("prix_clean")
    fig_bar = px.bar(
        cat, x="prix_clean", y="nom_catégorie", orientation="h",
        title="🏷️ CA par catégorie",
        labels={"prix_clean": "CA (€)", "nom_catégorie": ""},
        color_discrete_sequence=["#5D6D7E"]
    )
    fig_bar.update_layout(paper_bgcolor="white", plot_bgcolor="white")
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")
c1, c2 = st.columns(2)

with c1:
    pay = dff.groupby("mode de paiement")["prix_clean"].sum().reset_index()
    fig_pie = px.pie(
        pay, values="prix_clean", names="mode de paiement",
        title="💳 Répartition par mode de paiement",
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with c2:
    notes = dff["note_avis"].dropna().value_counts().reset_index()
    notes.columns = ["note", "count"]
    notes = notes.sort_values("note")
    fig_notes = px.bar(
        notes, x="note", y="count",
        title="⭐ Distribution des notes",
        labels={"note": "Note", "count": "Nombre d'avis"},
        color_discrete_sequence=["#1A5276"]
    )
    fig_notes.update_layout(paper_bgcolor="white", plot_bgcolor="white")
    st.plotly_chart(fig_notes, use_container_width=True)

st.markdown("---")
d1, d2 = st.columns(2)

with d1:
    genre = dff.groupby("genre")["prix_clean"].sum().reset_index()
    fig_genre = px.pie(
        genre, values="prix_clean", names="genre",
        title="👥 CA par genre",
        color_discrete_sequence=["#2E86C1", "#E91E8C"]
    )
    st.plotly_chart(fig_genre, use_container_width=True)

with d2:
    dff["tranche_age"] = pd.cut(dff["age"], bins=[0,25,35,45,55,65,100],
                                 labels=["<25","25-35","35-45","45-55","55-65","65+"])
    age_ca = dff.groupby("tranche_age", observed=True)["prix_clean"].sum().reset_index()
    fig_age = px.bar(
        age_ca, x="tranche_age", y="prix_clean",
        title="🎂 CA par tranche d'âge",
        labels={"tranche_age": "Tranche d'âge", "prix_clean": "CA (€)"},
        color_discrete_sequence=["#1F618D"]
    )
    fig_age.update_layout(paper_bgcolor="white", plot_bgcolor="white")
    st.plotly_chart(fig_age, use_container_width=True)

# ── Top produits ──────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🏆 Top 10 produits")
top = (
    dff.groupby("nom_produit")["prix_clean"]
    .sum().reset_index()
    .sort_values("prix_clean", ascending=False)
    .head(10)
)
fig_top = px.bar(
    top, x="prix_clean", y="nom_produit", orientation="h",
    labels={"prix_clean": "CA (€)", "nom_produit": ""},
    color_discrete_sequence=["#2E4053"]
)
fig_top.update_layout(yaxis=dict(autorange="reversed"), paper_bgcolor="white", plot_bgcolor="white")
st.plotly_chart(fig_top, use_container_width=True)
