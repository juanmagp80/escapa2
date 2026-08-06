# Decisiones arquitectónicas

Este documento registra las decisiones arquitectónicas relevantes del proyecto. Cada entrada debe ser breve y explicar el contexto, la decisión y las alternativas descartadas.

## ADR-001: Aplicación Android nativa con backend separado

- **Estado:** Aceptada.
- **Contexto:** El producto necesita búsquedas programadas, historial de precios, notificaciones y uso de Gemini con una API key que nunca debe estar en el dispositivo.
- **Decisión:** Aplicación Android nativa (Kotlin + Jetpack Compose) y backend separado en Python/FastAPI.
- **Alternativas descartadas:** Backend serverless con funciones; API key de Gemini en el cliente; aplicación híbrida.
- **Consecuencias:** Gemini se invoca siempre desde el backend. La app nunca contiene credenciales de proveedores.

## ADR-002: Gemini detrás de una interfaz propia

- **Estado:** Aceptada.
- **Contexto:** Queremos poder cambiar de modelo, SDK o proveedor de IA sin afectar al resto del sistema.
- **Decisión:** Definir un protocolo `AiProvider` en el dominio. Implementar `FakeAiProvider` (determinista, para desarrollo y tests) y `GeminiAiProvider` (SDK oficial `google-genai`).
- **Consecuencias:** Toda generación de IA pasa por la interfaz. El sistema funciona completamente con `GEMINI_ENABLED=false`.

## ADR-003: PostgreSQL como única fuente de verdad

- **Estado:** Aceptada.
- **Contexto:** Necesitamos criterios de búsqueda, snapshots de precios, historial y resultados normalizados de forma persistente.
- **Decisión:** PostgreSQL con SQLAlchemy 2 y Alembic para migraciones.
- **Consecuencias:** La caché local de Android (Room) es solo de presentación; el backend mantiene el estado canónico.

## ADR-004: Proveedores externos detrás de interfaces

- **Estado:** Aceptada.
- **Contexto:** Amadeus, Google Routes, gasolineras, etc. tienen contratos distintos y cambian con frecuencia.
- **Decisión:** Cada proveedor implementa un protocolo en el dominio y expone modelos internos normalizados. Nunca se acopla el dominio al JSON original del proveedor.
- **Consecuencias:** En desarrollo se usan mocks. El cambio a proveedores reales no afecta a routers ni a la lógica de negocio.

## ADR-005: La IA nunca inventa precios ni disponibilidad

- **Estado:** Aceptada.
- **Contexto:** Gemini no es fuente de datos transaccionales.
- **Decisión:** Gemini recibe únicamente datos confirmados o estimados marcados explícitamente. Sus salidas estructuradas se validan con Pydantic y tienen fallback por reglas.
- **Consecuencias:** Las recomendaciones son orientativas y se muestran como tal al usuario.

## ADR-006: Monorepo

- **Estado:** Aceptada.
- **Contexto:** El producto consta de backend, app Android e infraestructura relacionada.
- **Decisión:** Monorepo con `android-app/`, `backend/`, `docs/`, `infra/`, `scripts/`.
- **Consecuencias:** Commits atómicos por funcionalidad; CI único que prueba ambas partes.

## ADR-007: Usuario de desarrollo fijo durante el vertical slice

- **Estado:** Aceptada temporalmente.
- **Contexto:** La autenticación real llega en Fase 6.
- **Decisión:** Durante el vertical slice se usa un usuario de desarrollo generado por el backend.
- **Consecuencias:** Los endpoints no requieren token hasta que se implemente Firebase Authentication.

## ADR-008: Converter oficial de Retrofit para kotlinx-serialization

- **Estado:** Aceptada.
- **Contexto:** El proyecto usa Retrofit 2.11 y Kotlin Serialization. El catálogo de versiones declaraba el converter oficial `com.squareup.retrofit2:converter-kotlinx-serialization:2.11.0`, pero el código importaba la extensión del artefacto antiguo de JakeWharton, que no compila contra esa dependencia.
- **Decisión:** Usar el converter oficial. Su API pública en Kotlin es la función de extensión `retrofit2.converter.kotlinx.serialization.asConverterFactory` sobre `StringFormat`/`BinaryFormat`; la clase `KotlinSerializationConverterFactory` solo es la fachada JVM generada por `@file:JvmName` y no se referencia desde Kotlin.
- **Consecuencias:** Se evita el artefacto de JakeWharton; la configuración del `Retrofit.Builder` usa `json.asConverterFactory(contentType)` y queda alineada con el mantenimiento oficial de Square.

## ADR-009: Persistencia configurable en el backend

- **Estado:** Aceptada.
- **Contexto:** El vertical slice usa datos simulados en memoria, pero las oportunidades, perfiles y disponibilidad deben persistirse para el radar diario y el historial de precios.
- **Decisión:** `PERSISTENCE_BACKEND=memory|sql` (por defecto `memory`). Con `sql`, los repositorios usan SQLAlchemy + PostgreSQL vía `app/repositories/sql_*_repository.py`, se siembran las oportunidades de referencia al primer uso y los endpoints `/dev/seed` y `/dev/reset` quedan disponibles solo con `APP_ENV=development`.
- **Consecuencias:** Los routers dependen de los mismos contratos de repositorio; el cambio a SQL no altera servicios ni API. En producción solo se usará `sql`.

