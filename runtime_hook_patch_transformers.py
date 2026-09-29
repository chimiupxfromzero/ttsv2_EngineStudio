# runtime_hook_patch_transformers.py
# Parchea transformers ANTES de que se importe para evitar errores de torchcodec y TorchScript
# También mockea ko_speech_tools para evitar import error (no se necesita soporte coreano)

import sys
import os

# 1. Parchear transformers ANTES de que se importe
import transformers.utils.import_utils
transformers.utils.import_utils._torchcodec_available = False
transformers.utils.import_utils.is_torchcodec_available = lambda: False
print("[RUNTIME HOOK] _torchcodec_available = False, is_torchcodec_available patched", flush=True)

# 2. Setear versión dummy en audio_utils
try:
    import transformers.utils.audio_utils
    transformers.utils.audio_utils.TORCHCODEC_VERSION = "0.0.0"
    print("[RUNTIME HOOK] TORCHCODEC_VERSION = 0.0.0", flush=True)
except Exception as e:
    print(f"[RUNTIME HOOK] Warning patching audio_utils: {e}", flush=True)

# 3. Neutralizar auto_docstring para evitar TorchScript source access
try:
    import transformers.utils.auto_docstring
    transformers.utils.auto_docstring.auto_docstring = lambda *a, **k: (lambda f: f)
    print("[RUNTIME HOOK] auto_docstring neutralized", flush=True)
except Exception as e:
    print(f"[RUNTIME HOOK] Warning patching auto_docstring: {e}", flush=True)

# 4. Parchear TTS.utils.import_utils para evitar error de torchcodec
try:
    import TTS.utils.import_utils
    TTS.utils.import_utils.TORCHCODEC_IMPORT_ERROR = ""
    TTS.utils.import_utils.TORCHCODEC_AVAILABLE = True
    TTS.utils.import_utils.PYTORCH_IMPORT_ERROR = ""
    print("[RUNTIME HOOK] TTS utils patched (torchcodec check disabled)", flush=True)
except Exception as e:
    print(f"[RUNTIME HOOK] Warning patching TTS import_utils: {e}", flush=True)

# 5. Parchear is_torchcodec_available en TTS también
try:
    import TTS
    import transformers.utils.import_utils
    TTS.is_torchcodec_available = transformers.utils.import_utils.is_torchcodec_available
    print("[RUNTIME HOOK] TTS.is_torchcodec_available patched", flush=True)
except Exception as e:
    print(f"[RUNTIME HOOK] Warning patching TTS: {e}", flush=True)

# 6. Mock ko_speech_tools ANTES de que TTS lo intente importar
class MockKoSpeechTools:
    class data:
        jamo = type('jamo', (), {})()
    hangul_romanize = lambda x: x
    g2p = type('g2p', (), {
        'utils': type('utils', (), {})(),
        'regular': type('regular', (), {})(),
        'numerals': type('numerals', (), {})(),
        'cmudict': type('cmudict', (), {})(),
        'g2p': type('g2p', (), {})(),
        'special': type('special', (), {})(),
        'english': type('english', (), {})(),
    })()
    romanize = lambda x: x

sys.modules['ko_speech_tools'] = MockKoSpeechTools()
sys.modules['ko_speech_tools.data'] = MockKoSpeechTools.data
sys.modules['ko_speech_tools.data.jamo'] = MockKoSpeechTools.data.jamo
sys.modules['ko_speech_tools.g2p'] = MockKoSpeechTools.g2p
sys.modules['ko_speech_tools.romanize'] = type('romanize', (), {})
print("[RUNTIME HOOK] ko_speech_tools mocked", flush=True)

# 7. Parchear transformers ANTES de que se importe
import transformers.utils.import_utils
transformers.utils.import_utils._torchcodec_available = False
transformers.utils.import_utils.is_torchcodec_available = lambda: False
print("[RUNTIME HOOK] _torchcodec_available = False, is_torchcodec_available patched", flush=True)

# 6. Setear versión dummy en audio_utils
try:
    import transformers.utils.audio_utils
    transformers.utils.audio_utils.TORCHCODEC_VERSION = "0.0.0"
    print("[RUNTIME HOOK] TORCHCODEC_VERSION = 0.0.0", flush=True)
except Exception as e:
    print(f"[RUNTIME HOOK] Warning patching audio_utils: {e}", flush=True)

# 7. Neutralizar auto_docstring para evitar TorchScript source access
try:
    import transformers.utils.auto_docstring
    transformers.utils.auto_docstring.auto_docstring = lambda *a, **k: (lambda f: f)
    print("[RUNTIME HOOK] auto_docstring neutralized", flush=True)
except Exception as e:
    print(f"[RUNTIME HOOK] Warning patching auto_docstring: {e}", flush=True)

# 8. Parchear TTS.utils.import_utils para evitar error de torchcodec
try:
    import TTS.utils.import_utils
    TTS.utils.import_utils.TORCHCODEC_IMPORT_ERROR = ""
    TTS.utils.import_utils.TORCHCODEC_AVAILABLE = True
    TTS.utils.import_utils.PYTORCH_IMPORT_ERROR = ""
    print("[RUNTIME HOOK] TTS utils patched (torchcodec check disabled)", flush=True)
