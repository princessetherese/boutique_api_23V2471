# app_supabase_final.py - Version avec 40 produits et modification des commandes
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
import time
import warnings
warnings.filterwarnings('ignore')

# ==================== CONNEXION SUPABASE ====================
def init_supabase():
    """Initialise la connexion Supabase"""
    try:
        SUPABASE_URL = st.secrets["SUPABASE_URL"]
        SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Erreur de connexion à Supabase : {e}")
        return None

supabase = init_supabase()

# ==================== FONCTION DE CONVERSION POUR JSON ====================
def convertir_pour_json(valeur):
    """Convertit les types numpy en types Python standards pour JSON"""
    if isinstance(valeur, (np.int64, np.int32)):
        return int(valeur)
    elif isinstance(valeur, (np.float64, np.float32)):
        return float(valeur)
    elif isinstance(valeur, np.ndarray):
        return valeur.tolist()
    elif hasattr(valeur, 'item'):
        return valeur.item()
    elif pd.isna(valeur):
        return None
    else:
        return valeur

# ==================== FONCTIONS BASE DE DONNÉES CORRIGÉES ====================
def charger_clients():
    """Charge les clients depuis Supabase"""
    if supabase is None:
        return pd.DataFrame()
    try:
        response = supabase.table("clients").select("*").execute()
        if response.data:
            return pd.DataFrame(response.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur chargement clients : {e}")
        return pd.DataFrame()

def sauvegarder_client(client):
    """Sauvegarde un nouveau client dans Supabase"""
    if supabase is None:
        return None
    try:
        client_clean = {k: convertir_pour_json(v) for k, v in client.items()}
        response = supabase.table("clients").insert(client_clean).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Erreur sauvegarde client : {e}")
        return None

def mettre_a_jour_client(client_id, data):
    """Met à jour un client existant"""
    if supabase is None:
        return False
    try:
        data_clean = {k: convertir_pour_json(v) for k, v in data.items()}
        supabase.table("clients").update(data_clean).eq("client_id", client_id).execute()
        return True
    except Exception as e:
        st.error(f"Erreur mise à jour client : {e}")
        return False

def charger_achats():
    """Charge les achats depuis Supabase"""
    if supabase is None:
        return pd.DataFrame()
    try:
        response = supabase.table("achats").select("*").order("order_id", desc=True).execute()
        if response.data:
            return pd.DataFrame(response.data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur chargement achats : {e}")
        return pd.DataFrame()

def sauvegarder_achat(achat):
    """Sauvegarde un nouvel achat dans Supabase"""
    if supabase is None:
        return None
    try:
        achat_clean = {k: convertir_pour_json(v) for k, v in achat.items()}
        response = supabase.table("achats").insert(achat_clean).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Erreur sauvegarde achat : {e}")
        return None

def mettre_a_jour_achat(order_id, data):
    """Met à jour un achat existant"""
    if supabase is None:
        return False
    try:
        data_clean = {k: convertir_pour_json(v) for k, v in data.items()}
        supabase.table("achats").update(data_clean).eq("order_id", order_id).execute()
        return True
    except Exception as e:
        st.error(f"Erreur mise à jour achat : {e}")
        return False

def supprimer_achat(order_id):
    """Supprime un achat"""
    if supabase is None:
        return False
    try:
        supabase.table("achats").delete().eq("order_id", order_id).execute()
        return True
    except Exception as e:
        st.error(f"Erreur suppression achat : {e}")
        return False

# ==================== CHARGEMENT INITIAL ====================
if 'df_clients' not in st.session_state:
    st.session_state.df_clients = charger_clients()

if 'df_achats' not in st.session_state:
    st.session_state.df_achats = charger_achats()
    
if 'edit_order_id' not in st.session_state:
    st.session_state.edit_order_id = None

# ==================== CATALOGUE PRODUITS - 10 PRODUITS PAR CATÉGORIE ====================
PRODUITS = {
    # ÉLECTRONIQUE (10 produits)
    '📱 Smartphone Tecno Camon 20 Pro': {'prix': 150000, 'categorie': 'Électronique', 'desc': '8Go RAM, 128Go stockage'},
    '📱 iPhone 14 Pro Max': {'prix': 850000, 'categorie': 'Électronique', 'desc': 'Apple A16, 256Go'},
    '📱 Samsung Galaxy S23 Ultra': {'prix': 750000, 'categorie': 'Électronique', 'desc': '12Go RAM, 256Go'},
    '📱 Xiaomi Redmi Note 12': {'prix': 180000, 'categorie': 'Électronique', 'desc': '6Go RAM, 128Go'},
    '💻 PC Portable HP Pavilion': {'prix': 450000, 'categorie': 'Électronique', 'desc': 'Core i7, 16Go RAM'},
    '💻 PC Dell XPS 13': {'prix': 800000, 'categorie': 'Électronique', 'desc': 'Core i9, 32Go RAM'},
    '💻 PC Lenovo ThinkPad': {'prix': 550000, 'categorie': 'Électronique', 'desc': 'Core i5, 8Go RAM'},
    '🎧 Casque Sony WH-1000XM5': {'prix': 120000, 'categorie': 'Électronique', 'desc': 'Réduction de bruit'},
    '⌚ Apple Watch Series 8': {'prix': 250000, 'categorie': 'Électronique', 'desc': 'GPS + Cellular'},
    '🔊 Enceinte JBL Charge 5': {'prix': 85000, 'categorie': 'Électronique', 'desc': 'Bluetooth, 20W'},
    
    # MODE (10 produits)
    '👕 T-shirt Lacoste Homme': {'prix': 25000, 'categorie': 'Mode', 'desc': '100% coton, taille S-XXL'},
    '👕 Chemise Hugo Boss': {'prix': 65000, 'categorie': 'Mode', 'desc': 'Luxe, coupe slim'},
    '👖 Jean Levi\'s 501': {'prix': 45000, 'categorie': 'Mode', 'desc': 'Jean brut original'},
    '👗 Robe Zara Collection': {'prix': 35000, 'categorie': 'Mode', 'desc': 'Soirée, longue'},
    '👟 Basket Nike Air Max': {'prix': 85000, 'categorie': 'Mode', 'desc': 'Confort, style sport'},
    '👟 Basket Adidas Ultraboost': {'prix': 95000, 'categorie': 'Mode', 'desc': 'Running léger'},
    '🧥 Manteau Ralph Lauren': {'prix': 120000, 'categorie': 'Mode', 'desc': 'Hiver, doudoune'},
    '🧣 Écharpe Burberry': {'prix': 55000, 'categorie': 'Mode', 'desc': 'Cachemire luxe'},
    '👔 Costume Armani': {'prix': 250000, 'categorie': 'Mode', 'desc': 'Tailleur 3 pièces'},
    '🕶️ Lunettes Ray-Ban': {'prix': 75000, 'categorie': 'Mode', 'desc': 'Solaire, classique'},
    
    # MAISON (10 produits)
    '🛋️ Canapé convertible 3 places': {'prix': 350000, 'categorie': 'Maison', 'desc': 'Cuir, noir'},
    '🛏️ Lit King Size': {'prix': 280000, 'categorie': 'Maison', 'desc': 'Avec sommier et matelas'},
    '🚪 Armoire 5 portes': {'prix': 250000, 'categorie': 'Maison', 'desc': 'Chêne massif'},
    '🍽️ Table à manger extensible': {'prix': 180000, 'categorie': 'Maison', 'desc': '6-8 places, bois'},
    '💡 Lampe sur pied design': {'prix': 45000, 'categorie': 'Maison', 'desc': 'LED, moderne'},
    '🪑 Lot de 6 chaises': {'prix': 120000, 'categorie': 'Maison', 'desc': 'Moderne, confortables'},
    '📺 Téléviseur Samsung 65"': {'prix': 500000, 'categorie': 'Maison', 'desc': '4K Ultra HD Smart TV'},
    '❄️ Réfrigérateur Samsung': {'prix': 400000, 'categorie': 'Maison', 'desc': '520L, No Frost'},
    '🧺 Machine à laver LG': {'prix': 300000, 'categorie': 'Maison', 'desc': '9kg, Silencieuse'},
    '🍳 Four micro-ondes Samsung': {'prix': 85000, 'categorie': 'Maison', 'desc': 'Grill, 25L'},
    
    # SPORTS (10 produits)
    '⚽ Ballon de football officiel': {'prix': 15000, 'categorie': 'Sports', 'desc': 'Taille 5, FIFA Quality'},
    '🏀 Ballon de basketball NBA': {'prix': 20000, 'categorie': 'Sports', 'desc': 'Taille 7, cuir synthétique'},
    '🎾 Raquette de tennis Babolat': {'prix': 65000, 'categorie': 'Sports', 'desc': 'Pro, carbone'},
    '🏋️ Set haltères 20kg': {'prix': 45000, 'categorie': 'Sports', 'desc': 'Avec barre, 2 haltères'},
    '🚴 Vélo de route Triban': {'prix': 250000, 'categorie': 'Sports', 'desc': '21 vitesses, alu'},
    '🏃 Tapis de course électrique': {'prix': 350000, 'categorie': 'Sports', 'desc': 'Moteur 2.5HP, pliable'},
    '🥊 Gants de boxe Everlast': {'prix': 28000, 'categorie': 'Sports', 'desc': 'Cuir, 14oz'},
    '🏊 Lunettes de natation Speedo': {'prix': 12000, 'categorie': 'Sports', 'desc': 'Anti-buée, UV'},
    '🧘 Tapis de yoga premium': {'prix': 18000, 'categorie': 'Sports', 'desc': 'Anti-dérapant, 10mm'},
    '⚽ Maillot PSG domicile': {'prix': 35000, 'categorie': 'Sports', 'desc': 'Officiel, Messi #30'}
}

def format_fcfa(x):
    if pd.isna(x) or x == 0:
        return "0 FCFA"
    return f"{x:,.0f} FCFA".replace(",", " ")

def enregistrer_achat(client_id, client_nom, produits_achetes, montant_total, mode_paiement, phone_number=None):
    """Enregistre un nouvel achat dans Supabase"""
    if len(st.session_state.df_achats) == 0:
        order_id = 1
    else:
        order_id = int(st.session_state.df_achats['order_id'].max()) + 1
    
    nouvel_achat = {
        'order_id': order_id,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'client_id': int(client_id),
        'client_nom': client_nom,
        'produits': ', '.join(produits_achetes),
        'montant_fcfa': int(montant_total),
        'mode_paiement': mode_paiement,
        'nb_articles': len(produits_achetes),
        'telephone': phone_number if phone_number else '',
        'statut': 'Confirmé'
    }
    
    resultat = sauvegarder_achat(nouvel_achat)
    if resultat:
        st.session_state.df_achats = charger_achats()
        
        # Mettre à jour le CA du client
        idx = st.session_state.df_clients[st.session_state.df_clients['client_id'] == client_id].index
        if len(idx) > 0:
            nouveau_ca = int(st.session_state.df_clients.loc[idx[0], 'ca_total_fcfa'] + montant_total)
            nouveau_nb = int(st.session_state.df_clients.loc[idx[0], 'nb_achats'] + 1)
            mettre_a_jour_client(client_id, {
                'ca_total_fcfa': nouveau_ca,
                'nb_achats': nouveau_nb,
                'dernier_achat': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            st.session_state.df_clients = charger_clients()
    
    return order_id

def modifier_commande(order_id, nouveaux_produits, nouveau_montant):
    """Modifie une commande existante"""
    commande = st.session_state.df_achats[st.session_state.df_achats['order_id'] == order_id]
    if len(commande) == 0:
        return False
    
    ancien_montant = int(commande.iloc[0]['montant_fcfa'])
    client_id = int(commande.iloc[0]['client_id'])
    
    mise_a_jour = {
        'produits': ', '.join(nouveaux_produits),
        'montant_fcfa': int(nouveau_montant),
        'nb_articles': len(nouveaux_produits),
        'statut': 'Modifié'
    }
    
    if mettre_a_jour_achat(order_id, mise_a_jour):
        st.session_state.df_achats = charger_achats()
        
        # Mettre à jour le CA du client
        idx = st.session_state.df_clients[st.session_state.df_clients['client_id'] == client_id].index
        if len(idx) > 0:
            nouveau_ca = int(st.session_state.df_clients.loc[idx[0], 'ca_total_fcfa'] + (nouveau_montant - ancien_montant))
            mettre_a_jour_client(client_id, {'ca_total_fcfa': nouveau_ca})
            st.session_state.df_clients = charger_clients()
        
        return True
    return False

def supprimer_commande(order_id):
    """Supprime une commande"""
    commande = st.session_state.df_achats[st.session_state.df_achats['order_id'] == order_id]
    if len(commande) == 0:
        return False
    
    client_id = int(commande.iloc[0]['client_id'])
    montant = int(commande.iloc[0]['montant_fcfa'])
    
    if supprimer_achat(order_id):
        st.session_state.df_achats = charger_achats()
        
        # Mettre à jour le CA du client
        idx = st.session_state.df_clients[st.session_state.df_clients['client_id'] == client_id].index
        if len(idx) > 0:
            nouveau_ca = int(st.session_state.df_clients.loc[idx[0], 'ca_total_fcfa'] - montant)
            nouveau_nb = int(st.session_state.df_clients.loc[idx[0], 'nb_achats'] - 1)
            mettre_a_jour_client(client_id, {
                'ca_total_fcfa': nouveau_ca,
                'nb_achats': nouveau_nb
            })
            st.session_state.df_clients = charger_clients()
        
        return True
    return False

# ==================== CSS ====================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .mobile-money-card {
        background: linear-gradient(135deg, #FF6600 0%, #FF8533 100%);
        padding: 1rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
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
    .footer {
        text-align: center;
        padding: 1.5rem;
        margin-top: 2rem;
        border-top: 1px solid #e9ecef;
        color: #6c757d;
    }
    .order-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ==================== HEADER ====================
st.markdown("""
<div class="main-header">
    <h1>🛍️ ShopAnalyzer Pro</h1>
    <p>Plateforme intelligente de collecte et d'analyse de données e-commerce</p>
    <div style="margin-top: 1rem;">
        <span style="background:#FF6600; padding:0.2rem 0.8rem; border-radius:20px;">📱 Mobile Money</span>
        <span style="background:#2196F3; padding:0.2rem 0.8rem; border-radius:20px;">✏️ Modification</span>
        <span style="background:#dc3545; padding:0.2rem 0.8rem; border-radius:20px;">🗑️ Suppression</span>
        <span style="background:#28a745; padding:0.2rem 0.8rem; border-radius:20px;">🎁 40 Produits</span>
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
    <div style='background: #667eea15; padding: 1rem; border-radius: 15px;'>
        <div>💰 CHIFFRE D'AFFAIRES</div>
        <div style='font-size: 1.5rem; font-weight: bold;'>{format_fcfa(total_ventes)}</div>
        <hr>
        <div>📦 COMMANDES</div>
        <div style='font-size: 1.5rem; font-weight: bold;'>{nb_commandes}</div>
        <hr>
        <div>👥 CLIENTS</div>
        <div style='font-size: 1.5rem; font-weight: bold;'>{nb_clients}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="mobile-money-card">
        📱 <strong>Mobile Money</strong><br>
        <small>Paiement instantané<br>MTN, Orange, Camtel</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.success(f"🎁 **{len(PRODUITS)} produits** disponibles dans 4 catégories")
    st.markdown("---")
    st.caption("© 2024 ShopAnalyzer Pro by Armelle")

# ==================== MENU PRINCIPAL ====================
menu = st.sidebar.radio(
    "Navigation",
    ["🛒 Nouvel Achat", "📊 Dashboard", "📋 Mes Commandes", "👤 Clients"],
    index=0
)

# ==================== PAGE 1: NOUVEL ACHAT ====================
if menu == "🛒 Nouvel Achat":
    st.markdown("## 🛒 **Nouvelle commande**")
    st.caption(f"📦 **{len(PRODUITS)} produits** disponibles - Choisissez vos articles ci-dessous")
    
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
            else:
                col_a, col_b = st.columns(2)
                with col_a:
                    client_nom = st.text_input("Nom complet *", placeholder="Jean Dupont")
                    age = st.number_input("Âge *", 18, 80, 30)
                    ville = st.selectbox("Ville *", ['Douala', 'Yaoundé', 'Garoua', 'Bafoussam', 'Bamenda'])
                with col_b:
                    email = st.text_input("Email *", placeholder="jean@email.com")
                    avatar = st.selectbox("Avatar", ['👨', '👩', '👧', '👴', '👵'])
                    revenu_client = st.number_input("Revenu annuel (FCFA) *", 50000, 100000000, 2500000, step=50000)
        
        with col2:
            st.markdown("### 📦 **Catalogue produits**")
            
            produits_selectionnes = []
            montant_total = 0
            
            # Affichage des 4 catégories avec les 10 produits chacune
            categories = ['Électronique', 'Mode', 'Maison', 'Sports']
            for categorie in categories:
                produits_cat = [(nom, info) for nom, info in PRODUITS.items() if info['categorie'] == categorie]
                with st.expander(f"📂 {categorie} - {len(produits_cat)} produits", expanded=(categorie == 'Électronique')):
                    # Affichage en 2 colonnes pour mieux utiliser l'espace
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
                            quantite = st.number_input("Qté", min_value=0, max_value=10, key=f"{categorie}_{produit}", label_visibility="collapsed")
                            if quantite > 0:
                                produits_selectionnes.extend([produit] * quantite)
                                montant_total += info['prix'] * quantite
            
            st.markdown("---")
            st.markdown("### 💳 **Mode de paiement**")
            
            mode_paiement = st.radio(
                "Choisissez votre moyen de paiement",
                ["💳 Carte bancaire", "🚚 Livraison", "📱 Mobile Money (MTN/Orange/Camtel)"],
                index=2
            )
            
            phone_number = None
            if "Mobile Money" in mode_paiement:
                phone_number = st.text_input("📱 Numéro de téléphone Mobile Money", 
                                            placeholder="6X XX XX XX XX",
                                            help="Obligatoire pour le paiement Mobile Money")
                if phone_number:
                    st.success(f"✅ Paiement avec Mobile Money au {phone_number}")
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #FF6600 0%, #FF8533 100%); 
                        padding: 1rem; border-radius: 15px; text-align: center;'>
                <div style='color: white;'>💰 TOTAL À PAYER</div>
                <div style='font-size: 2rem; font-weight: bold; color: white;'>{format_fcfa(montant_total)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        submitted = st.form_submit_button("✅ Confirmer la commande", use_container_width=True)
        
        if submitted:
            if montant_total == 0:
                st.error("❌ Sélectionnez au moins un produit")
            elif option_client == "✨ Nouveau client" and (not client_nom or not email):
                st.error("❌ Remplissez vos informations")
            elif "Mobile Money" in mode_paiement and not phone_number:
                st.error("❌ Veuillez saisir votre numéro de téléphone pour le paiement Mobile Money")
            else:
                with st.spinner("Traitement en cours..."):
                    time.sleep(0.5)
                    
                    if option_client == "✨ Nouveau client":
                        nouveau_client = {
                            'nom': client_nom,
                            'email': email,
                            'age': int(age),
                            'ville': ville,
                            'avatar': avatar,
                            'revenu_annuel_fcfa': int(revenu_client),
                            'ca_total_fcfa': 0,
                            'nb_achats': 0,
                            'dernier_achat': ''
                        }
                        resultat = sauvegarder_client(nouveau_client)
                        if resultat:
                            st.session_state.df_clients = charger_clients()
                            client_id = resultat['client_id']
                            st.success("✅ Compte créé !")
                        else:
                            st.error("❌ Erreur création compte")
                            st.stop()
                    
                    order_id = enregistrer_achat(client_id, client_nom, produits_selectionnes, montant_total, mode_paiement, phone_number)
                    st.balloons()
                    st.success(f"🎉 Commande #{order_id} confirmée !")
                    st.info("💡 Vous pouvez modifier ou supprimer cette commande dans l'onglet 'Mes Commandes'")

# ==================== PAGE 2: DASHBOARD ====================
elif menu == "📊 Dashboard":
    st.markdown("## 📊 **Tableau de bord**")
    
    if len(st.session_state.df_clients) == 0:
        st.info("📊 Pas encore de données. Commencez par passer des commandes !")
    else:
        col1, col2, col3, col4 = st.columns(4)
        
        total_ventes = st.session_state.df_achats['montant_fcfa'].sum() if len(st.session_state.df_achats) > 0 else 0
        nb_commandes = len(st.session_state.df_achats)
        nb_clients_actifs = len(st.session_state.df_clients[st.session_state.df_clients['nb_achats'] > 0])
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
            df_ventes = st.session_state.df_achats.copy()
            df_ventes['date'] = pd.to_datetime(df_ventes['date'])
            ventes_par_jour = df_ventes.groupby(df_ventes['date'].dt.date)['montant_fcfa'].sum().reset_index()
            
            fig = px.line(ventes_par_jour, x='date', y='montant_fcfa', title="📈 Évolution des ventes")
            st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE 3: MES COMMANDES (AVEC MODIFICATION) ====================
elif menu == "📋 Mes Commandes":
    st.markdown("## 📋 **Mes commandes**")
    
    if len(st.session_state.df_clients) == 0:
        st.info("📭 Aucun client enregistré")
    else:
        client_options = {f"{row['nom']} ({row['ville']})": row['client_id'] 
                         for _, row in st.session_state.df_clients.iterrows()}
        selected_client = st.selectbox("👤 Sélectionnez votre compte", list(client_options.keys()))
        client_id = client_options[selected_client]
        
        commandes_client = st.session_state.df_achats[st.session_state.df_achats['client_id'] == client_id]
        
        if len(commandes_client) == 0:
            st.info("📭 Vous n'avez pas encore de commandes")
        else:
            for _, commande in commandes_client.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="order-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>📦 Commande #{int(commande['order_id'])}</strong>
                                <span style="margin-left: 1rem; font-size: 0.8rem;">{commande['date']}</span>
                            </div>
                            <span style="background: {'#28a745' if commande['statut'] == 'Confirmé' else '#ffc107'}; 
                                         color: {'white' if commande['statut'] == 'Confirmé' else 'black'}; 
                                         padding: 0.2rem 0.5rem; border-radius: 10px; font-size: 0.7rem;">
                                {commande['statut']}
                            </span>
                        </div>
                        <div style="margin-top: 0.5rem;">
                            <strong>Produits:</strong> {commande['produits']}<br>
                            <strong>Articles:</strong> {int(commande['nb_articles'])}<br>
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
                                st.success("✅ Commande supprimée !")
                                st.rerun()
        
        # Formulaire de modification
        if st.session_state.edit_order_id is not None:
            st.markdown("---")
            st.markdown("## ✏️ **Modifier ma commande**")
            
            commande_to_edit = st.session_state.df_achats[st.session_state.df_achats['order_id'] == st.session_state.edit_order_id]
            if len(commande_to_edit) > 0:
                commande = commande_to_edit.iloc[0]
                produits_actuels = commande['produits'].split(', ') if commande['produits'] else []
                
                with st.form("edit_form"):
                    st.subheader("📦 Modifier les produits")
                    
                    produits_modifies = []
                    nouveau_montant = 0
                    
                    for categorie in ['Électronique', 'Mode', 'Maison', 'Sports']:
                        produits_cat = [(nom, info) for nom, info in PRODUITS.items() if info['categorie'] == categorie]
                        with st.expander(f"📂 {categorie}"):
                            cols = st.columns(2)
                            for i, (produit, info) in enumerate(produits_cat):
                                with cols[i % 2]:
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
                    <div style='background: #2196F3; padding: 1rem; border-radius: 15px; text-align: center; margin-top: 1rem;'>
                        <div style='color: white;'>💰 NOUVEAU TOTAL</div>
                        <div style='font-size: 1.5rem; font-weight: bold; color: white;'>{format_fcfa(nouveau_montant)}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Enregistrer les modifications", use_container_width=True):
                            if modifier_commande(st.session_state.edit_order_id, produits_modifies, nouveau_montant):
                                st.success(f"✅ Commande #{st.session_state.edit_order_id} modifiée !")
                                st.session_state.edit_order_id = None
                                st.rerun()
                            else:
                                st.error("❌ Erreur lors de la modification")
                    with col2:
                        if st.form_submit_button("❌ Annuler", use_container_width=True):
                            st.session_state.edit_order_id = None
                            st.rerun()

# ==================== PAGE 4: LISTE CLIENTS ====================
else:
    st.markdown("## 👤 **Liste des clients**")
    
    if len(st.session_state.df_clients) == 0:
        st.info("📭 Aucun client enregistré")
    else:
        df_display = st.session_state.df_clients.copy()
        df_display['revenu_annuel_fcfa'] = df_display['revenu_annuel_fcfa'].apply(format_fcfa)
        df_display['ca_total_fcfa'] = df_display['ca_total_fcfa'].apply(format_fcfa)
        st.dataframe(df_display[['client_id', 'nom', 'email', 'âge', 'ville', 'revenu_annuel_fcfa', 
                                 'ca_total_fcfa', 'nb_achats', 'dernier_achat']], use_container_width=True)
        
        # Export CSV
        csv_clients = st.session_state.df_clients.to_csv(index=False)
        st.download_button("📥 Exporter la liste des clients (CSV)", csv_clients, "clients.csv", "text/csv")

# ==================== FOOTER ====================
st.markdown("""
<div class="footer">
    <p>🛍️ <strong>ShopAnalyzer Pro</strong> - Réalisé par <strong>Armelle</strong></p>
    <p>💰 Francs CFA | 📱 Mobile Money | ✏️ Modifier/Supprimer | 🎁 40 produits disponibles</p>
    <p>📦 Électronique • Mode • Maison • Sports — 10 produits par catégorie</p>
</div>
""", unsafe_allow_html=True)