## ADR-010: Room como caché local con fallback offline

- **Estado:** Aceptada.
- **Contexto:** La app debe poder consultar viajes guardados sin conexión (AGENTS.md 15.2).
- **Decisión:** Room (2.6.1) con una entidad `OpportunityEntity` en snake_case para que el `ORDER BY cost_per_useful_hour_eur` funcione correctamente. `CachedOpportunityRepository` envuelve al repositorio remoto: guarda resultados y sirve datos cacheados si la red falla.
- **Consecuencias:** La app muestra contenido mientras haya caché; el backend sigue siendo la fuente de verdad.

## ADR-011: Score de valor, gasolineras y alertas como módulos de dominio puros

- **Estado:** Aceptada.
- **Contexto:** AGENTS.md 9.4/9.5/9.6 exige cálculos explicables y con pruebas unitarias.
- **Decisión:** Módulos puros `app/domain/scoring.py` (pesos 0.30/0.25/0.20/0.15/0.10), `app/domain/fuel_stations.py` (ahorro neto = bruto − coste de desvío − penalización de tiempo) y `app/domain/alerts.py` (reglas de umbral, bajadas, mínimo histórico, subidas consecutivas y ajuste a presupuesto). El `MockOpportunityProvider` calcula ahora `value_score` con el rango de precios de las cuatro oportunidades como referencia.
- **Consecuencias:** El `value_score` de las oportunidades simuladas es explicable y queda listo para conectarse a proveedores reales y al scheduler.

## ADR-012: Servicio de IA con cuota, caché y fallback

- **Estado:** Aceptada.
- **Contexto:** AGENTS.md 5.7 exige control de coste y abuso en las llamadas a Gemini, y la app debe seguir funcionando si la IA falla.
- **Decisión:** `AiService` es el único punto de contacto con la IA. Aplica una cuota diaria por usuario (`GEMINI_MAX_REQUESTS_PER_USER_DAY`), sirve respuestas cacheadas por hash de datos + versión de prompt (`AiResponseCache`), y cae a fallback determinista cuando el proveedor externo no está disponible. Con `FakeAiProvider` no se aplica cuota ni caché.
- **Consecuencias:** Los routers solo dependen del servicio; la cuota se comparte a nivel de proceso mediante una instancia única en `deps.py`. El rate limiter y la caché son por defecto en memoria, lo que obligará a Redis cuando haya múltiples workers.

## ADR-013: Perfil Android editable y seguimiento de búsquedas desde el detalle

- **Estado:** Aceptada.
- **Contexto:** AGENTS.md 11.2/11.4/11.6 pide un Home con dashboard, un detalle con historial y un perfil configurable, y el usuario reportó que la app era demasiado básica.
- **Decisión:** En Android se añaden `TravelProfile`/`AirportPreference` con `FakeProfileRepository` (en memoria) y una `ProfileScreen` editable (ciudad, moneda, presupuesto, máximo en coche, transporte, intereses, exclusiones; aeropuertos en solo lectura). `SearchWatchRepository.createWatch()` permite seguir una búsqueda desde el detalle. El Home deriva el dashboard de datos ya existentes: mejor oportunidad por `valueScore` (desempate por coste/hora útil), mayor bajada por `previousTotalCostEur`, próximas fechas y última verificación. `Opportunity` incorpora `previousTotalCostEur` y `valueScore` opcionales (solo presentación; la caché Room no los persiste).
- **Consecuencias:** Los datos del perfil y los seguimientos creados son por sesión mientras no exista backend real. El historial de precios del detalle es derivado (anterior → actual) hasta la Fase 4. La caché offline de Room no conserva los campos nuevos del modelo.

## ADR-014: Backend desplegado en Render con persistencia en memoria

- **Estado:** Aceptada (provisional hasta Fase 3/4).
- **Contexto:** El APK del móvil debe conectarse a un backend por HTTPS. El usuario quiere probar la app en su teléfono; Supabase no ejecuta FastAPI, así que se necesita un host Python.
- **Decisión:** Desplegar el backend en Render como servicio web Docker (`backend/Dockerfile`, Python 3.12 + uvicorn), con `PERSISTENCE_BACKEND=memory` en el primer despliegue para no depender de una base de datos. `render.yaml` declara el blueprint; `GEMINI_API_KEY` se configura a mano en el panel de Render (`sync: false`). `APP_ENV=production` desactiva los endpoints `/dev/*`.
- **Alternativas descartadas:** Railway y Fly.io (equivalente pero sin servicio Docker en el plan gratuito tan directo), Hugging Face Spaces (sin garantías para API pública).
- **Consecuencias:** Las oportunidades y el perfil vuelven a estado de fábrica al reiniciar el servicio. El radar diario y el historial persistente requieren pasar a PostgreSQL en Fases 3/4.

