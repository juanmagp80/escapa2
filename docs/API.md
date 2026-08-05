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
