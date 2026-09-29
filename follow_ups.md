# Follow-up: TTS Engine Studio - Próximos Pasos

## Estado Actual
- ✅ App funciona en modo headless (generación y clonación de voz) - **SOLO en entorno desarrollo (uv run)**
- ✅ Linux executable se genera (~2.7GB) pero **falla al ejecutarse** (errores de importación en runtime)
- ✅ Modelos XTTS v2, YourTTS, VITS ya descargados en `models/`
- ✅ PyInstaller config base funcionando (unittest removido, UPX desactivado, paths corregidos)
- ✅ Conflicto de nombres resuelto: `config.py` → `app_config.py`

## Problemas del Ejecutable (Pendientes)

### 1. `unittest` excluido pero requerido - **RESUELTO**
- **Causa**: `--exclude-module=unittest` en `pyproject.toml` y `.spec`
- **Fix aplicado**: Quitado `unittest` de `exclude-modules` + regenerado

### 2. Error C++ `GradBucket` duplicado (PyTorch) - **RESUELTO**
- **Causa**: PyInstaller incluye 2 copias de libtorch
- **Fix aplicado**: Desactivado UPX (`upx=False` en spec/pyproject.toml)

### 3. Imports dinámicos no detectados por PyInstaller - **BLOQUEANTE ACTUAL**
- **Causa raíz**: `transformers`/`TTS` usan checks en import-time que PyInstaller ejecuta durante fase de **análisis (build time)**, no solo runtime:
  - `transformers.utils.import_utils.is_torchcodec_available()` se evalúa al importar `TTS`
  - `TTS/__init__.py` línea 30-35: llama a `is_torchcodec_available()` y lanza `ImportError` si falla
  - `transformers.utils.import_utils._torchcodec_available` usa `importlib.util.find_spec("torchcodec")`
  - `typeguard`/`inflect` → `inspect.getsource()` falla en frozen executable (TorchScript)
  - Conflicto de nombres: `config.py` local vs `TTS.config` (resuelto renombrando a `app_config.py`)
- **Síntoma**: Ejecutable compila OK, pero falla en runtime: `ImportError: torchcodec library is required...`
- **Error fundamental**: PyInstaller ejecuta imports durante fase de **análisis (build time)**. El runtime hook se ejecuta **después** - demasiado tarde.

### 4. `ko_speech_tools` (coreano) - **EXCLUIDO**
- Usuario confirmó: **NO se necesita soporte coreano**
- Mockeado en runtime hook

---

## Historial de Intentos Fallidos

| Intento | Enfoque | Por qué falló |
|---------|---------|---------------|
| 1 | Hidden imports manuales | Parcial - siempre aparece uno nuevo |
| 2 | `hooksconfig collect_all: True` | No resuelve imports dinámicos en build time |
| 3 | Runtime hook pre-import | Se ejecuta **después** del análisis - tarde |
| 4 | Mock `torchcodec` en `sys.modules` | `find_spec` no ve mocks en `sys.modules` |
| 5 | Mock `importlib.metadata.version` | No afecta a `find_spec` |
| 6 | Incluir source TTS completo | Resuelve TorchScript pero no check torchcodec |
| 7 | Variable `TRANSFORMERS_NO_TORCHCODEC=1` | Se ignora en código de `transformers` |
| 8 | `is_torchcodec_available = lambda: False` en runtime hook | Se ejecuta **después** del análisis de PyInstaller |

---

## Plan de Acción para Próxima Sesión

### Opción A: Incluir torchcodec correctamente (Recomendado - más limpio)
1. **Agregar torchcodec como dependency real**:
   - `hiddenimports`: `'torchcodec', 'torchcodec.decoders'`
   - `datas`: incluir `torchcodec-*.dist-info` metadata
   - `hookspath`: custom hook para torchcodec si necesario
   - Verificar que `importlib.util.find_spec("torchcodec")` retorne válido en build time

2. **Eliminar runtime hooks complejos** - ya no necesarios si torchcodec está incluido

### Opción B: Wrapper script (Alternativa robusta)
1. **Crear `entry_point.py`** que:
   - Parchee todo ANTES de importar TTS
   - Luego `import TTS` y ejecute la app
   - Configurar `entry_point.py` como script principal en `.spec`

### Opción C: Hook personalizado de PyInstaller (Más técnico)
1. **Crear hook `hook-torchcodec.py`** en `hookspath` que:
   - Fuerza `_torchcodec_available = True` durante análisis
   - Proporciona metadata falsa si necesario

---

## Recomendación: **Opción A** (incluir torchcodec)

**Razones:**
- Es la solución "correcta" - torchcodec es dependency real de transformers 4.57+
- Elimina necesidad de parches frágiles
- Simplifica el build (menos hooks, menos runtime hooks)
- torchcodec ya está instalado en el venv (`0.16.0+cpu`)

---

## Próximos Pasos Inmediatos (Siguiente Sesión)

1. **Agregar torchcodec al build**:
   ```python
   # En .spec:
   hiddenimports += ['torchcodec', 'torchcodec.decoders']
   datas += [('/home/guillermo/Documentos/vozcoqui/.venv/lib/python3.11/site-packages/torchcodec-0.16.0+cpu.dist-info', 'torchcodec-0.16.0+cpu.dist-info')]
   ```

2. **Simplificar runtime hook** - solo lo esencial (typeguard, ko_speech_tools, inflect)

3. **Test build y ejecución**

4. **Si falla**: investigar hook específico para torchcodec

---

## Mejoras Pendientes (Post-fix)
- [] Loading splash al arrancar (modelos tardan ~30s en cargar)
- [] Progress bar real durante síntesis (no indeterminate)
- [] Evitar congelación UI en textos largos (ya usa multiprocessing)
- [] Instalador Windows (.exe) via GitHub Actions o VM
- [] Estructurar funcionalidad del menú superior
- [] Añadir configuración inicial al arrancar por primera vez (skippeable)
- [] Añadir vista previa del audio generado (Play)
- [*] Limpiar código legacy (archivos antiguos en /bin)
- [] Añadir en el menú Acerca de (brief de la app y desarrolladores)

---

## Contexto Técnico Clave

**Archivos modificados en esta sesión:**
- `bin/TTS_Engine_Studio.spec` - config principal PyInstaller
- `runtime_hook_patch_transformers.py` - runtime hook (muy agresivo, parchea todo)
- `config.py` → `app_config.py` - renombrado para evitar conflicto con `TTS.config`
- `app.py` - import actualizado a `app_config`

**Error actual:** `ImportError: From Pytorch 2.9, the torchcodec library is required...` - se lanza desde `TTS/__init__.py:35` durante análisis de PyInstaller.

**Ventana de contexto:** ~61% usado - suficiente para implementar fix en próxima sesión.