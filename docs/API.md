# API Reference

Base path: `/api/v1`.

Convenciones generales:

- JSON.
- Fechas y horas en ISO 8601 con zona horaria.
- Importes con moneda explícita.
- Identificadores UUID.
- Paginación en listas.
- Respuesta de error uniforme:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request is invalid",
    "details": {}
  }
}
```

## Sistema

### `GET /health`

Liveness. No depende de dependencias externas.

```json
{
  "status": "ok",
  "app": "Escapa2 Radar API",
  "version": "0.1.0"
}
```

### `GET /ready`

Readiness. Comprueba conexión con PostgreSQL.

```json
{
  "status": "ok",
  "checks": { "database": "up" }
}
```

Si la base de datos no está disponible devuelve HTTP 503 con `status: "degraded"`.

## Perfil

Base: `/api/v1/profile`.

Durante el vertical slice el perfil proviene de `MockProfileProvider` con un
usuario de desarrollo fijo (`origin_city=Madrid`, presupuesto 350 EUR).

### `GET /profile`

Devuelve el perfil de viaje de la pareja.

```json
{
  "id": "00000000-0000-4000-8000-000000000001",
  "origin_city": "Madrid",
  "currency": "EUR",
  "default_budget_eur": 350.0,
  "max_drive_minutes": 240,
  "preferred_transport": "EITHER",
  "interests": ["ciudad", "gastronomía"],
  "avoid_preferences": ["vida nocturna"],
  "created_at": "2026-08-05T12:00:00Z",
  "updated_at": "2026-08-05T12:00:00Z"
}
```

### `PUT /profile`

Reemplaza los campos editables del perfil. `id`, `created_at` se conservan y
`updated_at` se actualiza. La moneda y el modo de transporte se normalizan a
mayúsculas; las listas de intereses y exclusiones se recortan y eliminan vacíos.

Entrada:

```json
{
  "origin_city": "Barcelona",
  "currency": "eur",
  "default_budget_eur": 500.0,
  "max_drive_minutes": 300,
  "preferred_transport": "CAR",
  "interests": ["playa", "montaña"],
  "avoid_preferences": []
}
```

Devuelve el perfil actualizado. Errores de validación con `422` y código
`VALIDATION_ERROR`.

### `GET /profile/airports`

Lista los aeropuertos de salida aceptados.

```json
[
  {
    "id": "00000000-0000-4000-8000-000000000002",
    "travel_profile_id": "00000000-0000-4000-8000-000000000001",
    "iata_code": "MAD",
    "enabled": true,
    "transfer_cost_eur": 12.0,
    "transfer_minutes": 45
  }
]
```

### `PUT /profile/airports`

Reemplaza la lista completa de aeropuertos aceptados. Cada elemento recibe un
nuevo `id` y se asocia al perfil actual.

Entrada:

```json
[
  { "iata_code": "AGP", "enabled": true, "transfer_cost_eur": 25.0, "transfer_minutes": 20 },
  { "iata_code": "SVQ", "enabled": true }
]
```

### `GET /profile/vehicle`

Devuelve el vehículo por defecto de la pareja, usado para estimar los costes de
coche (combustible, desvíos a gasolineras y desgaste). Si no existe, se crea uno
de desarrollo igual que el resto del perfil.

```json
{
  "id": "00000000-0000-4000-8000-000000000004",
  "travel_profile_id": "00000000-0000-4000-8000-000000000001",
  "name": "Coche habitual",
  "fuel_type": "DIESEL",
  "average_consumption_l_per_100km": 6.0,
  "tank_capacity_l": 55.0,
  "estimated_cost_per_km_eur": 0.1,
  "max_fuel_detour_minutes": 15,
  "created_at": "2026-08-07T12:00:00Z",
  "updated_at": "2026-08-07T12:00:00Z"
}
```

`fuel_type` acepta `DIESEL`, `GASOLINE`, `HYBRID` o `ELECTRIC`. Para vehículos de
combustible `average_consumption_l_per_100km` es obligatorio; en eléctricos se
omite.

### `PUT /profile/vehicle`

Reemplaza los campos editables del vehículo por defecto.

Entrada:

```json
{
  "name": "Coche habitual",
  "fuel_type": "GASOLINE",
  "average_consumption_l_per_100km": 6.5,
  "tank_capacity_l": 50.0,
  "estimated_cost_per_km_eur": 0.12,
  "max_fuel_detour_minutes": 20
}
```

Se devuelve un `422` si falta `average_consumption_l_per_100km` en un vehículo
no eléctrico o si el `fuel_type` no es válido.

### `GET /profile/vehicle`

Devuelve el vehículo por defecto de la pareja, usado para estimar los costes de
coche (combustible, peajes, aparcamiento y desgaste en las rutas). Si no existe,
se crea uno de desarrollo.

```json
{
  "id": "00000000-0000-4000-8000-000000000004",
  "travel_profile_id": "00000000-0000-4000-8000-000000000001",
  "name": "Coche habitual",
  "fuel_type": "DIESEL",
  "average_consumption_l_per_100km": 6.0,
  "tank_capacity_l": 55.0,
  "estimated_cost_per_km_eur": 0.1,
  "max_fuel_detour_minutes": 15,
  "created_at": "2026-08-07T12:00:00Z",
  "updated_at": "2026-08-07T12:00:00Z"
}
```

`fuel_type` acepta `DIESEL`, `GASOLINE`, `HYBRID` o `ELECTRIC`. Para vehículos de
combustible `average_consumption_l_per_100km` es obligatorio.

### `PUT /profile/vehicle`

Reemplaza los campos editables del vehículo por defecto.

Entrada:

```json
{
  "name": "Furgoneta",
  "fuel_type": "GASOLINE",
  "average_consumption_l_per_100km": 7.5,
  "tank_capacity_l": 60.0,
  "estimated_cost_per_km_eur": 0.14,
  "max_fuel_detour_minutes": 20
}
```

## Disponibilidad

Base: `/api/v1/availability`.

Durante el vertical slice las ventanas provienen de `MockAvailabilityProvider`
con tres ventanas de ejemplo (dos de fin de semana y unas vacaciones).

### `GET /availability`

Lista todas las ventanas de disponibilidad.

```json
[
  {
    "id": "10000000-0000-4000-8000-000000000001",
    "start_at": "2026-08-14T16:00:00Z",
    "end_at": "2026-08-16T20:00:00Z",
    "kind": "WEEKEND",
    "is_flexible": true,
    "created_at": "2026-08-05T12:00:00Z"
  }
]
```

### `POST /availability`

Crea una ventana de disponibilidad. Devuelve `201` con la ventana creada.

Entrada:

```json
{
  "start_at": "2026-10-16T18:00:00+02:00",
  "end_at": "2026-10-18T22:00:00+02:00",
  "kind": "WEEKEND",
  "is_flexible": true
}
```

Si `end_at` no es posterior a `start_at` devuelve `422` con `VALIDATION_ERROR`.

### `PUT /availability/{id}`

Reemplaza los campos editables de una ventana. Devuelve `404` con `NOT_FOUND`
si no existe y `422` si el identificador no es un UUID válido.

### `DELETE /availability/{id}`

Elimina una ventana. Devuelve `204` sin contenido; `404` con `NOT_FOUND` si no
existe.

## IA

### `POST /ai/opportunity-summary`

Genera un resumen orientativo de una oportunidad de viaje.

Entrada:

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
  "pros": ["Está 38 EUR por debajo del presupuesto", "Vuelo directo"],
  "cons": ["El traslado al aeropuerto todavía no está incluido"],
  "confidence": "MEDIUM",
  "generated_by_ai": true
}
```

