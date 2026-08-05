# AGENTS.md — Escapa2 Radar

## 1. Propósito de este archivo

Este archivo contiene las instrucciones maestras para desarrollar **Escapa2 Radar** con OpenCode desde VS Code.

OpenCode debe tratar este documento como la fuente principal de verdad del proyecto. Antes de modificar código:

1. Lee este archivo completo.
2. Inspecciona el estado actual del repositorio.
3. Explica brevemente el plan de la tarea.
4. Implementa solamente el alcance solicitado.
5. Ejecuta compilación, lint y pruebas relacionadas.
6. Resume los cambios, archivos modificados, pruebas ejecutadas y asuntos pendientes.

No intentes construir toda la aplicación en una sola ejecución. Trabaja mediante incrementos pequeños, funcionales y comprobables.

---

## 2. Visión del producto

**Nombre provisional:** Escapa2 Radar.

Escapa2 Radar es una aplicación Android para encontrar escapadas económicas en pareja. Debe combinar disponibilidad de fechas, presupuesto, transporte, alojamiento, tiempo útil en destino y preferencias personales para recomendar el viaje completo más conveniente.

La propuesta central es:

> Dime cuándo podemos viajar, cuánto queremos gastar y desde dónde salimos; búscanos diariamente la mejor escapada completa, no simplemente el vuelo más barato.

La aplicación tendrá dos modos principales:

### 2.1. Escapadas de fin de semana

El usuario podrá indicar:

- Sábados disponibles.
- Hora mínima de salida el viernes.
- Hora máxima de regreso el domingo.
- Ciudad de origen.
- Aeropuertos de salida aceptados.
- Distancia máxima en coche.
- Presupuesto total para dos personas.
- Preferencia entre coche, avión o cualquiera.
- Intereses: playa, naturaleza, ciudad, montaña, gastronomía, tranquilidad o vida nocturna.
- Requisitos del alojamiento, como aparcamiento o cancelación gratuita.

La aplicación probará distintas combinaciones de fechas, horarios, aeropuertos y medios de transporte.

### 2.2. Vacaciones de 4 a 6 días

El usuario podrá indicar un intervalo de vacaciones y la aplicación deberá probar:

- Viajes de 4, 5 y 6 noches.
- Salidas en diferentes días dentro del intervalo.
- Regresos antes de que finalicen las vacaciones.
- Destinos concretos.
- Destinos abiertos en España o Europa.
- Aeropuertos alternativos.

---

## 3. Objetivo del MVP

El MVP debe permitir:

1. Crear un perfil de viaje básico.
2. Configurar ciudad y aeropuertos de salida.
3. Registrar fechas libres manualmente.
4. Configurar presupuesto para dos personas.
5. Explorar oportunidades de viaje.
6. Consultar una oportunidad con desglose de costes.
7. Guardar una búsqueda o viaje en seguimiento.
8. Mantener historial de precios.
9. Generar un informe explicativo con Gemini.
10. Generar un itinerario orientativo con Gemini a partir de datos estructurados.
11. Preparar la arquitectura para búsquedas programadas y notificaciones.
12. Usar datos simulados mientras no estén disponibles las credenciales de APIs de viajes.

No se implementarán reservas ni cancelaciones automáticas.

---

## 4. Principios obligatorios de desarrollo

### 4.1. Implementación incremental

- Cada fase debe producir una aplicación ejecutable.
- Evita cambios masivos que mezclen infraestructura, interfaz y lógica sin pruebas.
- Antes de añadir una dependencia, comprueba si ya existe una solución en el proyecto.
- No reescribas módulos funcionales sin una razón concreta.
- Mantén un `README.md` actualizado con instalación y comandos.
- Mantén un `docs/DECISIONS.md` con decisiones arquitectónicas relevantes.
- Usa TODO únicamente cuando incluya una explicación concreta y una fase prevista.

### 4.2. Calidad

- Nombres de clases, funciones, variables, tablas y endpoints en inglés.
- Textos visibles de la aplicación en español mediante recursos de strings.
- Código, comentarios técnicos y documentación interna preferentemente en inglés.
- Evita funciones largas y clases con múltiples responsabilidades.
- Usa tipos explícitos en contratos públicos.
- Valida toda entrada recibida por la API.
- No ignores excepciones.
- Devuelve errores consistentes y comprensibles.
- Añade pruebas para la lógica de negocio.

### 4.3. Restricciones funcionales

- No afirmar que se ha encontrado “el precio más barato de Internet”.
- Mostrar: “precio más barato encontrado entre las fuentes consultadas, verificado a esta hora”.
- No presentar como garantizado un precio indicativo.
- No permitir que Gemini invente precios, disponibilidad, horarios, tasas, rutas o estaciones de servicio.
- No reservar, cancelar ni comprar sin acción explícita del usuario.
- No tomar decisiones financieras por el usuario.
- Las recomendaciones de “comprar o esperar” deben mostrarse como orientativas.

---

## 5. Uso de inteligencia artificial con Gemini

### 5.1. Papel de Gemini

Gemini se utilizará como capa de inteligencia para:

- Interpretar preferencias escritas en lenguaje natural.
- Resumir cambios diarios de precios.
- Explicar por qué una opción puede ser mejor que otra.
- Generar informes diarios personalizados.
- Generar itinerarios a partir de horarios, lugares y datos aportados por APIs.
- Crear alternativas para lluvia o bajo presupuesto.
- Ordenar recomendaciones por compatibilidad con las preferencias de la pareja.
- Explicar la comparación entre coche y avión.
- Convertir datos técnicos en mensajes claros para el usuario.

Gemini **no será la fuente de precios ni disponibilidad**.

### 5.2. Arquitectura de Gemini

La aplicación Android nunca llamará directamente a Gemini.

Flujo obligatorio:

```text
Android app
    |
    | HTTPS + authenticated user
    v
Backend API
    |
    | server-side Gemini client
    v
Gemini API
```

La clave `GEMINI_API_KEY` solamente puede existir en el backend, en variables de entorno o en un gestor de secretos.

Está prohibido incluir la clave en:

- Código Kotlin.
- `BuildConfig`.
- `strings.xml`.
- Recursos Android.
- Repositorio Git.
- Aplicación distribuida.
- Logs.
- Respuestas de la API.

### 5.3. SDK y API

Usar el SDK oficial `google-genai` en el backend.

Preferir la API de Interactions si está disponible en la versión estable instalada. Mantener el proveedor detrás de una interfaz propia para poder actualizar el SDK o cambiar de modelo sin afectar al resto del sistema.

Variables:

```env
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.6-flash
GEMINI_ENABLED=true
GEMINI_TIMEOUT_SECONDS=30
GEMINI_MAX_REQUESTS_PER_USER_DAY=20
```

El modelo debe ser configurable. No dispersar su nombre por el código.

### 5.4. Salidas estructuradas

Para información que consuma la aplicación, solicitar respuestas ajustadas a esquemas JSON y validarlas con Pydantic.

Nunca confiar en texto libre para operaciones internas.

Ejemplo conceptual de respuesta de itinerario:

```json
{
  "summary": "Escapada urbana económica de dos noches",
  "warnings": [
    "Confirma los horarios antes de reservar"
  ],
  "days": [
    {
      "date": "2026-10-17",
      "title": "Centro histórico",
      "items": [
        {
          "start_time": "10:00",
          "end_time": "11:30",
          "title": "Ruta a pie",
          "estimated_cost_eur": 0,
          "source_place_id": "provider-place-id"
        }
      ]
    }
  ]
}
```

Si Gemini devuelve una respuesta inválida:

1. Registrar el fallo sin guardar contenido sensible.
2. Reintentar como máximo una vez.
3. Si vuelve a fallar, devolver una respuesta de fallback generada por reglas.
4. Nunca bloquear el resto del viaje por un fallo de IA.

### 5.5. Grounding de datos

Cada solicitud a Gemini debe incluir únicamente los datos necesarios.

Los prompts deben distinguir claramente:

- Datos confirmados por proveedor.
- Estimaciones.
- Preferencias del usuario.
- Restricciones.
- Información no disponible.

Las respuestas deben conservar identificadores de las fuentes cuando proceda.

Ejemplo:

```text
CONFIRMED_PROVIDER_DATA:
- Flight total: 142.80 EUR
- Hotel total: 176.00 EUR
- Arrival: 2026-10-17T09:15:00+02:00
- Departure: 2026-10-19T20:35:00+02:00

USER_PREFERENCES:
- Budget for two: 350 EUR
- Interests: historic center, local food
- Avoid: nightlife

RULES:
- Do not invent prices or opening hours.
- Mention unknown information explicitly.
```

### 5.6. Function calling

La llamada a funciones podrá incorporarse en fases posteriores para que Gemini solicite datos al backend mediante herramientas controladas, por ejemplo:

- `get_trip_offer`
- `get_price_history`
- `get_places`
- `get_route_summary`
- `get_fuel_stations`

Gemini propone la llamada, pero el backend:

1. Valida argumentos.
2. Comprueba autorización.
3. Ejecuta la función.
4. Filtra la respuesta.
5. Devuelve el resultado a Gemini.

Gemini nunca ejecuta directamente consultas a bases de datos ni acciones externas.

### 5.7. Control de coste y abuso

Implementar:

- Límite por usuario y día.
- Timeout.
- Reintentos limitados.
- Caché por hash de datos y versión del prompt.
- Registro de tokens o unidades de consumo cuando el SDK lo permita.
- Desactivación global mediante `GEMINI_ENABLED=false`.
- Fallback sin IA.
- No enviar documentos personales ni credenciales al modelo.
- No guardar prompts completos que contengan datos privados.
- Pruebas con un `FakeAiProvider`.

---

## 6. Arquitectura general

Usar un monorepo:

```text
escapa2-radar/
├── AGENTS.md
├── README.md
├── .gitignore
├── .editorconfig
├── docker-compose.yml
├── android-app/
├── backend/
├── docs/
│   ├── DECISIONS.md
│   ├── API.md
│   └── ROADMAP.md
├── infra/
└── scripts/
```

### 6.1. Android

Tecnologías:

