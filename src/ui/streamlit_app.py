import streamlit as st
import logging
from config.logger_config import setup_logger
from pathlib import Path

from src.ui.components.model_selector import ModelSelector
from src.ui.components.database_viewer import DatabaseViewer
from src.generator.generator_manager import GeneratorManager
from src.ui.pages.home import HomePage
from src.ui.pages.settings import SettingsPage
from config.config import test_user_id

logger = setup_logger(__name__, level=logging.INFO)

class StreamlitApp:
    def __init__(self):
        # Configure the page
        st.set_page_config(
            page_title="Resume Builder TeX",
            page_icon="📝",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Load and apply CSS
        self._load_css()
        
        # Initialize session state first - Call it explicitly
        self.setup_session_state()  # Changed from static method to instance method
        
        # Initialize components after session state is set up
        self.model_selector = ModelSelector()
        self.generator_manager = GeneratorManager(st.session_state['user_id'])
        
        # Initialize pages
        self.home_page = HomePage(self.model_selector, self.generator_manager)
        self.settings_page = SettingsPage(self.model_selector)
        
        if 'components_initialized' not in st.session_state:
            self._store_components()
            st.session_state['components_initialized'] = True

    def _store_components(self):
        """Store components in session state"""
        st.session_state['model_selector'] = self.model_selector
        st.session_state['generator_manager'] = self.generator_manager
        logger.debug("Components stored in session state")

    def setup_session_state(self):  # Removed @staticmethod and @st.cache_resource
        """Initialize session state variables"""
        if 'user_id' not in st.session_state:
            logger.debug(f"Setting user_id in session state to: {test_user_id}")
            st.session_state['user_id'] = test_user_id
        else:
            logger.debug(f"Current user_id in session state: {st.session_state['user_id']}")
        if 'portfolio_initialized' not in st.session_state:
            st.session_state['portfolio_initialized'] = False

    def _load_css(self):
        css_file = Path(__file__).parent / "static" / "styles.css"
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    def run(self):
        logger.info("Starting StreamlitApp")
        st.title("Resume Builder TeX")
        
        # Sidebar navigation
        with st.sidebar:
            # Center the logo
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                try:
                    ico_path = Path(__file__).parent / "ico" / "ico.png"
                    if ico_path.exists():
                        with open(ico_path, "rb") as f:
                            image_data = f.read()
                        st.image(image_data, width=80)
                except Exception as e:
                    logger.error(f"Error loading icon: {e}")
                    st.markdown("")
            
            # Navigation menu using buttons
            if 'current_page' not in st.session_state:
                st.session_state.current_page = "home"
            
            # Navigation buttons
            if st.button("🏠 Home", key="nav_home", use_container_width=True):
                st.session_state.current_page = "home"
                
            if st.button("⚙️ Settings", key="nav_settings", use_container_width=True):
                st.session_state.current_page = "settings"
                
            if st.button("🗄️ Database", key="nav_database", use_container_width=True):
                st.session_state.current_page = "database"
                
            
        # Render selected page
        if st.session_state.current_page == "home":
            self.home_page.render()
        elif st.session_state.current_page == "settings":
            self.settings_page.render()
        else:
            DatabaseViewer().render()
