# PersonaLock Project Blueprint

## 1. Executive Summary
PersonaLock is a multi-platform AI companion designed to offer personalized support, primarily focusing on mental wellness. The application aims to provide a local-first, privacy-centric AI experience, allowing users to interact with an AI assistant that understands their emotional state, provides relevant information, and helps manage their mental well-being. The core value proposition lies in its ability to offer personalized, secure, and private AI interactions, adapting to the user's emotional context and offering proactive support without relying heavily on external cloud services for sensitive data processing.

## 2. Tech Stack & Architecture

### Language & Frameworks
- **Python**: For the AI backend, personality engine, memory management, and various AI backend integrations (LLM Studio, Ollama, Claude, OpenAI, Groq, DeepSeek).
- **Flutter (Dart)**: For the cross-platform mobile and desktop wellness application (`personalock_wellness/`).
- **JavaScript/Node.js**: Likely for the `facility_dashboard/` and `PersonaLock_Dashboard/` components, indicated by `server.py` and `requirements.txt` in these directories, although the `.js` files are not explicitly listed in the top level. The `PersonaLock_Dashboard/requirements.txt` indicates a Python backend for the dashboard.

### Key Dependencies

**Python Backend (`pyproject.toml`):**
- `neo4j`: Graph database for structured memory and relationships.
- `chromadb`: Vector database for semantic memory search and embeddings.
- `anthropic`, `google-generativeai`, `llm`, `llm-claude-3`, `llm-gemini`, `ollama`, `openai`, `typer`, `groq`: Various AI model integrations and CLI framework.
- `pydantic`: Data validation and settings management.
- `python-dotenv`: Environment variable management.
- `pyyaml`: Configuration file parsing.
- `realtimestt`, `realtimetts`, `elevenlabs`, `pyttsx3`: Real-time speech-to-text and text-to-speech capabilities.
- `python-telegram-bot`: Telegram integration for the business edition.

**Flutter Frontend (`personalock_wellness/pubspec.yaml`):**
- `flutter`: Core Flutter framework.
- `sqflite_sqlcipher`: Encrypted SQLite database for local-first data storage.
- `path_provider`, `path`: File system utilities.
- `flutter_secure_storage`: Secure key-value storage.
- `uuid`: UUID generation.
- `provider`: State management.
- `http`: HTTP client for API calls.
- `url_launcher`: For launching URLs (phone, SMS, web).
- `share_plus`: For data export/sharing.
- `local_auth`: Biometric and PIN authentication.

### Infrastructure Pattern
PersonaLock employs a hybrid architecture with a strong emphasis on local-first processing and privacy. The core AI logic, personality engine, and memory management are primarily Python-based, designed to run locally or connect to various local/cloud LLM backends. The Flutter application serves as a rich client, communicating with these local AI services and managing user-specific data securely on the device using an encrypted SQLite database. 

**Data Flow:**
- **User Input (Flutter App)**: User interacts with chat or mood tracking features.
- **Frontend Logic (Flutter)**: `ChatController`, `MoodController` process UI events and interact with core services.
- **AI Coordination (Flutter Services)**: `AIService`, `AICoordinator`, `PersonaService` orchestrate calls to the backend AI.
- **Local Data Storage (Flutter App)**: `DatabaseHelper` and `Encryption` manage an `sqflite_sqlcipher` database for conversations, mood entries, memories, etc.
- **AI Backend (Python)**: The Python modules (`modules/`) handle:
  - **Personality Engine**: `modules/personality_engine/engine.py` loads persona profiles and applies edition-specific overrides from `assets/persona.json`.
  - **Memory Management**: `modules/memory_vault/memory_manager.py` uses `neo4j_client.py` (graph DB) and `chroma_store.py` (vector DB) for long-term memory, context recall, and relationship management.
  - **Brain Backends**: `modules/brain_backends/` provides a factory (`brain_factory.py`) and implementations for various LLMs (LM Studio, Ollama, Claude, OpenAI, Groq), allowing for flexible AI model integration.
  - **Task Management**: `modules/task_manager.py` for managing scheduled tasks like morning briefings.
- **Dashboards (Python/Web)**: `facility_dashboard/` and `PersonaLock_Dashboard/` suggest separate web-based interfaces for monitoring or management, likely interacting with the same core Python services or data stores.

## 3. Target Directory Tree

