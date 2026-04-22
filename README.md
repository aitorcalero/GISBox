# GISBox - Sincronización Bidireccional ArcGIS ↔ Local

**GISBox** es un proyecto para crear un servicio de sincronización de archivos entre una cuenta de **ArcGIS Online** o **ArcGIS Enterprise** y un sistema de archivos local. Permite a los usuarios gestionar su contenido de ArcGIS (documentos, CSVs, Shapefiles, etc.) de manera similar a como lo harían con servicios como Dropbox o OneDrive.

Este proyecto utiliza la [ArcGIS API for Python](https://developers.arcgis.com/python/).

## 🚀 Funcionalidades Actualizadas

El proyecto ha sido mejorado con un sistema de **pruebas unitarias** robusto utilizando `pytest` y una configuración de **logging** más detallada y centralizada.

### Logging Mejorado

Ahora, el logging utiliza un formato estructurado (`%(asctime)s - %(name)s - %(levelname)s - %(message)s`) y loggers con nombre (`GISBoxSync`, `GISBoxMonitor`), lo que facilita el seguimiento de los eventos y la depuración.

### Pruebas Unitarias

Se ha creado una suite de pruebas unitarias para asegurar la fiabilidad de las clases principales:
- `tests/test_gisbox_sync.py`: Pruebas para la conexión, preparación del directorio y la lógica de descarga de `GISBoxSync`.
- `tests/test_gisbox_monitor.py`: Pruebas para la lógica de monitorización de archivos, subida y eliminación de elementos en ArcGIS de `GISBoxMonitor`.

Para ejecutar las pruebas:
```bash
pip install pytest pytest-mock
pytest
```

---

## 🛠️ Configuración y Requisitos

El proyecto ha sido refactorizado para ofrecer dos modos de operación:

1.  **Modo Backup/Descarga (`gisbox_sync.py`):** Sincronización de solo lectura. Descarga todo el contenido de ArcGIS (elementos de tipo archivo) a la estructura de carpetas local.
2.  **Modo Monitor/Subida (`gisbox_monitor.py`):** Sincronización de solo escritura. Monitoriza el directorio local y sube automáticamente los archivos nuevos, modificados o eliminados a ArcGIS Online/Enterprise.

La combinación de ambos scripts permite una **sincronización bidireccional** completa.

## 🛠️ Configuración y Requisitos

### Dependencias

Necesitas Python 3.x. Instala las dependencias usando `pip`:

```bash
pip install -r requirements.txt
```

### Configuración

El proyecto utiliza un archivo `.env` para la configuración de la conexión y las rutas. Edita el archivo `.env` en la raíz del proyecto para introducir tus credenciales y la ruta de sincronización local.

```ini
# Ejemplo de .env
ARCGIS_URL=https://www.arcgis.com
ARCGIS_USERNAME=tu_usuario
ARCGIS_PASSWORD=tu_contraseña
LOCAL_SYNC_DIR=/ruta/a/tu/carpeta/local/GISBox_Sync
```

## ⚙️ Uso

## 🧪 CLI MVP (recomendado)

Se añadió una CLI mínima para operar el proyecto desde un solo punto de entrada:

```bash
python gisbox_cli.py check-config
python gisbox_cli.py sync-down
python gisbox_cli.py monitor
```

### 1. Sincronización Inicial (Descarga)

Ejecuta el script de sincronización para descargar el contenido de ArcGIS a tu directorio local:

```bash
python gisbox_sync.py
```

### 2. Monitorización y Subida Automática

Una vez que el directorio local está poblado, puedes iniciar el monitor para sincronizar los cambios locales con ArcGIS:

```bash
python gisbox_monitor.py
```

Presiona `CTRL+C` para detener el monitor.

## 🗺️ Roadmap Original y Estado Actual

| Fase | Descripción | Estado |
| :--- | :--- | :--- |
| 1 | Clonación de la estructura de carpetas | ✅ **Completado** (`gisbox_sync.py`) |
| 2 | Sincronización de solo lectura (descarga) | ✅ **Completado** (`gisbox_sync.py`) |
| 3 | Sincronización completa (subida automática) | ✅ **Completado** (`gisbox_monitor.py`) |
| 4 | Publicación con menú contextual | ❌ **No Implementado** (Requiere aplicación de escritorio) |
