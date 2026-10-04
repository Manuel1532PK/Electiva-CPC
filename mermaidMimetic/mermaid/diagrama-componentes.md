# MIMETIC

## Diagrama de componentes - Arquitectura en capas

```mermaid
flowchart TB
    subgraph C1["Capa de presentacion - Interfaz de usuario"]
        direction TB
        UI["React App<br/>SPA"]
        Vistas["Vistas<br/>Panel, Urgencias, Alertas, Clima"]
        Estado["Estado global<br/>Context / Redux"]
        ClienteHTTP["Cliente HTTP<br/>Axios / Fetch"]

        UI --> Vistas
        Vistas --> Estado
        Vistas --> ClienteHTTP
    end

    subgraph C2["Capa de servicios - API Backend Python"]
        direction TB
        API["FastAPI<br/>Uvicorn"]

        subgraph Controladores["Controladores REST"]
            CtrlClima["WeatherController"]
            CtrlClinico["ClinicalController"]
            CtrlAlertas["AlertController"]
            CtrlMetricas["MetricsController"]
            CtrlAuth["AuthController"]
        end

        subgraph Servicios["Servicios de dominio"]
            ServClima["WeatherService"]
            ServClinico["ClinicalService"]
            ServAlertas["AlertService"]
            ServMetricas["MetricsService"]
        end

        subgraph Repos["Repositorios"]
            RepoClima["WeatherRepository"]
            RepoClinico["ClinicalRepository"]
            RepoAlertas["AlertRepository"]
            RepoMetricas["MetricsRepository"]
        end

        Middleware["Middleware<br/>Autenticacion, RBAC, Logging, Manejo de errores"]

        API --> Middleware
        Middleware --> Controladores
        Controladores --> Servicios
        Servicios --> Repos
    end

    subgraph C3["Capa de procesamiento - Pipeline de datos"]
        direction TB
        Pipeline["Pipeline ETL"]
        Cleaner[["MIMETICDataCleaner"]]
        Pandas["Pandas<br/>DataFrame"]
        Validador["Validador de esquema<br/>Pydantic"]
        Transformador["Transformador de documentos<br/>BSON"]
        ClienteOWM["Cliente HTTP<br/>OpenWeatherMap API"]

        Pipeline --> Cleaner
        Cleaner <--> Pandas
        Cleaner --> Validador
        Validador --> Transformador
        ClienteOWM --> Cleaner
    end

    subgraph C4["Capa de persistencia - MongoDB"]
        direction TB
        Driver["MongoDB Connection<br/>PyMongo"]
        DB[("MongoDB<br/>clinico_mimetic")]
        ColClima[("coleccion: clima")]
        ColUrg[("coleccion: registros_urgencia")]
        ColAlertas[("coleccion: alertas_iot")]
        ColMetricas[("coleccion: metricas_sistema")]

        Driver --> DB
        DB --> ColClima
        DB --> ColUrg
        DB --> ColAlertas
        DB --> ColMetricas
    end

    subgraph Externos["Fuentes externas"]
        OWM["OpenWeatherMap<br/>API REST"]
        DispIoT["Dispositivos IoT<br/>Sensores y monitores"]
    end

    ClienteHTTP -->|"JSON / HTTPS"| API
    Repos -->|"consultas y escrituras"| Driver
    Cleaner -->|"lectura de respuesta"| OWM
    Transformador -->|"insert_one / bulk_write"| Driver
    DispIoT -->|"MQTT / HTTP"| CtrlAlertas

    classDef ui fill:#e3f2fd,stroke:#1565c0,color:#0d47a1
    classDef api fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20
    classDef pipe fill:#fff8e1,stroke:#f9a825,color:#e65100
    classDef db fill:#fce4ec,stroke:#c2185b,color:#880e4f
    classDef ext fill:#f3e5f5,stroke:#7b1fa2,color:#4a148c

    class UI,Vistas,Estado,ClienteHTTP ui
    class API,Middleware,CtrlClima,CtrlClinico,CtrlAlertas,CtrlMetricas,CtrlAuth,ServClima,ServClinico,ServAlertas,ServMetricas,RepoClima,RepoClinico,RepoAlertas,RepoMetricas api
    class Pipeline,Cleaner,Pandas,Validador,Transformador,ClienteOWM pipe
    class Driver,DB,ColClima,ColUrg,ColAlertas,ColMetricas db
    class OWM,DispIoT ext
```

**Flujo de extremo a extremo:** React → API FastAPI → Controlador → Servicio → Repositorio → PyMongo → MongoDB.
El pipeline de limpieza se apoya en el pipeline de datos: descarga de OpenWeatherMap → `MIMETICDataCleaner` (Pandas) → validación de esquema → documento BSON → escritura en MongoDB.