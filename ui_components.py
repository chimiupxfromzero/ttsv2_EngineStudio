import customtkinter as ctk
from tkinter import filedialog
import os


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, "bbox") else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip_window = tw = ctk.CTkToplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = ctk.CTkLabel(tw, text=self.text, fg_color=("#333333", "#dddddd"), corner_radius=4, padx=8, pady=4)
        label.pack()

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class LabeledComboBox(ctk.CTkFrame):
    def __init__(self, master, label_text, values, variable, command=None, width=200, tooltip=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.variable = variable
        self.command = command

        self.label = ctk.CTkLabel(self, text=label_text, font=("Arial", 11))
        self.label.pack(side="left", padx=(0, 5))

        self.combo = ctk.CTkComboBox(
            self,
            values=values,
            variable=variable,
            width=width,
            command=self._on_change,
        )
        self.combo.pack(side="left")

        if tooltip:
            ToolTip(self.combo, tooltip)

    def _on_change(self, choice):
        if self.command:
            self.command(choice)

    def get(self):
        return self.variable.get()

    def set(self, value):
        self.variable.set(value)

    def configure_values(self, values):
        self.combo.configure(values=values)
        if values and self.variable.get() not in values:
            self.variable.set(values[0])


class FileSelector(ctk.CTkFrame):
    def __init__(self, master, label_text, filetypes, variable, command=None, width=300, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.variable = variable
        self.command = command
        self.filetypes = filetypes

        self.btn = ctk.CTkButton(self, text=label_text, width=width, command=self._select_file)
        self.btn.pack(side="left", padx=(0, 10))

        self.label = ctk.CTkLabel(self, text="Ningún archivo seleccionado", font=("Arial", 11, "italic"))
        self.label.pack(side="left")

    def _select_file(self):
        path = filedialog.askopenfilename(filetypes=self.filetypes)
        if path:
            self.variable.set(path)
            self.label.configure(text=os.path.basename(path))
            if self.command:
                self.command(path)

    def set_path(self, path):
        if path and os.path.exists(path):
            self.variable.set(path)
            self.label.configure(text=os.path.basename(path))

    def get_path(self):
        return self.variable.get()


class DirectorySelector(ctk.CTkFrame):
    def __init__(self, master, label_text, variable, command=None, width=300, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.variable = variable
        self.command = command

        self.btn = ctk.CTkButton(self, text=label_text, width=width, command=self._select_dir)
        self.btn.pack(side="left", padx=(0, 10))

        display = variable.get()
        if len(display) > 40:
            display = "..." + display[-37:]
        self.label = ctk.CTkLabel(self, text=f"Salida: {display}", font=("Arial", 11))
        self.label.pack(side="left")

    def _select_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.variable.set(path)
            display = path
            if len(display) > 40:
                display = "..." + display[-37:]
            self.label.configure(text=f"Salida: {display}")
            if self.command:
                self.command(path)

    def set_path(self, path):
        self.variable.set(path)
        display = path
        if len(display) > 40:
            display = "..." + display[-37:]
        self.label.configure(text=f"Salida: {display}")


class StatusBar(ctk.CTkFrame):
    def __init__(self, master, width=500, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.status_label = ctk.CTkLabel(self, text="Listo", font=("Arial", 11, "bold"), text_color="#3498db")
        self.status_label.pack(side="left", padx=5)

        self.progress_bar = ctk.CTkProgressBar(self, width=width, mode="determinate")
        self.progress_bar.pack(side="left", padx=5)
        self.progress_bar.set(0.0)

        self.eta_label = ctk.CTkLabel(self, text="", font=("Arial", 10), text_color=("gray40", "gray60"))
        self.eta_label.pack(side="left", padx=5)

    def set_status(self, text, progress=None, elapsed=None, eta=None):
        self.status_label.configure(text=text)
        if progress is not None:
            self.progress_bar.set(progress)
        if elapsed is not None and eta is not None:
            self.eta_label.configure(text=f"⏱ {elapsed}s | ⏳ ~{eta}s")
        elif elapsed is not None:
            self.eta_label.configure(text=f"⏱ {elapsed}s")
        else:
            self.eta_label.configure(text="")

    def reset(self):
        self.status_label.configure(text="Listo")
        self.progress_bar.set(0.0)
        self.eta_label.configure(text="")


class ModeSwitcher(ctk.CTkFrame):
    def __init__(self, master, variable, command=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.variable = variable
        self.command = command

        self.rb_preset = ctk.CTkRadioButton(
            self, text="Voces predefinidas", variable=variable, value="preset", command=self._on_change
        )
        self.rb_preset.pack(side="left", padx=10)

        self.rb_clone = ctk.CTkRadioButton(
            self, text="Clonar mi voz", variable=variable, value="clone", command=self._on_change
        )
        self.rb_clone.pack(side="left", padx=10)

    def _on_change(self):
        if self.command:
            self.command(self.variable.get())

    def get(self):
        return self.variable.get()