except Exception as e:
    print(f"[RUNTIME HOOK] Warning patching TTS import_utils: {e}", flush=True)

# 9. Mock ko_speech_tools ANTES de que TTS lo intente importar
class MockKoSpeechTools:
    class data:
        jamo = type('jamo', (), {})()
    hangul_romanize = lambda x: x
    g2p = type('g2p', (), {
        'utils': type('utils', (), {})(),
        'regular': type('regular', (), {})(),
        'numerals': type('numerals', (), {})(),
        'cmudict': type('cmudict', (), {})(),
        'g2p': type('g2p', (), {})(),
        'special': type('special', (), {})(),
        'english': type('english', (), {})(),
    })()
    romanize = lambda x: x

sys.modules['ko_speech_tools'] = MockKoSpeechTools()
sys.modules['ko_speech_tools.data'] = MockKoSpeechTools.data
sys.modules['ko_speech_tools.data.jamo'] = MockKoSpeechTools.data.jamo
sys.modules['ko_speech_tools.g2p'] = MockKoSpeechTools.g2p
sys.modules['ko_speech_tools.romanize'] = type('romanize', (), {})
print("[RUNTIME HOOK] ko_speech_tools mocked", flush=True)

# 10. Parchear transformers ANTES de que se importe
import transformers.utils.import_utils
transformers.utils.import_utils._torchcodec_available = False
transformers.utils.import_utils.is_torchcodec_available = lambda: False
print("[RUNTIME HOOK] _torchcodec_available = False, is_torchcodec_available patched", flush=True)

# 11. Setear versión dummy en audio_utils
try:
    import transformers.utils.audio_utils
    transformers.utils.audio_utils.TORCHCODEC_VERSION = "0.0.0"
    print("[RUNTIME HOOK] TORCHCODEC_VERSION = 0.0.0", flush=True)
except Exception as e:
    print(f"[RUNTIME HOOK] Warning patching audio_utils: {e}", flush=True)

# 12. Neutralizar auto_docstring para evitar TorchScript source access
try:
    import transformers.utils.auto_docstring
    transformers.utils.auto_docstring.auto_docstring = lambda *a, **k: (lambda f: f)
    print("[RUNTIME HOOK] auto_docstring neutralized", flush=True)
except Exception as e:
    print(f"[RUNTIME HOOK] Warning patching auto_docstring: {e}", flush=True)

# 13. Parchear TTS.utils.import_utils para evitar error de torchcodec
try:
    import TTS.utils.import_utils
    TTS.utils.import_utils.TORCHCODEC_IMPORT_ERROR = ""
    TTS.utils.import_utils.TORCHCODEC_AVAILABLE = True
    TTS.utils.import_utils.PYTORCH_IMPORT_ERROR = ""
    print("[RUNTIME HOOK] TTS utils patched (torchcodec check disabled)", flush=True)
except Exception as e:
    print(f"[RUNTIME HOOK] Warning patching TTS import_utils: {e}", flush=True)

# 14. Mock ko_speech_tools ANTES de que TTS lo intente importar
class MockKoSpeechTools:
    class data:
        jamo = type('jamo', (), {})()
    hangul_romanize = lambda x: x
    g2p = type('g2p', (), {
        'utils': type('utils', (), {})(),
        'regular': type('regular', (), {})(),
        'numerals': type('numerals', (), {})(),
        'cmudict': type('cmudict', (), {})(),
        'g2p': type('g2p', (), {})(),
        'special': type('special', (), {})(),
        'english': type('english', (), {})(),
    })()
    romanize = lambda x: x

sys.modules['ko_speech_tools'] = MockKoSpeechTools()
sys.modules['ko_speech_tools.data'] = MockKoSpeechTools.data
sys.modules['ko_speech_tools.data.jamo'] = MockKoSpeechTools.data.jamo
sys.modules['ko_speech_tools.g2p'] = MockKoSpeechTools.g2p
sys.modules['ko_speech_tools.romanize'] = type('romanize', (), {})
print("[RUNTIME HOOK] ko_speech_tools mocked", flush=True)

# 15. Parchear transformers ANTES de que se importe
import transformers.utils.import_utils
transformers.utils.import_utils._torchcodec_available = False
transformers.utils.import_utils.is_torchcodec_available = lambda: False
print("[RUNTIME HOOK] _torchcodec_available = False, is_torchcodec_available patched", flush=True)

# 16. Setear versión dummy en audio_utils
try:
    import transformers.utils.audio_utils
    transformers.utils.audio_utils.TORCHCODEC_VERSION = "0.0.0"
    print("[RUNTIME HOOK] TORCHCODEC_VERSION = 0.0.0", flush=True)
except Exception as e:
    print(f"[RUNTIME HOOK] Warning patching audio_utils: {e}", flush=True)