Comportamiento:

- Con `GEMINI_ENABLED=false` devuelve una respuesta determinista con `generated_by_ai=false`.
- El backend valida la salida estructurada de Gemini contra el esquema Pydantic.
- Si Gemini falla o devuelve JSON inválido, se reintenta una vez y luego se usa el fallback por reglas.

### `POST /ai/interpret-search`

Interpreta una búsqueda escrita en lenguaje natural y la convierte en criterios
estructurados. Solo rellena campos claramente expresados en la consulta.

Entrada:

```json
{
  "query": "Queremos salir desde Madrid con un presupuesto de 400 euros para dos, en coche, y nos gusta la playa."
}
```

Salida:

```json
{
  "origin_city": "Madrid",
  "budget_eur": 400.0,
  "travelers": 2,
  "preferred_transport": "CAR",
  "interests": ["playa"],
  "max_drive_minutes": null,
  "start_window": null,
  "end_window": null,
  "duration_days": null,
  "confidence": "HIGH",
  "generated_by_ai": false
}
```

Con `GEMINI_ENABLED=false` la interpretación es determinista por reglas
(reconocimiento de origen, presupuesto, viajeros, transporte, intereses, límite
de conducción y fechas).

### `POST /ai/itineraries`

Genera un itinerario orientativo a partir de datos confirmados. Los costes
estimados solo se incluyen si el proveedor los confirma; nunca se inventan.

