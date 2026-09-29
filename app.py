import os
import sys
import time
import threading
import traceback
from multiprocessing import Queue, Process, freeze_support
from pathlib import Path

import customtkinter as ctk
from tkinter import messagebox, filedialog

from app_config import load_config, save_config, get_output_dir
from speakers import (
    get_speakers_for_accent,
    get_accents_for_language,
    get_accent_display_name,
    DEFAULT_SPEAKER,
    DEFAULT_ACCENT,
    DEFAULT_LANGUAGE,
)
from ui_components import (
    LabeledComboBox,
    FileSelector,
    DirectorySelector,
    StatusBar,
    ModeSwitcher,
    ToolTip,
)
from tts_worker import run_tts_worker
from headless_tts import run_headless_tts


class TTSApp:
    def __init__(self, headless_args=None):
        self.config = load_config()
        self.headless_args = headless_args

        ctk.set_appearance_mode(self.config.get("theme", "System"))
        ctk.set_default_color_theme("blue")

        self.ventana = ctk.CTk()
        self.ventana.title("TTS Engine Studio - XTTS v2")
        geometry = self.config.get("window_geometry", "850x750")
        self.ventana.geometry(geometry)
        self.ventana.minsize(750, 650)

        self.ventana.grid_columnconfigure(0, weight=1)
        self.ventana.grid_rowconfigure(1, weight=1)

        self.queue_in = Queue()
        self.queue_out = Queue()
        self.worker_process = None
        self.worker_ready = False
        self.is_processing = False
        self.headless_args = headless_args
        self.headless_complete = False
        self.headless_success = False
        self.headless_error = None

        self._setup_variables()
        self._create_menu_bar()
        self._create_main_layout()
        self._bind_events()

        if headless_args:
            self._run_headless(headless_args)
        else:
            self._start_worker()
            self._check_queue()

    def _setup_variables(self):
        self.lang_var = ctk.StringVar(value=self.config.get("language", DEFAULT_LANGUAGE))
        self.accent_var = ctk.StringVar(value=self.config.get("accent", DEFAULT_ACCENT))
        self.mode_var = ctk.StringVar(value=self.config.get("mode", "preset"))
        self.speaker_var = ctk.StringVar(value=self.config.get("speaker", DEFAULT_SPEAKER))
        self.output_dir_var = ctk.StringVar(value=self.config.get("output_dir", str(Path.cwd() / "output")))
        self.filename_var = ctk.StringVar(value="voz_generada.wav")
        self.reference_audio_var = ctk.StringVar(value=self.config.get("reference_audio", ""))

    def _create_menu_bar(self):
        menu_bar = ctk.CTkFrame(self.ventana, height=35, corner_radius=0)
        menu_bar.grid(row=0, column=0, sticky="ew")
        menu_bar.grid_columnconfigure(4, weight=1)

        btn_file = ctk.CTkButton(menu_bar, text="Archivo", width=70, height=25, fg_color="transparent", text_color=("black", "white"), command=self._menu_file)
        btn_file.grid(row=0, column=0, padx=5, pady=5)

        btn_view = ctk.CTkButton(menu_bar, text="Ver (Tema)", width=90, height=25, fg_color="transparent", text_color=("black", "white"), command=self._toggle_theme)
        btn_view.grid(row=0, column=1, padx=5, pady=5)

        btn_tools = ctk.CTkButton(menu_bar, text="Herramientas", width=90, height=25, fg_color="transparent", text_color=("black", "white"), command=self._menu_tools)
        btn_tools.grid(row=0, column=2, padx=5, pady=5)

        btn_help = ctk.CTkButton(menu_bar, text="Ayuda", width=70, height=25, fg_color="transparent", text_color=("black", "white"), command=self._show_help)
        btn_help.grid(row=0, column=3, padx=5, pady=5)

    def _create_main_layout(self):
        main_frame = ctk.CTkFrame(self.ventana, fg_color="transparent")
        main_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)

        row = 0
        ctk.CTkLabel(main_frame, text="Texto a procesar:", font=("Arial", 12, "bold")).grid(row=row, column=0, sticky="w", pady=(5, 2))
        row += 1

        self.text_input = ctk.CTkTextbox(main_frame, height=180, width=750, activate_scrollbars=True, fg_color=("#f0f0f0", "#2b2b2b"), text_color=("black", "white"))
        self.text_input.grid(row=row, column=0, sticky="ew", pady=5)
        self.text_input.insert("1.0", "Hola, bienvenido a TTS Engine Studio.\nEsta aplicación clona voces usando XTTS v2.")
        row += 1

        lang_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        lang_frame.grid(row=row, column=0, sticky="w", pady=10)
        row += 1

        ctk.CTkLabel(lang_frame, text="Idioma:").pack(side="left", padx=5)
        self.lang_combo = ctk.CTkComboBox(lang_frame, values=["es", "en"], variable=self.lang_var, width=80, command=self._on_language_change)
        self.lang_combo.pack(side="left", padx=5)

        ctk.CTkLabel(lang_frame, text="Acento:").pack(side="left", padx=5)
        initial_accents = get_accents_for_language(self.lang_var.get())
        accent_values = [get_accent_display_name(a) for a in initial_accents]
        self.accent_var_display = ctk.StringVar(value=get_accent_display_name(self.accent_var.get()))
        self.accent_combo = ctk.CTkComboBox(lang_frame, values=accent_values, variable=self.accent_var_display, width=180, command=self._on_accent_change)
        self.accent_combo.pack(side="left", padx=5)

        ctk.CTkLabel(lang_frame, text="Modo:").pack(side="left", padx=(20, 5))
        self.mode_switch = ModeSwitcher(lang_frame, self.mode_var, command=self._on_mode_change)
        self.mode_switch.pack(side="left", padx=5)
        row += 1

        self.speaker_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.speaker_frame.grid(row=row, column=0, sticky="w", pady=5)
        row += 1

        ctk.CTkLabel(self.speaker_frame, text="Voz (Speaker):").pack(side="left", padx=5)
        initial_speakers = get_speakers_for_accent(self.accent_var.get())
        self.speaker_combo = ctk.CTkComboBox(self.speaker_frame, values=initial_speakers, variable=self.speaker_var, width=250)
        self.speaker_combo.pack(side="left", padx=5)
        row += 1

        self.ref_audio_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.ref_audio_frame.grid(row=row, column=0, sticky="ew", pady=5)
        row += 1

        self.ref_audio_selector = FileSelector(
            self.ref_audio_frame,
            "Seleccionar Voz de Referencia (.wav)",
            [("Archivos WAV", "*.wav")],
            self.reference_audio_var,
            width=250,
        )
        self.ref_audio_selector.pack(side="left", padx=5)
        ToolTip(self.ref_audio_selector.btn, "Archivo WAV de 5-10 segundos para clonar tu voz")

        out_frame = ctk.CTkFrame(main_frame)
        out_frame.grid(row=row, column=0, sticky="ew", pady=10)
        out_frame.grid_columnconfigure(0, weight=1)
        row += 1

        self.dir_selector = DirectorySelector(out_frame, "Cambiar Ruta", self.output_dir_var, command=self._on_output_dir_change)
        self.dir_selector.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        row += 1

        ctk.CTkLabel(main_frame, text="Nombre del archivo final:").grid(row=row, column=0, sticky="w", padx=5)
        row += 1
        ctk.CTkEntry(main_frame, textvariable=self.filename_var, width=300).grid(row=row, column=0, sticky="w", padx=5, pady=2)
        row += 1

        self.status_bar = StatusBar(main_frame, width=550)
        self.status_bar.grid(row=row, column=0, pady=(15, 5), sticky="ew")
        row += 1

        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.grid(row=row, column=0, pady=20)
        row += 1

        self.btn_generate = ctk.CTkButton(
            btn_frame,
            text="Generar y Guardar",
            width=250,
            height=45,
            font=("Arial", 14, "bold"),
            command=self._on_generate_click,
        )
        self.btn_generate.pack()

        self._update_mode_ui()

        if self.reference_audio_var.get() and os.path.exists(self.reference_audio_var.get()):
            self.ref_audio_selector.set_path(self.reference_audio_var.get())

    def _bind_events(self):
        self.ventana.protocol("WM_DELETE_WINDOW", self._on_close)

    def _start_worker(self):
        self.worker_process = Process(target=run_tts_worker, args=(self.queue_in, self.queue_out), daemon=True)
        self.worker_process.start()

    def _check_queue(self):
        try:
            while True:
                msg = self.queue_out.get_nowait()
                self._handle_worker_message(msg)
        except Exception:
            pass

        if self.worker_process and self.worker_process.is_alive():
            self.ventana.after(100, self._check_queue)

    def _handle_worker_message(self, msg):
        msg_type = msg.get("type")

        if msg_type == "ready":
            self.worker_ready = True
            if not self.headless_args:
                self.status_bar.set_status("Modelo XTTS v2 cargado ✓")

        elif msg_type == "progress":
            if not self.headless_args:
                self.status_bar.set_status(
                    msg.get("message", ""),
                    progress=msg.get("progress", 0),
                    elapsed=msg.get("elapsed"),
                    eta=msg.get("eta"),
                )

        elif msg_type == "complete":
            self.is_processing = False
            if not self.headless_args:
                self.btn_generate.configure(state="normal", text="Generar y Guardar")
                self.status_bar.set_status("¡Completado con éxito!", progress=1.0, elapsed=msg.get("elapsed", 0))
                messagebox.showinfo("Éxito", msg.get("message", "Audio generado correctamente"))

        elif msg_type == "error":
            self.is_processing = False
            if not self.headless_args:
                self.btn_generate.configure(state="normal", text="Generar y Guardar")
                self.status_bar.set_status("Error", progress=0)
                messagebox.showerror("Error", msg.get("message", "Error desconocido"))

    def _on_language_change(self, choice):
        self.lang_var.set(choice)
        accents = get_accents_for_language(choice)
        accent_values = [get_accent_display_name(a) for a in accents]
        self.accent_combo.configure(values=accent_values)
        if accents:
            self.accent_var.set(accents[0])
            self.accent_var_display.set(get_accent_display_name(accents[0]))
            self._on_accent_change(get_accent_display_name(accents[0]))
        self._save_config()

    def _on_accent_change(self, choice):
        for code, name in [
            ("es-MX", "Español - México 🇲🇽"),
            ("es-CO", "Español - Colombia 🇨🇴"),
            ("es-VE", "Español - Venezuela 🇻🇪"),
            ("es-AR", "Español - Argentina 🇦🇷"),
            ("es-ES", "Español - España 🇪🇸"),
            ("en-US", "English - US 🇺🇸"),
            ("en-GB", "English - UK 🇬🇧"),
        ]:
            if name == choice:
                self.accent_var.set(code)
                break
        speakers = get_speakers_for_accent(self.accent_var.get())
        self.speaker_combo.configure(values=speakers)
        if speakers and self.speaker_var.get() not in speakers:
            self.speaker_var.set(speakers[0])
        self._save_config()

    def _on_mode_change(self, mode):
        self._update_mode_ui()
        self._save_config()

    def _update_mode_ui(self):
        mode = self.mode_var.get()
        if mode == "preset":
            self.speaker_frame.grid()
            self.ref_audio_frame.grid_remove()
        else:
            self.speaker_frame.grid_remove()
            self.ref_audio_frame.grid()

    def _on_output_dir_change(self, path):
        self._save_config()

    def _on_generate_click(self):
        if self.is_processing:
            return

        if not self.worker_ready:
            messagebox.showwarning("Espera", "El modelo aún se está cargando...")
            return

        text = self.text_input.get("1.0", "end").strip()
        if not text:
            messagebox.showerror("Error", "Ingresa un texto para sintetizar")
            return

        mode = self.mode_var.get()
        if mode == "clone":
            ref_path = self.reference_audio_var.get()
            if not ref_path or not os.path.exists(ref_path):
                messagebox.showerror("Error", "Selecciona un archivo .wav de referencia para clonar")
                return

        filename = self.filename_var.get().strip()
        if not filename.endswith(".wav"):
            filename += ".wav"

        output_dir = get_output_dir(self.config)
        output_path = os.path.join(output_dir, filename)

        self.is_processing = True
        self.btn_generate.configure(state="disabled", text="Generando...")
        self.status_bar.reset()

        task = {
            "type": "synthesize",
            "text": text,
            "language": self.lang_var.get(),
            "speaker": self.speaker_var.get() if mode == "preset" else None,
            "speaker_wav": self.reference_audio_var.get() if mode == "clone" else None,
            "output_path": output_path,
            "mode": mode,
        }
        self.queue_in.put(task)

    def _menu_file(self):
        new_dir = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if new_dir:
            self.output_dir_var.set(new_dir)
            self.dir_selector.set_path(new_dir)
            self._save_config()

    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        new_theme = "Light" if current == "Dark" else "Dark"
        ctk.set_appearance_mode(new_theme)
        self.config["theme"] = new_theme
        self._save_config()

    def _menu_tools(self):
        self._show_hardware_info()

    def _show_hardware_info(self):
        import psutil
        try:
            import torch
            cuda_ok = torch.cuda.is_available()
            gpu_name = torch.cuda.get_device_name(0) if cuda_ok else "No detectada"
        except Exception:
            cuda_ok = False
            gpu_name = "No detectada"

        ram_gb = round(psutil.virtual_memory().total / (1024**3))

        report = f"--- REPORTE DE HARDWARE ---\n\n"
        report += f"• Memoria RAM: {ram_gb} GB\n"
        report += f"• GPU Nvidia (CUDA): {'SÍ' if cuda_ok else 'NO'} ({gpu_name})\n\n"

        if cuda_ok and ram_gb >= 16:
            report += "Recomendación: ¡Excelente! Puedes correr XTTS v2 en GPU volando."
        elif ram_gb >= 16:
            report += "Recomendación: Tienes buena RAM. XTTS v2 en CPU funcionará bien dividiendo párrafos."
        else:
            report += "Recomendación: Recursos limitados. Considera modelos más ligeros."

        messagebox.showinfo("Escaneo de Hardware", report)

    def _show_help(self):
        faq = "--- PREGUNTAS FRECUENTES (FAQ) ---\n\n"
        faq += "¿Por qué tarda en textos largos?\n"
        faq += "XTTS v2 analiza el contexto completo. La app segmenta por párrafos para evitar saturar la CPU.\n\n"
        faq += "¿Cómo usar mi propia voz?\n"
        faq += "Selecciona 'Clonar mi voz', elige un archivo .wav de 5-10 segundos y genera.\n\n"
        faq += "¿Qué son las voces predefinidas?\n"
        faq += "Son 80+ speakers integrados en XTTS v2, organizados por acento (México, Colombia, Venezuela, Argentina, España, US, UK).\n\n"
        faq += "¿Puedo usar GPU?\n"
        faq += "Sí, si tienes GPU Nvidia con CUDA, la app la detecta y usa automáticamente.\n\n"
        faq += "¿Dónde se guardan los audios?\n"
        faq += "En la carpeta 'output' del proyecto (configurable en Archivo > Cambiar ruta)."

        messagebox.showinfo("Ayuda & FAQ", faq)

    def _save_config(self):
        self.config.update({
            "theme": ctk.get_appearance_mode(),
            "output_dir": self.output_dir_var.get(),
            "language": self.lang_var.get(),
            "accent": self.accent_var.get(),
            "mode": self.mode_var.get(),
            "speaker": self.speaker_var.get(),
            "reference_audio": self.reference_audio_var.get(),
            "window_geometry": self.ventana.geometry(),
        })
        save_config(self.config)

    def _on_close(self):
        self._save_config()
        if self.worker_process and self.worker_process.is_alive():
            self.queue_in.put("STOP")
            self.worker_process.join(timeout=3)
        self.ventana.destroy()

    def _run_headless(self, args):
        text = args.text
        language = args.language
        speaker = args.speaker
        speaker_wav = args.speaker_wav
        output_path = args.output
        mode = "clone" if speaker_wav else "preset"

        if not text:
            print("Error: No text provided")
            self.ventana.after(100, self.ventana.destroy)
            return

        if mode == "clone" and (not speaker_wav or not os.path.exists(speaker_wav)):
            print("Error: Reference audio required for clone mode")
            self.ventana.after(100, self.ventana.destroy)
            return

        self.headless_complete = False
        self.headless_success = False
        self.headless_error = None

        def run_synthesis():
            success, message = run_headless_tts(text, language, speaker, speaker_wav, output_path, mode)
            self.headless_complete = True
            self.headless_success = success
            self.headless_error = message if not success else None
            if success:
                print(f"[HEADLESS] Success: {message}")
            else:
                print(f"[HEADLESS] Error: {message}")

        # Run synthesis in a thread to not block the simple loop
        thread = threading.Thread(target=run_synthesis, daemon=True)
        thread.start()

        # Use a simple loop instead of mainloop for headless
        while not self.headless_complete:
            try:
                time.sleep(0.1)
            except Exception:
                pass

        # Clean up
        self.ventana.destroy()
        sys.exit(0 if self.headless_success else 1)

    def run(self):
        self.ventana.mainloop()


def run_gui(headless_args=None):
    app = TTSApp(headless_args=headless_args)
    app.run()