# 17. Neutralizar auto_docstring para evitar TorchScript source access
try:
    import transformers.utils.auto_docstring
    transformers.utils.auto_docstring.auto_docstring = lambda *a, **k: (lambda f: f)
    print("[RUNTIME HOOK] auto_docstring neutralized", flush=True)
except Exception as e:
    print(f"[RUNTIME HOOK] Warning patching auto_docstring: {e}", flush=True)

# 18. Parchear TTS.utils.import_utils para evitar error de torchcodec
try:
    import TTS.utils.import_utils
    TTS.utils.import_utils.TORCHCODEC_IMPORT_ERROR = ""
    TTS.utils.import_utils.TORCHCODEC_AVAILABLE = True
    TTS.utils.import_utils.PYTORCH_IMPORT_ERROR = ""
    print("[RUNTIME HOOK] TTS utils patched (torchcodec check disabled)", flush=True)
except Exception as e:
    print(f"[RUNTIME HOOK] Warning patching TTS import_utils: {e}", flush=True)

# 19. Mock ko_speech_tools ANTES de que TTS lo intente importar
class MockKoSpeechTools:
    class data:
        jamo = type('jamo', (), {})()
    hangul_romanize = lambda x: x
    g2p = type('g2p', (), {
        'utils': type('utils', (), {})(),
        'regular': type('regular', (), {})(),
        'numerals': type('numerals', (), {})(),
        'cmudict': type('cmudict', (), {})(),
        'g2p': type('g2p', (), {})(),
        'special': type('special', (), {})(),
        'english': type('english', (), {})(),
    })()
    romanize = lambda x: x

sys.modules['ko_speech_tools'] = MockKoSpeechTools()
sys.modules['ko_speech_tools.data'] = MockKoSpeechTools.data
sys.modules['ko_speech_tools.data.jamo'] = MockKoSpeechTools.data.jamo
sys.modules['ko_speech_tools.g2p'] = MockKoSpeechTools.g2p
sys.modules['ko_speech_tools.romanize'] = type('romanize', (), {})
print("[RUNTIME HOOK] ko_speech_tools mocked", flush=True)

# 20. Desactivar typeguard completamente
os.environ['TYPEGUARD_DISABLE'] = '1'

# Mock typeguard ANTES de que inflect lo importe
class MockTypeguard:
    def __getattr__(self, name):
        return lambda *args, **kwargs: (lambda f: f)

sys.modules['typeguard'] = MockTypeguard()
sys.modules['typeguard._decorators'] = MockTypeguard()
sys.modules['typeguard._config'] = MockTypeguard()
print("[RUNTIME HOOK] typeguard mocked", flush=True)

# 21. Parchear inflect para evitar typeguard
try:
    import inflect
    class MockEngine:
        def __init__(self):
            pass
        def __getattr__(self, name):
            return lambda *a, **k: ""
    
    inflect.engine = lambda: MockEngine()
    print("[RUNTIME HOOK] inflect engine mocked", flush=True)
except Exception as e:
    print(f"[RUNTIME HOOK] Warning patching inflect: {e}", flush=True)

# 22. Desactivar typeguard completamente
os.environ['TYPEGUARD_DISABLE'] = '1'

# Mock typeguard ANTES de que inflect lo importe
class MockTypeguard:
    def __getattr__(self, name):
        return lambda *args, **kwargs: (lambda f: f)

sys.modules['typeguard'] = MockTypeguard()
sys.modules['typeguard._decorators'] = MockTypeguard()
sys.modules['typeguard._config'] = MockTypeguard()
print("[RUNTIME HOOK] typeguard mocked", flush=True)

# 23. Parchear inflect para evitar typeguard
try:
    import inflect
    class MockEngine:
        def __init__(self):
            pass
        def __getattr__(self, name):
            return lambda *a, **k: ""
    
    inflect.engine = lambda: MockEngine()
    print("[RUNTIME HOOK] inflect engine mocked", flush=True)
except Exception as e:
    print(f"[RUNTIME HOOK] Warning patching inflect: {e}", flush=True)

# 24. Desactivar typeguard completamente
os.environ['TYPEGUARD_DISABLE'] = '1'

# 25. Asegurar que TTS source esté en sys.path para TorchScript
if hasattr(sys, '_MEIPASS'):
    meipass = sys._MEIPASS
    tts_path = os.path.join(meipass, 'TTS')
    if os.path.exists(tts_path) and tts_path not in sys.path:
        sys.path.insert(0, tts_path)
        print(f"[RUNTIME HOOK] Added TTS to sys.path: {tts_path}", flush=True)
    else:
        print(f"[RUNTIME HOOK] TTS not found at: {tts_path}", flush=True)
        for root, dirs, files in os.walk(meipass):
            if 'TTS' in dirs:
                found = os.path.join(root, 'TTS')
                if found not in sys.path:
                    sys.path.insert(0, found)
                    print(f"[RUNTIME HOOK] Found TTS at: {found}", flush=True)
                break

print("[RUNTIME HOOK] All patches applied successfully", flush=True)