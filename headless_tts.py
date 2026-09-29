import os
import sys
import time
import traceback

os.environ["COQUI_TOS_AGREED"] = "1"
os.environ["TTS_HOME"] = os.path.abspath("models")
os.environ["TRANSFORMERS_NO_TORCHCODEC"] = "1"
os.environ["TORCHCODEC_VERSION"] = "0.0.0"  # Dummy version to avoid metadata lookup


def run_headless_tts(text, language, speaker, speaker_wav, output_path, mode):
    try:
        from TTS.api import TTS
        import torch
    except Exception as e:
        print(f"[HEADLESS] Error: Failed to import TTS: {e}")
        return False, str(e)

    model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
    tts = None
    use_gpu = False

    try:
        if torch.cuda.is_available():
            use_gpu = True
            print("[HEADLESS] CUDA available, loading XTTS v2 on GPU...", flush=True)
            tts = TTS(model_name=model_name, gpu=True)
            if hasattr(tts, "model") and tts.model is not None:
                tts.model.half()
        else:
            print("[HEADLESS] CUDA not available, loading XTTS v2 on CPU...", flush=True)
            tts = TTS(model_name=model_name, gpu=False)
    except Exception as e:
        print(f"[HEADLESS] Error: Failed to load model: {e}\n{traceback.format_exc()}")
        return False, f"Failed to load model: {e}"

    print("[HEADLESS] Model loaded successfully", flush=True)

    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    total_paragraphs = len(paragraphs)

    if total_paragraphs == 0:
        return False, "No valid paragraphs"

    try:
        start_time = time.time()
        print(f"[HEADLESS] Starting synthesis ({total_paragraphs} paragraphs)...", flush=True)

        for idx, paragraph in enumerate(paragraphs):
            elapsed = time.time() - start_time
            progress = (idx + 1) / total_paragraphs
            avg_time = elapsed / (idx + 1) if idx >= 0 else 0
            remaining = avg_time * (total_paragraphs - idx - 1)

            print(f"[HEADLESS] Processing paragraph {idx + 1}/{total_paragraphs} (progress: {progress:.1%}, elapsed: {int(elapsed)}s, ETA: {int(remaining)}s)", flush=True)

            if idx == total_paragraphs - 1:
                try:
                    if mode == "clone" and speaker_wav and os.path.exists(speaker_wav):
                        tts.tts_to_file(
                            text=paragraph,
                            speaker_wav=speaker_wav,
                            language=language,
                            file_path=output_path,
                        )
                    else:
                        tts.tts_to_file(
                            text=paragraph,
                            speaker=speaker,
                            language=language,
                            file_path=output_path,
                        )
                except Exception as e:
                    print(f"[HEADLESS] Error: Synthesis failed: {e}\n{traceback.format_exc()}")
                    return False, f"Synthesis failed: {e}"

        total_elapsed = time.time() - start_time
        print(f"[HEADLESS] Success: Audio saved to {output_path} (elapsed: {int(total_elapsed)}s)", flush=True)
        return True, f"Audio saved to {output_path}"

    except Exception as e:
        print(f"[HEADLESS] Error: Unexpected error: {e}\n{traceback.format_exc()}")
        return False, f"Unexpected error: {e}"