## ADR-015: Repositorios remotos en Android con fallback a fakes

- **Estado:** Aceptada.
- **Contexto:** La app funcionaba solo con repositorios fake; para el despliegue debe consumir la API real y seguir funcionando si el backend no está disponible o durante el desarrollo sin servidor.
- **Decisión:** La URL base se configura en tiempo de build mediante `BuildConfig.API_BASE_URL` (propiedad Gradle `escapa2ApiBaseUrl`; por defecto apunta al backend de Render). En `NetworkModule`, cada repositorio se envuelve en un fallback: `FallbackOpportunityRepository`, `FallbackAiRepository` y `FallbackProfileRepository` intentan el remoto y caen al fake local solo ante `IOException` o errores 5xx (nunca ante 4xx, para no enmascarar bugs). `CachedOpportunityRepository` sigue guardando en Room. Los DTOs usan `@SerialName` para alinearse con el JSON snake_case del backend. Los seguimientos (Radar) siguen con fakes porque el backend aún no expone `/watches`.
- **Consecuencias:** La app funciona con backend, sin backend (fakes), y sin red (caché Room). El debug permite HTTP en LAN (`usesCleartextTraffic` en `src/debug`) para probar contra un backend local; release solo HTTPS.

## ADR-016: Endpoint /watches y Radar Android conectado al backend

- **Estado:** Aceptada.
- **Contexto:** El Radar de Android mostraba seguimientos simulados porque el backend no exponía `/watches`. AGENTS.md 10.4 define el contrato CRUD + run.
- **Decisión:** Se implementa `/api/v1/watches` siguiendo el patrón de `availability`: dominio `SearchWatch`, provider (`MockSearchWatchProvider` y `SqlSearchWatchRepository`), servicio `SearchWatchService` con `create/update/delete/list_watches/run`, y router registrado en `deps.py`. `POST /watches/{id}/run` simula una ejecución: refresca `last_run_at`/`next_run_at` y filtra las oportunidades por `max_total_cost_eur` y `transport_mode` de `criteria_json`. Se añade la columna `couple_id` a `search_watches` (migración `0003`). En Android, `RemoteSearchWatchRepository` + `FallbackSearchWatchRepository` consumen el endpoint con el mismo fallback que el resto de repositorios; el modelo `SearchWatch` local deriva `minRecordedEur` y `alertRules` de `criteria_json`/`alert_rules_json`.
- **Consecuencias:** El Radar ya no depende de fakes cuando el backend está disponible. El `run` es una simulación; la evaluación de alertas y snapshots reales llegará con la Fase 4.

## ADR-017: Campos informativos de oportunidad y exploración completa en Android

- **Estado:** Aceptada.
- **Contexto:** El detalle de oportunidad no mostraba desglose de precios ni enlaces de reserva, el perfil tenía aeropuertos en solo lectura, Explorar no permitía buscar con origen/fechas/intereses y el Home no usaba la disponibilidad del backend. AGENTS.md 8.1 y 9.1 definen los componentes de coste; 10.3 y 10.5 definen los contratos de disponibilidad y oportunidades.
- **Decisión:** El backend añade campos opcionales a `Opportunity` (`origin_city`, `interests`, `flight_cost_eur`, `hotel_cost_eur`, `route_cost_eur`, `booking_url`; migración `0004`) y el mock los rellena cuando el proveedor puede aportarlos. En Android: el detalle muestra desglose de costes y botón de reserva externo; el perfil permite añadir, habilitar/deshabilitar y eliminar aeropuertos; Explorar incluye origen, fechas libres (`/availability`), tipo de destino y el botón "Buscar escapada" (además de "Sorpréndeme"); el Home usa `AvailabilityRepository` para "próximas fechas libres". El filtro de noches se aplica localmente porque el backend aún no lo soporta.
- **Consecuencias:** La app cubre el flujo completo del vertical slice sin fakes cuando el backend está disponible. El desglose y el enlace se muestran solo cuando el proveedor los aporta; nunca los inventa la IA.

## ADR-018: Informe diario de IA con datos confirmados

- **Estado:** Aceptada.
- **Contexto:** El contrato AGENTS.md 10.6 incluye `POST /ai/daily-report`, pero el backend no lo exponía. El informe diario es el resumen personalizado del radar que Gemini debe generar a partir de los cambios de precios (AGENTS.md 5.1 y 16).
- **Decisión:** Se añade `DailyReportRequest`/`DailyReportResponse` (schema con `watches`, precios actual/anterior, mínimo registrado, presupuesto e historial), el método `generate_daily_report` al protocolo `AiProvider`, la implementación de reglas en `FakeAiProvider`/fallback (calcula bajada, porcentaje, nuevo mínimo y encaje en presupuesto) y la de Gemini con un prompt anclado en datos confirmados. `AiService` lo expone con la misma caché y cuota diaria que el resto de endpoints.
- **Consecuencias:** El informe nunca inventa precios: solo resume los datos aportados. Las alertas y el scheduler reales que generen el historial de precios llegarán con el resto de la Fase 4.

