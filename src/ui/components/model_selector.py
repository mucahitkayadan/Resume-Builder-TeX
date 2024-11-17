import streamlit as st

class ModelSelector:
    def __init__(self):
        self.model_types = ["OpenAI", "Claude", "Ollama"]
        self.model_options = {
            "OpenAI": ["gpt-4o", "gpt-4o-mini", "gpt-4o-2024-08-06", "o1-mini",
                                            "gpt-4o-2024-05-13"],
            "Claude": ["claude-3-5-sonnet-latest", "claude-3-opus-latest",
                                                                    "claude-3-5-sonnet-20241022",
                                                                    "claude-3-5-sonnet-20240620",
                                                                    "claude-3-opus-20240229",
                                                                    "claude-3-sonnet-20240229"],
            "Ollama": ["llama3.1", "llama2", "llama2-uncensored", "mistral", 
                                                                   "mixtral", "codellama", "neural-chat"]
        }

    def get_model_settings(self):
        """
        Creates a UI for selecting AI model settings.
        
        Returns:
            tuple: (model_type, model_name, temperature) containing the selected settings
        """
        st.subheader("Model Settings")

        # Model type selection
        model_type = st.selectbox(
            "Select Model Type",
            self.model_types,
            index=0
        )

        # Model name selection based on type
        model_name = st.selectbox(
            "Select Model",
            self.model_options[model_type],
            index=0
        )

        # Temperature slider
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.1,
            help="Higher values make the output more creative but less focused"
        )

        return model_type, model_name, temperature