- Kotlin.
- Jetpack Compose.
- Material 3.
- Arquitectura de una sola actividad.
- Navigation Compose o la solución estable de navegación recomendada por Android al crear el proyecto.
- ViewModel.
- Coroutines y Flow.
- Hilt.
- Retrofit + OkHttp para la API.
- Kotlin Serialization.
- Room para caché y modo sin conexión.
- DataStore para preferencias locales.
- WorkManager únicamente para sincronización local flexible.
- Firebase Cloud Messaging en la fase de notificaciones.
- Gradle Kotlin DSL.
- Catálogo de versiones de Gradle.

Arquitectura por capas:

```text
UI -> ViewModel -> Use cases -> Repositories -> Local/Remote data sources
```

Usar flujo unidireccional de datos.

Cada pantalla debe exponer un único `UiState` inmutable y acciones explícitas.

### 6.2. Backend

Tecnologías:

- Python 3.12 o superior compatible.
- FastAPI.
- Pydantic v2.
- SQLAlchemy 2.
- Alembic.
- PostgreSQL.
- `httpx`.
- SDK oficial `google-genai`.
- `pytest`.
- `ruff`.
- `mypy` en módulos de dominio y servicios.
- Docker.
- Redis opcional cuando se implemente caché compartida o cola.
- Scheduler simple en desarrollo y worker/scheduler separado en producción.

Arquitectura:

```text
API routers
    -> application services
        -> domain services
            -> repositories / provider interfaces
                -> PostgreSQL / external APIs / Gemini
```

No colocar lógica de negocio en routers ni modelos ORM.

### 6.3. Comunicación

- API REST bajo `/api/v1`.
- JSON.
- Fechas y horas en ISO 8601 con zona horaria.
- Importes con moneda explícita.
- Identificadores UUID.
- Paginación en listas.
- Idempotencia en endpoints que creen seguimientos o trabajos.
- Respuesta de error uniforme.

Ejemplo:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request is invalid",
    "details": {}
  }
}
```

---

## 7. Proveedores externos

Todos los proveedores se implementarán detrás de interfaces.

```python
class FlightProvider(Protocol):
    async def search(self, request: FlightSearchRequest) -> list[FlightOffer]:
        ...

class HotelProvider(Protocol):
    async def search(self, request: HotelSearchRequest) -> list[HotelOffer]:
        ...

class RouteProvider(Protocol):
    async def calculate(self, request: RouteRequest) -> RouteOffer:
        ...

class PlacesProvider(Protocol):
    async def search(self, request: PlacesSearchRequest) -> list[Place]:
        ...

class FuelPriceProvider(Protocol):
    async def stations_near_route(
        self,
        request: FuelStationsRequest,
    ) -> list[FuelStation]:
        ...

class AiProvider(Protocol):
    async def generate_itinerary(
        self,
        request: ItineraryAiRequest,
    ) -> ItineraryAiResponse:
        ...
