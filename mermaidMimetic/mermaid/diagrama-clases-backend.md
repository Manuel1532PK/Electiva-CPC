# MIMETIC

## Diagrama de clases - Backend de procesamiento de datos y logica de negocio

```mermaid
classDiagram
    direction TB

    class Config {
        +str mongo_uri
        +str mongo_database
        +str openweathermap_api_key
        +str openweathermap_base_url
        +int request_timeout
        +load_dotenv()$ void
        +validate()$ void
    }

    class MongoDBConnection {
        -Client client
        -Database database
        +str uri
        +str database_name
        +connect()$ Database
        +disconnect()$ void
        +ping()$ bool
        +get_collection(name)$ Collection
        +server_info()$ dict
    }

    class BaseRepository {
        -MongoDBConnection connection
        -Collection collection
        +insert_one(document)$ str
        +insert_many(documents)$ int
        +find_one(filters)$ dict
        +find_many(filters, limit)$ list
        +update_one(filters, update)$ int
        +delete_one(filters)$ int
        +aggregate(pipeline)$ list
        +create_index(keys, options)$ str
    }

    class WeatherRepository {
        +find_by_city_and_date(city, date)$ list
        +latest_for_city(city)$ dict
        +upsert_observation(document)$ str
    }

    class ClinicalRepository {
        +find_by_patient(document_id)$ list
        +find_by_triage_level(level)$ list
        +find_active_cases()$ list
        +upsert_urgency_record(document)$ str
    }

    class AlertRepository {
        +find_open_alerts()$ list
        +find_by_device(device_id)$ list
        +acknowledge(alert_id, user_id)$ bool
    }

    class MetricsRepository {
        +aggregate_by_timeframe(metric, timeframe)$ list
        +latest(metric)$ dict
        +record(metric, value, tags)$ str
    }

    class WeatherAPIClient {
        -str api_key
        -str base_url
        -int timeout
        +request_current(city, units)$ dict
        +request_forecast(city, days)$ dict
        +build_url(endpoint, params)$ str
        +handle_status(code)$ void
    }

    class DataCleaner {
        <<interface>>
        +clean(dataset)$ DataFrame
        +validate(dataset)$ bool
        +transform(dataset)$ list
    }

    class MIMETICDataCleaner {
        -DataFrame raw_data
        -DataFrame cleaned_data
        -list validation_errors
        -int duplicates_removed
        -int nulls_filled
        -int outliers_flagged
        +fetch_weather_data(city, endpoint)$ DataFrame
        +drop_duplicates(keys)$ DataFrame
        +handle_missing_values(strategy)$ DataFrame
        +normalize_column_types()$ DataFrame
        +normalize_dates(column, fmt)$ DataFrame
        +detect_outliers(column, threshold)$ DataFrame
        +validate_ranges(rules)$ DataFrame
        +transform_to_documents()$ list
        +get_summary()$ dict
        +run(city)$ list
    }

    class SchemaValidator {
        -dict schema
        -PydanticModel model
        +validate_document(document)$ bool
        +validate_batch(documents)$ dict
        +get_errors()$ list
    }

    class WeatherService {
        -WeatherAPIClient api_client
        -MIMETICDataCleaner cleaner
        -WeatherRepository repository
        +get_current_weather(city)$ dict
        +get_forecast(city, days)$ list
        +ingest_and_store(city)$ int
    }

    class ClinicalService {
        -ClinicalRepository repository
        +register_patient(data)$ str
        +register_urgency(data)$ str
        +get_patient_history(document_id)$ list
        +assign_triage_level(symptoms)$ str
    }

    class AlertService {
        -AlertRepository repository
        +register_iot_event(payload)$ str
        +evaluate_threshold(metric, value, threshold)$ str
        +acknowledge_alert(alert_id, user_id)$ bool
        +get_open_alerts()$ list
    }

    class MetricsService {
        -MetricsRepository repository
        +track(metric, value, tags)$ void
        +get_dashboard(timeframe)$ dict
    }

    class APIController {
        <<abstract>>
        -APIRouter router
        -FastAPI app
        +register_routes()$ void
        +handle_exception(exc)$ JSONResponse
        +health_check()$ dict
    }

    class WeatherController {
        -WeatherService weather_service
        +get_current(city)$ dict
        +get_forecast(city, days)$ list
        +ingest(city)$ dict
    }

    class ClinicalController {
        -ClinicalService clinical_service
        -AuthService auth_service
        +create_patient(data)$ dict
        +create_urgency(data)$ dict
        +get_patient_history(document_id)$ list
    }

    class AlertController {
        -AlertService alert_service
        +receive_sensor_event(payload)$ dict
        +acknowledge(alert_id)$ dict
        +list_alerts(status)$ list
    }

    class MetricsController {
        -MetricsService metrics_service
        +get_metrics(timeframe)$ dict
    }

    class AuthService {
        -str jwt_secret
        +login(credentials)$ dict
        +verify_token(token)$ dict
        +authorize(token, role)$ bool
    }

    Config --> MongoDBConnection : configura
    MongoDBConnection o-- BaseRepository : expone colecciones
    BaseRepository <|-- WeatherRepository
    BaseRepository <|-- ClinicalRepository
    BaseRepository <|-- AlertRepository
    BaseRepository <|-- MetricsRepository

    WeatherAPIClient --> Config : usa
    MIMETICDataCleaner ..> DataCleaner : implements
    MIMETICDataCleaner --> WeatherAPIClient : consume
    MIMETICDataCleaner --> SchemaValidator : valida
    MIMETICDataCleaner ..> WeatherRepository : persiste

    WeatherService --> WeatherAPIClient
    WeatherService --> MIMETICDataCleaner
    WeatherService --> WeatherRepository
    ClinicalService --> ClinicalRepository
    AlertService --> AlertRepository
    MetricsService --> MetricsRepository

    APIController <|-- WeatherController
    APIController <|-- ClinicalController
    APIController <|-- AlertController
    APIController <|-- MetricsController

    WeatherController --> WeatherService
    ClinicalController --> ClinicalService
    AlertController --> AlertService
    MetricsController --> MetricsService
    ClinicalController --> AuthService
```

**Clases principales:** `MIMETICDataCleaner` (pipeline de limpieza con Pandas), `WeatherAPIClient` (integracion con OpenWeatherMap), la jerarquia `BaseRepository` sobre `MongoDBConnection` (PyMongo) y los controladores REST que exponen los servicios de dominio.