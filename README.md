# Escapa2 Radar

Aplicación Android para encontrar escapadas económicas en pareja. Combina disponibilidad de fechas, presupuesto, transporte, alojamiento, tiempo útil en destino y preferencias personales para recomendar el viaje completo más conveniente.

> Dime cuándo podemos viajar, cuánto queremos gastar y desde dónde salimos; búscanos diariamente la mejor escapada completa, no simplemente el vuelo más barato.

## Repositorio

```text
escapa2-radar/
├── android-app/   # App Android (Kotlin, Jetpack Compose, Hilt, Room)
├── backend/       # API (Python 3.12, FastAPI, SQLAlchemy, Alembic)
├── docs/          # API.md, DECISIONS.md, ROADMAP.md
├── scripts/       # Scripts de desarrollo (ver scripts/README.md)
└── docker-compose.yml  # PostgreSQL
```

## Estado actual

Fase 0 completa, Fase 1 y Fase 2 (Gemini) backend completo: perfil, disponibilidad, oportunidades simuladas con métricas de coste y scoring, persistencia SQL opcional, pantallas Home/Explorar/Detalle/Radar/Perfil, caché Room con fallback offline, módulos de dominio puros (costes, horas útiles, score de valor, ahorro neto de gasolineras y reglas de alerta), y capa de IA con resumen de oportunidad, interpretación de búsqueda natural, itinerario estructurado, fallback determinista, rate limiting y caché.

La app Android incluye: Home con dashboard (mejor oportunidad, mayor bajada, próximas fechas, vigilados y última actualización), Explorar con filtros de presupuesto, transporte, horas útiles, destino y duración, detalle con historial de precios, explicación de IA y botón para seguir la búsqueda, perfil editable con aeropuertos, y Radar con seguimientos simulados.

## Requisitos

- Python 3.12 o superior.
- JDK 17.
- Android Studio (para ejecutar la app).
- Docker (opcional, para PostgreSQL).

## Backend

```powershell
cd backend
Copy-Item .env.example .env        # configura variables (sin secretos por defecto)
powershell -ExecutionPolicy Bypass -File ../scripts/backend_setup.ps1   # venv + dependencias
powershell -ExecutionPolicy Bypass -File ../scripts/backend_run.ps1     # uvicorn con reload
```

- Sin credenciales, la app arranca con proveedores simulados. Con `GEMINI_ENABLED=true` es obligatorio `GEMINI_API_KEY`.
- `PERSISTENCE_BACKEND=memory` (por defecto) usa datos en memoria. Con `PERSISTENCE_BACKEND=sql` persiste en PostgreSQL (Alembic) y siembra las oportunidades de referencia al primer uso. `/dev/seed` y `/dev/reset` solo existen con `APP_ENV=development`.

### Calidad

```powershell
cd backend
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m mypy app
.\.venv\Scripts\python.exe -m pytest
```

### PostgreSQL

```bash
docker compose up -d postgres
cd backend
.\.venv\Scripts\python.exe -m alembic upgrade head
```

## Android

```powershell
cd android-app
.\gradlew.bat assembleDebug
.\gradlew.bat test
.\gradlew.bat lint
```

Instala el APK generado en `android-app/app/build/outputs/apk/debug/app-debug.apk` o ejecuta desde Android Studio. En desarrollo la app usa repositorios fake (perfil, oportunidades, seguimientos), con caché Room para datos consultados.

## Documentación

- `docs/API.md`: contrato de la API.
- `docs/DECISIONS.md`: decisiones arquitectónicas (ADRs).
- `docs/ROADMAP.md`: fases y estado.
- `scripts/README.md`: scripts de desarrollo.

## Notas de seguridad

- La clave de Gemini vive solo en el backend (`backend/.env`, ignorado por Git).
- No hay reservas ni cancelaciones automáticas; los precios mostrados se indican como verificados a una hora concreta.