```
.editorconfig
.env.sample
.gitignore
assistant_config.yml
main_base_assistant.py
main_telegram.py
main_typer_assistant.py
pyproject.toml
README.md
start_server.bat

├── ai_docs/
│   └── ai_docs.md
├── api/
│   └── routes.py
├── assets/
│   └── persona.json
├── commands/
│   ├── template_empty.py
│   └── template.py
├── core/
│   └── personality_engine.py
├── data/
│   └── chroma/
├── facility_dashboard/ (likely web UI/backend)
│   ├── delete_seed.py
│   ├── seed_data.py
│   └── server.py
├── llm/
│   ├── inference.py
│   └── local_inference.py
├── memory/
│   ├── embeddings.py
│   └── memory_vault.py
├── modules/
│   ├── assistant_config.py
│   ├── base_assistant.py
│   ├── data_types.py
│   ├── deepseek.py
│   ├── execute_python.py
│   ├── lm_studio.py
│   ├── morning_briefing.py
│   ├── ollama.py
│   ├── stability_helpers.py
│   ├── task_manager.py
│   ├── telegram_bridge.py
│   ├── typer_agent.py
│   └── utils.py
│   ├── brain_backends/
│   │   ├── __init__.py
│   │   ├── base_backend.py
│   │   ├── brain_factory.py
│   │   ├── claude_backend.py
│   │   ├── groq_backend.py
│   │   ├── lm_studio_backend.py
│   │   ├── openai_backend.py
│   │   └── ollama_backend.py
│   ├── memory_vault/
│   │   ├── chroma_store.py
│   │   ├── memory_manager.py
│   │   └── neo4j_client.py
│   └── personality_engine/
│       ├── __init__.py
│       ├── api.py
│       ├── engine.py
│       └── profile.py
├── PersonaLock_Dashboard/ (likely web UI/backend)
│   ├── requirements.txt
│   ├── server.py
│   └── START_SERVER.bat
├── personalock_wellness/ (Flutter App)
│   ├── .gitignore
│   ├── pubspec.yaml
│   ├── README.md
│   ├── android/
│   ├── assets/
│   │   ├── icons/
│   │   └── persona.json
│   ├── ios/
│   ├── lib/
│   │   ├── app.dart
│   │   ├── main.dart
│   │   ├── screens/
│   │   │   ├── home_screen.dart
│   │   │   └── support_network_screen.dart
│   │   ├── widgets/
│   │   │   └── common/
│   │   ├── core/
│   │   │   ├── config/
│   │   │   │   ├── constants.dart
│   │   │   │   ├── system_prompt.dart
│   │   │   │   └── theme.dart
│   │   │   ├── database/
│   │   │   │   ├── database_helper.dart
│   │   │   │   ├── encryption.dart
│   │   │   │   └── schema.dart
│   │   │   ├── models/
│   │   │   │   ├── conversation.dart
│   │   │   │   ├── message.dart
│   │   │   │   ├── memory.dart
│   │   │   │   ├── mood_entry.dart
│   │   │   │   ├── pattern.dart
│   │   │   │   └── support_contact.dart
│   │   │   └── services/
│   │   │       ├── ai_coordinator.dart
│   │   │       ├── ai_service.dart
│   │   │       ├── memory_extraction_service.dart
│   │   │       ├── memory_service.dart
│   │   │       ├── observer_service.dart
│   │   │       ├── persona_service.dart
│   │   │       ├── privacy_service.dart
│   │   │       ├── prompt_builder.dart
│   │   │       ├── providers/
│   │   │       │   └── venice_ai_provider.dart
│   │   │       ├── report_service.dart
│   │   │       └── storage_service.dart
│   │   └── features/
│   │       ├── auth/
│   │       │   ├── auth_gate.dart
│   │       │   ├── auth_service.dart
│   │       │   ├── pin_entry_screen.dart
│   │       │   └── pin_setup_screen.dart
│   │       ├── chat/
│   │       │   ├── chat_controller.dart
│   │       │   └── chat_screen.dart
│   │       ├── crisis/
│   │       │   └── crisis_resources_screen.dart
│   │       ├── mood/
│   │       │   ├── mood_checkin_screen.dart
│   │       │   ├── mood_controller.dart
│   │       │   └── mood_screen.dart
│   │       ├── onboarding/
│   │       │   └── onboarding_screen.dart
│   │       ├── recovery/
│   │       │   └── recovery_dashboard_screen.dart
│   │       └── settings/
│   │           ├── export_handler.dart
│   │           ├── settings_controller.dart
│   │           └── settings_screen.dart
│   └── test/
├── profiles/
│   └── sam.json
├── prompts/
│   ├── concise-assistant-response.xml
│   └── typer-commands.xml
├── scripts/
│   ├── chroma_quick.py
│   └── memory_vault_smoke.py
├── tests/
│   ├── __init__.py
│   ├── data_types_test.py
│   ├── deepseek_test.py
│   ├── execute_python_test.py
│   ├── test_integration.py
│   ├── test_morning_briefing.py
│   ├── test_telegram_bridge.py
│   └── test_memory_vault_smoke.py
└── utils/
    └── embedding_utils.py
```

## 4. Core Feature Deep-Dive

### AI Chat & Conversation (Flutter App & Python Backend)
- **User Experience**: Users interact with the AI assistant through a chat interface, sending messages and receiving personalized responses. A 