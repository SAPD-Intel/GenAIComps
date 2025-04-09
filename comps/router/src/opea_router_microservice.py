import os
import logging
import yaml
from comps import (
    CustomLogger,
    TextDoc,
    ServiceType,
    register_microservice,
    opea_microservices,
)
from comps.router.src.integrations.controllers.controller_factory import ControllerFactory
from pydantic import BaseModel, Field

# Data model for endpoint response
class RouteEndpointDoc(BaseModel):
    url: str = Field(..., description="URL of the chosen inference endpoint")

# Set up logging
logger = CustomLogger("opea_router_microservice")
logflag = os.getenv("LOGFLAG", False)

CONFIG_PATH = os.getenv("CONFIG_PATH", "/app/config.yaml")

_config_data = {}
_controller_factory = None
_controller = None

def _load_config():
    global _config_data, _controller_factory, _controller

    try:
        with open(CONFIG_PATH, "r") as f:
            new_data = yaml.safe_load(f) or {}
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        raise RuntimeError(f"Failed to load config: {e}")

    _config_data = new_data
    logger.info(f"[Router] Loaded config data from: {CONFIG_PATH}")

    if _controller_factory is None:
        _controller_factory = ControllerFactory()

    model_map = _config_data.get("model_map", {})
    controller_config_path = _config_data.get("controller_config_path")

    _controller = _controller_factory.factory(
        controller_config=controller_config_path,
        model_map=model_map
    )

    logger.info("[Router] Controller re-initialized successfully.")

# Initial config load at startup
_load_config()

@register_microservice(
    name="opea_service@router",
    service_type=ServiceType.LLM,
    endpoint="/v1/route",
    host="0.0.0.0",
    port=6000,
    input_datatype=TextDoc,
    output_datatype=RouteEndpointDoc,
)
def route_microservice(input: TextDoc) -> RouteEndpointDoc:
    """
    Microservice that decides which model endpoint is best for the given text input.
    Returns only the route URL (does not forward).
    """
    if not _controller:
        raise RuntimeError("Controller is not initialized — config load failed?")

    query_content = input.text
    messages = [{"content": query_content}]

    try:
        endpoint = _controller.route(messages)
        if not endpoint:
            raise ValueError("No suitable model endpoint found.")
        return RouteEndpointDoc(url=endpoint)

    except Exception as e:
        logger.error(f"[Router] Error during model routing: {e}")
        raise

if __name__ == "__main__":
    logger.info("OPEA Router Microservice is starting...")
    opea_microservices["opea_service@router"].start()
