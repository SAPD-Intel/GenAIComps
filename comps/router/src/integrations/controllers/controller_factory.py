from typing import Dict
import yaml
from comps.router.src.integrations.controllers.routellm.routellm_controller import RouteLLMController
from comps.router.src.integrations.controllers.semantic_router.semantic_router_controller import SemanticRouterController
import os
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv('HF_TOKEN', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

class ControllerFactory:

    @staticmethod
    def get_controller_config(config_filename: str) -> Dict:
        try:
            with open(config_filename, "r") as file:
                config = yaml.safe_load(file)
            return config
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Configuration file '{config_filename}' not found.") from e
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing the configuration file: {e}") from e
    
    @staticmethod
    def factory(controller_config: str, model_map: Dict):
        """Returns an instance of the appropriate controller based on the controller_type."""

        config = ControllerFactory.get_controller_config(controller_config)
        controller_type = config.get("controller_type", "routellm")
        
        if controller_type == "routellm":
            return RouteLLMController(config=config, api_key=OPENAI_API_KEY, hf_token=HF_TOKEN, model_map=model_map)
        
        elif controller_type == "semantic_router":
            return SemanticRouterController(
                config=config, 
                api_key=OPENAI_API_KEY, 
                model_map=model_map
            )
        else:
            raise ValueError(f"Unknown controller type: {controller_type}")
