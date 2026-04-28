 # app_final_corrected.py - Version sans dépendance statsmodels
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
import warnings
warnings.filterwarnings('ignore')

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="ShopAnalyzer - Armelle",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="auto"
)

# ==================== FONT AWESOME CDN ====================
st.markdown("""
<!-- Font Awesome 6 CDN -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    :root {
        --primary: #667eea;
        --primary-dark: #5a67d8;
        --secondary: #764ba2;
        --success: #48bb78;
        --danger: #f56565;
        --warning: #ed8936;
    }
    
    .main-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        padding: clamp(1rem, 5vw, 2rem);
        border-radius: clamp(10px, 3vw, 20px);
        margin-bottom: clamp(1rem, 4vw, 2rem);
        color: white;
        text-align: center;
    }
    
    .main-header h1 {
        font-size: clamp(1.5rem, 6vw, 2.5rem);
        margin: 0;
    }
    
    .main-header p {
        font-size: clamp(0.8rem, 3vw, 1rem);
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: clamp(0.8rem, 3vw, 1.2rem);
        border-radius: clamp(10px, 3vw, 15px);
        text-align: center;
        transition: transform 0.3s ease;
        border: 1px solid rgba(102, 126, 234, 0.1);
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: clamp(1.2rem, 4vw, 1.8rem);
        font-weight: 700;
        color: var(--primary);
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: clamp(0.7rem, 2.5vw, 0.85rem);
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .product-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .product-card:hover {
        border-color: var(--primary);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }
    
    .product-name {
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .product-price {
        color: var(--primary);
        font-weight: 700;
    }
    
    .info-box {
        background: #e3f2fd;
        border-left: 4px solid var(--primary);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .success-box {
        background: #d4edda;
        border-left: 4px solid var(--success);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .stats-box {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .footer {
        text-align: center;
        padding: 1rem;
        color: #6c757d;
        font-size: 0.7rem;
        margin-top: 2rem;
        border-top: 1px solid #e2e8f0;
    }
    
    @media (max-width: 768px) {
        .metric-card {
            padding: 0.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==================== INITIALISATION ====================
if 'df_clients' not in st.session_state:
    np.random.seed(42)
    n = 100
    
    st.session_state.df_clients = pd.DataFrame({
        'client_id': range(1, n+1),
        'nom': [f"Client_{i}" for i in range(1, n+1)],
        'email': [f"client{i}@email.com" for i in range(1, n+1)],
        'âge': np.random.normal(35, 12, n).clip(18, 70).astype(int),
        'ville': np.random.choice(['Douala', 'Yaoundé', 'Garoua', 'Bafoussam', 'Bamenda'], n),
        'revenu_annuel_fcfa': np.random.normal(2_500_000, 800_000, n).clip(1_000_000, 8_000_000).astype(int),
        'ca_total_fcfa': np.random.exponential(500000, n).astype(int),
        'nb_achats': np.random.poisson(3, n)
    })
    st.session_state.historique_achats = []

# ==================== CATALOGUE PRODUITS ====================
PRODUITS = {
    'Smartphone Tecno': {'prix': 150000, 'categorie': 'Électronique', 'description': 'Téléphone dernière génération'},
    'Ordinateur Portable': {'prix': 450000, 'categorie': 'Électronique', 'description': 'PC haute performance'},
    'Écouteurs Bluetooth': {'prix': 25000, 'categorie': 'Électronique', 'description': 'Son haute qualité'},
    'Montre Connectée': {'prix': 75000, 'categorie': 'Électronique', 'description': 'Suivi santé'},
    'T-shirt Premium': {'prix': 8500, 'categorie': 'Mode', 'description': 'Coton bio'},
    'Jean Slim Fit': {'prix': 15000, 'categorie': 'Mode', 'description': 'Taille parfaite'},
    'Basket Sport': {'prix': 45000, 'categorie': 'Mode', 'description': 'Confortable'},
    'Veste Imperméable': {'prix': 35000, 'categorie': 'Mode', 'description': 'Anti-pluie'},
    'Canapé Moderne': {'prix': 250000, 'categorie': 'Maison', 'description': '3 places'},
    'Lampe LED': {'prix': 12000, 'categorie': 'Maison', 'description': 'Économique'},
    'Tapis Design': {'prix': 35000, 'categorie': 'Maison', 'description': 'Laine naturelle'},
    'Batterie Cuisine': {'prix': 55000, 'categorie': 'Maison', 'description': 'Anti-adhésive'},
    'Vélo Appartement': {'prix': 180000, 'categorie': 'Sports', 'description': 'Fitness'},
    'Ballon Match': {'prix': 8000, 'categorie': 'Sports', 'description': 'Taille 5'},
    'Sac Sport': {'prix': 20000, 'categorie': 'Sports', 'description': 'Grande capacité'},
    'Tapis Course': {'prix': 120000, 'categorie': 'Sports', 'description': 'Amorti renforcé'}
}

MODES_PAIEMENT = ['MTN Mobile Money', 'Orange Money', 'Carte Bancaire', 'Virement Bancaire']

def format_fcfa(x):
    if pd.isna(x) or x == 0:
        return "0 FCFA"
    return f"{x:,.0f} FCFA".replace(",", " ")

def enregistrer_achat(client_id, produits_achetes, montant_total, mode_paiement):
    achat = {
        'date': datetime.now(),
        'client_id': client_id,
        'produits': produits_achetes,
        'montant_fcfa': montant_total,
        'mode_paiement': mode_paiement,
        'nb_articles': len(produits_achetes)
    }
    st.session_state.historique_achats.append(achat)
    
    idx = st.session_state.df_clients[st.session_state.df_clients['client_id'] == client_id].index[0]
    st.session_state.df_clients.loc[idx, 'ca_total_fcfa'] += montant_total
    st.session_state.df_clients.loc[idx, 'nb_achats'] += 1
    
    return True

# ==================== HEADER ====================
st.markdown("""
<div class="main-header">
    <h1><i class="fas fa-store"></i> ShopAnalyzer Pro</h1>
    <p><i class="fas fa-chart-line"></i> Plateforme intelligente de collecte et d'analyse de données e-commerce</p>
    <p style="font-size: 0.85rem; margin-top: 0.5rem;">
        <i class="fas fa-mobile-alt"></i> Interface responsive | 
        <i class="fab fa-font-awesome"></i> Icônes Font Awesome | 
        <i class="fas fa-chart-bar"></i> Analyse descriptive incluse
    </p>
</div>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("## 🎯 Navigation")
    
    menu = st.radio(
        "Menu",
        ["Nouvelle Commande", "Tableau de Bord", "Analyse Descriptive", "Analyses ML", "Clients", "Conseils"]
    )
    
    st.markdown("---")
    
    total_ventes = sum(a['montant_fcfa'] for a in st.session_state.historique_achats)
    nb_commandes = len(st.session_state.historique_achats)
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); padding: 1rem; border-radius: 15px;'>
        <div style='display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;'>
            <i class='fas fa-money-bill-wave' style='font-size: 1.5rem; color: #667eea;'></i>
            <div>
                <div style='font-size: 0.7rem; color: #666;'>CA TOTAL</div>
                <div style='font-weight: bold;'>{format_fcfa(total_ventes)}</div>
            </div>
        </div>
        <div style='display: flex; align-items: center; gap: 0.5rem;'>
            <i class='fas fa-shopping-cart' style='font-size: 1.5rem; color: #667eea;'></i>
            <div>
                <div style='font-size: 0.7rem; color: #666;'>COMMANDES</div>
                <div style='font-weight: bold;'>{nb_commandes}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("Développé par **Armelle** | Version 4.0")

