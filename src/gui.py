import customtkinter as ctk
from tkinter import messagebox, scrolledtext
import time
import os
import logging
from datetime import datetime
from history import save_history, read_history 
from config import fare_config
from taximeter import calculate_time_fare, calculate_distance_fare

# =========================
# Configuración de logging
# =========================
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    filename='logs/taximeter_gui.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# =========================
# Configuración global
# =========================
config = fare_config()  # Carga tarifas desde .env

# Variables globales para el viaje
trip_active = False
start_time = None
stopped_time = 0
moving_time = 0
state = None

# =========================
# Funciones de control
# =========================

def start_trip():
    global trip_active, start_time, stopped_time, moving_time, state
    if trip_active:
        messagebox.showwarning("Advertencia", "Ya hay un viaje en curso")
        logging.error("Intento de iniciar un viaje cuando ya hay uno en curso")
        return
    trip_active = True
    start_time = time.time()
    stopped_time = 0
    moving_time = 0
    state = 'stopped'
    messagebox.showinfo("Info", "El viaje ha sido iniciado. Estado inicial: parado.")
    logging.info("Viaje iniciado (modo GUI)")

def stop_trip():
    global trip_active, start_time, stopped_time, moving_time, state
    if not trip_active:
        messagebox.showwarning("Advertencia", "No hay un viaje en curso")
        logging.error("Intento de parar un viaje cuando no hay uno en curso")
        return
    now = time.time()
    if state == 'moving':
        moving_time += now - start_time
    else:
        stopped_time += now - start_time
    state = 'stopped'
    start_time = now
    update_labels()
    logging.info("Estado cambiado a parado")

def move_trip():
    global trip_active, start_time, stopped_time, moving_time, state
    if not trip_active:
        messagebox.showwarning("Advertencia", "No hay un viaje en curso")
        logging.error("Intento de mover un viaje cuando no hay uno en curso")
        return
    now = time.time()
    if state == 'stopped':
        stopped_time += now - start_time
    else:
        moving_time += now - start_time
    state = 'moving'
    start_time = now
    update_labels()
    logging.info("Estado cambiado a en movimiento")

def finish_trip():
    global trip_active, start_time, stopped_time, moving_time, state
    if not trip_active:
        messagebox.showwarning("Advertencia", "No hay un viaje en curso")
        logging.error("Intento de finalizar un viaje cuando no hay uno en curso")
        return
    now = time.time()
    if state == 'stopped':
        stopped_time += now - start_time
    else:
        moving_time += now - start_time
    trip_active = False
    total_fare = calculate_time_fare(stopped_time, moving_time)
    messagebox.showinfo(
        "Fin del viaje, resumen",
        f"Tiempo parado: {stopped_time:.2f} s\n"
        f"Tiempo en movimiento: {moving_time:.2f} s\n"
        f"Total a pagar: {total_fare:.2f} €"
    )
    # Guardar en historial
    trip_info = {
        'fecha': datetime.now(),
        'tipo': 'tiempo',
        'tiempo_parado': round(stopped_time, 2),
        'tiempo_movimiento': round(moving_time, 2),
        'duracion_total': round(stopped_time + moving_time, 2),
        'coste_total': round(total_fare, 2)
    }
    save_history(trip_info)
    logging.info("Trayecto por tiempo guardado en historial")
    reset_time_trip()

def start_distance_trip():
    try:
        distance = float(distance_entry.get())
        if distance <= 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning("Advertencia", "Distancia inválida. Debe ser un número positivo.")
        logging.error("Distancia inválida ingresada para viaje por distancia")
        return
    total_fare = calculate_distance_fare(distance)
    messagebox.showinfo(
        "Fin del viaje por distancia, resumen: ",
        f"Distancia: {distance:.2f} km\nTotal a pagar: {total_fare:.2f} €"
    )
    trip_info = {
        'fecha': datetime.now(),
        'tipo': 'distancia',
        'distancia_total': round(distance, 2),
        'coste_total': round(total_fare, 2)
    }
    save_history(trip_info)
    logging.info("Trayecto por distancia guardado en historial")
    fare_distance_label.configure(text="Tarifa actual: 0.00 €")
    distance_entry.delete(0, ctk.END)

def reset_time_trip():
    global trip_active, start_time, stopped_time, moving_time, state
    trip_active = False
    start_time = None
    stopped_time = 0
    moving_time = 0
    state = None
    update_labels()

def update_labels():
    stopped_label.configure(text=f"Tiempo parado: {stopped_time:.2f} s")
    moving_label.configure(text=f"Tiempo en movimiento: {moving_time:.2f} s")
    fare_label.configure(
        text=f"Tarifa actual: {calculate_time_fare(stopped_time, moving_time):.2f} €"
        if trip_active else "Tarifa actual: 0.00 €"
    )

