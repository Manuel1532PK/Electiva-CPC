# Tecnologías Específicas del Proyecto MIMETIC AI

## 1. Backend
- **Python 3.11+**: Lenguaje base para el núcleo del sistema, la orquestación y el desarrollo de agentes.
- **FastAPI**: Framework web asíncrono en Python utilizado como punto de entrada HTTP del sistema.
- **Uvicorn**: Servidor ASGI para la ejecución de la aplicación FastAPI.
- **Pydantic**: Validación y modelado de datos del backend.
- **Motor**: Cliente asíncrono de MongoDB para Python.
- **APIs REST**: Estilo de arquitectura de las interfaces expuestas por el backend.

## 2. Frontend
- **React 18.3.1**: Librería para la construcción de la interfaz de usuario.
- **Vite**: Herramienta de compilación y servidor de desarrollo del proyecto web.
- **TypeScript**: Tipado estático para el código de la interfaz.
- **React Router DOM**: Enrutamiento del lado del cliente.
- **@react-oauth/google**: Integración del inicio de sesión con Google en la interfaz.
- **JavaScript / TypeScript**: Lenguajes de programación de la interfaz web.
- **HTML5**: Lenguaje de marcado para la estructura de la interfaz.
- **Tailwind CSS**: Framework de estilos utilitarios para el diseño de la interfaz.

## 3. Persistencia y Almacenamiento de Datos
- **MongoDB Atlas**: Base de datos NoSQL en la nube para logs estructurados, eventos e historiales.
- **JSON**: Formato estandarizado para la configuración de entornos y la transferencia local de archivos de datos.

## 4. IA y Servicios Externos
- **Gmail API**: Integración con el correo de Google.
- **SMTP**: Protocolo para el envío de correos electrónicos.
- **SendGrid**: Servicio de envío de correos electrónicos.
- **Google OAuth 2.0**: Protocolo de autenticación y autorización con cuentas de Google.

## 5. Agentes y Arquitectura de Control
- **Coding Agent y Research Agent**: Agentes especializados integrados en el framework.
- **Router y Gateway de LLM interno**: Módulo de enrutamiento de proveedores de modelos de lenguaje con seguimiento de costos.
- **Sistema de Memoria Interna**: Memoria volátil a corto plazo y memoria persistente a largo plazo.
- **Guardrails & Security**: Sistema integrado de validación y permisos.

## 6. Herramientas de Desarrollo y Despliegue
- **Git & GitHub**: Control de versiones y gestión del repositorio de código fuente.
- **Docker**: Plataforma de contenedorización para el empaquetado y despliegue del entorno.
- **OpenCode & Antigravity IDE**: Entorno de desarrollo con el plugin `@rolled-potatoes/opencode-mermaid` y la extensión de Figma (`figma.figma-vscode-extension`).