```

Implementaciones previstas:

- Vuelos iniciales: Amadeus Self-Service.
- Exploración flexible futura: Skyscanner Indicative.
- Verificación futura: Skyscanner Live o Amadeus.
- Alojamientos iniciales: Amadeus Hotels.
- Alojamientos posteriores: Booking Demand API u otro proveedor autorizado.
- Rutas y peajes: Google Routes.
- Lugares: Google Places.
- Gasolineras españolas: servicio oficial de precios de carburantes.
- Notificaciones: Firebase Cloud Messaging.
- IA: Gemini.

Durante las primeras fases crear:

- `MockFlightProvider`
- `MockHotelProvider`
- `MockRouteProvider`
- `MockPlacesProvider`
- `MockFuelPriceProvider`
- `FakeAiProvider`
- `GeminiAiProvider`

Nunca acoplar el dominio a la respuesta JSON original de un proveedor. Crear modelos internos normalizados.

---

## 8. Modelo de dominio

### 8.1. Entidades principales

#### User

- `id`
- `email`
- `display_name`
- `timezone`
- `created_at`
- `updated_at`

#### Couple

- `id`
- `name`
- `created_at`

#### CoupleMember

- `couple_id`
- `user_id`
- `role`
- `joined_at`

#### TravelProfile

- `id`
- `couple_id`
- `origin_city`
- `currency`
- `default_budget_eur`
- `max_drive_minutes`
- `preferred_transport`
- `interests`
- `avoid_preferences`
- `created_at`
- `updated_at`

#### AirportPreference

- `id`
- `travel_profile_id`
- `iata_code`
- `enabled`
- `transfer_cost_eur`
- `transfer_minutes`

#### VehicleProfile

- `id`
- `couple_id`
- `name`
- `fuel_type`
- `average_consumption_l_per_100km`
- `tank_capacity_l`
- `estimated_cost_per_km_eur`
- `max_fuel_detour_minutes`

#### AvailabilityWindow

- `id`
- `couple_id`
- `start_at`
- `end_at`
- `kind`: `WEEKEND` o `VACATION`
- `is_flexible`
- `created_at`

#### SearchWatch

- `id`
- `couple_id`
- `name`
- `status`
- `criteria_json`
- `alert_rules_json`
- `last_run_at`
- `next_run_at`
- `created_at`
- `updated_at`

#### TravelOpportunity

- `id`
- `search_watch_id`
- `destination_code`
- `destination_name`
- `transport_mode`
- `start_at`
- `end_at`
- `useful_hours`
- `total_cost_eur`
- `cost_per_person_eur`
- `cost_per_night_eur`
- `cost_per_useful_hour_eur`
- `comfort_score`
- `value_score`
- `provider_verified_at`
- `created_at`

#### PriceSnapshot

- `id`
- `travel_opportunity_id`
- `total_cost_eur`
- `flight_cost_eur`
- `hotel_cost_eur`
- `route_cost_eur`
- `local_transport_cost_eur`
- `fees_cost_eur`
- `captured_at`
- `source_summary_json`

#### FlightOffer

- `id`
- `travel_opportunity_id`
- `provider`
- `provider_offer_id`
- `origin`
- `destination`
- `departure_at`
- `arrival_at`
- `return_departure_at`
- `return_arrival_at`
- `base_price_eur`
- `baggage_price_eur`
- `seat_price_eur`
- `total_price_eur`
- `booking_url`
- `verified_at`
- `expires_at`

#### HotelOffer

- `id`
- `travel_opportunity_id`
- `provider`
- `provider_offer_id`
- `hotel_name`
- `check_in`
- `check_out`
- `room_name`
- `total_price_eur`
- `taxes_included`
- `free_cancellation_until`
- `breakfast_included`
- `parking_available`
- `rating`
- `review_count`
- `booking_url`
- `verified_at`
- `expires_at`

#### RouteOffer

- `id`
- `travel_opportunity_id`
- `distance_km`
- `duration_minutes`
- `fuel_cost_eur`
- `toll_cost_eur`
- `parking_cost_eur`
- `vehicle_wear_cost_eur`
- `total_cost_eur`
- `route_polyline`
- `verified_at`

#### Itinerary

- `id`
- `travel_opportunity_id`
- `status`
- `source_data_hash`
- `prompt_version`
- `model`
- `content_json`
- `created_at`

#### Vote

- `id`
- `couple_id`
- `user_id`
- `travel_opportunity_id`
- `value`: `LOVE`, `MAYBE` o `NO`
- `created_at`
- `updated_at`

#### NotificationLog

- `id`
- `user_id`
- `search_watch_id`
- `type`
- `title`
- `body`
- `payload_json`
- `sent_at`
- `status`

### 8.2. Alcance inicial de base de datos

No es necesario crear todas las tablas en la primera tarea.

Primera migración:

- `travel_profiles`
- `availability_windows`
- `search_watches`
- `travel_opportunities`
- `price_snapshots`
- `itineraries`

La autenticación y las entidades de pareja pueden comenzar con un usuario de desarrollo fijo y añadirse en una fase posterior.

---

## 9. Reglas de cálculo

Todos los cálculos deben vivir en funciones puras o servicios de dominio y tener pruebas unitarias.

### 9.1. Coste total

```text
total_trip_cost =
    flight_total
    + airport_transfer_total
    + airport_parking_total
    + hotel_total
    + destination_transport_total
    + route_fuel_total
    + toll_total
    + destination_parking_total
    + vehicle_wear_total
    + known_taxes_and_fees
```

No sumar componentes que no apliquen.

### 9.2. Métricas

```text
cost_per_person = total_trip_cost / travelers
cost_per_night = total_trip_cost / nights
cost_per_useful_hour = total_trip_cost / useful_hours
```

Evitar división por cero y devolver `null` cuando una métrica no sea calculable.

### 9.3. Horas útiles

Las horas útiles representan el tiempo disponible en destino descontando:

- Traslado desde origen.
- Espera en aeropuerto.
- Vuelo o conducción.
- Traslado al alojamiento.
- Margen necesario antes del regreso.
- Traslado de vuelta.

El cálculo debe guardar un desglose explicable.

### 9.4. Gasolineras

```text
gross_savings =
    liters_to_refuel * (reference_price_per_liter - station_price_per_liter)

detour_fuel_cost =
    detour_distance_km
    * vehicle_consumption_l_per_100km
    / 100
    * station_price_per_liter

net_savings =
    gross_savings
    - detour_fuel_cost
    - time_penalty_eur
```

La aplicación recomendará la estación por ahorro neto, no solamente por precio por litro.

### 9.5. Alertas de precio

Soportar reglas como:

- Viaje completo por debajo de un umbral.
- Bajada porcentual superior a un umbral.
- Bajada absoluta superior a un umbral.
- Nuevo mínimo histórico.
- Incremento durante varios registros consecutivos.
- Nueva oportunidad dentro del presupuesto.

No enviar alertas repetidas si no existe un cambio significativo.

### 9.6. Value score

El score debe ser transparente y configurable.

Primera versión orientativa:

```text
value_score =
    budget_fit_score * 0.30
    + relative_price_score * 0.25
    + useful_time_score * 0.20
    + schedule_fit_score * 0.15
    + comfort_score * 0.10