def update_distance_fare(event=None):
    try:
        distance = float(distance_entry.get())
        fare = calculate_distance_fare(distance)
        fare_distance_label.configure(text=f"Tarifa actual: {fare:.2f} €")
    except ValueError:
        fare_distance_label.configure(text="Tarifa actual: 0.00 €")

def update_time_labels():
    if trip_active and start_time is not None:
        now = time.time()
        duration = now - start_time
        current_stopped = stopped_time + duration if state == 'stopped' else stopped_time
        current_moving = moving_time + duration if state == 'moving' else moving_time
        stopped_label.configure(text=f"Tiempo parado: {current_stopped:.2f} s")
        moving_label.configure(text=f"Tiempo en movimiento: {current_moving:.2f} s")
        fare_label.configure(text=f"Tarifa actual: {calculate_time_fare(current_stopped, current_moving):.2f} €")
    root.after(1000, update_time_labels)

# =========================
# Función para mostrar historial con estética CustomTkinter
# =========================
def show_history():
    hist_window = ctk.CTkToplevel()
    hist_window.title("Historial de viajes")
    hist_window.geometry("500x500")
    
    title_label = ctk.CTkLabel(hist_window, text="Historial de Viajes", font=("Arial", 16, "bold"))
    title_label.pack(pady=10)
    
    frame_scroll = ctk.CTkFrame(hist_window)
    frame_scroll.pack(fill="both", expand=True, padx=10, pady=10)
    
    st = scrolledtext.ScrolledText(frame_scroll, width=60, height=25, font=("Consolas", 11), bg="#2B2B2B", fg="white", insertbackground="white")
    st.pack(fill="both", expand=True)
    st.insert(ctk.END, read_history())
    st.configure(state='disabled')

# =========================
# Construcción de la GUI con CustomTkinter
# =========================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Taxímetro GUI")
root.geometry("500x550")

# Bienvenida
welcome_label = ctk.CTkLabel(root, text="¡Bienvenido al Taxímetro!\nElige una opción para comenzar.", font=("Arial", 16, "bold"))
welcome_label.pack(pady=15)

# --- Viaje por Tiempo ---
ctk.CTkLabel(root, text="--- Viaje por Tiempo ---", font=("Arial", 14, "bold")).pack(pady=7)
stopped_label = ctk.CTkLabel(root, text="Tiempo parado: 0.00 s")
stopped_label.pack()
moving_label = ctk.CTkLabel(root, text="Tiempo en movimiento: 0.00 s")
moving_label.pack()
fare_label = ctk.CTkLabel(root, text="Tarifa actual: 0.00 €")
fare_label.pack()

frame_buttons = ctk.CTkFrame(root)
frame_buttons.pack(pady=10)
start_button = ctk.CTkButton(frame_buttons, text="Iniciar", command=start_trip, fg_color="#4CAF50")
start_button.pack(side="left", padx=5)
stop_button = ctk.CTkButton(frame_buttons, text="Parar", command=stop_trip, fg_color="#F44336")
stop_button.pack(side="left", padx=5)
move_button = ctk.CTkButton(frame_buttons, text="Mover", command=move_trip, fg_color="#2196F3")
move_button.pack(side="left", padx=5)
finish_button = ctk.CTkButton(frame_buttons, text="Finalizar", command=finish_trip, fg_color="#FFC107")
finish_button.pack(side="left", padx=5)

update_time_labels()

# --- Viaje por Distancia ---
ctk.CTkLabel(root, text="--- Viaje por Distancia ---", font=("Arial", 14, "bold")).pack(pady=7)
distance_label = ctk.CTkLabel(root, text="Introduce la distancia en kilómetros:")
distance_label.pack()
distance_entry = ctk.CTkEntry(root)
distance_entry.pack(pady=5)
distance_entry.bind("<KeyRelease>", update_distance_fare)
fare_distance_label = ctk.CTkLabel(root, text="Tarifa actual: 0.00 €")
fare_distance_label.pack()
distance_button = ctk.CTkButton(root, text="Calcular Tarifa por Distancia", command=start_distance_trip, fg_color="#9C27B0")
distance_button.pack(pady=5)

# Botón historial
history_button = ctk.CTkButton(root, text="Ver historial", command=show_history, fg_color="#795548")
history_button.pack(pady=5)

# Botón salir
exit_button = ctk.CTkButton(root, text="Salir", command=root.quit, fg_color="#607D8B")
exit_button.pack(pady=10)

root.mainloop()