# ==================== PAGE 1: FORMULAIRE ====================
if menu == "Nouvelle Commande":
    st.markdown("## 🛒 Passer une commande")
    
    with st.form("formulaire_achat", clear_on_submit=True):
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.markdown("### 👤 Vos informations")
            
            option_client = st.radio(
                "Type de client",
                ["Nouveau client", "Client existant"],
                horizontal=True
            )
            
            if option_client == "Client existant":
                client_id = st.selectbox(
                    "Sélectionnez votre compte",
                    st.session_state.df_clients['client_id'].tolist(),
                    format_func=lambda x: f"#{x} - {st.session_state.df_clients[st.session_state.df_clients['client_id']==x]['nom'].values[0]}"
                )
            else:
                col_a, col_b = st.columns(2)
                with col_a:
                    nom = st.text_input("Nom complet", placeholder="Votre nom")
                    age = st.number_input("Âge", 18, 100, 30)
                with col_b:
                    email = st.text_input("Email", placeholder="votre@email.com")
                    ville = st.selectbox("Ville", ['Douala', 'Yaoundé', 'Garoua', 'Bafoussam', 'Bamenda'])
        
        with col2:
            st.markdown("### 🛍️ Votre panier")
            
            produits_selectionnes = []
            montant_total = 0
            
            for categorie in ['Électronique', 'Mode', 'Maison', 'Sports']:
                with st.expander(f"📂 {categorie}"):
                    produits_cat = [(nom, info) for nom, info in PRODUITS.items() if info['categorie'] == categorie]
                    
                    for produit, info in produits_cat:
                        cols = st.columns([3, 1, 1])
                        with cols[0]:
                            st.markdown(f"""
                            <div class="product-card">
                                <span class="product-name">{produit}</span><br>
                                <span class="product-price">{format_fcfa(info['prix'])}</span>
                                <br><small>{info['description']}</small>
                            </div>
                            """, unsafe_allow_html=True)
                        with cols[1]:
                            quantite = st.number_input(
                                "Qté",
                                min_value=0, max_value=5,
                                key=produit,
                                label_visibility="collapsed"
                            )
                        with cols[2]:
                            if quantite > 0:
                                st.markdown(f'<span style="color: #48bb78;">✓ +{format_fcfa(info["prix"] * quantite)}</span>', 
                                          unsafe_allow_html=True)
                        
                        if quantite > 0:
                            produits_selectionnes.extend([produit] * quantite)
                            montant_total += info['prix'] * quantite
        
        st.markdown("---")
        st.markdown("### 💳 Paiement")
        
        mode_paiement = st.selectbox("Choisissez votre moyen de paiement", MODES_PAIEMENT)
        
        st.markdown(f"""
        <div class="success-box" style="text-align: center;">
            <i class="fas fa-receipt" style="font-size: 1.5rem;"></i>
            <div style="font-size: 0.9rem; margin-top: 0.5rem;">Total à payer</div>
            <div style="font-size: clamp(1.5rem, 5vw, 2rem); font-weight: 700; color: #667eea;">
                {format_fcfa(montant_total)}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        submitted = st.form_submit_button("✅ Confirmer la commande", use_container_width=True)
        
        if submitted:
            if montant_total == 0:
                st.error("❌ Veuillez sélectionner au moins un produit !")
            elif option_client == "Nouveau client" and ('nom' not in dir() or not nom):
                st.error("❌ Veuillez remplir vos informations")
            else:
                with st.spinner("⏳ Traitement de votre commande..."):
                    time.sleep(0.8)
                    
                    if option_client == "Nouveau client":
                        new_id = len(st.session_state.df_clients) + 1
                        nouveau_client = pd.DataFrame({
                            'client_id': [new_id],
                            'nom': [nom],
                            'email': [email],
                            'âge': [age],
                            'ville': [ville],
                            'revenu_annuel_fcfa': [0],
                            'ca_total_fcfa': [0],
                            'nb_achats': [0]
                        })
                        st.session_state.df_clients = pd.concat([st.session_state.df_clients, nouveau_client], ignore_index=True)
                        client_id = new_id
                    else:
                        client_id = client_id
                    
                    if enregistrer_achat(client_id, produits_selectionnes, montant_total, mode_paiement):
                        st.balloons()
                        st.success(f"🎉 Commande confirmée ! Merci pour votre achat de {format_fcfa(montant_total)}")

# ==================== PAGE 2: DASHBOARD ====================
elif menu == "Tableau de Bord":
    st.markdown("## 📊 Tableau de bord")
    
    total_ventes = sum(a['montant_fcfa'] for a in st.session_state.historique_achats)
    nb_commandes = len(st.session_state.historique_achats)
    nb_clients_actifs = len(st.session_state.df_clients[st.session_state.df_clients['nb_achats'] > 0])
    panier_moyen = total_ventes / nb_commandes if nb_commandes > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{format_fcfa(total_ventes)}</div>
            <div class="metric-label">Chiffre d'affaires</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{nb_commandes}</div>
            <div class="metric-label">Commandes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{nb_clients_actifs}</div>
            <div class="metric-label">Clients actifs</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{format_fcfa(panier_moyen)}</div>
            <div class="metric-label">Panier moyen</div>
        </div>
        """, unsafe_allow_html=True)
    
    if st.session_state.historique_achats:
        col1, col2 = st.columns(2)
        
        with col1:
            df_ventes = pd.DataFrame(st.session_state.historique_achats)
            df_ventes['date'] = pd.to_datetime(df_ventes['date'])
            df_ventes['jour'] = df_ventes['date'].dt.date
            ventes_par_jour = df_ventes.groupby('jour')['montant_fcfa'].sum().reset_index()
            
            fig = px.bar(ventes_par_jour, x='jour', y='montant_fcfa',
                        title="📈 Évolution des ventes",
                        labels={'jour':'Date', 'montant_fcfa':'CA (FCFA)'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            tous_produits = []
            for achat in st.session_state.historique_achats:
                tous_produits.extend(achat['produits'])
            
            if tous_produits:
                top_produits = pd.Series(tous_produits).value_counts().head(6)
                fig = px.bar(x=top_produits.values, y=top_produits.index,
                            orientation='h', title="🏆 Top produits",
                            labels={'x':'Nombre de ventes', 'y':''})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE 3: ANALYSE DESCRIPTIVE ====================
elif menu == "Analyse Descriptive":
    st.markdown("## 📊 Analyse descriptive des données")
    st.markdown("*Statistiques détaillées et visualisations exploratoires*")
    
    # Sélection du jeu de données
    tab1, tab2, tab3 = st.tabs(["📋 Clients", "🛍️ Ventes", "📈 Corrélations"])
    
    with tab1:
        st.markdown("### Analyse des clients")
        
        df_clients = st.session_state.df_clients
        
        # 1. Statistiques générales
        st.markdown("#### 📊 Statistiques générales")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stats-box">
                <i class="fas fa-users" style="font-size: 1.5rem; color: #667eea;"></i>
                <div style="font-size: 0.8rem;">Total clients</div>
                <div style="font-size: 1.5rem; font-weight: bold;">{len(df_clients)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            age_moyen = df_clients['âge'].mean()
            st.markdown(f"""
            <div class="stats-box">
                <i class="fas fa-calendar" style="font-size: 1.5rem; color: #667eea;"></i>
                <div style="font-size: 0.8rem;">Âge moyen</div>
                <div style="font-size: 1.5rem; font-weight: bold;">{age_moyen:.1f} ans</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            revenu_moyen = df_clients['revenu_annuel_fcfa'].mean()
            st.markdown(f"""
            <div class="stats-box">
                <i class="fas fa-money-bill" style="font-size: 1.5rem; color: #667eea;"></i>
                <div style="font-size: 0.8rem;">Revenu moyen</div>
                <div style="font-size: 1rem; font-weight: bold;">{format_fcfa(revenu_moyen)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            ca_moyen = df_clients['ca_total_fcfa'].mean()
            st.markdown(f"""
            <div class="stats-box">
                <i class="fas fa-chart-line" style="font-size: 1.5rem; color: #667eea;"></i>
                <div style="font-size: 0.8rem;">CA moyen/client</div>
                <div style="font-size: 1rem; font-weight: bold;">{format_fcfa(ca_moyen)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # 2. Distribution des âges
        st.markdown("#### 📈 Distribution des âges")
        fig_ages = px.histogram(df_clients, x='âge', nbins=30,
                                title="Distribution des âges des clients",
                                labels={'âge':'Âge', 'count':'Nombre de clients'},
                                color_discrete_sequence=['#667eea'])
        fig_ages.add_vline(x=df_clients['âge'].mean(), line_dash="dash", line_color="red",
                          annotation_text=f"Moyenne: {df_clients['âge'].mean():.1f}")
        st.plotly_chart(fig_ages, use_container_width=True)
        
        # 3. Répartition par ville
        st.markdown("#### 🗺️ Répartition géographique")
        col1, col2 = st.columns(2)
        
        with col1:
            ville_counts = df_clients['ville'].value_counts()
            fig_ville = px.pie(values=ville_counts.values, names=ville_counts.index,
                              title="Clients par ville",
                              color_discrete_sequence=px.colors.sequential.Viridis)
            st.plotly_chart(fig_ville, use_container_width=True)
        
        with col2:
            # CA moyen par ville
            ca_par_ville = df_clients.groupby('ville')['ca_total_fcfa'].mean().sort_values(ascending=True)
            fig_ca_ville = px.bar(x=ca_par_ville.values, y=ca_par_ville.index,
                                  orientation='h', title="CA moyen par ville (FCFA)",
                                  labels={'x':'CA moyen', 'y':'Ville'},
                                  color=ca_par_ville.values, color_continuous_scale='Viridis')
            st.plotly_chart(fig_ca_ville, use_container_width=True)
        
        # 4. Boxplot des revenus par tranche d'âge
        st.markdown("#### 📊 Revenu par tranche d'âge")
        df_clients['tranche_age'] = pd.cut(df_clients['âge'], bins=[18, 25, 35, 45, 55, 70],
                                           labels=['18-25', '26-35', '36-45', '46-55', '56+'])
        fig_revenu_age = px.box(df_clients, x='tranche_age', y='revenu_annuel_fcfa',
                                title="Distribution des revenus par tranche d'âge",
                                labels={'tranche_age':'Tranche d\'âge', 'revenu_annuel_fcfa':'Revenu annuel (FCFA)'})
        st.plotly_chart(fig_revenu_age, use_container_width=True)
        
        # 5. Tableau des statistiques détaillées
        st.markdown("#### 📋 Tableau des statistiques descriptives")
        stats_desc = df_clients[['âge', 'revenu_annuel_fcfa', 'ca_total_fcfa', 'nb_achats']].describe()
        stats_desc = stats_desc.round(0)
        stats_desc.index = ['Nombre', 'Moyenne', 'Écart-type', 'Min', '25%', 'Médiane', '75%', 'Max']
        st.dataframe(stats_desc, use_container_width=True)
    
    with tab2:
        st.markdown("### Analyse des ventes")
        
        if st.session_state.historique_achats:
            df_ventes = pd.DataFrame(st.session_state.historique_achats)
            df_ventes['date'] = pd.to_datetime(df_ventes['date'])
            
            # 1. Métriques des ventes
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_ventes = df_ventes['montant_fcfa'].sum()
                st.markdown(f"""
                <div class="stats-box">
                    <i class="fas fa-shopping-cart" style="font-size: 1.5rem;"></i>
                    <div>CA Total</div>
                    <div style="font-weight: bold;">{format_fcfa(total_ventes)}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                nb_ventes = len(df_ventes)
                st.markdown(f"""
                <div class="stats-box">
                    <i class="fas fa-receipt" style="font-size: 1.5rem;"></i>
                    <div>Nombre ventes</div>
                    <div style="font-weight: bold;">{nb_ventes}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                panier_moyen = df_ventes['montant_fcfa'].mean()
                st.markdown(f"""
                <div class="stats-box">
                    <i class="fas fa-basket-shopping" style="font-size: 1.5rem;"></i>
                    <div>Panier moyen</div>
                    <div style="font-weight: bold;">{format_fcfa(panier_moyen)}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                articles_moyen = df_ventes['nb_articles'].mean()
                st.markdown(f"""
                <div class="stats-box">
                    <i class="fas fa-box" style="font-size: 1.5rem;"></i>
                    <div>Articles/commande</div>
                    <div style="font-weight: bold;">{articles_moyen:.1f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # 2. Évolution temporelle
            st.markdown("#### 📈 Évolution des ventes dans le temps")
            
            # Ventes par jour
            ventes_jour = df_ventes.groupby(df_ventes['date'].dt.date)['montant_fcfa'].sum().reset_index()
            fig_evol = px.line(ventes_jour, x='date', y='montant_fcfa',
                              title="Évolution du chiffre d'affaires",
                              labels={'date':'Date', 'montant_fcfa':'CA (FCFA)'},
                              markers=True)
            st.plotly_chart(fig_evol, use_container_width=True)
            
            # 3. Distribution des montants
            col1, col2 = st.columns(2)
            
            with col1:
                fig_montants = px.histogram(df_ventes, x='montant_fcfa', nbins=30,
                                           title="Distribution des montants d'achat",
                                           labels={'montant_fcfa':'Montant (FCFA)', 'count':'Nombre de ventes'})
                st.plotly_chart(fig_montants, use_container_width=True)
            
            with col2:
                fig_articles = px.histogram(df_ventes, x='nb_articles', nbins=10,
                                           title="Distribution du nombre d'articles",
                                           labels={'nb_articles':'Nombre d\'articles', 'count':'Nombre de commandes'})
                st.plotly_chart(fig_articles, use_container_width=True)
            
            # 4. Modes de paiement
            st.markdown("#### 💳 Modes de paiement")
            paiements_counts = df_ventes['mode_paiement'].value_counts()
            fig_paiements = px.pie(values=paiements_counts.values, names=paiements_counts.index,
                                  title="Répartition des modes de paiement",
                                  color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig_paiements, use_container_width=True)
            
        else:
            st.info("📊 Aucune vente enregistrée pour le moment. Effectuez des achats pour voir l'analyse !")
    
    with tab3:
        st.markdown("### Analyse des corrélations")
        
        df_clients = st.session_state.df_clients
        
        # 1. Matrice de corrélation
        st.markdown("#### 🔗 Matrice de corrélation")
        
        cols_corr = ['âge', 'revenu_annuel_fcfa', 'ca_total_fcfa', 'nb_achats']
        corr_matrix = df_clients[cols_corr].corr()
        
        fig_corr = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                             title="Matrice de corrélation entre variables",
                             labels=dict(color="Corrélation"),
                             color_continuous_scale='RdBu', zmin=-1, zmax=1)
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # 2. Interprétation
        st.markdown("#### 📝 Interprétation des corrélations")
        
        corr_age_ca = corr_matrix.loc['âge', 'ca_total_fcfa']
        corr_revenu_ca = corr_matrix.loc['revenu_annuel_fcfa', 'ca_total_fcfa']
        
        st.markdown(f"""
        <div class="info-box">
            <i class="fas fa-chart-line"></i> <strong>Analyse des corrélations :</strong><br><br>
            • <strong>Âge vs CA :</strong> Corrélation de {corr_age_ca:.2f} - 
            {"Corrélation positive faible" if corr_age_ca > 0 else "Corrélation négative"}<br>
            • <strong>Revenu vs CA :</strong> Corrélation de {corr_revenu_ca:.2f} - 
            {"Les clients avec un revenu élevé dépensent plus" if abs(corr_revenu_ca) > 0.3 else "Lien modéré entre revenu et dépenses"}<br><br>
            <i class="fas fa-lightbulb"></i> <strong>Insight :</strong> 
            {"Le revenu est le facteur le plus prédictif du chiffre d'affaires." if abs(corr_revenu_ca) > abs(corr_age_ca) else "L'âge influence légèrement plus le comportement d'achat que le revenu."}
        </div>
        """, unsafe_allow_html=True)
        
        # 3. Scatter plots (sans trendline pour éviter statsmodels)
        st.markdown("#### 📊 Relations entre variables")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_scatter1 = px.scatter(df_clients, x='revenu_annuel_fcfa', y='ca_total_fcfa',
                                      title="Revenu vs Chiffre d'affaires",
                                      labels={'revenu_annuel_fcfa':'Revenu (FCFA)', 'ca_total_fcfa':'CA (FCFA)'},
                                      opacity=0.6)
            st.plotly_chart(fig_scatter1, use_container_width=True)
        
        with col2:
            fig_scatter2 = px.scatter(df_clients, x='âge', y='ca_total_fcfa',
                                      title="Âge vs Chiffre d'affaires",
                                      labels={'âge':'Âge', 'ca_total_fcfa':'CA (FCFA)'},
                                      opacity=0.6)
            st.plotly_chart(fig_scatter2, use_container_width=True)

# ==================== PAGE 4: ANALYSES ML ====================
elif menu == "Analyses ML":
    st.markdown("## 📈 Analyses prédictives")
    
    df_ml = st.session_state.df_clients[st.session_state.df_clients['nb_achats'] > 0]
    
    if len(df_ml) > 5:
        tab1, tab2, tab3 = st.tabs(["📊 Régression", "🎯 Clustering", "🔮 Prédiction"])
        
        with tab1:
            st.markdown("### Prédiction du Chiffre d'Affaires")
            
            X = df_ml[['âge', 'revenu_annuel_fcfa']]
            y = df_ml['ca_total_fcfa']
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            reg_simple = LinearRegression()
            reg_simple.fit(X_train[['âge']], y_train)
            score_simple = reg_simple.score(X_test[['âge']], y_test)
            
            reg_multiple = LinearRegression()
            reg_multiple.fit(X_train, y_train)
            score_multiple = reg_multiple.score(X_test, y_test)
            
            # Calcul des prédictions pour le graphique
            y_pred_simple = reg_simple.predict(X_test[['âge']])
            y_pred_multiple = reg_multiple.predict(X_test)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Régression simple", f"{max(0, score_simple):.2%}")
                st.caption("Basée uniquement sur l'âge")
            with col2:
                st.metric("Régression multiple", f"{max(0, score_multiple):.2%}")
                st.caption("Âge + Revenu")
            
            # Graphique de comparaison
            fig_compare = go.Figure()
            fig_compare.add_trace(go.Scatter(x=y_test, y=y_pred_multiple, mode='markers',
                                            name='Prédictions', marker=dict(color='#667eea')))
            fig_compare.add_trace(go.Scatter(x=[y.min(), y.max()], y=[y.min(), y.max()],
                                            mode='lines', name='Parfait', line=dict(dash='dash', color='red')))
            fig_compare.update_layout(title="Prédiction vs Réalité (Régression multiple)",
                                     xaxis_title="CA réel (FCFA)",
                                     yaxis_title="CA prédit (FCFA)")
            st.plotly_chart(fig_compare, use_container_width=True)
            
            # Afficher les coefficients
            st.markdown("#### 📊 Coefficients du modèle")
            coef_df = pd.DataFrame({
                'Variable': ['Âge', 'Revenu annuel'],
                'Coefficient': [reg_multiple.coef_[0], reg_multiple.coef_[1]]
            })
            st.dataframe(coef_df, use_container_width=True)
        
        with tab2:
            st.markdown("### Segmentation clients")
            
            features = df_ml[['âge', 'ca_total_fcfa']]
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            df_ml['segment'] = kmeans.fit_predict(features_scaled)
            
            sil_score = silhouette_score(features_scaled, df_ml['segment'])
            st.metric("Qualité du clustering (Silhouette)", f"{sil_score:.2%}")
            
            fig_clust = px.scatter(df_ml, x='ca_total_fcfa', y='âge',
                                   color='segment', size='nb_achats',
                                   title="Segmentation des clients",
                                   labels={'ca_total_fcfa':'CA (FCFA)', 'âge':'Âge'},
                                   color_continuous_scale='Viridis')
            st.plotly_chart(fig_clust, use_container_width=True)
            
            # Profil des segments
            st.markdown("#### 📝 Profil des segments")
            for seg in sorted(df_ml['segment'].unique()):
                seg_data = df_ml[df_ml['segment'] == seg]
                st.markdown(f"""
                <div class="info-box">
                    <strong>Segment {seg}</strong> ({len(seg_data)} clients)<br>
                    Âge moyen: {seg_data['âge'].mean():.0f} ans<br>
                    CA moyen: {format_fcfa(seg_data['ca_total_fcfa'].mean())}<br>
                    Achats moyen: {seg_data['nb_achats'].mean():.1f}
                </div>
                """, unsafe_allow_html=True)
        
        with tab3:
            st.markdown("### Prédiction personnalisée")
            
            col1, col2 = st.columns(2)
            with col1:
                age_pred = st.slider("Âge du client", 18, 70, 35)
                revenu_pred = st.number_input("Revenu annuel (FCFA)", 500000, 8000000, 2500000, step=100000)
            
            with col2:
                if st.button("🎯 Prédire le CA", use_container_width=True):
                    prediction = reg_multiple.predict([[age_pred, revenu_pred]])[0]
                    st.markdown(f"""
                    <div style="text-align: center; background: #d4edda; padding: 1rem; border-radius: 10px;">
                        <i class="fas fa-chart-line" style="font-size: 2rem; color: #155724;"></i>
                        <div style="font-size: 1.2rem; margin-top: 0.5rem;">CA annuel estimé</div>
                        <div style="font-size: 2rem; font-weight: bold; color: #155724;">{format_fcfa(prediction)}</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("📊 Besoin d'au moins 5 clients actifs pour l'analyse. Continuez à collecter des données !")

# ==================== PAGE 5: CLIENTS ====================
elif menu == "Clients":
    st.markdown("## 👥 Gestion des clients")
    
    df_display = st.session_state.df_clients.copy()
    df_display['ca_total_fcfa'] = df_display['ca_total_fcfa'].apply(format_fcfa)
    df_display['revenu_annuel_fcfa'] = df_display['revenu_annuel_fcfa'].apply(format_fcfa)
    st.dataframe(df_display, use_container_width=True)
    
    if st.session_state.historique_achats:
        st.markdown("### 📜 Historique des commandes")
        df_histo = pd.DataFrame(st.session_state.historique_achats)
        df_histo['date'] = df_histo['date'].dt.strftime('%d/%m/%Y %H:%M')
        df_histo['montant_fcfa'] = df_histo['montant_fcfa'].apply(format_fcfa)
        st.dataframe(df_histo, use_container_width=True)

# ==================== PAGE 6: CONSEILS ====================
else:
    st.markdown("## 💡 Conseils et bonnes pratiques")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-box">
            <h3><i class="fas fa-mobile-alt"></i> Pour une meilleure expérience</h3>
            <ul>
                <li><i class="fas fa-globe"></i> Utilisez Chrome, Firefox ou Safari</li>
                <li><i class="fas fa-tablet-alt"></i> Le site est adapté aux mobiles</li>
                <li><i class="fas fa-lock"></i> Vos données sont sécurisées</li>
                <li><i class="fas fa-credit-card"></i> Paiements sécurisés</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-box">
            <h3><i class="fas fa-star"></i> Fonctionnalités clés</h3>
            <ul>
                <li><i class="fas fa-chart-pie"></i> Dashboard interactif</li>
                <li><i class="fas fa-chart-bar"></i> Analyse descriptive complète</li>
                <li><i class="fas fa-robot"></i> Prédiction du CA par IA</li>
                <li><i class="fas fa-chart-line"></i> Segmentation clients</li>
                <li><i class="fas fa-mobile-alt"></i> Interface 100% responsive</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ==================== FOOTER ====================
st.markdown(f"""
<div class="footer">
    <hr>
    <p>
        <i class="fas fa-store"></i> ShopAnalyzer by Armelle | 
        <i class="fas fa-chart-bar"></i> Analyse descriptive incluse |
        <i class="fas fa-robot"></i> ML prédictif
    </p>
    <p>
        <i class="fas fa-money-bill-wave"></i> Toutes les valeurs en FCFA | 
        <i class="fas fa-calendar-alt"></i> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
    </p>
</div>
""", unsafe_allow_html=True)
