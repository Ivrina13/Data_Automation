# 3_Data_Automation
Pipeline d'automatisation de monitoring de stocks : extraction via Google Sheets API, analyse de données avec Pandas et alertes en temps réel sur Slack.

## 📦 Stock Automation
Ce projet automatise la surveillance des stocks pour un e-commerce en connectant Google Sheets, Python et Slack.

## 🛠️ Technologies utilisées
- **Python** (Pandas pour l'analyse, Requests pour les Webhooks)
- **Google Cloud Platform** (API Google Sheets & Drive)
- **Slack API** (Notifications automatiques)

## 🚀 Fonctionnement
1. **Extraction** : Le script se connecte à l'API Google Sheets pour récupérer les données de ventes et de stocks.
2. **Analyse** : Analyse des quantités par rapport à un seuil critique défini.
3. **Alerte** : Envoi immédiat d'une notification structurée sur Slack si un produit est en rupture ou proche de l'être.

## 📊 Impact Business
Ce système élimine la vérification manuelle quotidienne et permet une réactivité immédiate pour éviter les pertes de chiffre d'affaires dues aux ruptures de stocks.
