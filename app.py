# app_final_complete.py - Version finale avec toutes les fonctionnalités
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
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import r2_score, silhouette_score, classification_report, confusion_matrix
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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    /* Badges */
    .badge-momo {
        background: #FF6600;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        display: inline-block;
        margin: 0 0.2rem;
    }
    
    .badge-edit {
        background: #2196F3;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .badge-delete {
        background: #dc3545;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .badge-ml {
        background: #9C27B0;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        display: inline-block;
    }
    
    /* Cartes métriques */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    /* Cartes produit */
    .product-card {
        background: white;
        border-radius: 12px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .product-card:hover {
        border-color: #FF6600;
        box-shadow: 0 4px 12px rgba(255,102,0,0.15);
    }
    
    /* Mobile Money */
    .mobile-money-card {
        background: linear-gradient(135deg, #FF6600 0%, #FF8533 100%);
        padding: 1rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .mobile-money-card:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 20px rgba(255,102,0,0.3);
    }
    
    /* Cartes commande */
    .order-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 1.5rem;
        margin-top: 2rem;
        border-top: 1px solid #e9ecef;
        color: #6c757d;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# ==================== GESTION DES FICHIERS ====================
CLIENTS_FILE = "clients.csv"
ACHATS_FILE = "achats.csv"

def charger_clients():
    if os.path.exists(CLIENTS_FILE):
        df = pd.read_csv(CLIENTS_FILE)
        if 'client_id' not in df.columns:
            df['client_id'] = range(1, len(df) + 1)
        return df
    else:
        df = pd.DataFrame({
            'client_id': [1, 2, 3],
            'nom': ['Jean Dupont', 'Marie Kamga', 'Paul Biya'],
            'email': ['jean@email.com', 'marie@email.com', 'paul@email.com'],
            'âge': [28, 32, 45],
            'ville': ['Douala', 'Yaoundé', 'Garoua'],
            'avatar': ['👨', '👩', '👨'],
            'revenu_annuel_fcfa': [2500000, 3200000, 4500000],
            'ca_total_fcfa': [0, 0, 0],
            'nb_achats': [0, 0, 0],
            'dernier_achat': ['' for _ in range(3)]
        })
        df.to_csv(CLIENTS_FILE, index=False)
        return df

def sauvegarder_clients(df):
    df.to_csv(CLIENTS_FILE, index=False)

def charger_achats():
    if os.path.exists(ACHATS_FILE):
        df = pd.read_csv(ACHATS_FILE)
        if 'order_id' not in df.columns:
            df['order_id'] = range(1, len(df) + 1)
        if 'statut' not in df.columns:
            df['statut'] = 'Confirmé'
        return df
    else:
        df = pd.DataFrame(columns=['order_id', 'date', 'client_id', 'client_nom', 'produits', 
                                   'montant_fcfa', 'mode_paiement', 'nb_articles', 'telephone', 'statut'])
        df.to_csv(ACHATS_FILE, index=False)
        return df

def sauvegarder_achats(df):
    df.to_csv(ACHATS_FILE, index=False)

# Chargement des données
if 'df_clients' not in st.session_state:
    st.session_state.df_clients = charger_clients()

if 'df_achats' not in st.session_state:
    st.session_state.df_achats = charger_achats()
    
if 'edit_order_id' not in st.session_state:
    st.session_state.edit_order_id = None

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

def enregistrer_achat(client_id, client_nom, produits_achetes, montant_total, mode_paiement, phone_number=None):
    if len(st.session_state.df_achats) == 0:
        order_id = 1
    else:
        order_id = st.session_state.df_achats['order_id'].max() + 1
    
    nouvel_achat = pd.DataFrame([{
        'order_id': order_id,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'client_id': client_id,
        'client_nom': client_nom,
        'produits': ', '.join(produits_achetes),
        'montant_fcfa': montant_total,
        'mode_paiement': mode_paiement,
        'nb_articles': len(produits_achetes),
        'telephone': phone_number if phone_number else '',
        'statut': 'Confirmé'
    }])
    
    st.session_state.df_achats = pd.concat([st.session_state.df_achats, nouvel_achat], ignore_index=True)
    sauvegarder_achats(st.session_state.df_achats)
    
    idx = st.session_state.df_clients[st.session_state.df_clients['client_id'] == client_id].index
    if len(idx) > 0:
        st.session_state.df_clients.loc[idx[0], 'ca_total_fcfa'] += montant_total
        st.session_state.df_clients.loc[idx[0], 'nb_achats'] += 1
        st.session_state.df_clients.loc[idx[0], 'dernier_achat'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sauvegarder_clients(st.session_state.df_clients)
    
    return order_id

def modifier_commande(order_id, nouveaux_produits, nouveau_montant):
    mask = st.session_state.df_achats['order_id'] == order_id
    if not mask.any():
        return False
    
    idx = st.session_state.df_achats[mask].index[0]
    ancien_montant = st.session_state.df_achats.loc[idx, 'montant_fcfa']
    client_id = st.session_state.df_achats.loc[idx, 'client_id']
    
    st.session_state.df_achats.loc[idx, 'produits'] = ', '.join(nouveaux_produits)
    st.session_state.df_achats.loc[idx, 'montant_fcfa'] = nouveau_montant
    st.session_state.df_achats.loc[idx, 'nb_articles'] = len(nouveaux_produits)
    st.session_state.df_achats.loc[idx, 'statut'] = 'Modifié'
    
    sauvegarder_achats(st.session_state.df_achats)
    
    idx_client = st.session_state.df_clients[st.session_state.df_clients['client_id'] == client_id].index
    if len(idx_client) > 0:
        st.session_state.df_clients.loc[idx_client[0], 'ca_total_fcfa'] += (nouveau_montant - ancien_montant)
        sauvegarder_clients(st.session_state.df_clients)
    
    return True

def supprimer_commande(order_id):
    mask = st.session_state.df_achats['order_id'] == order_id
    if not mask.any():
        return False
    
    idx = st.session_state.df_achats[mask].index[0]
    client_id = st.session_state.df_achats.loc[idx, 'client_id']
    montant = st.session_state.df_achats.loc[idx, 'montant_fcfa']
    
    st.session_state.df_achats = st.session_state.df_achats.drop(idx).reset_index(drop=True)
    sauvegarder_achats(st.session_state.df_achats)
    
    idx_client = st.session_state.df_clients[st.session_state.df_clients['client_id'] == client_id].index
    if len(idx_client) > 0:
        st.session_state.df_clients.loc[idx_client[0], 'ca_total_fcfa'] -= montant
        st.session_state.df_clients.loc[idx_client[0], 'nb_achats'] -= 1
        sauvegarder_clients(st.session_state.df_clients)
    
    return True

# ==================== FONCTION ACP ====================
def analyser_acp(df):
    """Analyse en composantes principales pour la réduction de dimension"""
    features = ['âge', 'revenu_annuel_fcfa', 'ca_total_fcfa', 'nb_achats']
    df_acp = df[features].dropna()
    
    if len(df_acp) < 3:
        return None, None, None
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_acp)
    
    pca = PCA()
    pca_result = pca.fit_transform(X_scaled)
    
    var_individuelle = pca.explained_variance_ratio_
    var_cumulee = np.cumsum(var_individuelle)
    
    return pca, pca_result, {'individuelle': var_individuelle, 'cumulee': var_cumulee, 'features': features}

# ==================== FONCTION CLASSIFICATION ====================
def classifier_clients(df):
    """Classification supervisée - Prédire le type de client"""
    if len(df) < 5:
        return None, None, None, None
    
    # Créer la cible (Premium vs Standard)
    seuil = df['ca_total_fcfa'].median()
    df['type_client'] = ['Premium' if x > seuil else 'Standard' for x in df['ca_total_fcfa']]
    
    features = ['âge', 'revenu_annuel_fcfa', 'nb_achats']
    X = df[features].dropna()
    y = df.loc[X.index, 'type_client']
    
    if len(X) < 5:
        return None, None, None, None
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    if len(X_train) == 0 or len(X_test) == 0:
        return None, None, None, None
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    return clf, X_test, y_test, features

# ==================== HEADER ====================
st.markdown("""
<div class="main-header">
    <h1>🛍️ ShopAnalyzer Pro</h1>
    <p>Plateforme intelligente de collecte et d'analyse de données e-commerce</p>
    <div style="margin-top: 1rem;">
        <span class="badge-momo">📱 Mobile Money</span>
        <span class="badge-edit">✏️ Modification</span>
        <span class="badge-delete">🗑️ Suppression</span>
        <span class="badge-ml">🧠 ACP + Classification</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### 👩‍💻 **Armelle's Dashboard**")
    st.markdown("---")
    
    total_ventes = st.session_state.df_achats['montant_fcfa'].sum() if len(st.session_state.df_achats) > 0 else 0
    nb_commandes = len(st.session_state.df_achats)
    nb_clients = len(st.session_state.df_clients)
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); padding: 1rem; border-radius: 15px; margin: 0.5rem 0;'>
        <div style='font-size: 0.8rem; color: #666;'>💰 CHIFFRE D'AFFAIRES</div>
        <div style='font-size: 1.5rem; font-weight: 800; color: #667eea;'>{format_fcfa(total_ventes)}</div>
        <hr>
        <div style='font-size: 0.8rem; color: #666;'>📦 COMMANDES</div>
        <div style='font-size: 1.5rem; font-weight: 800; color: #667eea;'>{nb_commandes}</div>
        <hr>
        <div style='font-size: 0.8rem; color: #666;'>👥 CLIENTS</div>
        <div style='font-size: 1.5rem; font-weight: 800; color: #667eea;'>{nb_clients}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="mobile-money-card">
        📱 <strong>Mobile Money</strong><br>
        <small>Paiement instantané<br>MTN, Orange, Camtel</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 📋 **Clients enregistrés**")
    if len(st.session_state.df_clients) > 0:
        for _, client in st.session_state.df_clients.head(5).iterrows():
            st.markdown(f"""
            <div style='background: #f8f9fa; padding: 0.5rem; border-radius: 10px; margin: 0.3rem 0;'>
                <div>{client['avatar']} <strong>{client['nom']}</strong></div>
                <div style='font-size: 0.7rem; color: #666;'>{client['ville']}</div>
            </div>
            """, unsafe_allow_html=True)
        if len(st.session_state.df_clients) > 5:
            st.caption(f"... et {len(st.session_state.df_clients)-5} autres clients")
    else:
        st.caption("Aucun client enregistré")
    
    st.markdown("---")
    st.caption("© 2024 ShopAnalyzer Pro by Armelle")

# ==================== MENU PRINCIPAL ====================
menu = st.sidebar.radio(
    "Navigation",
    ["🛒 Nouvel Achat", "📊 Dashboard", "📈 Régression", "🎯 Classification", "🔍 Clustering", "📉 ACP", "📋 Mes Commandes", "👤 Liste Clients"],
    index=0
)

# ==================== PAGE 1: NOUVEL ACHAT ====================
if menu == "🛒 Nouvel Achat":
    st.markdown("## 🛒 **Nouvelle commande**")
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
                    client_options = {f"{row['nom']} ({row['ville']})": row['client_id'] 
                                     for _, row in st.session_state.df_clients.iterrows()}
                    selected_client_name = st.selectbox("Sélectionnez votre compte", list(client_options.keys()))
                    client_id = client_options[selected_client_name]
                    client_info = st.session_state.df_clients[st.session_state.df_clients['client_id'] == client_id].iloc[0]
                    st.success(f"👋 Bon retour {client_info['avatar']} {client_info['nom']} !")
                    client_nom = client_info['nom']
                    
                    st.info(f"💰 Revenu actuel : {format_fcfa(client_info['revenu_annuel_fcfa'])}")
                    
                    modifier_revenu = st.checkbox("Modifier mon revenu")
                    if modifier_revenu:
                        nouveau_revenu = st.number_input("Nouveau revenu (FCFA)", 
                                                         50000, 100000000, 
                                                         int(client_info['revenu_annuel_fcfa']), 
                                                         step=50000)
                        if nouveau_revenu != client_info['revenu_annuel_fcfa']:
                            idx = st.session_state.df_clients[st.session_state.df_clients['client_id'] == client_id].index
                            if len(idx) > 0:
                                st.session_state.df_clients.loc[idx[0], 'revenu_annuel_fcfa'] = nouveau_revenu
                                sauvegarder_clients(st.session_state.df_clients)
                                st.success("✅ Revenu mis à jour !")
                                st.rerun()
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
                                                    step=50000)
        
        with col2:
            st.markdown("### 📦 **Catalogue produits**")
            st.caption(f"📌 {len(PRODUITS)} produits disponibles")
            
            produits_selectionnes = []
            montant_total = 0
            
            tab1, tab2, tab3, tab4 = st.tabs(["📱 Électronique", "👕 Mode", "🏠 Maison", "⚽ Sports"])
            
            with tab1:
                produits_cat = [(nom, info) for nom, info in PRODUITS.items() if info['categorie'] == 'Électronique']
                cols = st.columns(2)
                for i, (produit, info) in enumerate(produits_cat):
                    with cols[i % 2]:
                        st.markdown(f"""
                        <div class="product-card">
                            <strong>{produit}</strong><br>
                            <small style="color:#666;">{info['desc']}</small><br>
                            <span style="color:#FF6600; font-weight:bold;">{format_fcfa(info['prix'])}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        quantite = st.number_input("Qté", min_value=0, max_value=10, key=f"elec_{produit}", label_visibility="collapsed")
                        if quantite > 0:
                            produits_selectionnes.extend([produit] * quantite)
                            montant_total += info['prix'] * quantite
            
            with tab2:
                produits_cat = [(nom, info) for nom, info in PRODUITS.items() if info['categorie'] == 'Mode']
                cols = st.columns(2)
                for i, (produit, info) in enumerate(produits_cat):
                    with cols[i % 2]:
                        st.markdown(f"""
                        <div class="product-card">
                            <strong>{produit}</strong><br>
                            <small style="color:#666;">{info['desc']}</small><br>
                            <span style="color:#FF6600; font-weight:bold;">{format_fcfa(info['prix'])}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        quantite = st.number_input("Qté", min_value=0, max_value=10, key=f"mode_{produit}", label_visibility="collapsed")
                        if quantite > 0:
                            produits_selectionnes.extend([produit] * quantite)
                            montant_total += info['prix'] * quantite
            
            with tab3:
                produits_cat = [(nom, info) for nom, info in PRODUITS.items() if info['categorie'] == 'Maison']
                cols = st.columns(2)
                for i, (produit, info) in enumerate(produits_cat):
                    with cols[i % 2]:
                        st.markdown(f"""
                        <div class="product-card">
                            <strong>{produit}</strong><br>
                            <small style="color:#666;">{info['desc']}</small><br>
                            <span style="color:#FF6600; font-weight:bold;">{format_fcfa(info['prix'])}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        quantite = st.number_input("Qté", min_value=0, max_value=10, key=f"maison_{produit}", label_visibility="collapsed")
                        if quantite > 0:
                            produits_selectionnes.extend([produit] * quantite)
                            montant_total += info['prix'] * quantite
            
            with tab4:
                produits_cat = [(nom, info) for nom, info in PRODUITS.items() if info['categorie'] == 'Sports']
                cols = st.columns(2)
                for i, (produit, info) in enumerate(produits_cat):
                    with cols[i % 2]:
                        st.markdown(f"""
                        <div class="product-card">
                            <strong>{produit}</strong><br>
                            <small style="color:#666;">{info['desc']}</small><br>
                            <span style="color:#FF6600; font-weight:bold;">{format_fcfa(info['prix'])}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        quantite = st.number_input("Qté", min_value=0, max_value=10, key=f"sport_{produit}", label_visibility="collapsed")
                        if quantite > 0:
                            produits_selectionnes.extend([produit] * quantite)
                            montant_total += info['prix'] * quantite
            
            st.markdown("---")
            st.markdown("### 💳 **Mode de paiement**")
            
            mode_paiement = st.radio(
                "Choisissez votre moyen de paiement",
                ["📱 Mobile Money (MTN/Orange/Camtel)", "💳 Carte bancaire", "🚚 Paiement à la livraison"]
            )
            
            phone_number = None
            if "Mobile Money" in mode_paiement:
                col_op, col_phone = st.columns(2)
                with col_op:
                    operateur = st.selectbox("Opérateur", ["MTN", "Orange", "Camtel", "Express Union"])
                with col_phone:
                    phone_number = st.text_input("Numéro de téléphone", placeholder="6X XX XX XX XX")
            
            total_color = "#FF6600" if "Mobile Money" in mode_paiement else "#667eea"
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, {total_color} 0%, {total_color}cc 100%); 
                        padding: 1rem; border-radius: 15px; color: white; text-align: center; margin-top: 1rem;'>
                <div style='font-size: 0.8rem;'>💰 TOTAL À PAYER</div>
                <div style='font-size: 2rem; font-weight: 800;'>{format_fcfa(montant_total)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        submitted = st.form_submit_button("✅ Confirmer la commande", use_container_width=True)
        
        if submitted:
            if montant_total == 0:
                st.error("❌ Veuillez sélectionner au moins un produit")
            elif option_client == "✨ Nouveau client" and (not client_nom or not email):
                st.error("❌ Veuillez remplir vos informations")
            elif "Mobile Money" in mode_paiement and not phone_number:
                st.error("❌ Veuillez saisir votre numéro de téléphone")
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
                    
                    order_id = enregistrer_achat(client_id, client_nom, produits_selectionnes, montant_total, mode_paiement, phone_number)
                    st.balloons()
                    st.success(f"🎉 Commande #{order_id} confirmée ! Merci {client_nom}")

# ==================== PAGE 2: DASHBOARD ====================
elif menu == "📊 Dashboard":
    st.markdown("## 📊 **Tableau de bord**")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_ventes = st.session_state.df_achats['montant_fcfa'].sum() if len(st.session_state.df_achats) > 0 else 0
    nb_commandes = len(st.session_state.df_achats)
    nb_clients_actifs = len(st.session_state.df_clients[st.session_state.df_clients['nb_achats'] > 0]) if len(st.session_state.df_clients) > 0 else 0
    panier_moyen = total_ventes / nb_commandes if nb_commandes > 0 else 0
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2rem;">💰</div>
            <div style="font-size: 1.5rem; font-weight: bold;">{format_fcfa(total_ventes)}</div>
            <div>CHIFFRE D'AFFAIRES</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2rem;">📦</div>
            <div style="font-size: 1.5rem; font-weight: bold;">{nb_commandes}</div>
            <div>COMMANDES</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2rem;">👥</div>
            <div style="font-size: 1.5rem; font-weight: bold;">{nb_clients_actifs}</div>
            <div>CLIENTS ACTIFS</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2rem;">🛒</div>
            <div style="font-size: 1.5rem; font-weight: bold;">{format_fcfa(panier_moyen)}</div>
            <div>PANIER MOYEN</div>
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
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            paiements = st.session_state.df_achats['mode_paiement'].value_counts()
            if len(paiements) > 0:
                fig = px.pie(values=paiements.values, names=paiements.index,
                            title="💳 Répartition des paiements",
                            color_discrete_sequence=['#FF6600', '#4CAF50', '#2196F3'])
                st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE 3: RÉGRESSION ====================
elif menu == "📈 Régression":
    st.markdown("## 📈 **Régression - Prédiction du CA**")
    st.markdown("---")
    
    df_ml = st.session_state.df_clients[st.session_state.df_clients['nb_achats'] > 0].copy()
    
    if len(df_ml) >= 5:
        st.subheader("📊 Régression linéaire multiple")
        
        X = df_ml[['âge', 'revenu_annuel_fcfa']]
        y = df_ml['ca_total_fcfa']
        
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
    else:
        st.info(f"📊 Besoin d'au moins 5 clients. Actuellement : {len(df_ml)} clients")

# ==================== PAGE 4: CLASSIFICATION SUPERVISÉE ====================
elif menu == "🎯 Classification":
    st.markdown("## 🎯 **Classification supervisée**")
    st.markdown("*Prédire si un client est Premium ou Standard*")
    st.markdown("---")
    
    df_ml = st.session_state.df_clients[st.session_state.df_clients['nb_achats'] > 0].copy()
    
    if len(df_ml) >= 5:
        clf, X_test, y_test, features = classifier_clients(df_ml)
        
        if clf is not None:
            y_pred = clf.predict(X_test)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Performance du modèle")
                st.text(classification_report(y_test, y_pred))
                
                cm = confusion_matrix(y_test, y_pred)
                fig = px.imshow(cm, text_auto=True, 
                               labels=dict(x="Prédit", y="Réel", color="Nombre"),
                               title="Matrice de confusion",
                               x=clf.classes_, y=clf.classes_)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("🔑 Importance des variables")
                importance_df = pd.DataFrame({
                    'Variable': ['Âge', 'Revenu', 'Nb achats'],
                    'Importance': clf.feature_importances_
                }).sort_values('Importance', ascending=True)
                
                fig = px.bar(importance_df, x='Importance', y='Variable', 
                            orientation='h', title="Variables déterminantes")
                st.plotly_chart(fig, use_container_width=True)
            
            # Prédiction interactive
            st.subheader("🔮 Prédiction en temps réel")
            col1, col2, col3 = st.columns(3)
            with col1:
                age_pred = st.slider("Âge", 18, 70, 35)
            with col2:
                revenu_pred = st.number_input("Revenu (FCFA)", 500000, 10000000, 2500000, step=100000)
            with col3:
                nb_achats_pred = st.slider("Nombre d'achats", 0, 20, 3)
            
            if st.button("🎯 Prédire le type de client"):
                input_data = pd.DataFrame([[age_pred, revenu_pred, nb_achats_pred]], 
                                          columns=['âge', 'revenu_annuel_fcfa', 'nb_achats'])
                prediction = clf.predict(input_data)[0]
                proba = clf.predict_proba(input_data)[0]
                
                if prediction == 'Premium':
                    st.success(f"🏆 Client **PREMIUM** avec {proba.max():.1%} de probabilité")
                    st.balloons()
                else:
                    st.info(f"📌 Client **STANDARD** avec {proba.max():.1%} de probabilité")
        else:
            st.info("📊 Pas assez de données pour la classification")
    else:
        st.info(f"📊 Besoin d'au moins 5 clients. Actuellement : {len(df_ml)} clients")

# ==================== PAGE 5: CLUSTERING ====================
elif menu == "🔍 Clustering":
    st.markdown("## 🔍 **Clustering - Segmentation clients**")
    st.markdown("---")
    
    df_ml = st.session_state.df_clients[st.session_state.df_clients['nb_achats'] > 0].copy()
    
    if len(df_ml) >= 5:
        features = df_ml[['âge', 'ca_total_fcfa', 'nb_achats']]
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        n_clusters = min(3, len(df_ml))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df_ml['segment'] = kmeans.fit_predict(features_scaled)
        
        sil_score = silhouette_score(features_scaled, df_ml['segment'])
        st.metric("📊 Silhouette Score", f"{sil_score:.2%}")
        
        fig = px.scatter(df_ml, x='ca_total_fcfa', y='nb_achats', 
                        color='segment', size='âge',
                        title="Segmentation clients",
                        labels={'ca_total_fcfa':'CA (FCFA)', 'nb_achats':'Nb achats'},
                        hover_data=['nom'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Profils des segments
        st.subheader("📝 Profil des segments")
        for segment in sorted(df_ml['segment'].unique()):
            seg_data = df_ml[df_ml['segment'] == segment]
            with st.expander(f"🎯 Segment {segment} - {len(seg_data)} clients"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Âge moyen", f"{seg_data['âge'].mean():.0f} ans")
                with col2:
                    st.metric("CA moyen", format_fcfa(seg_data['ca_total_fcfa'].mean()))
                with col3:
                    st.metric("Nb achats moyen", f"{seg_data['nb_achats'].mean():.1f}")
    else:
        st.info(f"📊 Besoin d'au moins 5 clients. Actuellement : {len(df_ml)} clients")

# ==================== PAGE 6: ACP ====================
elif menu == "📉 ACP":
    st.markdown("## 📉 **ACP - Réduction de dimensionnalité**")
    st.markdown("*Analyse en Composantes Principales*")
    st.markdown("---")
    
    df_acp = st.session_state.df_clients[st.session_state.df_clients['nb_achats'] > 0].copy()
    
    if len(df_acp) >= 5:
        resultat = analyser_acp(df_acp)
        
        if resultat[0] is not None:
            pca, pca_result, info = resultat
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Variance expliquée")
                var_df = pd.DataFrame({
                    'Composante': [f'PC{i+1}' for i in range(len(info['individuelle']))],
                    'Variance individuelle': info['individuelle'],
                    'Variance cumulée': info['cumulee']
                })
                
                fig = go.Figure()
                fig.add_trace(go.Bar(x=var_df['Composante'], y=var_df['Variance individuelle'],
                                    name='Variance individuelle', marker_color='#FF6600'))
                fig.add_trace(go.Scatter(x=var_df['Composante'], y=var_df['Variance cumulée'],
                                        name='Variance cumulée', yaxis='y2', line=dict(color='#667eea', width=3)))
                fig.update_layout(title="Variance expliquée par composante",
                                 yaxis2=dict(title='Cumulé', overlaying='y', side='right'))
                st.plotly_chart(fig, use_container_width=True)
                
                n_opt = np.argmax(info['cumulee'] >= 0.95) + 1
                st.success(f"✅ **Recommandation** : Garder {n_opt} composantes principales (variance conservée : {info['cumulee'][n_opt-1]:.1%})")
            
            with col2:
                st.subheader("📈 Projection 2D")
                fig = px.scatter(x=pca_result[:,0], y=pca_result[:,1],
                                title="Projection sur PC1 et PC2",
                                labels={'x':'Première composante (PC1)', 'y':'Deuxième composante (PC2)'})
                st.plotly_chart(fig, use_container_width=True)
            
            # Contribution des variables
            st.subheader("📊 Contribution des variables")
            loadings = pd.DataFrame(pca.components_[:3].T,
                                   columns=['PC1', 'PC2', 'PC3'],
                                   index=info['features'])
            fig = px.imshow(loadings, text_auto='.2f', 
                           title="Contribution des variables aux composantes",
                           color_continuous_scale='RdBu', aspect='auto')
            st.plotly_chart(fig, use_container_width=True)
            
            # Application pratique
            st.subheader("🔧 Réduction de dimension")
            n_components = st.slider("Nombre de composantes à garder", 1, 4, n_opt)
            st.success(f"✅ Dimension réduite de {len(info['features'])} à {n_components}")
            
            # Données réduites
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(df_acp[info['features']])
            pca_reduced = PCA(n_components=n_components)
            X_reduced = pca_reduced.fit_transform(X_scaled)
            reduced_df = pd.DataFrame(X_reduced[:10], columns=[f'PC{i+1}' for i in range(n_components)])
            st.dataframe(reduced_df, use_container_width=True)
        else:
            st.info("📊 Pas assez de données pour l'ACP")
    else:
        st.info(f"📊 Besoin d'au moins 5 clients. Actuellement : {len(df_acp)} clients")

# ==================== PAGE 7: MES COMMANDES ====================
elif menu == "📋 Mes Commandes":
    st.markdown("## 📋 **Mes commandes**")
    st.markdown("---")
    
    if len(st.session_state.df_clients) > 0:
        client_options = {f"{row['nom']} ({row['ville']})": row['client_id'] 
                         for _, row in st.session_state.df_clients.iterrows()}
        selected_client = st.selectbox("👤 Sélectionnez votre compte", list(client_options.keys()))
        client_id = client_options[selected_client]
        
        commandes_client = st.session_state.df_achats[st.session_state.df_achats['client_id'] == client_id]
        
        if len(commandes_client) > 0:
            for _, commande in commandes_client.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="order-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>📦 Commande #{int(commande['order_id'])}</strong>
                                <span style="margin-left: 1rem; font-size: 0.8rem;">{commande['date']}</span>
                            </div>
                            <span style="background: #28a745; color: white; padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.7rem;">{commande['statut']}</span>
                        </div>
                        <div style="margin-top: 0.5rem;">
                            <strong>Produits:</strong> {commande['produits']}<br>
                            <strong>Total:</strong> {format_fcfa(commande['montant_fcfa'])}<br>
                            <strong>Paiement:</strong> {commande['mode_paiement']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✏️ Modifier", key=f"edit_{int(commande['order_id'])}"):
                            st.session_state.edit_order_id = int(commande['order_id'])
                            st.rerun()
                    with col2:
                        if st.button(f"🗑️ Supprimer", key=f"delete_{int(commande['order_id'])}"):
                            if supprimer_commande(int(commande['order_id'])):
                                st.success(f"✅ Commande supprimée !")
                                st.rerun()
        else:
            st.info("📭 Vous n'avez pas encore de commandes")
    
    # Formulaire de modification
    if st.session_state.edit_order_id is not None:
        st.markdown("---")
        st.markdown("## ✏️ **Modifier ma commande**")
        
        commande_to_edit = st.session_state.df_achats[st.session_state.df_achats['order_id'] == st.session_state.edit_order_id]
        if len(commande_to_edit) > 0:
            commande = commande_to_edit.iloc[0]
            produits_actuels = commande['produits'].split(', ') if commande['produits'] else []
            
            with st.form("edit_form"):
                produits_modifies = []
                nouveau_montant = 0
                
                for categorie in ['Électronique', 'Mode', 'Maison', 'Sports']:
                    produits_cat = [(nom, info) for nom, info in PRODUITS.items() if info['categorie'] == categorie]
                    with st.expander(f"📂 {categorie}"):
                        for produit, info in produits_cat:
                            quantite_defaut = produits_actuels.count(produit) if produit in produits_actuels else 0
                            quantite = st.number_input(
                                f"{produit} - {format_fcfa(info['prix'])}",
                                min_value=0, max_value=10, value=quantite_defaut,
                                key=f"edit_{categorie}_{produit}"
                            )
                            if quantite > 0:
                                produits_modifies.extend([produit] * quantite)
                                nouveau_montant += info['prix'] * quantite
                
                st.markdown(f"""
                <div style='background: #2196F3; padding: 1rem; border-radius: 15px; text-align: center;'>
                    <div style='color: white;'>💰 NOUVEAU TOTAL</div>
                    <div style='font-size: 1.5rem; font-weight: bold; color: white;'>{format_fcfa(nouveau_montant)}</div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Enregistrer", use_container_width=True):
                        if modifier_commande(st.session_state.edit_order_id, produits_modifies, nouveau_montant):
                            st.success("✅ Commande modifiée !")
                            st.session_state.edit_order_id = None
                            st.rerun()
                with col2:
                    if st.form_submit_button("❌ Annuler", use_container_width=True):
                        st.session_state.edit_order_id = None
                        st.rerun()

# ==================== PAGE 8: LISTE CLIENTS ====================
else:
    st.markdown("## 👤 **Liste des clients**")
    st.markdown("---")
    
    if len(st.session_state.df_clients) > 0:
        df_display = st.session_state.df_clients.copy()
        df_display['revenu_annuel_fcfa'] = df_display['revenu_annuel_fcfa'].apply(format_fcfa)
        df_display['ca_total_fcfa'] = df_display['ca_total_fcfa'].apply(format_fcfa)
        st.dataframe(df_display[['client_id', 'nom', 'email', 'âge', 'ville', 'revenu_annuel_fcfa', 
                                 'ca_total_fcfa', 'nb_achats', 'dernier_achat']], 
                     use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total clients", len(st.session_state.df_clients))
        with col2:
            st.metric("Villes représentées", st.session_state.df_clients['ville'].nunique())
        with col3:
            st.metric("Âge moyen", f"{st.session_state.df_clients['âge'].mean():.0f} ans")
        
        csv_clients = st.session_state.df_clients.to_csv(index=False)
        st.download_button("📥 Exporter les clients (CSV)", csv_clients, "clients.csv", "text/csv")
    else:
        st.info("📭 Aucun client enregistré")

# ==================== FOOTER ====================
st.markdown("""
<div class="footer">
    <p>🛍️ <strong>ShopAnalyzer Pro</strong> - Réalisé par <strong>Armelle</strong></p>
    <p>💰 Francs CFA (FCFA) | 📱 Mobile Money disponible | ✏️ Modification/Suppression commandes</p>
    <p>🧠 ACP + Classification supervisée + Clustering + Régression | 👥 Base clients intégrée</p>
</div>
""", unsafe_allow_html=True)
