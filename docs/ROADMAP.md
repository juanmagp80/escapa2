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

- ✅ Proveedores normalizados detrás de interfaces (`FlightProvider`, `HotelProvider`).
- ✅ `AmadeusClient` con autenticación OAuth2 (client credentials), caché de token y transporte inyectable para pruebas.
- ✅ `AmadeusFlightProvider` (`/v2/shopping/flight-offers`) y `AmadeusHotelProvider` (`/v3/shopping/hotel-offers`) con modelos internos `FlightOffer`/`HotelOffer`.
- ✅ Mocks deterministas y factoría de proveedores (`providers/factory.py`): Amadeus cuando `AMADEUS_ENABLED=true`, mocks por defecto.
- ✅ Fail-fast al arrancar si un proveedor está activado sin credenciales (`validate_provider_credentials`).
- ✅ Tests con `httpx.MockTransport` (token, errores, normalización de fechas a UTC, expiración, cuota como `PROVIDER_QUOTA_EXCEEDED`).
- Historial.
- Gestión de cuota.
- Endpoints REST que expongan las ofertas reales de vuelos/hoteles (pendiente de la Fase 3 completa).

## Fase 4 — Radar diario

- ✅ Endpoint `/watches` (CRUD + run simulado) y Radar Android conectado al backend.
- ✅ Endpoint `POST /ai/daily-report` (informe diario por reglas o Gemini, con fallback y caché).
- ✅ `POST /watches/{id}/run` guarda snapshots de precio y evalúa las reglas de alerta configuradas.
- ✅ Historial de precios real en el detalle Android (`GET /opportunities/{id}/price-history`), conectado a los snapshots de cada ejecución del radar.
- ✅ Scheduler diario en backend (`SCHEDULER_ENABLED`): ejecuta en un hilo los seguimientos activos cuyo `next_run_at` ha pasado; desactivado por defecto.
- ✅ `POST /watches/daily-report`: informe diario generado desde los datos reales de los seguimientos (snapshots, mínimo registrado, cambio), con reglas o Gemini.
- ✅ Snapshots.
- ✅ Reglas de alerta.
- ✅ Informe diario.
- ✅ Registro de dispositivos y notificaciones push: `POST /devices`, `DELETE /devices/{token}`, `NotificationService` que envía un resumen por seguimiento al ejecutarse el radar y registra cada intento en el log con estado.
- ✅ `FirebaseNotificationSender` (multicast) con `firebase-admin` importado perezosamente y fallback a `MockNotificationSender`; `NotificationDevice` + `NotificationLogORM` con migración Alembic `0005`.
- ✅ Scheduler notifica tras cada ejecución del radar (alerta → push) sin romper la ejecución si el envío falla.
- Integración Android: registro del token FCM y pantalla de ajustes de notificaciones.

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

## Fase 8 — Rediseño visual y experiencia de uso

Pendiente, marcada por el usuario (2026-08-06): la app debe tener una estética
que atraiga usuarios, no solo funcional. Alcance orientativo:

- Revisar la paleta de color actual (excesivamente verde) y definir una
  identidad de viaje más cuidada con Material 3.
- Revisar tipografía, espaciado, tarjetas e iconografía.
- Revisar el Home: los viajes sugeridos no se perciben útiles mientras no haya
  datos reales de vuelos, hoteles y carburante; estudiar cómo presentar el valor
  en la fase de datos simulados.
- Encuestas visuales y refinamientos incrementales sobre las pantallas
  existentes.
