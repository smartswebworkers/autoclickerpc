import time
import threading
import pyautogui
import keyboard
import customtkinter as ctk
from tkinter import messagebox

# ----------   Logique de clic   ---------- #
clicking = False
stop_event = threading.Event()

def click_worker(interval, repeat, use_current, x, y):
    global clicking
    counter = 0
    while not stop_event.is_set():
        if clicking:
            if use_current:
                pyautogui.click()
            else:
                pyautogui.click(x, y)
            counter += 1
            if repeat != 0 and counter >= repeat:
                toggle_clicking()          # Arrêt auto
                break
        time.sleep(interval)

# ----------   UI   ---------- #
class AutoClickerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Fenêtre
        ctk.set_appearance_mode("System")       # Dark/Light auto
        ctk.set_default_color_theme("green")
        self.title("Auto Clicker Avancé")
        self.resizable(False, False)

        # Variables
        self.interval_var  = ctk.StringVar(value="1")
        self.repeat_var    = ctk.StringVar(value="0")
        self.use_current   = ctk.BooleanVar(value=True)
        self.x_var         = ctk.StringVar(value="")
        self.y_var         = ctk.StringVar(value="")

        # Widgets
        self.build_widgets()

        # Thread clic
        self.click_thread = None

        # Hotkey global F8
        keyboard.add_hotkey('F8', toggle_clicking)

    def build_widgets(self):
        pad = {"padx": 10, "pady": 5}

        # Intervalle
        ctk.CTkLabel(self, text="Intervalle (s)").grid(row=0, column=0, **pad)
        ctk.CTkEntry(self, textvariable=self.interval_var, width=80)\
             .grid(row=0, column=1, **pad)

        # Répétitions
        ctk.CTkLabel(self, text="Répéter (0 = infini)")\
             .grid(row=1, column=0, **pad)
        ctk.CTkEntry(self, textvariable=self.repeat_var, width=80)\
             .grid(row=1, column=1, **pad)

        # Position
        ctk.CTkCheckBox(self, text="Utiliser position actuelle",
                        variable=self.use_current, onvalue=True, offvalue=False)\
            .grid(row=2, column=0, columnspan=2, sticky="w", **pad)

        pos_frame = ctk.CTkFrame(self)
        pos_frame.grid(row=3, column=0, columnspan=2, **pad)
        ctk.CTkLabel(pos_frame, text="X").pack(side="left")
        ctk.CTkEntry(pos_frame, textvariable=self.x_var, width=60).pack(side="left", padx=4)
        ctk.CTkLabel(pos_frame, text="Y").pack(side="left")
        ctk.CTkEntry(pos_frame, textvariable=self.y_var, width=60).pack(side="left", padx=4)
        ctk.CTkButton(self, text="📍 Capturer position", command=self.capture_position)\
            .grid(row=4, column=0, columnspan=2, **pad)

        # Boutons Start / Stop
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=5, column=0, columnspan=2, **pad)
        self.start_btn = ctk.CTkButton(btn_frame, text="▶️ Démarrer", command=toggle_clicking)
        self.start_btn.pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="⏹ Quitter", command=self.on_closing).pack(side="left", padx=5)

        # Status
        self.status = ctk.CTkLabel(self, text="⏸ Inactif", text_color="orange")
        self.status.grid(row=6, column=0, columnspan=2, **pad)

    # --- Fonctions UI --- #
    def capture_position(self):
        x, y = pyautogui.position()
        self.x_var.set(str(x))
        self.y_var.set(str(y))
        self.use_current.set(False)
        self.status.configure(text=f"Position capturée : ({x}, {y})", text_color="blue")

    def on_closing(self):
        stop_event.set()
        keyboard.unhook_all_hotkeys()
        self.destroy()

app_instance = None  # Pour accéder depuis toggle_clicking

# ----------   Contrôle Start/Stop   ---------- #
def toggle_clicking():
    global clicking, app_instance

    if app_instance is None:
        return  # Pas encore initialisé

    if not clicking:
        # --- Démarrage --- #
        try:
            interval = float(app_instance.interval_var.get())
            repeat   = int(app_instance.repeat_var.get())
            if interval <= 0: raise ValueError
            if repeat < 0:    raise ValueError
        except ValueError:
            messagebox.showerror("Erreur", "Intervalle ou répétitions invalides.")
            return

        if app_instance.use_current.get():
            x = y = None
        else:
            try:
                x = int(app_instance.x_var.get())
                y = int(app_instance.y_var.get())
            except ValueError:
                messagebox.showerror("Erreur", "Coordonnées X/Y invalides.")
                return

        # Lancer le thread
        stop_event.clear()
        app_instance.click_thread = threading.Thread(
            target=click_worker,
            args=(interval, repeat, app_instance.use_current.get(), x, y),
            daemon=True
        )
        app_instance.click_thread.start()
        clicking = True
        app_instance.status.configure(text="✅ Clics en cours (F8 pour stop)", text_color="green")
        app_instance.start_btn.configure(text="⏸ Stop")
    else:
        # --- Arrêt --- #
        clicking = False
        stop_event.set()
        app_instance.status.configure(text="⏸ Inactif", text_color="orange")
        app_instance.start_btn.configure(text="▶️ Démarrer")

# ----------   Lancement   ---------- #
if __name__ == "__main__":
    app_instance = AutoClickerApp()
    app_instance.protocol("WM_DELETE_WINDOW", app_instance.on_closing)
    app_instance.mainloop()