```

Cada componente debe estar normalizado entre 0 y 100.

Guardar también los componentes del score para poder explicar el resultado.

---

## 10. API inicial

Base path:

```text
/api/v1
```

### 10.1. Sistema

```text
GET /health
GET /ready
```

### 10.2. Perfil

```text
GET    /profile
PUT    /profile
GET    /profile/airports
PUT    /profile/airports
```

### 10.3. Disponibilidad

```text
GET    /availability
POST   /availability
PUT    /availability/{id}
DELETE /availability/{id}
```

### 10.4. Seguimientos

```text
GET    /watches
POST   /watches
GET    /watches/{id}
PUT    /watches/{id}
DELETE /watches/{id}
POST   /watches/{id}/run
```

### 10.5. Oportunidades

```text
GET /opportunities
GET /opportunities/{id}
GET /opportunities/{id}/price-history
POST /opportunities/{id}/save
```

Filtros iniciales:

- `max_total_cost_eur`
- `transport_mode`
- `start_after`
- `end_before`
- `destination`
- `min_useful_hours`
- `sort`

### 10.6. IA

```text
POST /ai/interpret-search
POST /ai/opportunity-summary
POST /ai/itineraries
POST /ai/daily-report
```

Todos deben:

- Validar autorización.
- Aplicar rate limiting.
- Usar esquemas de entrada y salida.
- Permitir fallback.
- No exponer prompts internos.
- No devolver la clave ni información del servidor.

### 10.7. Desarrollo

Solo en entorno `development`:

```text
POST /dev/seed
POST /dev/reset
```

Nunca habilitar estos endpoints en producción.

---

## 11. Pantallas Android

### 11.1. Navegación inicial

Bottom navigation:

1. Inicio.
2. Explorar.
3. Radar.
4. Perfil.

### 11.2. Inicio

Mostrar:

- Próximas fechas libres.
- Mejor oportunidad actual.
- Mayor bajada de precio.
- Viajes vigilados.
- Estado de la última actualización.
- Botón “Buscar escapada”.

### 11.3. Explorar

Controles:

- Origen.
- Fechas.
- Presupuesto.
- Transporte.
- Tipo de destino.
- Duración.
- Botón “Sorpréndeme”.

Resultados en cards con:

- Destino.
- Fechas.
- Coste total para dos.
- Transporte.
- Horas útiles.
- Coste por hora útil.
- Estado del precio.
- Fecha de verificación.

### 11.4. Detalle de oportunidad

Secciones:

- Resumen.
- Desglose de costes.
- Horarios.
- Vuelo u opción de coche.
- Hotel.
- Tiempo útil.
- Historial de precio.
- Explicación de Gemini.
- Botón para seguir.
- Enlaces externos de reserva.
- Aviso de que precios y disponibilidad pueden cambiar.

### 11.5. Radar

Mostrar:

- Seguimientos activos.
- Última ejecución.
- Próxima ejecución.
- Cambio desde ayer.
- Mínimo registrado.
- Reglas de alerta.
- Historial.

### 11.6. Perfil

Campos iniciales:

- Ciudad de salida.
- Moneda.
- Presupuesto para dos.
- Aeropuertos.
- Máximo de horas en coche.
- Preferencia de transporte.
- Intereses.
- Exclusiones.

### 11.7. Estados de UI obligatorios

Cada pantalla debe contemplar:

- Loading.
- Empty.
- Content.
- Recoverable error.
- Offline cached content.
- Refreshing.

---

## 12. Diseño visual

Usar Material 3 con una identidad de viaje moderna y limpia.

Principios:

- Priorizar el coste total y las horas útiles.
- Evitar saturación de información.
- Mostrar claramente cuándo se verificó cada precio.
- Diferenciar precio confirmado, indicativo y estimado.
- Accesibilidad: contraste, tamaños táctiles y textos alternativos.
- No depender únicamente del color para expresar tendencia.
- Usar formatos locales españoles para moneda y fecha.
- Preparar recursos para futura traducción.

No dedicar tiempo a animaciones complejas durante el MVP.

---

## 13. Autenticación y privacidad

### 13.1. Desarrollo inicial

Durante el primer vertical slice puede utilizarse un usuario de desarrollo fijo generado por el backend.

### 13.2. Fase posterior

Usar Firebase Authentication o una solución equivalente para:

- Inicio de sesión.
- Obtención de token.
- Verificación del token en backend.
- Asociación del usuario con una pareja.
- Protección de recursos.

### 13.3. Privacidad

- Recopilar solamente los datos necesarios.
- Nunca registrar claves, tokens o contraseñas.
- No enviar documentos personales a Gemini.
- No almacenar datos de tarjetas.
- No almacenar credenciales de proveedores de reserva.
- Preparar eliminación de cuenta y exportación de datos.
- Separar datos analíticos de datos personales.
- Cifrar el tráfico mediante HTTPS.
- Aplicar autorización por recurso, no solo autenticación.

---

## 14. Variables de entorno del backend

Crear `backend/.env.example`:

```env
APP_NAME=Escapa2 Radar API
APP_ENV=development
APP_DEBUG=true
API_V1_PREFIX=/api/v1

DATABASE_URL=postgresql+psycopg://escapa2:escapa2@localhost:5432/escapa2
CORS_ALLOWED_ORIGINS=http://localhost:8080