Entrada:

```json
{
  "destination": "Santiago de Compostela",
  "start_date": "2026-08-14",
  "end_date": "2026-08-16",
  "transport_mode": "CAR",
  "budget_eur": 350.0,
  "interests": ["gastronomía", "ciudad"],
  "facts": ["Hotel with free cancellation"]
}
```

Salida:

```json
{
  "summary": "Itinerario orientativo de 3 días en Santiago de Compostela. Las actividades y horarios son una propuesta general, no una reserva.",
  "warnings": [
    "Itinerario orientativo generado por reglas: confirma horarios, aperturas y precios reales antes de planificar.",
    "Los costes estimados no están incluidos porque no son datos verificados."
  ],
  "days": [
    {
      "date": "2026-08-14",
      "title": "Día 1",
      "items": [
        { "start_time": "10:00", "end_time": "12:00", "title": "Explorar la zona de interés: gastronomía", "estimated_cost_eur": null, "source_place_id": null }
      ]
    }
  ],
  "generated_by_ai": false
}
```

### `POST /ai/daily-report`

Genera un informe diario personalizado a partir del historial de precios
confirmado de los viajes vigilados. La IA solo resume los datos aportados; nunca
inventa precios ni disponibilidad.

Entrada:

```json
{
  "report_date": "2026-08-06",
  "watches": [
    {
      "watch_name": "Porto finde",
      "destination": "Porto",
      "current_total_eur": 312.0,
      "previous_total_eur": 328.0,
      "min_recorded_eur": 312.0,
      "budget_eur": 350.0,
      "price_history": [
        { "captured_at": "2026-08-05T12:00:00Z", "total_eur": 328.0 },
        { "captured_at": "2026-08-06T12:00:00Z", "total_eur": 312.0 }
      ],
      "facts": ["Direct flight"]
    }
  ]
}
```

Salida:

```json
{
  "headline": "Porto bajó de precio hoy",
  "summary": "Los precios verificados hoy bajan respecto al registro anterior en Porto (-16.00 EUR). Verifica la disponibilidad antes de reservar; los precios pueden cambiar.",
  "entries": [
    {
      "watch_name": "Porto finde",
      "destination": "Porto",
      "change_eur": 16.0,
      "change_percent": 4.9,
      "is_new_low": true,
      "within_budget": true,
      "recommendation": "Nuevo mínimo registrado: es un buen momento para verificar y valorar la reserva.",
      "confidence": "HIGH"
    }
  ],
  "warnings": [
    "Informe orientativo basado en datos verificados a la hora indicada.",
    "Los precios y la disponibilidad pueden cambiar sin previo aviso."
  ],
  "generated_by_ai": false
}
```

Con `GEMINI_ENABLED=false` el informe es determinista por reglas: calcula la
bajada por viaje, detecta nuevos mínimos y comprueba el presupuesto.

### Límites y caché de IA

- Cuota diaria por usuario: `GEMINI_MAX_REQUESTS_PER_USER_DAY` (por defecto 20).
  Al superarla se devuelve `429` con `RATE_LIMITED`.
- Caché en memoria por hash de datos y versión de prompt: peticiones idénticas
  repetidas no vuelven a llamar a Gemini.
- Con `GEMINI_ENABLED=false` no hay límite de cuota ni llamadas externas.

## Oportunidades

Base: `/api/v1/opportunities`.

Durante el vertical slice los datos provienen de `MockOpportunityProvider` (cuatro
oportunidades de referencia: coche en España, avión en España, avión en Europa y una
opción más barata con menos horas útiles).

### `GET /opportunities`

Lista de oportunidades con filtros opcionales.

Parámetros de consulta:

