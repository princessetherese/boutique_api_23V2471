# app_pro.py - Version Design Professionnel
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.metrics import r2_score, silhouette_score
import time
import os
import warnings
warnings.filterwarnings('ignore')

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="ShopAnalyzer Pro - Armelle",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS DESIGN PROFESSIONNEL ====================
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    
    /* Header professionnel */
    .professional-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        position: relative;
        overflow: hidden;
    }
    
    .professional-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
        animation: pulse 8s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    .professional-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        position: relative;
        z-index: 1;
    }
    
    .professional-header p {
        font-size: 1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .professional-header .badge {
        background: rgba(255,255,255,0.2);
        display: inline-block;
        padding: 0.3rem 1rem;
        border-radius: 50px;
        font-size: 0.8rem;
        margin-top: 1rem;
        position: relative;
        z-index: 1;
    }
    
    /* Cartes métriques */
    .metric-card-pro {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 16px;
        padding: 1.2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(102, 126, 234, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card-pro::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .metric-card-pro:hover::after {
        transform: scaleX(1);
    }
    
    .metric-card-pro:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .metric-icon-pro {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-value-pro {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0.5rem 0;
    }
    
    .metric-label-pro {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #6c757d;
        font-weight: 600;
    }
    
    /* Formulaire professionnel */
    .form-container {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
    }
    
    /* Cartes produit */
    .product-card-pro {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .product-card-pro:hover {
        border-color: #667eea;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
        transform: translateY(-2px);
    }
    
    .product-emoji {
        font-size: 1.5rem;
        display: inline-block;
        margin-right: 0.5rem;
    }
    
    .product-name-pro {
        font-weight: 700;
        font-size: 0.95rem;
        color: #2c3e50;
        display: inline;
    }
    
    .product-desc-pro {
        font-size: 0.75rem;
        color: #6c757d;
        margin-top: 0.25rem;
    }
    
    .product-price-pro {
        font-size: 1rem;
        font-weight: 800;
        color: #667eea;
        margin-top: 0.5rem;
    }
    
    /* Sidebar stylée */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    /* Bouton Orange Money */
    .orange-money-btn {
        background: linear-gradient(135deg, #FF6600 0%, #FF8533 100%);
        color: white;
        padding: 0.75rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 700;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .orange-money-btn:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 20px rgba(255, 102, 0, 0.3);
    }
    
    /* Stats sidebar */
    .stats-sidebar {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
    }
    
    .stats-number {
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Footer */
    .professional-footer {
        text-align: center;
        padding: 1.5rem;
        margin-top: 2rem;
        border-top: 1px solid #e9ecef;
        color: #6c757d;
    }
    
    /* Badges */
    .badge-pro {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    
    .badge-success {
        background: #d4edda;
        color: #155724;
    }
    
    .badge-warning {
        background: #fff3cd;
        color: #856404;
    }
    
    /* Tabs personnalisés */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# ==================== GESTION DES FICHIERS ====================
CLIENTS_FILE = "clients.csv"
ACHATS_FILE = "achats.csv"

def charger_clients():
    if os.path.exists(CLIENTS_FILE):
        return pd.read_csv(CLIENTS_FILE)
    else:
        df = pd.DataFrame(columns=['client_id', 'nom', 'email', 'âge', 'ville', 'avatar', 
                                   'revenu_annuel_fcfa', 'ca_total_fcfa', 'nb_achats', 'dernier_achat'])
        df.to_csv(CLIENTS_FILE, index=False)
        return df

def sauvegarder_clients(df):
    df.to_csv(CLIENTS_FILE, index=False)

def charger_achats():
    if os.path.exists(ACHATS_FILE):
        return pd.read_csv(ACHATS_FILE)
    else:
        df = pd.DataFrame(columns=['date', 'client_id', 'client_nom', 'produits', 'montant_fcfa', 'mode_paiement', 'nb_articles'])
        df.to_csv(ACHATS_FILE, index=False)
        return df

def sauvegarder_achats(df):
    df.to_csv(ACHATS_FILE, index=False)

# Chargement des données
if 'df_clients' not in st.session_state:
    st.session_state.df_clients = charger_clients()

if 'df_achats' not in st.session_state:
    st.session_state.df_achats = charger_achats()

# ==================== CATALOGUE PRODUITS ====================
PRODUITS = {
    # ÉLECTRONIQUE
    '📱 Smartphone Tecno Camon 20': {'prix': 120000, 'categorie': 'Électronique', 'desc': '128Go, 6.6 pouces'},
    '📱 iPhone 13': {'prix': 450000, 'categorie': 'Électronique', 'desc': 'Apple 128Go'},
    '📱 Samsung Galaxy A14': {'prix': 150000, 'categorie': 'Électronique', 'desc': '4G 64Go'},
    '💻 PC Portable HP': {'prix': 350000, 'categorie': 'Électronique', 'desc': 'Core i5 8Go'},
    '💻 PC Dell Latitude': {'prix': 400000, 'categorie': 'Électronique', 'desc': 'Core i7 16Go'},
    '🎧 Casque JBL': {'prix': 30000, 'categorie': 'Électronique', 'desc': 'Bluetooth sans fil'},
    '⌚ Montre connectée': {'prix': 45000, 'categorie': 'Électronique', 'desc': 'Fitness tracker'},
    '🔊 Enceinte Bluetooth': {'prix': 25000, 'categorie': 'Électronique', 'desc': 'Portable 10W'},
    '💾 SSD 1To': {'prix': 55000, 'categorie': 'Électronique', 'desc': 'Externe USB 3.0'},
    '🖨️ Imprimante HP': {'prix': 120000, 'categorie': 'Électronique', 'desc': 'Multifonction'},
    
    # MODE
    '👕 T-shirt Premium': {'prix': 7500, 'categorie': 'Mode', 'desc': 'Coton bio'},
    '👕 T-shirt Femme': {'prix': 7000, 'categorie': 'Mode', 'desc': 'Col V'},
    '👖 Jean Slim': {'prix': 15000, 'categorie': 'Mode', 'desc': 'Slim stretch'},
    '👗 Robe Chic': {'prix': 25000, 'categorie': 'Mode', 'desc': 'Cérémonie'},
    '👟 Basket Nike': {'prix': 55000, 'categorie': 'Mode', 'desc': 'Air running'},
    '👟 Basket Adidas': {'prix': 45000, 'categorie': 'Mode', 'desc': 'Lifestyle'},
    '🧥 Manteau Hiver': {'prix': 35000, 'categorie': 'Mode', 'desc': 'Doudoune'},
    '🧣 Écharpe Luxe': {'prix': 8000, 'categorie': 'Mode', 'desc': 'Cachemire'},
    '👔 Chemise Homme': {'prix': 12000, 'categorie': 'Mode', 'desc': 'Blanche'},
    '🩳 Short Sport': {'prix': 6000, 'categorie': 'Mode', 'desc': 'Sport'},
    
    # MAISON
    '🛋️ Canapé 3 places': {'prix': 250000, 'categorie': 'Maison', 'desc': 'Cuir'},
    '🛏️ Lit 2 places': {'prix': 180000, 'categorie': 'Maison', 'desc': 'Avec sommier'},
    '🚪 Armoire 3 portes': {'prix': 150000, 'categorie': 'Maison', 'desc': 'Miroir'},
    '🍽️ Table à manger': {'prix': 120000, 'categorie': 'Maison', 'desc': '6 places bois'},
    '💡 Lampe LED': {'prix': 15000, 'categorie': 'Maison', 'desc': 'Lampadaire'},
    '🪑 Chaise bureau': {'prix': 35000, 'categorie': 'Maison', 'desc': 'Ergonomique'},
    '📺 TV 55 pouces': {'prix': 300000, 'categorie': 'Maison', 'desc': 'Smart 4K'},
    '❄️ Climatiseur': {'prix': 280000, 'categorie': 'Maison', 'desc': '12000 BTU'},
    '🧺 Machine à laver': {'prix': 200000, 'categorie': 'Maison', 'desc': '7kg'},
    '🍳 Micro-ondes': {'prix': 75000, 'categorie': 'Maison', 'desc': '20L'},
    
    # SPORTS
    '⚽ Ballon foot': {'prix': 8000, 'categorie': 'Sports', 'desc': 'Taille 5'},
    '🏀 Ballon basket': {'prix': 10000, 'categorie': 'Sports', 'desc': 'Taille 7'},
    '🎾 Raquette tennis': {'prix': 25000, 'categorie': 'Sports', 'desc': 'Alu'},
    '🏋️ Haltères 10kg': {'prix': 20000, 'categorie': 'Sports', 'desc': 'Set'},
    '🚴 Vélo route': {'prix': 150000, 'categorie': 'Sports', 'desc': '21 vitesses'},
    '🏃 Tapis course': {'prix': 250000, 'categorie': 'Sports', 'desc': 'Pliable'},
    '🥊 Gants boxe': {'prix': 18000, 'categorie': 'Sports', 'desc': 'Cuir'},
    '🏊 Lunettes natation': {'prix': 5000, 'categorie': 'Sports', 'desc': 'Anti-buée'},
    '🧘 Tapis yoga': {'prix': 12000, 'categorie': 'Sports', 'desc': 'Antidérapant'},
    '⚽ Maillot foot': {'prix': 10000, 'categorie': 'Sports', 'desc': 'Officiel'}
}

# ==================== FONCTIONS ====================
def format_fcfa(x):
    if pd.isna(x) or x == 0:
        return "0 FCFA"
    return f"{x:,.0f} FCFA".replace(",", " ")

def enregistrer_achat(client_id, client_nom, produits_achetes, montant_total, mode_paiement):
    nouvel_achat = pd.DataFrame([{
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'client_id': client_id,
        'client_nom': client_nom,
        'produits': ', '.join(produits_achetes),
        'montant_fcfa': montant_total,
        'mode_paiement': mode_paiement,
        'nb_articles': len(produits_achetes)
    }])
    
    st.session_state.df_achats = pd.concat([st.session_state.df_achats, nouvel_achat], ignore_index=True)
    sauvegarder_achats(st.session_state.df_achats)
    
    idx = st.session_state.df_clients[st.session_state.df_clients['client_id'] == client_id].index
    if len(idx) > 0:
        st.session_state.df_clients.loc[idx, 'ca_total_fcfa'] += montant_total
        st.session_state.df_clients.loc[idx, 'nb_achats'] += 1
        st.session_state.df_clients.loc[idx, 'dernier_achat'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sauvegarder_clients(st.session_state.df_clients)
    
    return True

# ==================== HEADER PROFESSIONNEL ====================
st.markdown("""
<div class="professional-header fade-in-up">
    <h1>🛍️ ShopAnalyzer Pro</h1>
    <p>Plateforme intelligente de collecte et d'analyse de données e-commerce</p>
    <div class="badge">🔒 Données sécurisées | 📊 Analytics en temps réel | 💳 Paiement Orange Money</div>
</div>
""", unsafe_allow_html=True)

# ==================== SIDEBAR PROFESSIONNELLE ====================
with st.sidebar:
    st.markdown("### 👩‍💻 **Armelle's Dashboard**")
    st.markdown("---")
    
    total_ventes = st.session_state.df_achats['montant_fcfa'].sum() if len(st.session_state.df_achats) > 0 else 0
    nb_commandes = len(st.session_state.df_achats)
    nb_clients = len(st.session_state.df_clients)
    
    st.markdown(f"""
    <div class="stats-sidebar">
        <div style="font-size: 0.8rem; color: #666;">📊 CHIFFRES CLÉS</div>
        <div style="margin-top: 0.8rem;">
            <div style="font-size: 0.7rem; color: #888;">CHIFFRE D'AFFAIRES</div>
            <div class="stats-number">{format_fcfa(total_ventes)}</div>
        </div>
        <div style="margin-top: 0.8rem;">
            <div style="font-size: 0.7rem; color: #888;">COMMANDES</div>
            <div class="stats-number">{nb_commandes}</div>
        </div>
        <div style="margin-top: 0.8rem;">
            <div style="font-size: 0.7rem; color: #888;">CLIENTS</div>
            <div class="stats-number">{nb_clients}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="orange-money-btn">📱 Orange Money disponible</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.caption("💡 **Conseil** : Utilisez Orange Money pour un paiement instantané")
    st.markdown("---")
    st.caption(f"🕐 Dernière connexion: {datetime.now().strftime('%H:%M:%S')}")
    st.caption("© 2024 ShopAnalyzer Pro")

# ==================== MENU PRINCIPAL ====================
menu = st.sidebar.radio(
    "Navigation",
    ["🛒 Nouvel Achat", "📊 Dashboard", "📈 Analyses ML", "📋 Données", "👥 Clients"],
    index=0
)

# ==================== PAGE 1: NOUVEL ACHAT ====================
if menu == "🛒 Nouvel Achat":
    st.markdown("## 🛒 **Nouvelle commande**")
    st.markdown("*Remplissez le formulaire ci-dessous pour passer commande*")
    st.markdown("---")
    
    with st.form("achat_form", clear_on_submit=True):
        col1, col2 = st.columns([1, 1.5])
        
        with col1:
            st.markdown("### 👤 **Informations client**")
            
            option_client = st.radio(
                "Type de client",
                ["✨ Nouveau client", "⭐ Client existant"],
                horizontal=True
            )
            
            if option_client == "⭐ Client existant":
                if len(st.session_state.df_clients) > 0:
                    client_ids = st.session_state.df_clients['client_id'].tolist()
                    client_noms = st.session_state.df_clients['nom'].tolist()
                    client_options = [f"#{cid} - {nom}" for cid, nom in zip(client_ids, client_noms)]
                    selected_client = st.selectbox("Sélectionnez votre compte", client_options)
                    client_id = int(selected_client.split(" - ")[0].replace("#", ""))
                    client_info = st.session_state.df_clients[st.session_state.df_clients['client_id'] == client_id].iloc[0]
                    st.success(f"👋 Bon retour {client_info['avatar']} {client_info['nom']} !")
                    client_nom = client_info['nom']
                    
                    st.info(f"💰 Revenu actuel : {format_fcfa(client_info['revenu_annuel_fcfa'])}")
                    
                    modifier_revenu = st.checkbox("Modifier mon revenu")
                    if modifier_revenu:
                        nouveau_revenu = st.number_input("Nouveau revenu (FCFA)", 
                                                         50000, 100000000, 
                                                         int(client_info['revenu_annuel_fcfa']), 
                                                         step=50000,
                                                         help="Minimum 50 000 FCFA")
                        if nouveau_revenu != client_info['revenu_annuel_fcfa']:
                            idx = st.session_state.df_clients[st.session_state.df_clients['client_id'] == client_id].index
                            st.session_state.df_clients.loc[idx, 'revenu_annuel_fcfa'] = nouveau_revenu
                            sauvegarder_clients(st.session_state.df_clients)
                            st.success("✅ Revenu mis à jour !")
                else:
                    st.warning("Aucun client existant. Créez un nouveau compte.")
                    option_client = "✨ Nouveau client"
                    client_nom = ""
            
            if option_client == "✨ Nouveau client":
                col_a, col_b = st.columns(2)
                with col_a:
                    client_nom = st.text_input("Nom complet *", placeholder="Jean Dupont")
                    age = st.number_input("Âge *", 18, 80, 30)
                    ville = st.selectbox("Ville *", ['Douala', 'Yaoundé', 'Garoua', 'Bafoussam', 'Bamenda'])
                with col_b:
                    email = st.text_input("Email *", placeholder="jean@email.com")
                    avatar = st.selectbox("Avatar", ['👨', '👩', '👧', '👴', '👵'])
                    revenu_client = st.number_input("Revenu annuel (FCFA) *", 
                                                    50000, 100000000, 2500000, 
                                                    step=50000,
                                                    help="Minimum 50 000 FCFA")
                st.caption("💡 Le revenu minimum est de **50 000 FCFA**")
        
        with col2:
            st.markdown("### 📦 **Catalogue produits**")
            st.caption(f"📌 {len(PRODUITS)} produits disponibles dans 4 catégories")
            
            produits_selectionnes = []
            montant_total = 0
            
            for categorie in ['Électronique', 'Mode', 'Maison', 'Sports']:
                produits_cat = [(nom, info) for nom, info in PRODUITS.items() if info['categorie'] == categorie]
                
                with st.expander(f"📂 {categorie} ({len(produits_cat)} articles)", expanded=True):
                    cols = st.columns(2)
                    for i, (produit, info) in enumerate(produits_cat):
                        with cols[i % 2]:
                            st.markdown(f"""
                            <div class="product-card-pro">
                                <div>
                                    <span class="product-emoji">{produit.split(' ')[0]}</span>
                                    <span class="product-name-pro">{produit}</span>
                                </div>
                                <div class="product-desc-pro">{info['desc']}</div>
                                <div class="product-price-pro">{format_fcfa(info['prix'])}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            quantite = st.number_input(
                                "Qté",
                                min_value=0, max_value=10, key=f"{categorie}_{produit}",
                                label_visibility="collapsed"
                            )
                            if quantite > 0:
                                produits_selectionnes.extend([produit] * quantite)
                                montant_total += info['prix'] * quantite
                            st.markdown("---")
            
            st.markdown("---")
            st.markdown("### 💳 **Mode de paiement**")
            
            mode_paiement = st.radio(
                "Choisissez votre moyen de paiement",
                ["📱 Orange Money (Recommandé)", "💳 Carte bancaire", "🚚 Paiement à la livraison"],
                help="Orange Money est instantané et sécurisé"
            )
            
            total_color = "#FF6600" if "Orange Money" in mode_paiement else "#667eea"
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, {total_color} 0%, {total_color}cc 100%); 
                        padding: 1.2rem; border-radius: 15px; color: white; text-align: center; margin-top: 1rem;'>
                <div style='font-size: 0.8rem; opacity: 0.9;'>TOTAL À PAYER</div>
                <div style='font-size: 2.2rem; font-weight: 800;'>{format_fcfa(montant_total)}</div>
                {'<div style="font-size: 0.7rem; margin-top: 0.5rem;">🔒 Paiement sécurisé Orange Money</div>' if "Orange Money" in mode_paiement else ''}
            </div>
            """, unsafe_allow_html=True)
        
        submitted = st.form_submit_button("✅ Confirmer la commande", use_container_width=True)
        
        if submitted:
            if montant_total == 0:
                st.error("❌ Veuillez sélectionner au moins un produit")
            elif option_client == "✨ Nouveau client" and (not client_nom or not email):
                st.error("❌ Veuillez remplir vos informations")
            else:
                with st.spinner("Traitement en cours..."):
                    time.sleep(0.8)
                    
                    if option_client == "✨ Nouveau client":
                        new_id = len(st.session_state.df_clients) + 1
                        nouveau_client = pd.DataFrame([{
                            'client_id': new_id,
                            'nom': client_nom,
                            'email': email,
                            'âge': age,
                            'ville': ville,
                            'avatar': avatar,
                            'revenu_annuel_fcfa': revenu_client,
                            'ca_total_fcfa': 0,
                            'nb_achats': 0,
                            'dernier_achat': ''
                        }])
                        st.session_state.df_clients = pd.concat([st.session_state.df_clients, nouveau_client], ignore_index=True)
                        sauvegarder_clients(st.session_state.df_clients)
                        client_id = new_id
                    
                    if enregistrer_achat(client_id, client_nom, produits_selectionnes, montant_total, mode_paiement):
                        st.balloons()
                        st.success(f"🎉 Commande confirmée ! Merci {client_nom}")
                        
                        with st.expander("📄 Récapitulatif", expanded=True):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("**Commande #**", len(st.session_state.df_achats))
                                st.write("**Date:**", datetime.now().strftime('%d/%m/%Y %H:%M'))
                                st.write("**Client:**", client_nom)
                            with col2:
                                st.write("**Articles:**", len(produits_selectionnes))
                                st.write("**Paiement:**", mode_paiement)
                                st.write("**Total:**", format_fcfa(montant_total))

# ==================== PAGE 2: DASHBOARD ====================
elif menu == "📊 Dashboard":
    st.markdown("## 📊 **Tableau de bord analytique**")
    st.markdown("*Vue d'ensemble des performances de la boutique*")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_ventes = st.session_state.df_achats['montant_fcfa'].sum() if len(st.session_state.df_achats) > 0 else 0
    nb_commandes = len(st.session_state.df_achats)
    nb_clients_actifs = len(st.session_state.df_clients[st.session_state.df_clients['nb_achats'] > 0]) if len(st.session_state.df_clients) > 0 else 0
    panier_moyen = total_ventes / nb_commandes if nb_commandes > 0 else 0
    
    with col1:
        st.markdown(f"""
        <div class="metric-card-pro">
            <div class="metric-icon-pro">💰</div>
            <div class="metric-value-pro">{format_fcfa(total_ventes)}</div>
            <div class="metric-label-pro">CHIFFRE D'AFFAIRES</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card-pro">
            <div class="metric-icon-pro">📦</div>
            <div class="metric-value-pro">{nb_commandes}</div>
            <div class="metric-label-pro">COMMANDES</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card-pro">
            <div class="metric-icon-pro">👥</div>
            <div class="metric-value-pro">{nb_clients_actifs}</div>
            <div class="metric-label-pro">CLIENTS ACTIFS</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card-pro">
            <div class="metric-icon-pro">🛒</div>
            <div class="metric-value-pro">{format_fcfa(panier_moyen)}</div>
            <div class="metric-label-pro">PANIER MOYEN</div>
        </div>
        """, unsafe_allow_html=True)
    
    if len(st.session_state.df_achats) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            df_ventes = st.session_state.df_achats.copy()
            df_ventes['date'] = pd.to_datetime(df_ventes['date'])
            df_ventes['jour'] = df_ventes['date'].dt.date
            ventes_par_jour = df_ventes.groupby('jour')['montant_fcfa'].sum().reset_index()
            
            fig = px.line(ventes_par_jour, x='jour', y='montant_fcfa',
                         title="📈 Évolution des ventes",
                         labels={'jour':'Date', 'montant_fcfa':'CA (FCFA)'})
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            tous_produits = []
            for produits in st.session_state.df_achats['produits']:
                tous_produits.extend(produits.split(', '))
            
            if tous_produits:
                top_produits = pd.Series(tous_produits).value_counts().head(10)
                fig = px.bar(x=top_produits.values, y=top_produits.index,
                            orientation='h', title="🏆 Top 10 produits",
                            labels={'x':'Ventes', 'y':'Produits'})
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
        
        paiements = st.session_state.df_achats['mode_paiement'].value_counts()
        fig = px.pie(values=paiements.values, names=paiements.index,
                    title="💳 Répartition des paiements",
                    color_discrete_sequence=['#FF6600', '#4CAF50', '#2196F3'])
        st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE 3: ANALYSES ML ====================
elif menu == "📈 Analyses ML":
    st.markdown("## 📈 **Intelligence Artificielle**")
    st.markdown("*Modèles prédictifs et segmentation automatique*")
    st.markdown("---")
    
    df_ml = st.session_state.df_clients[st.session_state.df_clients['nb_achats'] > 0].copy()
    
    if len(df_ml) > 5:
        tab1, tab2 = st.tabs(["📈 Régression", "🔍 Clustering"])
        
        with tab1:
            st.subheader("Prédiction du Chiffre d'Affaires")
            
            X = df_ml[['âge', 'revenu_annuel_fcfa']]
            y = df_ml['ca_total_fcfa']
            
            if len(X) > 1:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                reg = LinearRegression()
                reg.fit(X_train, y_train)
                score = reg.score(X_test, y_test)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("🎯 R² Score", f"{max(0, score):.2%}")
                    if score > 0:
                        st.progress(min(1, max(0, score)))
                    st.write("**Impact des variables :**")
                    st.write(f"- Âge : +{reg.coef_[0]:.0f} FCFA/an")
                    st.write(f"- Revenu : +{int(reg.coef_[1]):,} FCFA".replace(",", " "))
                
                with col2:
                    y_pred = reg.predict(X_test)
                    fig = px.scatter(x=y_test, y=y_pred,
                                    title="Prédiction vs Réalité",
                                    labels={'x':'CA réel (FCFA)', 'y':'CA prédit (FCFA)'})
                    fig.add_trace(go.Scatter(x=[y.min(), y.max()], y=[y.min(), y.max()],
                                            mode='lines', name='Parfait', line=dict(dash='dash', color='red')))
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.subheader("Segmentation automatique des clients")
            
            features = df_ml[['âge', 'ca_total_fcfa', 'nb_achats']]
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            df_ml['segment'] = kmeans.fit_predict(features_scaled)
            
            sil_score = silhouette_score(features_scaled, df_ml['segment'])
            st.metric("📊 Silhouette Score", f"{sil_score:.2%}")
            
            fig = px.scatter(df_ml, x='ca_total_fcfa', y='nb_achats', 
                            color='segment', size='âge',
                            title="Segmentation clients",
                            labels={'ca_total_fcfa':'CA (FCFA)', 'nb_achats':'Nb achats'},
                            hover_data=['nom'])
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"📊 Besoin d'au moins 5 clients. Actuellement : {len(df_ml)} clients.")

# ==================== PAGE 4: DONNÉES ====================
elif menu == "📋 Données":
    st.markdown("## 📋 **Données collectées**")
    st.markdown("*Historique complet des transactions*")
    st.markdown("---")
    
    st.markdown("""
    <div style='background: #d4edda; padding: 0.8rem; border-radius: 10px; margin-bottom: 1rem;'>
        ✅ Données sauvegardées et persistantes
    </div>
    """, unsafe_allow_html=True)
    
    if len(st.session_state.df_achats) > 0:
        sub, exp = st.columns([1, 1])
        with sub:
            st.subheader("📜 Historique des achats")
        
        df_display = st.session_state.df_achats.copy()
        df_display['montant_fcfa'] = df_display['montant_fcfa'].apply(format_fcfa)
        st.dataframe(df_display, use_container_width=True, height=300)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total commandes", len(st.session_state.df_achats))
        with col2:
            csv_achats = st.session_state.df_achats.to_csv(index=False)
            st.download_button("📥 Télécharger (CSV)", csv_achats, "achats.csv", "text/csv")
    else:
        st.info("📭 Aucune donnée pour le moment")

# ==================== PAGE 5: CLIENTS ====================
else:
    st.markdown("## 👥 **Base clients**")
    st.markdown("*Gestion des clients enregistrés*")
    st.markdown("---")
    
    if len(st.session_state.df_clients) > 0:
        df_display = st.session_state.df_clients.copy()
        df_display['revenu_annuel_fcfa'] = df_display['revenu_annuel_fcfa'].apply(format_fcfa)
        df_display['ca_total_fcfa'] = df_display['ca_total_fcfa'].apply(format_fcfa)
        st.dataframe(df_display, use_container_width=True, height=400)
        
        csv_clients = st.session_state.df_clients.to_csv(index=False)
        st.download_button("📥 Exporter les clients (CSV)", csv_clients, "clients.csv", "text/csv")
    else:
        st.info("📭 Aucun client enregistré")

# ==================== FOOTER ====================
st.markdown("""
<div class="professional-footer">
    <p>🛍️ <strong>ShopAnalyzer Pro</strong> - Réalisé par <strong>Armelle</strong></p>
    <p>💰 Francs CFA (FCFA) | 📱 Orange Money accepté | 🔒 Données sécurisées</p>
    <p style="font-size: 0.7rem;">© 2024 Tous droits réservés</p>
</div>
""", unsafe_allow_html=True)