GEMINI_ENABLED=true
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.6-flash
GEMINI_TIMEOUT_SECONDS=30
GEMINI_MAX_REQUESTS_PER_USER_DAY=20

AMADEUS_ENABLED=false
AMADEUS_CLIENT_ID=
AMADEUS_CLIENT_SECRET=

GOOGLE_MAPS_ENABLED=false
GOOGLE_MAPS_API_KEY=

FIREBASE_ENABLED=false
FIREBASE_PROJECT_ID=
FIREBASE_CREDENTIALS_FILE=

SCHEDULER_ENABLED=false
LOG_LEVEL=INFO
```

Reglas:

- `.env` debe estar ignorado por Git.
- `.env.example` no contiene secretos.
- La aplicación debe arrancar sin claves externas cuando los proveedores estén desactivados.
- Los proveedores simulados serán la opción predeterminada en desarrollo.
- Fallar al arrancar si un proveedor está activado y faltan sus credenciales.

---

## 15. Persistencia y caché

### 15.1. Backend

PostgreSQL será la fuente de verdad.

Guardar:

- Criterios de búsqueda.
- Resultados normalizados.
- Historial de precios.
- Fecha de verificación.
- Fuente.
- Resumen del proveedor.
- Hash del conjunto de datos enviado a Gemini.
- Resultado estructurado de IA.

No guardar respuestas brutas completas indefinidamente si contienen información innecesaria.

### 15.2. Android

Room almacenará:

- Perfil cacheado.
- Disponibilidad.
- Oportunidades guardadas.
- Últimos resultados.
- Historial visible.
- Itinerarios.
- Marca temporal de sincronización.

La app debe poder consultar viajes guardados sin conexión.

---

## 16. Scheduler y radar diario

La búsqueda diaria se ejecutará en el servidor, no solamente en el teléfono.

Flujo:

1. Scheduler selecciona seguimientos activos.
2. Valida límites y frecuencia.
3. Consulta proveedores.
4. Normaliza ofertas.
5. Calcula costes y scores.
6. Guarda snapshots.
7. Evalúa alertas.
8. Genera resumen con reglas o Gemini.
9. Envía notificación.
10. Registra resultado.

En desarrollo:

- Permitir ejecución manual mediante endpoint.
- Scheduler desactivado por defecto.
- No ejecutar consultas externas en pruebas.

En producción:

- Worker separado.
- Bloqueo distribuido para evitar ejecuciones duplicadas.
- Reintentos con backoff.
- Idempotencia por seguimiento y ventana temporal.
- Métricas de duración, éxito y coste.

---

## 17. Notificaciones

Implementar Firebase Cloud Messaging después de completar el historial de precios.

Tipos:

- `NEW_LOW`
- `PRICE_DROP`
- `BUDGET_MATCH`
- `NEW_OPPORTUNITY`
- `PRICE_RISING`
- `DAILY_REPORT`

Cada notificación debe incluir un deep link a la pantalla correspondiente.

No enviar notificación cuando:

- El cambio esté por debajo del umbral.
- Ya se haya enviado el mismo evento.
- El seguimiento esté pausado.
- El usuario esté dentro del horario silencioso, salvo evento urgente explícitamente configurado.

---

## 18. Manejo de errores

Crear códigos de dominio estables:

- `VALIDATION_ERROR`
- `NOT_FOUND`
- `UNAUTHORIZED`
- `FORBIDDEN`
- `RATE_LIMITED`
- `PROVIDER_UNAVAILABLE`
- `PROVIDER_QUOTA_EXCEEDED`
- `STALE_PRICE`
- `AI_DISABLED`
- `AI_INVALID_RESPONSE`
- `INTERNAL_ERROR`

Los mensajes técnicos detallados deben ir a logs; el cliente recibe mensajes seguros.

Mostrar al usuario:

- Qué ha fallado.
- Qué datos siguen disponibles.
- Cuándo se verificó la información.
- Si puede reintentar.
- Si se está usando información cacheada.

---

## 19. Logging y observabilidad

Backend:

- Logging estructurado.
- `request_id`.
- `user_id` anonimizado cuando proceda.
- Nombre del proveedor.
- Latencia.
- Estado.
- Número de resultados.
- Nunca guardar secretos.
- Nunca guardar cabeceras de autorización completas.
- No guardar el prompt completo de Gemini por defecto.

Preparar métricas:

- Búsquedas por proveedor.
- Errores por proveedor.
- Latencia.
- Resultados encontrados.
- Tokens o consumo de IA.
- Alertas enviadas.
- Ratio de caché.
- Antigüedad de precios.

---

## 20. Pruebas

### 20.1. Backend

Pruebas unitarias obligatorias para:

- Cálculo del coste total.
- Coste por persona, noche y hora útil.
- Cálculo de horas útiles.
- Score de valor.
- Ahorro neto de gasolinera.
- Reglas de alerta.
- Normalización de proveedores.
- Validación de respuesta de Gemini.
- Fallback de IA.
- Rate limiting de IA.

Pruebas de integración:

- Health endpoint.
- CRUD de perfil.
- CRUD de disponibilidad.
- CRUD de seguimiento.
- Consulta de oportunidades.
- Creación de itinerario con `FakeAiProvider`.
- Persistencia de snapshots.

No llamar a APIs reales en pruebas automatizadas.

### 20.2. Android

Pruebas para:

- ViewModels.
- Mapeo de DTO a modelos.
- Repositorios con fakes.
- Estados loading, empty, content y error.
- Navegación esencial.
- Formateo de precio y fecha.
- Persistencia Room básica.

Añadir tests de UI solo para los flujos críticos del MVP.

### 20.3. Comandos de calidad

El repositorio deberá proporcionar comandos equivalentes a:

```bash
# Backend
cd backend
ruff check .
ruff format --check .
mypy app
pytest

