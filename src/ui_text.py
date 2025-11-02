#!/usr/bin/env python3
"""
UI Text Constants

All user-facing text should be defined here for easy internationalization.
This keeps the code clean and allows for future localization.
"""

# Main UI Text
MAIN_UI = {
    "title": "CAFA - Context Auto Feed Agent",
    "welcome_message": """
=================================
Welcome to CAFA (Context Auto Feed Agent)
=================================

Features:
• 🤖 Select Model - Local LLM or Online API
• 🔑 Set API Key - Automatic provider detection
• 🧠 Memory Management - Intelligent memory storage
• 💬 Context-aware conversation

Shortcuts:
• Ctrl+Enter - Send message

Start chatting now!
=================================
""",
}

# Button Text
BUTTONS = {
    "select_model": "🤖 Select Model",
    "set_api": "🔑 Set API",
    "memory": "Memory Management",
    "clear": "Clear",
    "detect": "Detect",
    "cancel": "Cancel",
    "confirm": "Confirm",
    "confirm_and_set": "Confirm and Set",
    "show_key": "Show Key",
    "hide_key": "Hide Key",
    "store": "Store",
    "recall": "Recall",
    "refresh_stats": "Refresh Stats",
}

# Model Selection Dialog
MODEL_SELECTION = {
    "title": "🤖 Select Model Service",
    "subtitle": "Choose between local model or online API service",
    "local_title": "Local Model (Gemma)",
    "local_running": "• Uses local Gemma-3-12B model\n• No API key required\n• Fully offline",
    "local_not_running": "• Service not running\n• Please start local model server first",
    "online_title": "Online API (GPT/Claude etc.)",
    "online_running": "• Supports OpenAI, Anthropic, etc.\n• API key required\n• More powerful models",
    "online_not_running": "• Service not running\n• Please start online API server first",
    "no_service_warning": "⚠️ No available service, please start a model server first",
    "switch_success": "Switched to: {service_name} ({url})",
}

# API Key Dialog
API_KEY_DIALOG = {
    "title": "🔑 Set API Key",
    "subtitle": "Enter your API key, system will automatically detect the provider\n💡 For Ollama (local): just enter 'ollama'",
    "input_label": "API Key (or 'ollama' for local)",
    "result_label": "Detection Result",
    "initial_text": "Enter API key and click 'Detect' button to identify...\n\n💡 Tip: For Ollama local service, just enter 'ollama'",
    "format_valid": "✅ API key format validation passed\n\n",
    "detected_provider": "Detected provider: {provider}\n",
    "confidence": "Confidence: {confidence:.0f}%\n\n",
    "description": "Description: {description}\n\n",
    "api_url": "API URL: {base_url}\n",
    "default_model": "Default model: {model}\n",
    "supported_models": "\nSupported models:\n",
    "model_item": "  • {model}\n",
    "model_count": "  ... and {count} more models\n",
    "warning": "\n⚠️  {warning}\n",
    "validation_failed": "❌ Validation failed\n\n{error}",
    "request_failed": "❌ Request failed (HTTP {status_code})",
    "set_success": "API key set successfully!\n\nProvider: {provider}\nModel: {model}",
    "set_failed": "Setting failed",
}

# Memory Management Dialog
MEMORY_DIALOG = {
    "title": "Memory Management",
    "store_tab": "Store Memory",
    "recall_tab": "Recall Memory",
    "stats_tab": "Memory Stats",
    "store_label": "Enter memory to store:",
    "store_success": "Success",
    "store_success_msg": "Memory stored successfully!",
    "recall_label": "Enter search keywords:",
    "recall_button": "Recall",
    "matches_found": "Found {count} matching memories:\n\n",
    "match_item": "{index}. [{similarity:.3f}] {text}\n\n",
    "no_matches": "No matching memories found.",
    "stats_title": "Memory Service Statistics\n=================================\n\n",
    "stats_url": "Service URL: {url}\n",
    "stats_status": "Status: {status}\n\n",
    "stats_endpoints": "API Endpoints:\n• Store: POST /store\n• Recall: GET /recall\n• Decay: POST /decay\n\n",
    "stats_docs": "Documentation:\n• Swagger UI: {url}/docs\n• ReDoc: {url}/redoc\n\n",
    "stats_features": "Features:\n✓ Semantic search\n✓ Memory weight management\n✓ Automatic decay\n✓ Similarity matching\n\n=================================\n",
    "memory_not_enabled": "Memory feature not enabled",
    "memory_not_enabled_msg": "Memory server is not running!\n\nPlease start memory server:\npython run_memory_api.py",
}

# Messages
MESSAGES = {
    "empty_input": "Input is empty",
    "enter_api_key": "Please enter API key!",
    "enter_memory": "Please enter memory content!",
    "enter_keywords": "Please enter search keywords!",
    "no_selection": "No selection",
    "select_service": "Please select a model service!",
    "timeout": "Timeout",
    "timeout_msg": "Request timeout, please check if server is running",
    "connection_failed": "Connection failed",
    "connection_failed_msg": "Cannot connect to server, please ensure online API server is running",
    "error": "Error",
    "error_occurred": "Error occurred: {error}",
    "request_timeout": "Request timeout",
    "cannot_connect": "Cannot connect to server",
}

# Status Messages
STATUS = {
    "api_detecting": "API: Detecting...",
    "api_connected": "API: {provider}/{model}",
    "api_not_connected": "API: Not connected",
    "memory_detecting": "Memory: Detecting...",
    "memory_enabled": "Memory: Enabled",
    "memory_not_enabled": "Memory: Not enabled",
    "system_prefix": "System: ",
    "user_prefix": "User",
    "assistant_prefix": "Assistant",
}

# Chat Messages (system messages in English, can be translated)
CHAT = {
    "api_switch": "Switched to: {service_name} ({url})",
    "relevant_memory": "\nRelevant memory: {memories}",
    "request_failed": "Request failed: HTTP {status_code}",
    "request_timeout": "Request timeout",
    "no_server": "Cannot connect to server",
}


def get_text(key_path, **kwargs):
    """
    Get UI text by key path.
    
    Args:
        key_path: Dot-separated key path (e.g., "BUTTONS.confirm")
        **kwargs: Format parameters for string formatting
    
    Returns:
        Formatted text string
    
    Example:
        >>> get_text("MODEL_SELECTION.switch_success", service_name="Local", url="http://localhost:5000")
        "Switched to: Local (http://localhost:5000)"
    """
    parts = key_path.split('.')
    value = globals()[parts[0]]
    
    for part in parts[1:]:
        value = value[part]
    
    if kwargs:
        return value.format(**kwargs)
    return value

