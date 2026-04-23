# app_premium_fixed.py - Version corrigée
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import r2_score, silhouette_score, classification_report
import base64
from streamlit_option_menu import option_menu
import time
import warnings
warnings.filterwarnings('ignore')

# ==================== CONFIGURATION DESIGN ====================
st.set_page_config(
    page_title="Gestion de ma boutique", 
    page_icon="🛍️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un design moderne
st.markdown("""
<style>
    /* Police et fond */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header personnalisé */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Cartes métriques */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        text-align: center;
        transition: transform 0.3s ease;
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #667eea;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Formulaire stylisé */
    .stForm {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        border: 1px solid #e9ecef;
    }
    
    /* Boutons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Cartes produit */
    .product-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .product-card:hover {
        border-color: #667eea;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }
    
    /* Animation */
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
    
    .fade-in {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Badge de performance */
    .performance-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .performance-good {
        background: #d4edda;
        color: #155724;
    }
    
    .performance-medium {
        background: #fff3cd;
        color: #856404;
    }
    
    .performance-bad {
        background: #f8d7da;
        color: #721c24;
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
        'avatar': np.random.choice(['👨', '👩', '👧', '👴', '👵'], n),
        'revenu_annuel_fcfa': np.random.normal(2_500_000, 800_000, n).clip(1_000_000, 8_000_000).astype(int),
        'ca_total_fcfa': 0,
        'nb_achats': 0,
        'dernier_achat': None
    })
    
    st.session_state.historique_achats = []

# Catalogue produits
PRODUITS = {
    '📱 Smartphone Tecno Camon': {'prix': 150000, 'categorie': 'Électronique', 'stock': 50, 'image': '📱'},
    '💻 PC Portable HP': {'prix': 450000, 'categorie': 'Électronique', 'stock': 30, 'image': '💻'},
    '🎧 Casque Bluetooth': {'prix': 25000, 'categorie': 'Électronique', 'stock': 100, 'image': '🎧'},
    '👕 T-shirt Premium': {'prix': 8500, 'categorie': 'Mode', 'stock': 200, 'image': '👕'},
    '👖 Jean Slim': {'prix': 15000, 'categorie': 'Mode', 'stock': 150, 'image': '👖'},
    '👟 Basket Nike': {'prix': 45000, 'categorie': 'Mode', 'stock': 80, 'image': '👟'},
    '🛋️ Canapé 3 places': {'prix': 250000, 'categorie': 'Maison', 'stock': 20, 'image': '🛋️'},
    '💡 Lampe LED': {'prix': 12000, 'categorie': 'Maison', 'stock': 60, 'image': '💡'},
    '🏠 Tapis de salon': {'prix': 35000, 'categorie': 'Maison', 'stock': 40, 'image': '🏠'},
    '🚴 Vélo d\'appartement': {'prix': 180000, 'categorie': 'Sports', 'stock': 25, 'image': '🚴'},
    '⚽ Ballon de foot': {'prix': 8000, 'categorie': 'Sports', 'stock': 100, 'image': '⚽'},
    '🎒 Sac de sport': {'prix': 20000, 'categorie': 'Sports', 'stock': 70, 'image': '🎒'}
}

def format_fcfa(x):
    """Formate un nombre en FCFA"""
    if pd.isna(x) or x == 0:
        return "0 FCFA"
    return f"{x:,.0f} FCFA".replace(",", " ")

def enregistrer_achat(client_id, produits_achetes, montant_total, mode_paiement):
    """Enregistre un achat dans l'historique"""
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
    st.session_state.df_clients.loc[idx, 'dernier_achat'] = datetime.now()
    
    return True

def get_performance_badge(score):
    """Retourne un badge HTML basé sur le score"""
    if score >= 0.7:
        return '<span class="performance-badge performance-good">👍 Excellente</span>'
    elif score >= 0.4:
        return '<span class="performance-badge performance-medium">📊 Moyenne</span>'
    else:
        return '<span class="performance-badge performance-bad">⚠️ À améliorer</span>'

# ==================== HEADER ====================
st.markdown("""
<div class="main-header fade-in">
    <h1>🛍️ ShopAnalyzer Pro</h1>
    <p>Plateforme intelligente de collecte et d'analyse de données e-commerce</p>
</div>
""", unsafe_allow_html=True)

# ==================== MENU ====================
with st.sidebar:
    st.markdown("### 🎯 Navigation")
    selected = option_menu(
        menu_title=None,
        options=["🛒 Nouvel Achat", "📊 Dashboard", "📈 Analyses ML", "👥 Clients", "💡 Insights"],
        icons=["cart-plus", "bar-chart", "graph-up", "people", "lightbulb"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#667eea", "font-size": "1.2rem"},
            "nav-link": {
                "font-size": "1rem",
                "text-align": "left",
                "margin": "0.2rem 0",
                "border-radius": "10px",
                "transition": "all 0.3s ease"
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                "font-weight": "600"
            },
        }
    )
    
    st.markdown("---")
    st.markdown("### 📊 Statistiques")
    
    total_ventes = sum(a['montant_fcfa'] for a in st.session_state.historique_achats)
    nb_commandes = len(st.session_state.historique_achats)
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); padding: 1rem; border-radius: 15px; margin: 0.5rem 0;'>
        <div style='font-size: 0.85rem; color: #666;'>💰 CA Total</div>
        <div style='font-size: 1.5rem; font-weight: 700; color: #667eea;'>{format_fcfa(total_ventes)}</div>
    </div>
    <div style='background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); padding: 1rem; border-radius: 15px; margin: 0.5rem 0;'>
        <div style='font-size: 0.85rem; color: #666;'>📦 Commandes</div>
        <div style='font-size: 1.5rem; font-weight: 700; color: #667eea;'>{nb_commandes}</div>
    </div>
    """, unsafe_allow_html=True)

# ==================== PAGE 1: FORMULAIRE D'ACHAT ====================
if selected == "🛒 Nouvel Achat":
    st.markdown("## 🛒 Nouvelle commande")
    st.markdown("*Remplissez le formulaire ci-dessous pour passer commande*")
    
    with st.form(key="formulaire_achat", clear_on_submit=True):
        col1, col2 = st.columns([1, 1.5])
        
        with col1:
            st.markdown("### 👤 Informations client")
            
            option_client = st.radio(
                "Type de client",
                ["✨ Nouveau client", "⭐ Client existant"],
                horizontal=True
            )
            
            if option_client == "⭐ Client existant":
                client_id = st.selectbox(
                    "Sélectionnez votre compte",
                    st.session_state.df_clients['client_id'].tolist(),
                    format_func=lambda x: f"#{x} - {st.session_state.df_clients[st.session_state.df_clients['client_id']==x]['nom'].values[0]}"
                )
                client_info = st.session_state.df_clients[st.session_state.df_clients['client_id'] == client_id].iloc[0]
                st.success(f"👋 Bon retour {client_info['avatar']} {client_info['nom']} !")
            else:
                col_a, col_b = st.columns(2)
                with col_a:
                    nom = st.text_input("Nom complet", placeholder="Jean Dupont")
                    age = st.number_input("Âge", 18, 100, 30)
                    ville = st.selectbox("Ville", ['Douala', 'Yaoundé', 'Garoua', 'Bafoussam', 'Bamenda'])
                with col_b:
                    email = st.text_input("Email", placeholder="jean@email.com")
                    avatar = st.selectbox("Avatar", ['👨', '👩', '👧', '👴', '👵'])
                    revenu = st.number_input("Revenu annuel (FCFA)", 500000, 10000000, 2500000, step=100000)
        
        with col2:
            st.markdown("### 📦 Panier")
            
            produits_selectionnes = []
            montant_total = 0
            
            for categorie in ['Électronique', 'Mode', 'Maison', 'Sports']:
                with st.expander(f"📂 {categorie}", expanded=(categorie == 'Électronique')):
                    produits_cat = [(nom, info) for nom, info in PRODUITS.items() if info['categorie'] == categorie]
                    
                    for produit, info in produits_cat:
                        col_qty, col_price = st.columns([1, 1])
                        with col_qty:
                            quantite = st.number_input(
                                f"{info['image']} {produit.replace(info['image']+' ', '')}",
                                min_value=0, max_value=min(5, info['stock']),
                                key=produit,
                                label_visibility="collapsed"
                            )
                        with col_price:
                            st.markdown(f"<small>{format_fcfa(info['prix'])}</small>", unsafe_allow_html=True)
                        
                        if quantite > 0:
                            produits_selectionnes.extend([produit] * quantite)
                            montant_total += info['prix'] * quantite
            
            st.markdown("---")
            st.markdown("### 💳 Paiement")
            mode_paiement = st.selectbox(
                "Mode de paiement",
                ["📱 Mobile Money (MTN)", "📱 Mobile Money (Orange)", "💳 Carte bancaire", "🚚 Paiement à la livraison"]
            )
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 1rem; border-radius: 15px; color: white; text-align: center; margin-top: 1rem;'>
                <div style='font-size: 0.9rem; opacity: 0.9;'>Total à payer</div>
                <div style='font-size: 2rem; font-weight: 700;'>{format_fcfa(montant_total)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        submitted = st.form_submit_button("✅ Confirmer la commande", use_container_width=True)
        
        if submitted:
            if montant_total == 0:
                st.error("❌ Veuillez sélectionner au moins un produit !")
            elif option_client == "✨ Nouveau client" and (not nom or not email):
                st.error("❌ Veuillez remplir vos informations")
            else:
                with st.spinner("Traitement de votre commande..."):
                    time.sleep(0.5)
                    
                    if option_client == "✨ Nouveau client":
                        new_id = len(st.session_state.df_clients) + 1
                        nouveau_client = pd.DataFrame({
                            'client_id': [new_id],
                            'nom': [nom],
                            'email': [email],
                            'âge': [age],
                            'ville': [ville],
                            'avatar': [avatar],
                            'revenu_annuel_fcfa': [revenu],
                            'ca_total_fcfa': [0],
                            'nb_achats': [0],
                            'dernier_achat': [None]
                        })
                        st.session_state.df_clients = pd.concat([st.session_state.df_clients, nouveau_client], ignore_index=True)
                        client_id = new_id
                    
                    if enregistrer_achat(client_id, produits_selectionnes, montant_total, mode_paiement):
                        st.balloons()
                        st.success(f"🎉 Commande confirmée ! Merci pour votre achat de {format_fcfa(montant_total)}")
                        
                        with st.expander("📄 Voir le récapitulatif", expanded=True):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("**🆔 Commande #**", len(st.session_state.historique_achats))
                                st.write("**📅 Date:**", datetime.now().strftime('%d/%m/%Y %H:%M'))
                                st.write("**👤 Client:**", client_id)
                            with col2:
                                st.write("**📦 Articles:**", len(produits_selectionnes))
                                st.write("**💳 Paiement:**", mode_paiement)
                                st.write("**💰 Total:**", format_fcfa(montant_total))
    
    if st.session_state.historique_achats:
        st.markdown("---")
        st.markdown("### 📜 Activité récente")
        derniers = st.session_state.historique_achats[-3:]
        for achat in reversed(derniers):
            st.info(f"🛒 **Commande #{len(st.session_state.historique_achats) - len(derniers) + derniers.index(achat) + 1}** - {achat['date'].strftime('%H:%M:%S')} - {achat['nb_articles']} articles - {format_fcfa(achat['montant_fcfa'])}")

# ==================== PAGE 2: DASHBOARD ====================
elif selected == "📊 Dashboard":
    st.markdown("## 📊 Tableau de bord")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_ventes = sum(a['montant_fcfa'] for a in st.session_state.historique_achats)
    nb_commandes = len(st.session_state.historique_achats)
    nb_clients_actifs = len(st.session_state.df_clients[st.session_state.df_clients['nb_achats'] > 0])
    panier_moyen = total_ventes / nb_commandes if nb_commandes > 0 else 0
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">💰</div>
            <div class="metric-value">{format_fcfa(total_ventes)}</div>
            <div class="metric-label">Chiffre d'affaires</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📦</div>
            <div class="metric-value">{nb_commandes}</div>
            <div class="metric-label">Commandes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">👥</div>
            <div class="metric-value">{nb_clients_actifs}</div>
            <div class="metric-label">Clients actifs</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🛒</div>
            <div class="metric-value">{format_fcfa(panier_moyen)}</div>
            <div class="metric-label">Panier moyen</div>
        </div>
        """, unsafe_allow_html=True)
    
    if st.session_state.historique_achats:
        col1, col2 = st.columns(2)
        
        with col1:
            df_ventes = pd.DataFrame(st.session_state.historique_achats)
            df_ventes['date'] = pd.to_datetime(df_ventes['date'])
            df_ventes['heure'] = df_ventes['date'].dt.hour
            
            ventes_par_heure = df_ventes.groupby('heure')['montant_fcfa'].sum().reset_index()
            fig = px.bar(ventes_par_heure, x='heure', y='montant_fcfa',
                        title="📈 Ventes par heure",
                        labels={'heure':'Heure', 'montant_fcfa':'CA (FCFA)'},
                        color_discrete_sequence=['#667eea'])
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            tous_produits = []
            for achat in st.session_state.historique_achats:
                tous_produits.extend(achat['produits'])
            
            if tous_produits:
                top_produits = pd.Series(tous_produits).value_counts().head(8)
                fig = px.bar(x=top_produits.values, y=top_produits.index,
                            orientation='h', title="🏆 Top produits",
                            labels={'x':'Ventes', 'y':''},
                            color_discrete_sequence=['#764ba2'])
                fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
        
        # Modes de paiement
        paiements = pd.DataFrame(st.session_state.historique_achats)['mode_paiement'].value_counts()
        fig = px.pie(values=paiements.values, names=paiements.index,
                    title="💳 Répartition des paiements",
                    color_discrete_sequence=px.colors.sequential.Viridis)
        st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE 3: ANALYSES ML ====================