# Android
cd android-app
./gradlew lint
./gradlew test
./gradlew assembleDebug
```

En Windows, documentar la variante `gradlew.bat`.

---

## 21. Seguridad

Obligatorio:

- Dependencias oficiales y mantenidas.
- Validación estricta de URL de reserva.
- No seguir redirecciones no confiables desde el backend.
- Timeouts en todas las llamadas externas.
- Límites de tamaño de respuesta.
- Rate limiting.
- Protección contra SSRF en proveedores configurables.
- Consultas SQL parametrizadas mediante ORM.
- No construir SQL desde texto de Gemini.
- Escapar texto remoto al mostrarlo.
- Revisar permisos Android.
- Solicitar ubicación solamente cuando sea necesaria.
- No activar backups de datos sensibles sin decisión explícita.
- Escaneo de secretos antes de commits.
- Añadir cabeceras de seguridad apropiadas en producción.

---

## 22. Roadmap

### Fase 0 — Repositorio y herramientas

- Monorepo.
- Backend mínimo.
- Android mínimo.
- Docker Compose con PostgreSQL.
- CI.
- README.
- Convenciones.
- Health checks.

### Fase 1 — Vertical slice con datos simulados

- Perfil.
- Disponibilidad.
- Oportunidades simuladas.
- Costes.
- Pantalla de inicio.
- Explorar.
- Detalle.
- Persistencia.
- Pruebas.

### Fase 2 — Gemini

- `AiProvider`.
- `FakeAiProvider`.
- `GeminiAiProvider`.
- Resumen de oportunidad.
- Interpretación de búsqueda natural.
- Itinerario estructurado.
- Fallback.
- Rate limiting y caché.

### Fase 3 — Vuelos y hoteles reales

- Integración Amadeus.
- Normalización.
- Precios y expiración.
- Enlaces externos.
- Historial.
- Gestión de cuota.

### Fase 4 — Radar diario

- Scheduler.
- Snapshots.
- Reglas de alerta.
- Informe diario.
- Firebase Cloud Messaging.
- Deep links.

### Fase 5 — Coche

- Google Routes.
- Coste de combustible.
- Peajes.
- Perfil de vehículo.
- Comparador coche-avión.
- Gasolineras oficiales.
- Ahorro neto.

### Fase 6 — Pareja y personalización

- Autenticación.
- Pareja.
- Calendario compartido.
- Votaciones.
- Favoritos.
- Destinos visitados.
- Modo sorpresa.

### Fase 7 — Reservas vigiladas y mejoras

- Seguimiento de hotel con cancelación gratuita.
- Recomendaciones de cambio.
- Gastos reales.
- Presupuesto anual.
- Predicción orientativa.
- Exportación de viaje.

---

## 23. Primera tarea que OpenCode debe ejecutar

Al recibir por primera vez este archivo en un repositorio vacío, OpenCode debe implementar únicamente la **Fase 0** y la base mínima de la **Fase 1**.

### 23.1. Entregables

Crear:

```text
escapa2-radar/
├── AGENTS.md
├── README.md
├── .gitignore
├── .editorconfig
├── docker-compose.yml
├── android-app/
├── backend/
├── docs/
│   ├── DECISIONS.md
│   ├── API.md
│   └── ROADMAP.md
└── scripts/
```

Backend:

- FastAPI operativo.
- `GET /health`.
- Configuración mediante variables de entorno.
- SQLAlchemy y Alembic configurados.
- PostgreSQL en Docker Compose.
- Proveedor de IA abstracto.
- `FakeAiProvider`.
- `GeminiAiProvider` detrás de `GEMINI_ENABLED`.
- Endpoint `POST /api/v1/ai/opportunity-summary`.
- Modelos Pydantic para la entrada y salida.
- Tests sin acceso real a Gemini.
- `.env.example`.

Android:

- Proyecto compilable.
- Jetpack Compose y Material 3.
- Una actividad.
- Navegación inicial.
- Pantallas placeholder funcionales:
  - Home.
  - Explore.
  - Radar.
  - Profile.
- Tema básico.
- Hilt.
- Cliente de API preparado.
- Repositorio fake para desarrollo.
- Estados `Loading`, `Content`, `Empty` y `Error`.
- Tests mínimos de ViewModel.

Infraestructura:

- Docker Compose con PostgreSQL.
- Scripts o instrucciones claras para arrancar.
- CI que ejecute pruebas del backend y Android si el entorno lo permite.
- No añadir credenciales reales.

### 23.2. Datos simulados

Crear al menos cuatro oportunidades:

- Destino español en coche.
- Destino español en avión.
- Destino europeo en avión.
- Opción ligeramente más barata pero con menos horas útiles.

Los datos deben demostrar:

- Coste total.
- Coste por persona.
- Coste por noche.
- Coste por hora útil.
- Diferencia entre precio actual y anterior.
- Fecha de verificación.

### 23.3. Endpoint IA inicial

Entrada orientativa:

```json
{
  "destination": "Bologna",
  "travelers": 2,
  "total_cost_eur": 312.0,
  "budget_eur": 350.0,
  "useful_hours": 29.0,
  "transport_mode": "FLIGHT",
  "verified_at": "2026-08-05T12:00:00Z",
  "facts": [
    "Direct flight",
    "Two hotel nights",
    "Airport transfer not included"
  ]
}
```

Salida:

```json
{
  "headline": "Buena opción dentro del presupuesto",
  "summary": "La escapada entra en el presupuesto y ofrece un vuelo directo, aunque conviene añadir el traslado al aeropuerto antes de comparar.",
  "pros": [
    "Está 38 EUR por debajo del presupuesto",
    "Vuelo directo"
  ],
  "cons": [
    "El traslado al aeropuerto todavía no está incluido"
  ],
  "confidence": "MEDIUM",
  "generated_by_ai": true
}
```

Con `GEMINI_ENABLED=false`, devolver una respuesta determinista basada en reglas con `generated_by_ai=false`.

### 23.4. Criterio de finalización de la primera tarea

La tarea termina cuando:

- Backend arranca.
- `/health` responde.
- Tests backend pasan.
- Android compila.
- Tests Android mínimos pasan.
- No existen secretos.
- README explica los comandos.
- Docker Compose levanta PostgreSQL.
- Se documentan problemas conocidos.
- OpenCode muestra el resumen final y se detiene.

No continuar automáticamente con Amadeus, Firebase, Google Routes o gasolineras.

---

## 24. Flujo de trabajo para tareas posteriores

Cuando el usuario solicite una nueva función:

1. Identificar la fase.
2. Inspeccionar código existente.
3. Proponer un plan breve.
4. Escribir o actualizar pruebas.
5. Implementar.
6. Ejecutar pruebas focalizadas.
7. Ejecutar lint.
8. Actualizar documentación si cambia el contrato.
9. Informar:
   - Qué se hizo.
   - Archivos principales.
   - Comandos ejecutados.
   - Resultado.
   - Limitaciones.
   - Próximo paso lógico.

No ocultar pruebas fallidas. No declarar completado algo que no se haya ejecutado o verificado.

---

## 25. Definición de terminado

Una funcionalidad está terminada cuando:

- Cumple los criterios de aceptación.
- Tiene manejo de errores.
- Tiene pruebas razonables.
- No expone secretos.
- No rompe compilación.
- No introduce warnings evitables.
- El contrato API está documentado.
- La UI contempla loading, error y vacío.
- Los datos dinámicos muestran fuente y fecha de verificación.
- La parte de Gemini tiene fallback.
- El README o documentación se actualiza cuando sea necesario.

---

## 26. Decisiones iniciales ya tomadas

- Aplicación Android nativa.
- Kotlin y Jetpack Compose.
- Backend separado obligatorio.
- Python y FastAPI para el backend.
- PostgreSQL.
- Arquitectura por capas.
- Proveedores externos detrás de interfaces.
- Datos simulados primero.
- Gemini desde backend mediante API key.
- Salidas de Gemini estructuradas y validadas.
- No exponer la clave en Android.
- No reservar ni cancelar automáticamente.
- Desarrollo por fases.
- Coste total para dos y horas útiles como métricas centrales.

Cualquier cambio a estas decisiones debe documentarse en `docs/DECISIONS.md` antes de implementarse.

---

## 27. Referencias técnicas oficiales

- OpenCode rules and `AGENTS.md`: https://opencode.ai/docs/rules/
- Android app architecture: https://developer.android.com/topic/architecture
- Android architecture recommendations: https://developer.android.com/topic/architecture/recommendations
- Firebase Cloud Messaging: https://firebase.google.com/docs/cloud-messaging
- Gemini API keys: https://ai.google.dev/gemini-api/docs/api-key
- Gemini text generation: https://ai.google.dev/gemini-api/docs/text-generation
- Gemini structured output: https://ai.google.dev/gemini-api/docs/structured-output
- Gemini function calling: https://ai.google.dev/gemini-api/docs/function-calling

---

## 28. Instrucción final para OpenCode

Empieza inspeccionando el repositorio.

Si está vacío, ejecuta la primera tarea descrita en la sección 23.

Si ya contiene código, no recrees el proyecto: compara el estado real con este documento, identifica la siguiente brecha pequeña y trabaja únicamente en ella.

No uses una clave real de Gemini durante la generación inicial. Crea la integración y las pruebas con `FakeAiProvider`, documenta cómo añadir `GEMINI_API_KEY` en `backend/.env`, y mantén el sistema completamente funcional con Gemini desactivado.