| Parámetro           | Tipo          | Descripción                                  |
| ------------------- | ------------- | -------------------------------------------- |
| `max_total_cost_eur`| `float` ≥ 0   | Máximo coste total para dos.                 |
| `transport_mode`    | `FLIGHT`, `CAR`, `EITHER` | Modo de transporte.              |
| `start_after`       | ISO 8601      | Salida igual o posterior.                    |
| `end_before`        | ISO 8601      | Regreso igual o anterior.                    |
| `destination`       | `string`      | Subcadena, sin distinguir mayúsculas.        |
| `min_useful_hours`  | `float` ≥ 0   | Mínimo de horas útiles.                      |
| `sort`              | `string`      | Campo con prefijo opcional `-` para descender. Valores: `total_cost_eur`, `useful_hours`, `cost_per_useful_hour_eur`, `provider_verified_at`. |

Respuesta:

```json
[
  {
    "id": "11111111-1111-4111-8111-111111111111",
    "destination_code": "GAL",
    "destination_name": "Santiago de Compostela",
    "transport_mode": "CAR",
    "start_at": "2026-08-14T16:30:00Z",
    "end_at": "2026-08-16T18:00:00Z",
    "useful_hours": 34.0,
    "total_cost_eur": 198.0,
    "cost_per_person_eur": 99.0,
    "cost_per_night_eur": 99.0,
    "cost_per_useful_hour_eur": 5.82,
    "comfort_score": null,
    "value_score": null,
    "provider_verified_at": "2026-08-05T12:00:00Z"
  }
]
```

### `GET /opportunities/{id}`

Detalle de una oportunidad. Devuelve `404` con `NOT_FOUND` si no existe y `422`
con `VALIDATION_ERROR` si el identificador no es un UUID válido.

### `GET /opportunities/{id}/price-history`

Historial de precios de una oportunidad, ordenado de más antiguo a más reciente.

```json
[
  {
    "id": "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
    "travel_opportunity_id": "33333333-3333-4333-8333-333333333333",
    "total_cost_eur": 328.0,
    "flight_cost_eur": 226.0,
    "hotel_cost_eur": 72.0,
    "route_cost_eur": null,
    "local_transport_cost_eur": null,
    "fees_cost_eur": null,
    "captured_at": "2026-08-02T12:00:00Z",
    "source_summary_json": { "provider": "mock", "currency": "EUR" }
  }
]
```

## Seguimientos (Radar)

Base: `/api/v1/watches`.

Durante el vertical slice los datos provienen de `MockSearchWatchProvider` con dos
seguimientos de referencia. `criteria_json` y `alert_rules_json` son objetos JSON
libres; la app Android usa `initial_price_eur` en los criterios y `rules` (array de
strings) en las reglas de alerta.

### `GET /watches`

Lista los seguimientos activos.

### `POST /watches`

Crea un seguimiento.

```json
{
  "name": "Roma en avión",
  "status": "ACTIVE",
  "criteria": { "max_total_cost_eur": 400, "transport_mode": "FLIGHT" },
  "alert_rules": { "rules": ["Nuevo mínimo histórico"] }
}
```

### `GET /watches/{id}`

Detalle de un seguimiento. `404` con `NOT_FOUND` si no existe.

### `PUT /watches/{id}`

Actualiza campos opcionales (`name`, `status`, `criteria`, `alert_rules`). Solo se
aplican los campos presentes.

### `DELETE /watches/{id}`

Elimina un seguimiento. `204` en caso de éxito.

### `POST /watches/daily-report`

Genera el informe diario conectado a los datos reales de los seguimientos. El
backend construye la entrada desde los watches `ACTIVE` con oportunidades
coincidentes: para cada uno toma la oportunidad más barata que encaje en sus
criterios, su historial de `PriceSnapshot`, el presupuesto
(`budget_eur`/`max_total_cost_eur`), el precio anterior, el mínimo registrado y
datos del transporte. Después resume el conjunto con reglas deterministas
(`generated_by_ai=false`) o con Gemini cuando `GEMINI_ENABLED=true`.

Respuesta (`200`):

```json
{
  "report_date": "2026-08-06",
  "headline": "Santiago de Compostela marca un nuevo mínimo registrado",
  "generated_by_ai": false,
  "entries": [
    {
      "watch_name": "Roma en avión",
      "destination": "Porto (horario ajustado)",
      "current_total_eur": 214.0,
      "previous_total_eur": 246.0,
      "min_recorded_eur": 214.0,
      "change_eur": -32.0,
      "change_percent": -13.0
    }
  ]
}
```