elif selected == "📈 Analyses ML":
    st.markdown("## 📈 Intelligence Artificielle")
    st.markdown("*Modèles prédictifs et segmentation automatique*")
    
    if len(st.session_state.historique_achats) < 5:
        st.warning("⚠️ Besoin de plus de données ! Effectuez au moins 5 achats pour les analyses.")
    else:
        df_clients_ml = st.session_state.df_clients[st.session_state.df_clients['nb_achats'] > 0].copy()
        
        if len(df_clients_ml) > 0:
            tab1, tab2, tab3 = st.tabs(["📈 Régression", "🎯 Clustering", "🔮 Prédictions"])
            
            with tab1:
                st.subheader("Prédiction du Chiffre d'Affaires")
                
                features = ['âge', 'revenu_annuel_fcfa']
                X = df_clients_ml[features]
                y = df_clients_ml['ca_total_fcfa']
                
                if len(X) > 1:
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                    
                    reg = LinearRegression()
                    reg.fit(X_train, y_train)
                    score = reg.score(X_test, y_test)
                    
                    # Correction: éviter les valeurs NaN pour la progress bar
                    score_progress = max(0, min(1, score)) if not np.isnan(score) else 0
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("🎯 Précision du modèle (R²)", f"{max(0, score):.2%}")
                        
                        # Afficher le badge de performance
                        st.markdown(get_performance_badge(score), unsafe_allow_html=True)
                        
                        # Barre de progression (corrigée)
                        if score_progress > 0:
                            st.progress(score_progress)
                        else:
                            st.info("📊 Modèle en cours d'apprentissage...")
                        
                        # Impact des variables
                        fig = px.bar(x=features, y=reg.coef_,
                                    title="Impact sur le CA",
                                    labels={'x':'Variable', 'y':'Coefficient'},
                                    color=features, color_discrete_sequence=['#667eea', '#764ba2'])
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        y_pred = reg.predict(X_test)
                        fig = px.scatter(x=y_test, y=y_pred,
                                        title="Prédiction vs Réalité",
                                        labels={'x':'CA réel (FCFA)', 'y':'CA prédit (FCFA)'})
                        fig.add_trace(go.Scatter(x=[y.min(), y.max()], y=[y.min(), y.max()],
                                                mode='lines', name='Parfait', line=dict(dash='dash', color='red')))
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("📊 Pas assez de données pour la régression. Continuez à collecter des données !")
            
            with tab2:
                st.subheader("Segmentation automatique des clients")
                
                features_clust = ['âge', 'ca_total_fcfa', 'nb_achats']
                X_clust = df_clients_ml[features_clust]
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X_clust)
                
                if len(X_clust) >= 3:
                    kmeans = KMeans(n_clusters=min(3, len(X_clust)), random_state=42, n_init=10)
                    df_clients_ml['segment'] = kmeans.fit_predict(X_scaled)
                    
                    sil_score = silhouette_score(X_scaled, df_clients_ml['segment'])
                    st.metric("📊 Qualité de segmentation", f"{sil_score:.2%}")
                    
                    fig = px.scatter(df_clients_ml, x='ca_total_fcfa', y='nb_achats',
                                    color='segment', size='âge',
                                    title="Segmentation clients",
                                    labels={'ca_total_fcfa':'CA total (FCFA)', 'nb_achats':'Nb achats'},
                                    hover_data=['nom', 'ville'])
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Profils des segments
                    for segment in sorted(df_clients_ml['segment'].unique()):
                        seg_data = df_clients_ml[df_clients_ml['segment'] == segment]
                        with st.expander(f"🎯 Segment {segment} - {len(seg_data)} clients"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Âge moyen", f"{seg_data['âge'].mean():.0f} ans")
                            with col2:
                                st.metric("CA moyen", format_fcfa(seg_data['ca_total_fcfa'].mean()))
                            with col3:
                                st.metric("Nb achats moyen", f"{seg_data['nb_achats'].mean():.1f}")
                else:
                    st.info("📊 Pas assez de données pour le clustering. Continuez à collecter des données !")
            
            with tab3:
                st.subheader("🔮 Prédiction personnalisée")
                
                col1, col2 = st.columns(2)
                with col1:
                    age_pred = st.slider("Âge", 18, 70, 35)
                    revenu_pred = st.number_input("Revenu annuel (FCFA)", 1000000, 8000000, 3000000, step=100000)
                
                with col2:
                    if st.button("🎯 Prédire le CA potentiel", use_container_width=True):
                        if 'reg' in locals():
                            prediction = reg.predict([[age_pred, revenu_pred]])[0]
                            st.success(f"💰 CA annuel estimé : **{format_fcfa(prediction)}**")
                            st.info(f"📊 Intervalle de confiance : {format_fcfa(prediction * 0.8)} - {format_fcfa(prediction * 1.2)}")
                        else:
                            st.warning("⚠️ Modèle non disponible. Effectuez d'abord l'analyse de régression.")

# ==================== PAGE 4: CLIENTS ====================
elif selected == "👥 Clients":
    st.markdown("## 👥 Gestion des clients")
    
    df_display = st.session_state.df_clients.copy()
    df_display['ca_total_fcfa'] = df_display['ca_total_fcfa'].apply(lambda x: format_fcfa(x))
    df_display['revenu_annuel_fcfa'] = df_display['revenu_annuel_fcfa'].apply(lambda x: format_fcfa(x))
    
    st.dataframe(df_display, use_container_width=True, height=400)
    
    if st.session_state.historique_achats:
        st.markdown("---")
        st.markdown("### 📜 Historique complet")
        df_histo = pd.DataFrame(st.session_state.historique_achats)
        df_histo['date'] = df_histo['date'].dt.strftime('%d/%m/%Y %H:%M')
        df_histo['montant_fcfa'] = df_histo['montant_fcfa'].apply(lambda x: format_fcfa(x))
        st.dataframe(df_histo, use_container_width=True)

# ==================== PAGE 5: INSIGHTS ====================
else:
    st.markdown("## 💡 Insights & Recommandations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); padding: 1.5rem; border-radius: 15px; margin: 1rem 0;'>
            <h3>🎯 Recommandations IA</h3>
            <ul style='list-style-type: none; padding-left: 0;'>
        """, unsafe_allow_html=True)
        
        if st.session_state.historique_achats:
            df_ventes = pd.DataFrame(st.session_state.historique_achats)
            meilleure_heure = df_ventes['date'].dt.hour.mode()[0] if len(df_ventes) > 0 else 14
            st.markdown(f"<li>⏰ **Meilleure heure pour vendre** : {meilleure_heure}h</li>", unsafe_allow_html=True)
            
            tous_produits = []
            for achat in st.session_state.historique_achats:
                tous_produits.extend(achat['produits'])
            if tous_produits:
                top_produit = pd.Series(tous_produits).value_counts().index[0]
                st.markdown(f"<li>🏆 **Produit star** : {top_produit.replace('📱', '').replace('💻', '').replace('🎧', '').strip()}</li>", unsafe_allow_html=True)
        
        st.markdown("""
            <li>💡 **Action recommandée** : Cibler les 25-35 ans</li>
            <li>📱 **Paiement préféré** : Mobile Money</li>
            <li>🎯 **Segment prioritaire** : Premium</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); padding: 1.5rem; border-radius: 15px; margin: 1rem 0;'>
            <h3>📊 KPIs Stratégiques</h3>
        """, unsafe_allow_html=True)
        
        if st.session_state.historique_achats:
            nb_clients_actifs = len(st.session_state.df_clients[st.session_state.df_clients['nb_achats'] > 0])
            clients_fideles = len(st.session_state.df_clients[st.session_state.df_clients['nb_achats'] >= 3])
            taux_fidelisation = (clients_fideles / nb_clients_actifs * 100) if nb_clients_actifs > 0 else 0
            
            st.metric("👥 Taux de fidélisation", f"{taux_fidelisation:.1f}%")
            st.metric("🔄 Réachat moyen", f"{st.session_state.df_clients['nb_achats'].mean():.1f} fois")
            
            if len(st.session_state.historique_achats) >= 2 and st.session_state.historique_achats[0]['date']:
                        delta_jours = max(1, (datetime.now() - st.session_state.historique_achats[0]['date']).days)
                        ca_moyen_jour = total_ventes / delta_jours
                        st.metric("📈 CA moyen / jour", format_fcfa(ca_moyen_jour))
        
        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #6c757d; font-size: 0.8rem; padding: 1rem;'>
    <p>🛍️ ShopAnalyzer Pro v2.0 | TP - Collecte de données en ligne | Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
    <p style='font-size: 0.75rem;'>💰 Toutes les valeurs sont en Francs CFA (FCFA)</p>
</div>
""", unsafe_allow_html=True)