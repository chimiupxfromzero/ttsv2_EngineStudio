import os
import sys
import time
import traceback
from multiprocessing import Queue

os.environ["COQUI_TOS_AGREED"] = "1"
os.environ["TTS_HOME"] = os.path.abspath("models")
os.environ["TRANSFORMERS_NO_TORCHCODEC"] = "1"


def _patch_transformers():
    """Pre-import transformers modules to avoid lazy loading issues in PyInstaller."""
    import sys
    import os
    print(f"[WORKER DEBUG] sys.path: {sys.path}", flush=True)
    print(f"[WORKER DEBUG] sys._MEIPASS: {getattr(sys, '_MEIPASS', 'NOT SET')}", flush=True)
    # Fix sys.path for PyInstaller multiprocessing
    if hasattr(sys, '_MEIPASS'):
        meipass = sys._MEIPASS
        # Add the extracted bundle paths
        if meipass not in sys.path:
            sys.path.insert(0, meipass)
        # Check for common PyInstaller bundle structures
        for subdir in ['site-packages', 'lib', 'lib/python3.11/site-packages']:
            path = os.path.join(meipass, subdir)
            if os.path.exists(path) and path not in sys.path:
                sys.path.insert(0, path)
        # Also check parent directory of meipass
        parent = os.path.dirname(meipass)
        if os.path.exists(parent) and parent not in sys.path:
            sys.path.insert(0, parent)
        print(f"[WORKER DEBUG] Fixed sys.path: {sys.path}", flush=True)
    try:
        import transformers.models.gpt2.modeling_gpt2
        import transformers.models.gpt2.configuration_gpt2
        import transformers.models.auto
        print("[WORKER] Transformers modules pre-imported successfully", flush=True)
    except Exception as e:
        print(f"[WORKER] Warning: Could not pre-import transformers: {e}", flush=True)


def run_tts_worker(queue_in: Queue, queue_out: Queue) -> None:
    _patch_transformers()
    try:
        from TTS.api import TTS
        import torch
    except Exception as e:
        queue_out.put({"type": "error", "message": f"Failed to import TTS: {e}"})
        return

    model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
    tts = None
    use_gpu = False

    try:
        if torch.cuda.is_available():
            use_gpu = True
            print("[WORKER] CUDA available, loading XTTS v2 on GPU...", flush=True)
            tts = TTS(model_name=model_name, gpu=True)
            if hasattr(tts, "model") and tts.model is not None:
                tts.model.half()
        else:
            print("[WORKER] CUDA not available, loading XTTS v2 on CPU...", flush=True)
            tts = TTS(model_name=model_name, gpu=False)
    except Exception as e:
        queue_out.put({"type": "error", "message": f"Failed to load model: {e}\n{traceback.format_exc()}"})
        return

    queue_out.put({"type": "ready", "message": "Model loaded successfully"})

    while True:
        task = queue_in.get()
        if task is None or task == "STOP":
            break

        task_type = task.get("type")
        if task_type != "synthesize":
            continue

        text = task.get("text", "").strip()
        language = task.get("language", "es")
        speaker = task.get("speaker")
        speaker_wav = task.get("speaker_wav")
        output_path = task.get("output_path")
        mode = task.get("mode", "preset")

        if not text:
            queue_out.put({"type": "error", "message": "Empty text"})
            continue

        if not output_path:
            queue_out.put({"type": "error", "message": "No output path specified"})
            continue

        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        total_paragraphs = len(paragraphs)

        if total_paragraphs == 0:
            queue_out.put({"type": "error", "message": "No valid paragraphs"})
            continue

        try:
            start_time = time.time()
            queue_out.put({"type": "progress", "progress": 0.0, "message": f"Starting synthesis ({total_paragraphs} paragraphs)...", "elapsed": 0, "eta": 0})

            for idx, paragraph in enumerate(paragraphs):
                elapsed = time.time() - start_time
                progress = (idx + 1) / total_paragraphs
                avg_time = elapsed / (idx + 1) if idx >= 0 else 0
                remaining = avg_time * (total_paragraphs - idx - 1)

                queue_out.put({
                    "type": "progress",
                    "progress": progress,
                    "message": f"Processing paragraph {idx + 1}/{total_paragraphs}",
                    "elapsed": int(elapsed),
                    "eta": int(remaining),
                })

                if idx == total_paragraphs - 1:
                    try:
                        if mode == "clone" and speaker_wav and os.path.exists(speaker_wav):
                            tts.tts_to_file(
                                text=text,
                                speaker_wav=speaker_wav,
                                language=language,
                                file_path=output_path,
                            )
                        else:
                            tts.tts_to_file(
                                text=text,
                                speaker=speaker,
                                language=language,
                                file_path=output_path,
                            )
                    except Exception as e:
                        queue_out.put({"type": "error", "message": f"Synthesis failed: {e}\n{traceback.format_exc()}"})
                        break

            else:
                total_elapsed = time.time() - start_time
                queue_out.put({
                    "type": "complete",
                    "message": f"Audio saved to {output_path}",
                    "output_path": output_path,
                    "elapsed": int(total_elapsed),
                })

        except Exception as e:
            queue_out.put({"type": "error", "message": f"Unexpected error: {e}\n{traceback.format_exc()}"})

    print("[WORKER] Shutting down...", flush=True)


if __name__ == "__main__":
    from multiprocessing import Queue, Process

    q_in = Queue()
    q_out = Queue()

    p = Process(target=run_tts_worker, args=(q_in, q_out), daemon=True)
    p.start()

    while True:
        msg = q_out.get()
        print(f"[MAIN] {msg}")
        if msg.get("type") == "ready":
            break

    test_task = {
        "type": "synthesize",
        "text": "Hola, esta es una prueba de síntesis.",
        "language": "es",
        "speaker": "Luis Moray",
        "output_path": "output/test_worker.wav",
        "mode": "preset",
    }
    q_in.put(test_task)

    while True:
        msg = q_out.get()
        print(f"[MAIN] {msg}")
        if msg.get("type") in ("complete", "error"):
            break

    q_in.put("STOP")
    p.join(timeout=5)
    print("[MAIN] Worker test finished")