Errores:

- `404 NOT_FOUND` cuando no hay ningún watch `ACTIVE` con oportunidades
  coincidentes.

### `POST /watches/{id}/run`

Ejecuta un seguimiento: refresca `last_run_at` y `next_run_at`, guarda un
`PriceSnapshot` por cada oportunidad que coincide con los criterios almacenados
(`max_total_cost_eur` y `transport_mode`) y evalúa las reglas de alerta
configuradas en `alert_rules.rules` contra el historial de precios registrado.

Reglas de alerta reconocidas (texto libre, sin distinguir mayúsculas):

- `"Viaje por debajo de 350 EUR"` → umbral absoluto.
- `"Bajada superior a 10%"` o `"Bajada de 5%"` → porcentaje de bajada.
- `"Bajada de 40 EUR"` → bajada absoluta.
- `"Nuevo mínimo histórico"` → nuevo mínimo registrado.
- `"Vuelve a estar dentro del presupuesto"` → encaje en el presupuesto.

El presupuesto y el precio inicial se toman de `criteria_json`
(`budget_eur`/`max_total_cost_eur` y `initial_price_eur`). Si la oportunidad ya
tiene historial, el `previous` y el mínimo se calculan de sus snapshots reales.

Respuesta:

```json
{
  "last_run_at": "2026-08-06T12:00:00Z",
  "next_run_at": "2026-08-07T12:00:00Z",
  "matched_opportunities": [
    {
      "id": "22222222-2222-4222-8222-222222222222",
      "destination_code": "SVQ",
      "destination_name": "Sevilla",
      "transport_mode": "FLIGHT",
      "total_cost_eur": 246.0
    }
  ],
  "alerts": [
    {
      "rule": "new_low",
      "message": "Nuevo mínimo histórico: 246 EUR"
    }
  ]
}
```

La evaluación es idempotente por seguimiento y oportunidad: cada ejecución
añade un snapshot nuevo con su propio UUID y `captured_at`, por lo que el
historial crece de forma natural hacia el radar diario.

## Notificaciones push

Base: `/api/v1/devices`.

El registro de dispositivos usa un usuario de desarrollo fijo
(`dev-user`) hasta que exista autenticación. El envío real usa Firebase Cloud
Messaging cuando `FIREBASE_ENABLED=true`; en caso contrario se registra el envío
simulado en el log.

### `POST /devices`

Registra un token de dispositivo para recibir notificaciones. Idempotente por
`token` y usuario: si ya existe devuelve el registro existente.

Entrada:

```json
{
  "token": "device-token-123",
  "platform": "android"
}
```

Respuesta (`201`):

```json
{
  "id": "e2000000-0000-4000-8000-000000000001",
  "user_id": "dev-user",
  "token": "device-token-123",
  "platform": "android",
  "created_at": "2026-08-06T12:00:00Z",
  "updated_at": "2026-08-06T12:00:00Z"
}
```

### `DELETE /devices/{token}`

Elimina el registro de un token. `204` si se eliminó; `404` con `NOT_FOUND` si no
existía.

La app Android registra un token estable por instalación mediante este endpoint
mientras no esté configurado Firebase Messaging; al habilitar FCM se usará el
token real de Firebase.

### Notificaciones del radar

Al ejecutar el radar (`POST /watches/{id}/run` o el scheduler), si el seguimiento
genera alertas se envía **un solo mensaje por seguimiento** a todos los tokens
registrados del usuario, con un resumen de las alertas disparadas. El payload
FCM incluye `watch_id`, `kind` (`RADAR_ALERT`) y `deep_link` (`escapa2://radar`)
para que al tocar la notificación la app abra la pantalla Radar. Cada alerta se
registra individualmente en el log con estado `SENT`, `SKIPPED` o `FAILED`.

Tipos de notificación según la regla:

| Regla                                   | Tipo            |
| --------------------------------------- | --------------- |
| `new_low`                               | `NEW_LOW`       |
| `budget_match` / presupuesto            | `BUDGET_MATCH`  |
| `consecutive_rise`                      | `PRICE_RISING`  |
| resto (umbral, bajada absoluta, etc.)   | `PRICE_DROP`    |

Un fallo del proveedor de notificaciones nunca interrumpe la ejecución del radar:
el resto de la ejecución continúa y el envío se registra como `FAILED`.
