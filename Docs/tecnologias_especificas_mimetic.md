# Tecnologías Específicas del Proyecto MIMETIC

## 1. Lenguaje de Programación y Entorno
- **Python 3.x**: Lenguaje base para el núcleo del sistema, orquestación y desarrollo de agentes.

## 2. API y Orquestación Backend
- **FastAPI**: Framework web asíncrono utilizado como punto de entrada HTTP (`interfaces/api/main.py`).
- **Claude (Anthropic API)**: LLM Provider especificado directamente en la configuración del entorno (`config/environments/dev.yaml` y `prod.yaml`).
- **Router y Gateway de LLM Interno**: Módulo de enrutamiento (`core/llm_gateway/provider_router.py`) con seguimiento de costos (`core/llm_gateway/cost_tracker.py`).

## 3. Persistencia y Almacenamiento de Datos
- **MongoDB**: Base de datos NoSQL asíncrona para la gestión de datos persistentes del sistema.
- **SQLite**: Motor de base de datos relacional liviano para persistencia local y pruebas.
- **JSON**: Formato estandarizado para la configuración de entornos y transferencia de archivos de datos localmente.

## 4. Agentes y Arquitectura de Control
- **Coding Agent y Research Agent**: Agentes especializados integrados en el framework (`agents/coding_agent/`, `agents/research_agent/`).
- **Sistema de Memoria Interna**: Memoria volátil a corto plazo (`core/memory/short_term.py`) y persistente a largo plazo (`core/memory/long_term.py`).
- **Guardrails & Security**: Sistema de validación y permisos integrados (`core/security/guardrails.py`, `core/security/permissions.py`).

## 5. Integraciones y Herramientas Externas
- **GitHub Client**: Cliente personalizado para la integración con GitHub (`tools/github_client.py`).
- **Slack API Client**: Módulo de integración para alertas y mensajería en Slack (`tools/slack_client.py`).
- **OpenCode & Antigravity IDE**: Entorno de desarrollo con el plugin `@rolled-potatoes/opencode-mermaid` y la extensión de Figma (`figma.figma-vscode-extension`).

## 6. Despliegue y Contenedorización
- **Docker**: Plataforma de contenedorización para el empaquetado y despliegue del entorno.
- **Git & GitHub**: Control de versiones y gestión de repositorio de código fuente.
