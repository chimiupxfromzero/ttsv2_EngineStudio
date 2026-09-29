#!/usr/bin/env python3
"""
TTS Engine Studio - XTTS v2 Voice Cloning & Synthesis
Entry point for the application.
"""

import os
import sys
import argparse
from multiprocessing import freeze_support

os.environ["COQUI_TOS_AGREED"] = "1"
os.environ["TTS_HOME"] = os.path.abspath("models")
os.environ["TRANSFORMERS_NO_TORCHCODEC"] = "1"
os.environ["TORCHCODEC_VERSION"] = "0.0.0"  # Dummy version to avoid metadata lookup

from app import run_gui


def parse_args():
    parser = argparse.ArgumentParser(
        description="TTS Engine Studio - XTTS v2 Voice Synthesis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run GUI
  python main.py

  # Headless synthesis with preset voice
  python main.py --text "Hola mundo" --language es --speaker "Luis Moray" --output output/hola.wav

  # Headless synthesis with voice cloning
  python main.py --text "Hola mundo" --language es --speaker-wav mi_voz.wav --output output/clonado.wav
        """
    )

    parser.add_argument("--text", "-t", type=str, help="Text to synthesize (headless mode)")
    parser.add_argument("--language", "-l", type=str, default="es", choices=["es", "en", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "hu", "ko", "ja", "hi"], help="Language code")
    parser.add_argument("--speaker", "-s", type=str, default="Luis Moray", help="Preset speaker name (XTTS v2 built-in)")
    parser.add_argument("--speaker-wav", "-w", type=str, help="Reference WAV file for voice cloning")
    parser.add_argument("--output", "-o", type=str, default="output/voz_generada.wav", help="Output WAV file path")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode (no GUI)")

    return parser.parse_args()


class HeadlessArgs:
    def __init__(self, text, language, speaker, speaker_wav, output):
        self.text = text
        self.language = language
        self.speaker = speaker
        self.speaker_wav = speaker_wav
        self.output = output


def main():
    freeze_support()

    args = parse_args()

    os.makedirs("output", exist_ok=True)
    os.makedirs("models", exist_ok=True)

    if args.headless or args.text:
        if not args.text:
            print("Error: --text is required in headless mode")
            sys.exit(1)

        headless_args = HeadlessArgs(
            text=args.text,
            language=args.language,
            speaker=args.speaker,
            speaker_wav=args.speaker_wav,
            output=args.output,
        )
        run_gui(headless_args=headless_args)
    else:
        run_gui()


if __name__ == "__main__":
    main()