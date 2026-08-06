# Roadmap

## Fase 0 — Repositorio y herramientas ✅ (en curso)

- Monorepo.
- Backend mínimo.
- Android mínimo.
- Docker Compose con PostgreSQL.
- Health checks.
- README y convenciones.

## Fase 1 — Vertical slice con datos simulados

- [x] Oportunidades simuladas (`GET /opportunities`, detalle e historial de precios).
- [x] Costes (funciones puras: coste total, por persona, por noche y por hora útil).
- [x] Perfil (`GET/PUT /profile` y `GET/PUT /profile/airports`).
- [x] Disponibilidad (CRUD `/availability`).
- [x] Pantalla de detalle de oportunidad en Android (resumen, desglose, horas útiles, aviso de precios).
- [x] Explorar con resultados (filtros de presupuesto, transporte, horas útiles, destino, origen, intereses, duración y fechas libres conectados al repositorio; botones "Buscar escapada" y "Sorpréndeme").
- [x] Persistencia (backend SQL opcional con `PERSISTENCE_BACKEND=sql` + migraciones Alembic; Room en Android con caché y fallback offline).
- [x] Radar con seguimientos simulados (última/próxima ejecución, cambio desde ayer, mínimo registrado, reglas de alerta, historial).
- [x] Pantalla Home con dashboard: mejor oportunidad (value score), mayor bajada de precio, próximas fechas, viajes vigilados y estado de última actualización.
- [x] Perfil Android editable (ciudad, moneda, presupuesto, máximo en coche, transporte, intereses, exclusiones) con aeropuertos editables (añadir, habilitar/deshabilitar y eliminar mediante `PUT /profile/airports`).
- [x] Detalle de oportunidad con historial de precios (anterior → actual), desglose de costes (vuelo/hotel/coche cuando el proveedor lo aporta), enlace de reserva externo y botón para seguir la búsqueda.
- [x] Oportunidades con campos informativos (`origin_city`, `interests`, `flight_cost_eur`, `hotel_cost_eur`, `route_cost_eur`, `booking_url`) servidos por el backend y mostrados en la app.
- [x] Disponibilidad conectada al Home ("próximas fechas libres") y al filtro de fechas de Explorar mediante `/availability`.
- [x] Pruebas (scoring 9.6, ahorro neto de gasolinera 9.4, reglas de alerta 9.5, repositorios SQL, persistencia Room).

## Fase 2 — Gemini

- [x] `AiProvider`, `FakeAiProvider`, `GeminiAiProvider`.
- [x] Resumen de oportunidad.
- [x] Interpretación de búsqueda natural (`POST /ai/interpret-search`).
- [x] Itinerario estructurado (`POST /ai/itineraries`).
- [x] Fallback, rate limiting por usuario/día y caché por hash de datos + versión de prompt.
- [x] Integración en Android de las explicaciones de IA (sección en el detalle con `AiRepository` + fake determinista).

## Fase 3 — Vuelos y hoteles reales

- Integración Amadeus.
- Normalización.
- Precios y expiración.
- Historial.
- Gestión de cuota.

## Fase 4 — Radar diario

- ✅ Endpoint `/watches` (CRUD + run simulado) y Radar Android conectado al backend.
- ✅ Endpoint `POST /ai/daily-report` (informe diario por reglas o Gemini, con fallback y caché).
- ✅ `POST /watches/{id}/run` guarda snapshots de precio y evalúa las reglas de alerta configuradas.
- ✅ Historial de precios real en el detalle Android (`GET /opportunities/{id}/price-history`), conectado a los snapshots de cada ejecución del radar.
- Scheduler.
- Snapshots.
- Reglas de alerta.
- Informe diario.
- Firebase Cloud Messaging.

## Fase 5 — Coche

- Google Routes.
- Coste de combustible.
- Peajes.
- Perfil de vehículo.
- Gasolineras oficiales.

## Fase 6 — Pareja y personalización

- Autenticación.
- Calendario compartido.
- Votaciones.
- Favoritos.

## Fase 7 — Reservas vigiladas y mejoras

- Seguimiento de hotel.
- Gastos reales.
- Predicción orientativa.
