"""The AI Agent HA integration."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.components.frontend import async_register_built_in_panel
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .agent import AiAgentHaAgent
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Config schema - this integration only supports config entries
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

# Define service schema to accept a custom prompt
SERVICE_SCHEMA = vol.Schema(
    {
        vol.Optional("prompt"): cv.string,
    }
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the AI Agent HA component."""
    return True


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old config entries to new version."""
    _LOGGER.debug("Migrating config entry from version %s", entry.version)

    if entry.version == 1:
        # No migration needed for version 1
        return True

    # Future migrations would go here
    # if entry.version < 2:
    #     # Migrate from version 1 to 2
    #     new_data = dict(entry.data)
    #     # Add migration logic here
    #     hass.config_entries.async_update_entry(entry, data=new_data, version=2)

    _LOGGER.info("Migration to version %s successful", entry.version)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AI Agent HA from a config entry."""
    try:
        # Handle version compatibility
        if not hasattr(entry, "version") or entry.version != 1:
            _LOGGER.warning(
                "Config entry has version %s, expected 1. Attempting compatibility mode.",
                getattr(entry, "version", "unknown"),
            )

        # Convert ConfigEntry to dict and ensure all required keys exist
        config_data = dict(entry.data)

        # Ensure backward compatibility - check for required keys
        if "ai_provider" not in config_data:
            _LOGGER.error(
                "Config entry missing required 'ai_provider' key. Entry data: %s",
                config_data,
            )
            raise ConfigEntryNotReady("Config entry missing required 'ai_provider' key")

        # Ensure models dict exists and has the provider's model
        provider = config_data["ai_provider"]
        if "models" not in config_data:
            config_data["models"] = {}
            _LOGGER.debug("Models dict missing, creating new one")
        
        # If the provider's model is missing, set default and update config entry
        from .config_flow import DEFAULT_MODELS
        if provider not in config_data["models"] or not config_data["models"][provider]:
            default_model = DEFAULT_MODELS.get(provider, "")
            config_data["models"][provider] = default_model
            _LOGGER.warning(
                "Model missing for provider %s, setting default: %s. Please reconfigure to set your preferred model.",
                provider,
                default_model,
            )
            # Update the config entry to preserve the default model
            hass.config_entries.async_update_entry(entry, data=config_data)

        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {"agents": {}, "configs": {}}

        # Provider was already set above, but ensure it's still valid
        provider = config_data["ai_provider"]

        # Validate provider
        if provider not in [
            "llama",
            "openai",
            "gemini",
            "openrouter",
            "anthropic",
            "alter",
            "zai",
            "bedrock",
            "local",
        ]:
            _LOGGER.error("Unknown AI provider: %s", provider)
            raise ConfigEntryNotReady(f"Unknown AI provider: {provider}")

        # Store config for this provider
        hass.data[DOMAIN]["configs"][provider] = config_data

        # Create agent for this provider
        _LOGGER.debug(
            "Creating AI agent for provider %s with config: %s",
            provider,
            {
                k: v
                for k, v in config_data.items()
                if                 k
                not in [
                    "llama_token",
                    "openai_token",
                    "gemini_token",
                    "openrouter_token",
                    "anthropic_token",
                    "zai_token",
                    "bedrock_access_key",
                    "bedrock_secret_key",
                ]
            },
        )
        hass.data[DOMAIN]["agents"][provider] = AiAgentHaAgent(hass, config_data)

        _LOGGER.info("Successfully set up AI Agent HA for provider: %s", provider)

    except KeyError as err:
        _LOGGER.error("Missing required configuration key: %s", err)
        raise ConfigEntryNotReady(f"Missing required configuration key: {err}")
    except Exception as err:
        _LOGGER.exception("Unexpected error setting up AI Agent HA")
        raise ConfigEntryNotReady(f"Error setting up AI Agent HA: {err}")

    # Modify the query service handler to use the correct provider
    async def async_handle_query(call):
        """Handle the query service call."""
        try:
            # Check if agents are available
            if DOMAIN not in hass.data or not hass.data[DOMAIN].get("agents"):
                _LOGGER.error(
                    "No AI agents available. Please configure the integration first."
                )
                result = {"error": "No AI agents configured"}
                hass.bus.async_fire("ai_agent_ha_response", result)
                return

            provider = call.data.get("provider")
            if provider not in hass.data[DOMAIN]["agents"]:
                # Get the first available provider
                available_providers = list(hass.data[DOMAIN]["agents"].keys())
                if not available_providers:
                    _LOGGER.error("No AI agents available")
                    result = {"error": "No AI agents configured"}
                    hass.bus.async_fire("ai_agent_ha_response", result)
                    return
                provider = available_providers[0]
                _LOGGER.debug(f"Using fallback provider: {provider}")

            agent = hass.data[DOMAIN]["agents"][provider]
            result = await agent.process_query(
                call.data.get("prompt", ""),
                provider=provider,
                debug=call.data.get("debug", False),
            )
            hass.bus.async_fire("ai_agent_ha_response", result)
        except Exception as e:
            _LOGGER.error(f"Error processing query: {e}")
            result = {"error": str(e)}
            hass.bus.async_fire("ai_agent_ha_response", result)

    async def async_handle_create_automation(call):
        """Handle the create_automation service call."""
        try:
            # Check if agents are available
            if DOMAIN not in hass.data or not hass.data[DOMAIN].get("agents"):
                _LOGGER.error(
                    "No AI agents available. Please configure the integration first."
                )
                return {"error": "No AI agents configured"}

            provider = call.data.get("provider")
            if provider not in hass.data[DOMAIN]["agents"]:
                # Get the first available provider
                available_providers = list(hass.data[DOMAIN]["agents"].keys())
                if not available_providers:
                    _LOGGER.error("No AI agents available")
                    return {"error": "No AI agents configured"}
                provider = available_providers[0]
                _LOGGER.debug(f"Using fallback provider: {provider}")

            agent = hass.data[DOMAIN]["agents"][provider]
            result = await agent.create_automation(call.data.get("automation", {}))
            return result
        except Exception as e:
            _LOGGER.error(f"Error creating automation: {e}")
            return {"error": str(e)}

    async def async_handle_save_prompt_history(call):
        """Handle the save_prompt_history service call."""
        try:
            # Check if agents are available
            if DOMAIN not in hass.data or not hass.data[DOMAIN].get("agents"):
                _LOGGER.error(
                    "No AI agents available. Please configure the integration first."
                )
                return {"error": "No AI agents configured"}

            provider = call.data.get("provider")
            if provider not in hass.data[DOMAIN]["agents"]:
                # Get the first available provider
                available_providers = list(hass.data[DOMAIN]["agents"].keys())
                if not available_providers:
                    _LOGGER.error("No AI agents available")
                    return {"error": "No AI agents configured"}
                provider = available_providers[0]
                _LOGGER.debug(f"Using fallback provider: {provider}")

            agent = hass.data[DOMAIN]["agents"][provider]
            user_id = call.context.user_id if call.context.user_id else "default"
            result = await agent.save_user_prompt_history(
                user_id, call.data.get("history", [])
            )
            return result
        except Exception as e:
            _LOGGER.error(f"Error saving prompt history: {e}")
            return {"error": str(e)}

    async def async_handle_load_prompt_history(call):
        """Handle the load_prompt_history service call."""
        try:
            # Check if agents are available
            if DOMAIN not in hass.data or not hass.data[DOMAIN].get("agents"):
                _LOGGER.error(
                    "No AI agents available. Please configure the integration first."
                )
                return {"error": "No AI agents configured"}

            provider = call.data.get("provider")
            if provider not in hass.data[DOMAIN]["agents"]:
                # Get the first available provider
                available_providers = list(hass.data[DOMAIN]["agents"].keys())
                if not available_providers:
                    _LOGGER.error("No AI agents available")
                    return {"error": "No AI agents configured"}
                provider = available_providers[0]
                _LOGGER.debug(f"Using fallback provider: {provider}")

            agent = hass.data[DOMAIN]["agents"][provider]
            user_id = call.context.user_id if call.context.user_id else "default"
            result = await agent.load_user_prompt_history(user_id)
            _LOGGER.debug("Load prompt history result: %s", result)
            return result
        except Exception as e:
            _LOGGER.error(f"Error loading prompt history: {e}")
            return {"error": str(e)}

    async def async_handle_create_dashboard(call):
        """Handle the create_dashboard service call."""
        try:
            # Check if agents are available
            if DOMAIN not in hass.data or not hass.data[DOMAIN].get("agents"):
                _LOGGER.error(
                    "No AI agents available. Please configure the integration first."
                )
                return {"error": "No AI agents configured"}

            provider = call.data.get("provider")
            if provider not in hass.data[DOMAIN]["agents"]:
                # Get the first available provider
                available_providers = list(hass.data[DOMAIN]["agents"].keys())
                if not available_providers:
                    _LOGGER.error("No AI agents available")
                    return {"error": "No AI agents configured"}
                provider = available_providers[0]
                _LOGGER.debug(f"Using fallback provider: {provider}")

            agent = hass.data[DOMAIN]["agents"][provider]

            # Parse dashboard config if it's a string
            dashboard_config = call.data.get("dashboard_config", {})
            if isinstance(dashboard_config, str):
                try:
                    import json

                    dashboard_config = json.loads(dashboard_config)
                except json.JSONDecodeError as e:
                    _LOGGER.error(f"Invalid JSON in dashboard_config: {e}")
                    return {"error": f"Invalid JSON in dashboard_config: {e}"}

            result = await agent.create_dashboard(dashboard_config)
            return result
        except Exception as e:
            _LOGGER.error(f"Error creating dashboard: {e}")
            return {"error": str(e)}

    async def async_handle_update_dashboard(call):
        """Handle the update_dashboard service call."""
        try:
            # Check if agents are available
            if DOMAIN not in hass.data or not hass.data[DOMAIN].get("agents"):
                _LOGGER.error(
                    "No AI agents available. Please configure the integration first."
                )
                return {"error": "No AI agents configured"}

            provider = call.data.get("provider")
            if provider not in hass.data[DOMAIN]["agents"]:
                # Get the first available provider
                available_providers = list(hass.data[DOMAIN]["agents"].keys())
                if not available_providers:
                    _LOGGER.error("No AI agents available")
                    return {"error": "No AI agents configured"}
                provider = available_providers[0]
                _LOGGER.debug(f"Using fallback provider: {provider}")

            agent = hass.data[DOMAIN]["agents"][provider]

            # Parse dashboard config if it's a string
            dashboard_config = call.data.get("dashboard_config", {})
            if isinstance(dashboard_config, str):
                try:
                    import json

                    dashboard_config = json.loads(dashboard_config)
                except json.JSONDecodeError as e:
                    _LOGGER.error(f"Invalid JSON in dashboard_config: {e}")
                    return {"error": f"Invalid JSON in dashboard_config: {e}"}

            dashboard_url = call.data.get("dashboard_url", "")
            if not dashboard_url:
                return {"error": "Dashboard URL is required"}

            result = await agent.update_dashboard(dashboard_url, dashboard_config)
            return result
        except Exception as e:
            _LOGGER.error(f"Error updating dashboard: {e}")
            return {"error": str(e)}

    async def async_handle_save_chat_messages(call):
        """Handle the save_chat_messages service call."""
        try:
            # Check if agents are available
            if DOMAIN not in hass.data or not hass.data[DOMAIN].get("agents"):
                _LOGGER.error(
                    "No AI agents available. Please configure the integration first."
                )
                return {"error": "No AI agents configured"}

            provider = call.data.get("provider")
            if provider not in hass.data[DOMAIN]["agents"]:
                # Get the first available provider
                available_providers = list(hass.data[DOMAIN]["agents"].keys())
                if not available_providers:
                    _LOGGER.error("No AI agents available")
                    return {"error": "No AI agents configured"}
                provider = available_providers[0]
                _LOGGER.debug(f"Using fallback provider: {provider}")

            agent = hass.data[DOMAIN]["agents"][provider]
            user_id = call.context.user_id if call.context.user_id else "default"
            messages = call.data.get("messages", [])
            
            result = await agent.save_chat_messages(user_id, messages, provider)
            return result
        except Exception as e:
            _LOGGER.error(f"Error saving chat messages: {e}")
            return {"error": str(e)}

    async def async_handle_load_chat_messages(call):
        """Handle the load_chat_messages service call."""
        try:
            # Check if agents are available
            if DOMAIN not in hass.data or not hass.data[DOMAIN].get("agents"):
                _LOGGER.error(
                    "No AI agents available. Please configure the integration first."
                )
                return {"error": "No AI agents configured"}

            provider = call.data.get("provider")
            if provider not in hass.data[DOMAIN]["agents"]:
                # Get the first available provider
                available_providers = list(hass.data[DOMAIN]["agents"].keys())
                if not available_providers:
                    _LOGGER.error("No AI agents available")
                    return {"error": "No AI agents configured"}
                provider = available_providers[0]
                _LOGGER.debug(f"Using fallback provider: {provider}")

            agent = hass.data[DOMAIN]["agents"][provider]
            user_id = call.context.user_id if call.context.user_id else "default"
            
            result = await agent.load_chat_messages(user_id, provider)
            return result
        except Exception as e:
            _LOGGER.error(f"Error loading chat messages: {e}")
            return {"error": str(e)}

    # Register services
    hass.services.async_register(DOMAIN, "query", async_handle_query)
    hass.services.async_register(
        DOMAIN, "create_automation", async_handle_create_automation
    )
    hass.services.async_register(
        DOMAIN, "save_prompt_history", async_handle_save_prompt_history
    )
    hass.services.async_register(
        DOMAIN, "load_prompt_history", async_handle_load_prompt_history
    )
    hass.services.async_register(
        DOMAIN, "create_dashboard", async_handle_create_dashboard
    )
    hass.services.async_register(
        DOMAIN, "update_dashboard", async_handle_update_dashboard
    )
    hass.services.async_register(
        DOMAIN, "save_chat_messages", async_handle_save_chat_messages
    )
    hass.services.async_register(
        DOMAIN, "load_chat_messages", async_handle_load_chat_messages
    )

    # Register static path for frontend
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                "/frontend/ai_agent_ha",
                hass.config.path("custom_components/ai_agent_ha/frontend"),
                False,
            )
        ]
    )

    # Panel registration with proper error handling
    panel_name = "ai_agent_ha"
    try:
        if await _panel_exists(hass, panel_name):
            _LOGGER.debug("AI Agent HA panel already exists, skipping registration")
            return True

        _LOGGER.debug("Registering AI Agent HA panel")
        async_register_built_in_panel(
            hass,
            component_name="custom",
            sidebar_title="AI Agent HA",
            sidebar_icon="mdi:robot",
            frontend_url_path=panel_name,
            require_admin=False,
            config={
                "_panel_custom": {
                    "name": "ai_agent_ha-panel",
                    "module_url": "/frontend/ai_agent_ha/ai_agent_ha-panel.js",
                    "embed_iframe": False,
                }
            },
        )
        _LOGGER.debug("AI Agent HA panel registered successfully")
    except Exception as e:
        error_msg = str(e)
        # If it's just a warning about overwriting, that's okay - panel already exists
        if "overwriting" in error_msg.lower() or "already exists" in error_msg.lower():
            _LOGGER.debug("Panel already registered (overwrite warning): %s", error_msg)
        else:
            _LOGGER.warning("Panel registration error: %s", error_msg)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if await _panel_exists(hass, "ai_agent_ha"):
        try:
            from homeassistant.components.frontend import async_remove_panel

            async_remove_panel(hass, "ai_agent_ha")
            _LOGGER.debug("AI Agent HA panel removed successfully")
        except Exception as e:
            _LOGGER.debug("Error removing panel: %s", str(e))

    # Remove services
    hass.services.async_remove(DOMAIN, "query")
    hass.services.async_remove(DOMAIN, "create_automation")
    hass.services.async_remove(DOMAIN, "save_prompt_history")
    hass.services.async_remove(DOMAIN, "load_prompt_history")
    hass.services.async_remove(DOMAIN, "create_dashboard")
    hass.services.async_remove(DOMAIN, "update_dashboard")
    hass.services.async_remove(DOMAIN, "save_chat_messages")
    hass.services.async_remove(DOMAIN, "load_chat_messages")
    # Remove data
    if DOMAIN in hass.data:
        hass.data.pop(DOMAIN)

    return True


async def _panel_exists(hass: HomeAssistant, panel_name: str) -> bool:
    """Check if a panel already exists."""
    try:
        # Check in hass.data.frontend_panels (newer HA versions)
        if hasattr(hass.data, "frontend_panels"):
            panels = hass.data.get("frontend_panels", {})
            if panel_name in panels:
                return True
        
        # Also check if panel is registered via frontend component
        if hasattr(hass.components, "frontend"):
            frontend = hass.components.frontend
            if hasattr(frontend, "panels"):
                if panel_name in frontend.panels:
                    return True
        
        return False
    except Exception as e:
        _LOGGER.debug("Error checking panel existence: %s", str(e))
        return False
