⚠️ **NOTA IMPORTANTE: ESTE PROYECTO AÚN ESTÁ EN CONSTRUCCIÓN / WORK IN PROGRESS** ⚠️

---

# TTS Engine Studio - XTTS v2 Voice Cloning & Synthesis

Aplicación de escritorio (GUI) para clonar voces y generar archivos de audio usando **XTTS v2** (Coqui TTS v2). Permite síntesis de voz con voces predefinidas (80+ speakers por acento) o clonación de voz propia mediante archivo de referencia WAV.

## 🎯 Descripción General

TTS Engine Studio es una interfaz gráfica de escritorio construida con **CustomTkinter** que aprovecha **Coqui TTS (XTTS v2)** para:
- **Síntesis con voces predefinidas**: 80+ speakers organizados por idioma y acento (Español: México, Colombia, Venezuela, Argentina, España; Inglés: US, UK, etc.)
- **Clonación de voz**: Usa un archivo WAV de referencia (5-10 segundos) para clonar cualquier voz
- **Modo headless**: Generación por línea de comandos para automatización
- **Multiprocesamiento**: El modelo corre en proceso separado para no congelar la UI

## 🏗️ Estado del Proyecto

| Componente | Estado | Completado |
|------------|--------|------------|
| GUI Principal (CustomTkinter) | ✅ Funcional | 95% |
| Integración XTTS v2 / Coqui TTS | ✅ Funcional (solo dev) | 90% |
| Clonación de voz (speaker_wav) | ✅ Funcional | 90% |
| Voces predefinidas por acento | ✅ Funcional | 100% |
| Modo Headless (CLI) | ✅ Funcional | 95% |
| Configuración persistente (JSON) | ✅ Funcional | 100% |
| Menú superior (Archivo, Ver, Herramientas, Ayuda) | 🟡 Parcial | 40% |
| **Ejecutable standalone (PyInstaller)** | ❌ **BLOQUEADO** | **15%** |
| Splash screen / Loading inicial | ❌ Pendiente | 0% |
| Progress bar real durante síntesis | ❌ Pendiente | 0% |
| Vista previa de audio (Play) | ❌ Pendiente | 0% |
| Instalador Windows (.exe) | ❌ Pendiente | 0% |
| Configuración inicial (first-run) | ❌ Pendiente | 0% |
| Limpieza código legacy (/bin) | 🟡 En progreso | 60% |

**Completado global estimado: ~65% (solo entorno desarrollo)**
**Ejecutable distribuible: ~15% (bloqueado por torchcodec)**

---

## 🚧 Problema Crítico Actual: Ejecutable No Funciona

El proyecto **funciona perfectamente en modo desarrollo** (`uv run main.py` o `python main.py`), pero **fallan al generar ejecutable standalone** con PyInstaller.

### Causa Raíz
`transformers` ≥4.57 requiere `torchcodec` en import-time. PyInstaller ejecuta imports durante la **fase de análisis (build time)**, no solo runtime. El check `is_torchcodec_available()` falla porque `torchcodec` no se incluye en el bundle.

### Error Actual
```
ImportError: From Pytorch 2.9, the torchcodec library is required to load audio files...
```
Lanzado desde `TTS/__init__.py:35` durante **análisis de PyInstaller**.

### Plan de Fix (Próxima Sesión)
Ver `follow_ups.md` - **Opción A recomendada**: Incluir `torchcodec` como dependency real en el build (hiddenimports + datas + metadata).

---

## 📋 Próximos Pasos Inmediatos

| Prioridad | Tarea | Detalle |
|-----------|-------|---------|
| 🔴 **Crítica** | Fix ejecutable (torchcodec) | Agregar `torchcodec` a hiddenimports/datas en `.spec`; simplificar runtime hook |
| 🟡 Alta | Splash screen | Modelo tarda ~30s en cargar; UX necesita feedback visual |
| 🟡 Alta | Progress bar real | Actualmente indeterminate; worker ya envía progreso real |
| 🟢 Media | Menú superior completo | Estructurar funcionalidad: Archivo, Ver, Herramientas, Ayuda |
| 🟢 Media | First-run config | Wizard configurable al arrancar por primera vez (skippeable) |
| 🟢 Media | Vista previa audio | Botón "Play" para escuchar antes de guardar |
| 🔵 Baja | Instalador Windows | Via GitHub Actions o VM Windows |
| 🔵 Baja | About dialog | Brief de la app y créditos |
| 🔵 Baja | Limpieza legacy | Archivos antiguos en `/bin` |

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología |
|------|------------|
| GUI | CustomTkinter (tkinter moderno) |
| TTS Engine | Coqui TTS / XTTS v2 |
| Deep Learning | PyTorch, transformers, torchcodec |
| Audio | torchaudio, scipy |
| Packaging | PyInstaller (spec personalizado) |
| Config | JSON local (`config.json`) |
| Multiprocesing | `multiprocessing.Process` + `Queue` |
| Hardware detection | `psutil`, `torch.cuda` |

---

## 📁 Estructura del Proyecto

```
ttsv2enginestudiocopy/
├── main.py                      # Entry point (CLI + GUI)
├── app.py                       # GUI principal (TTSApp class)
├── app_config.py                # Configuración JSON (load/save)
├── speakers.py                  # Speakers/acentos XTTS v2
├── ui_components.py             # Componentes UI reutilizables
├── tts_worker.py                # Worker process (carga modelo + síntesis)
├── headless_tts.py              # Lógica síntesis sin GUI
├── runtime_hook_patch_transformers.py  # Runtime hook PyInstaller (parches)
├── TtsV2_EngineStudio.spec      # Config PyInstaller principal
├── pyproject.toml               # Config build (uv/pip)
├── config.json                  # Config usuario (se genera en runtime)
├── models/                      # Modelos XTTS v2, YourTTS, VITS (gitignored)
├── output/                      # Audios generados (gitignored)
└── follow_ups.md                # Bitácora técnica detallada
```

---

## 🚀 Uso Rápido (Solo Entorno Desarrollo)

```bash
# Requisitos: Python 3.11+, uv (recomendado) o pip
# Modelos ya descargados en models/

# GUI interactiva
uv run main.py
# o: python main.py

# Headless - voz predefinida
uv run main.py --text "Hola mundo" --language es --speaker "Luis Moray" --output output/hola.wav

# Headless - clonación de voz
uv run main.py --text "Hola mundo" --language es --speaker-wav mi_voz.wav --output output/clonado.wav
```

---

## 📖 Documentación Técnica Detallada

Ver **`follow_ups.md`** para:
- Historial completo de intentos fallidos (8+ intentos)
- Análisis técnico profundo del problema torchcodec
- Plan de acción detallado para próxima sesión
- Contexto de archivos modificados
- Ventana de contexto disponible (~61%)

---

## 📄 Licencia

Proyecto privado / uso personal. Basado en Coqui TTS (MPL-2.0 / Apache-2.0).
