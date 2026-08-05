# Scripts de desarrollo

## Backend

### `scripts/backend_setup.ps1`

Crea el virtualenv, instala dependencias y prepara el entorno del backend en Windows.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/backend_setup.ps1
```

### `scripts/backend_run.ps1`

Arranca el servidor de desarrollo del backend (uvicorn con reload).

```powershell
powershell -ExecutionPolicy Bypass -File scripts/backend_run.ps1
```

### `scripts/backend_test.ps1`

Ejecuta ruff, mypy y pytest del backend.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/backend_test.ps1
```

## PostgreSQL

Levantar la base de datos:

```bash
docker compose up -d postgres
```

## Android

```bash
cd android-app
gradlew.bat assembleDebug
gradlew.bat test
```
