"""
Bubbabags Marketing Intelligence Platform
Dashboard ejecutivo para análisis de campañas
"""
import streamlit as st
import pandas as pd
from src.agent.agent import ask
from src.data.views import get_channel_summary, get_campaign_performance_monthly
from src.modeling.predict import get_prediction_summary, get_top_campaigns_by_predicted_roas

# =============================================================================
# CONFIGURACIÓN DE PÁGINA
# =============================================================================
st.set_page_config(
    page_title="Bubbabags | Marketing Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# ESTILOS CSS PERSONALIZADOS
# =============================================================================
st.markdown("""
<style>
    /* Fuente principal */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Header principal */
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 2rem 2.5rem;
        border-radius: 0 0 16px 16px;
        margin: -6rem -4rem 2rem -4rem;
        color: white;
    }
    
    .main-header h1 {
        font-size: 1.75rem;
        font-weight: 600;
        margin: 0;
        color: white;
    }
    
    .main-header p {
        font-size: 0.95rem;
        color: #a0aec0;
        margin: 0.5rem 0 0 0;
    }
    
    /* Cards de métricas */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    .metric-label {
        font-size: 0.8rem;
        font-weight: 500;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    .metric-delta-positive {
        font-size: 0.85rem;
        color: #059669;
        font-weight: 500;
    }
    
    .metric-delta-negative {
        font-size: 0.85rem;
        color: #dc2626;
        font-weight: 500;
    }
    
    /* Sección del chat */
    .chat-section {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
    }
    
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    /* Mensajes del chat */
    .user-message {
        background: #1e293b;
        color: white;
        padding: 1rem 1.25rem;
        border-radius: 12px 12px 4px 12px;
        margin: 0.75rem 0;
        font-size: 0.95rem;
    }
    
    .assistant-message {
        background: white;
        color: #1e293b;
        padding: 1rem 1.25rem;
        border-radius: 12px 12px 12px 4px;
        margin: 0.75rem 0;
        border: 1px solid #e2e8f0;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Sidebar */
    .sidebar-section {
        background: #f1f5f9;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .sidebar-title {
        font-size: 0.75rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.75rem;
    }
    
    /* Tabla de datos */
    .dataframe {
        font-size: 0.85rem;
    }
    
    /* Input del chat */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        padding: 0.75rem 1rem;
        font-size: 0.95rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Botones */
    .stButton > button {
        background: #1e293b;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    .stButton > button:hover {
        background: #334155;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: #f1f5f9;
        border-radius: 8px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================
@st.cache_data(ttl=300)
def load_channel_data():
    """Carga datos de canales con cache."""
    try:
        return get_channel_summary()
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_top_campaigns():
    """Carga top campañas con cache."""
    try:
        return get_top_campaigns_by_predicted_roas(top_n=5)
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_monthly_performance():
    """Carga rendimiento mensual con cache."""
    try:
        return get_campaign_performance_monthly()
    except Exception as e:
        return pd.DataFrame()

def format_number(num, prefix="", suffix=""):
    """Formatea números para display."""
    if num >= 1_000_000:
        return f"{prefix}{num/1_000_000:.2f}M{suffix}"
    elif num >= 1_000:
        return f"{prefix}{num/1_000:.1f}K{suffix}"
    else:
        return f"{prefix}{num:.2f}{suffix}"

# =============================================================================
# HEADER
# =============================================================================
st.markdown("""
<div class="main-header">
    <h1>Bubbabags Marketing Intelligence</h1>
    <p>Plataforma de análisis y predicción de campañas publicitarias</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# MÉTRICAS PRINCIPALES
# =============================================================================
channel_data = load_channel_data()

if not channel_data.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    google_data = channel_data[channel_data['channel'] == 'google_ads'].iloc[0] if len(channel_data[channel_data['channel'] == 'google_ads']) > 0 else None
    meta_data = channel_data[channel_data['channel'] == 'meta_ads'].iloc[0] if len(channel_data[channel_data['channel'] == 'meta_ads']) > 0 else None
    
    with col1:
        total_investment = channel_data['total_cost'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Inversión Total</div>
            <div class="metric-value">{format_number(total_investment, "$")}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_revenue = channel_data['total_revenue'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Revenue Total</div>
            <div class="metric-value">{format_number(total_revenue, "$")}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_roas = total_revenue / total_investment if total_investment > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">ROAS Promedio</div>
            <div class="metric-value">{avg_roas:.2f}x</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_campaigns = int(channel_data['total_campaigns'].sum())
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Campañas Activas</div>
            <div class="metric-value">{total_campaigns}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =============================================================================
# CONTENIDO PRINCIPAL
# =============================================================================
tab1, tab2, tab3 = st.tabs(["Consultas", "Rendimiento por Canal", "Top Campañas"])

# -----------------------------------------------------------------------------
# TAB 1: CONSULTAS (CHAT)
# -----------------------------------------------------------------------------
with tab1:
    col_chat, col_info = st.columns([2, 1])
    
    with col_chat:
        st.markdown('<div class="section-title">Asistente de Análisis</div>', unsafe_allow_html=True)
        
        # Inicializar historial
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Container para mensajes
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)
        
        # Input
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "Escribe tu consulta",
                placeholder="Ej: ¿Cuál canal tiene mejor ROAS?",
                label_visibility="collapsed"
            )
            submit = st.form_submit_button("Enviar consulta")
        
        if submit and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            with st.spinner("Procesando consulta..."):
                try:
                    response = ask(user_input)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Error al procesar la consulta: {str(e)}"
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            
            st.rerun()
    
    with col_info:
        st.markdown('<div class="section-title">Consultas Sugeridas</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-section">
            <div class="sidebar-title">Comparativas</div>
            <p style="font-size: 0.9rem; color: #475569; margin: 0.25rem 0;">¿Cuál canal tiene mejor ROAS?</p>
            <p style="font-size: 0.9rem; color: #475569; margin: 0.25rem 0;">Compara Google Ads vs Meta Ads</p>
        </div>
        
        <div class="sidebar-section">
            <div class="sidebar-title">Rendimiento</div>
            <p style="font-size: 0.9rem; color: #475569; margin: 0.25rem 0;">¿Cuál fue la mejor campaña?</p>
            <p style="font-size: 0.9rem; color: #475569; margin: 0.25rem 0;">¿Cómo evolucionó el CTR?</p>
        </div>
        
        <div class="sidebar-section">
            <div class="sidebar-title">Predicciones</div>
            <p style="font-size: 0.9rem; color: #475569; margin: 0.25rem 0;">¿Qué campaña tendrá mejor rendimiento?</p>
            <p style="font-size: 0.9rem; color: #475569; margin: 0.25rem 0;">¿Dónde debería invertir más?</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">Modelos Predictivos</div>', unsafe_allow_html=True)
        
        pred_info = get_prediction_summary()
        
        st.markdown(f"""
        <div class="sidebar-section">
            <div class="sidebar-title">Google Ads</div>
            <p style="font-size: 0.85rem; color: #1e293b; margin: 0;"><strong>Modelo:</strong> XGBoost</p>
            <p style="font-size: 0.85rem; color: #059669; margin: 0.25rem 0 0 0;">R² 0.684 | +24.1% vs baseline</p>
        </div>
        
        <div class="sidebar-section">
            <div class="sidebar-title">Meta Ads</div>
            <p style="font-size: 0.85rem; color: #1e293b; margin: 0;"><strong>Modelo:</strong> Baseline histórico</p>
            <p style="font-size: 0.85rem; color: #64748b; margin: 0.25rem 0 0 0;">R² 0.567</p>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 2: RENDIMIENTO POR CANAL
# -----------------------------------------------------------------------------
with tab2:
    st.markdown('<div class="section-title">Comparativa de Canales</div>', unsafe_allow_html=True)
    
    if not channel_data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Google Ads")
            if google_data is not None:
                metrics_google = {
                    "Campañas": int(google_data['total_campaigns']),
                    "Impresiones": format_number(google_data['total_impressions']),
                    "Clicks": format_number(google_data['total_clicks']),
                    "Inversión": format_number(google_data['total_cost'], "$"),
                    "Revenue": format_number(google_data['total_revenue'], "$"),
                    "CTR": f"{google_data['avg_ctr']*100:.2f}%",
                    "ROAS": f"{google_data['avg_roas']:.2f}x"
                }
                for label, value in metrics_google.items():
                    st.markdown(f"**{label}:** {value}")
        
        with col2:
            st.markdown("#### Meta Ads")
            if meta_data is not None:
                metrics_meta = {
                    "Campañas": int(meta_data['total_campaigns']),
                    "Impresiones": format_number(meta_data['total_impressions']),
                    "Clicks": format_number(meta_data['total_clicks']),
                    "Inversión": format_number(meta_data['total_cost'], "$"),
                    "Revenue": format_number(meta_data['total_revenue'], "$"),
                    "CTR": f"{meta_data['avg_ctr']*100:.2f}%",
                    "ROAS": f"{meta_data['avg_roas']:.2f}x"
                }
                for label, value in metrics_meta.items():
                    st.markdown(f"**{label}:** {value}")

# -----------------------------------------------------------------------------
# TAB 3: TOP CAMPAÑAS
# -----------------------------------------------------------------------------
with tab3:
    st.markdown('<div class="section-title">Campañas con Mejor ROAS</div>', unsafe_allow_html=True)
    
    top_campaigns = load_top_campaigns()
    
    if not top_campaigns.empty:
        display_df = top_campaigns[['campaign_name', 'channel', 'predicted_roas', 'cost', 'revenue']].copy()
        display_df.columns = ['Campaña', 'Canal', 'ROAS', 'Inversión', 'Revenue']
        display_df['Campaña'] = display_df['Campaña'].str[:50]
        display_df['ROAS'] = display_df['ROAS'].apply(lambda x: f"{x:.2f}x")
        display_df['Inversión'] = display_df['Inversión'].apply(lambda x: f"${x:,.2f}")
        display_df['Revenue'] = display_df['Revenue'].apply(lambda x: f"${x:,.2f}")
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No hay datos disponibles")

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 0.8rem; padding: 1rem; border-top: 1px solid #e2e8f0;">
    Bubbabags Marketing Intelligence Platform | Datos actualizados desde BigQuery
</div>
""", unsafe_allow_html=True)