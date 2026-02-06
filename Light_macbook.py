import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import json
import os

class AdvancedTrafficLight:
    def __init__(self, root):
        self.root = root
        self.root.title("🚦 Advanced Traffic Light - MacBook Air 13")
        self.root.geometry("800x900")
        
        # Темный стиль MacBook
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Цветовая схема темного режима MacBook
        self.colors = {
            'bg': '#000000',
            'panel': '#1d1d1f',
            'text': '#ffffff',
            'secondary': '#8a8d8f',
            'red': '#ff3b30',
            'yellow': '#ffcc00',
            'green': '#34c759',
            'button': '#2c2c2e',
            'button_hover': '#3a3a3c',
            'border': '#424245',
            'input': '#2c2c2e'
        }
        
        # Настройки по умолчанию
        self.current_state = "RED"
        self.auto_mode = True
        self.emergency_mode = False
        self.night_mode = False
        self.pedestrian_mode = False
        self.sound_enabled = True
        
        # Тайминги
        self.timings = {
            'RED': 5,
            'RED_YELLOW': 2,
            'GREEN': 5,
            'YELLOW': 2,
            'GREEN_BLINK': 3,
            'PEDESTRIAN': 10
        }
        
        self.state_start_time = time.time()
        self.running = True
        
        # Загрузка сохраненных настроек
        self.load_settings()
        
        # Создание интерфейса
        self.setup_gui()
        
        # Запуск потоков
        self.light_thread = threading.Thread(target=self.light_controller, daemon=True)
        self.light_thread.start()
        
        self.pedestrian_thread = threading.Thread(target=self.pedestrian_controller, daemon=True)
        self.pedestrian_thread.start()
    
    def setup_gui(self):
        """Создание полного GUI"""
        
        # Основной контейнер
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Заголовок
        self.create_header(main_frame)
        
        # Основной светофор
        self.create_main_traffic_light(main_frame)
        
        # Панель управления
        self.create_control_panel(main_frame)
        
        # Панель пешехода
        self.create_pedestrian_panel(main_frame)
        
        # Панель настроек
        self.create_settings_panel(main_frame)
        
        # Статус бар
        self.create_status_bar(main_frame)
    
    def create_header(self, parent):
        """Создание заголовка"""
        header_frame = tk.Frame(parent, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Лого и название
        logo_label = tk.Label(
            header_frame,
            text="🚦",
            font=("SF Pro Display", 28),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        logo_label.pack(side=tk.LEFT)
        
        title_label = tk.Label(
            header_frame,
            text="Advanced Traffic Light",
            font=("SF Pro Display", 22, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text']
        )
        title_label.pack(side=tk.LEFT, padx=10)
        
        # Версия
        version_label = tk.Label(
            header_frame,
            text="for MacBook Air 13",
            font=("SF Pro Text", 12),
            bg=self.colors['bg'],
            fg=self.colors['secondary']
        )
        version_label.pack(side=tk.RIGHT)
    
    def create_main_traffic_light(self, parent):
        """Создание основного светофора"""
        light_frame = tk.Frame(
            parent,
            bg=self.colors['panel'],
            highlightbackground=self.colors['border'],
            highlightthickness=2,
            relief=tk.FLAT
        )
        light_frame.pack(fill=tk.X, pady=10, padx=20, ipady=20)
        
        # Красный свет
        self.red_light = tk.Canvas(
            light_frame,
            width=100,
            height=100,
            bg=self.colors['panel'],
            highlightthickness=0
        )
        self.red_light.pack(side=tk.TOP, pady=15)
        self.red_circle = self.red_light.create_oval(10, 10, 90, 90, fill='#330000', outline='')
        
        # Желтый свет
        self.yellow_light = tk.Canvas(
            light_frame,
            width=100,
            height=100,
            bg=self.colors['panel'],
            highlightthickness=0
        )
        self.yellow_light.pack(side=tk.TOP, pady=15)
        self.yellow_circle = self.yellow_light.create_oval(10, 10, 90, 90, fill='#333300', outline='')
        
        # Зеленый свет
        self.green_light = tk.Canvas(
            light_frame,
            width=100,
            height=100,
            bg=self.colors['panel'],
            highlightthickness=0
        )
        self.green_light.pack(side=tk.TOP, pady=15)
        self.green_circle = self.green_light.create_oval(10, 10, 90, 90, fill='#003300', outline='')
        
        # Статус и таймер
        status_frame = tk.Frame(light_frame, bg=self.colors['panel'])
        status_frame.pack(pady=20)
        
        self.status_label = tk.Label(
            status_frame,
            text="STOP",
            font=("SF Pro Display", 24, "bold"),
            bg=self.colors['panel'],
            fg=self.colors['red']
        )
        self.status_label.pack()
        
        self.timer_label = tk.Label(
            status_frame,
            text="Time left: 5.0s",
            font=("SF Pro Text", 14),
            bg=self.colors['panel'],
            fg=self.colors['secondary']
        )
        self.timer_label.pack()
    
    def create_control_panel(self, parent):
        """Создание панели управления"""
        control_frame = tk.LabelFrame(
            parent,
            text=" Manual Control ",
            font=("SF Pro Text", 12, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text'],
            labelanchor='n'
        )
        control_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Кнопки ручного управления
        buttons_frame = tk.Frame(control_frame, bg=self.colors['bg'])
        buttons_frame.pack(pady=15)
        
        # Красный
        self.red_btn = tk.Button(
            buttons_frame,
            text="🔴 STOP",
            command=lambda: self.set_manual_state("RED"),
            font=("SF Pro Text", 13),
            bg=self.colors['button'],
            fg=self.colors['text'],
            activebackground=self.colors['button_hover'],
            activeforeground=self.colors['text'],
            borderwidth=0,
            width=12,
            height=2
        )
        self.red_btn.pack(side=tk.LEFT, padx=5)
        
        # Желтый
        self.yellow_btn = tk.Button(
            buttons_frame,
            text="🟡 CAUTION",
            command=lambda: self.set_manual_state("YELLOW"),
            font=("SF Pro Text", 13),
            bg=self.colors['button'],
            fg=self.colors['text'],
            activebackground=self.colors['button_hover'],
            activeforeground=self.colors['text'],
            borderwidth=0,
            width=12,
            height=2
        )
        self.yellow_btn.pack(side=tk.LEFT, padx=5)
        
        # Зеленый
        self.green_btn = tk.Button(
            buttons_frame,
            text="🟢 GO",
            command=lambda: self.set_manual_state("GREEN"),
            font=("SF Pro Text", 13),
            bg=self.colors['button'],
            fg=self.colors['text'],
            activebackground=self.colors['button_hover'],
            activeforeground=self.colors['text'],
            borderwidth=0,
            width=12,
            height=2
        )
        self.green_btn.pack(side=tk.LEFT, padx=5)
        
        # Режимы
        modes_frame = tk.Frame(control_frame, bg=self.colors['bg'])
        modes_frame.pack(pady=10)
        
        # Автоматический режим
        self.auto_var = tk.BooleanVar(value=self.auto_mode)
        self.auto_check = tk.Checkbutton(
            modes_frame,
            text="Automatic Mode",
            variable=self.auto_var,
            command=self.toggle_auto_mode,
            font=("SF Pro Text", 12),
            bg=self.colors['bg'],
            fg=self.colors['text'],
            selectcolor=self.colors['panel'],
            activebackground=self.colors['bg'],
            activeforeground=self.colors['text']
        )
        self.auto_check.pack(side=tk.LEFT, padx=10)
        
        # Аварийный режим
        self.emergency_var = tk.BooleanVar(value=self.emergency_mode)
        self.emergency_check = tk.Checkbutton(
            modes_frame,
            text="Emergency Mode",
            variable=self.emergency_var,
            command=self.toggle_emergency_mode,
            font=("SF Pro Text", 12),
            bg=self.colors['bg'],
            fg=self.colors['text'],
            selectcolor=self.colors['panel'],
            activebackground=self.colors['bg'],
            activeforeground=self.colors['text']
        )
        self.emergency_check.pack(side=tk.LEFT, padx=10)
        
        # Ночной режим
        self.night_var = tk.BooleanVar(value=self.night_mode)
        self.night_check = tk.Checkbutton(
            modes_frame,
            text="Night Mode",
            variable=self.night_var,
            command=self.toggle_night_mode,
            font=("SF Pro Text", 12),
            bg=self.colors['bg'],
            fg=self.colors['text'],
            selectcolor=self.colors['panel'],
            activebackground=self.colors['bg'],
            activeforeground=self.colors['text']
        )
        self.night_check.pack(side=tk.LEFT, padx=10)
    
    def create_pedestrian_panel(self, parent):
        """Создание панели пешехода"""
        ped_frame = tk.LabelFrame(
            parent,
            text=" Pedestrian Crossing ",
            font=("SF Pro Text", 12, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text'],
            labelanchor='n'
        )
        ped_frame.pack(fill=tk.X, pady=10, padx=20)
        
        ped_content = tk.Frame(ped_frame, bg=self.colors['bg'])
        ped_content.pack(pady=15, padx=10)
        
        # Кнопка вызова
        self.ped_button = tk.Button(
            ped_content,
            text="🚶 PUSH TO CROSS",
            command=self.pedestrian_request,
            font=("SF Pro Text", 14, "bold"),
            bg=self.colors['green'],
            fg=self.colors['text'],
            activebackground='#2ecc71',
            activeforeground=self.colors['text'],
            borderwidth=0,
            width=20,
            height=2,
            state=tk.NORMAL
        )
        self.ped_button.pack(side=tk.LEFT, padx=10)
        
        # Индикатор пешехода
        self.ped_light = tk.Canvas(
            ped_content,
            width=60,
            height=60,
            bg=self.colors['panel'],
            highlightthickness=0
        )
        self.ped_light.pack(side=tk.LEFT, padx=10)
        self.ped_circle = self.ped_light.create_oval(10, 10, 50, 50, fill='#330000', outline='')
        
        # Таймер пешехода
        self.ped_timer = tk.Label(
            ped_content,
            text="Wait: --",
            font=("SF Pro Text", 14),
            bg=self.colors['bg'],
            fg=self.colors['secondary']
        )
        self.ped_timer.pack(side=tk.LEFT, padx=10)
        
        # Статус пешехода
        self.ped_status = tk.Label(
            ped_content,
            text="Press button to cross",
            font=("SF Pro Text", 12),
            bg=self.colors['bg'],
            fg=self.colors['secondary']
        )
        self.ped_status.pack(side=tk.LEFT, padx=10)
    
    def create_settings_panel(self, parent):
        """Создание панели настроек"""
        settings_frame = tk.LabelFrame(
            parent,
            text=" Settings ",
            font=("SF Pro Text", 12, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text'],
            labelanchor='n'
        )
        settings_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # Сетка для настроек времени
        times_frame = tk.Frame(settings_frame, bg=self.colors['bg'])
        times_frame.pack(pady=15, padx=10)
        
        # Красное время
        tk.Label(
            times_frame,
            text="Red time (s):",
            font=("SF Pro Text", 11),
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).grid(row=0, column=0, padx=5, pady=5, sticky='e')
        
        self.red_time_var = tk.StringVar(value=str(self.timings['RED']))
        red_spin = tk.Spinbox(
            times_frame,
            from_=1,
            to=60,
            textvariable=self.red_time_var,
            width=8,
            font=("SF Pro Text", 11),
            bg=self.colors['input'],
            fg=self.colors['text'],
            insertbackground=self.colors['text']
        )
        red_spin.grid(row=0, column=1, padx=5, pady=5)
        
        # Желтое время
        tk.Label(
            times_frame,
            text="Yellow time (s):",
            font=("SF Pro Text", 11),
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).grid(row=0, column=2, padx=5, pady=5, sticky='e')
        
        self.yellow_time_var = tk.StringVar(value=str(self.timings['YELLOW']))
        yellow_spin = tk.Spinbox(
            times_frame,
            from_=1,
            to=30,
            textvariable=self.yellow_time_var,
            width=8,
            font=("SF Pro Text", 11),
            bg=self.colors['input'],
            fg=self.colors['text'],
            insertbackground=self.colors['text']
        )
        yellow_spin.grid(row=0, column=3, padx=5, pady=5)
        
        # Зеленое время
        tk.Label(
            times_frame,
            text="Green time (s):",
            font=("SF Pro Text", 11),
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).grid(row=1, column=0, padx=5, pady=5, sticky='e')
        
        self.green_time_var = tk.StringVar(value=str(self.timings['GREEN']))
        green_spin = tk.Spinbox(
            times_frame,
            from_=1,
            to=60,
            textvariable=self.green_time_var,
            width=8,
            font=("SF Pro Text", 11),
            bg=self.colors['input'],
            fg=self.colors['text'],
            insertbackground=self.colors['text']
        )
        green_spin.grid(row=1, column=1, padx=5, pady=5)
        
        # Пешеходное время
        tk.Label(
            times_frame,
            text="Pedestrian time (s):",
            font=("SF Pro Text", 11),
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).grid(row=1, column=2, padx=5, pady=5, sticky='e')
        
        self.ped_time_var = tk.StringVar(value=str(self.timings['PEDESTRIAN']))
        ped_spin = tk.Spinbox(
            times_frame,
            from_=5,
            to=30,
            textvariable=self.ped_time_var,
            width=8,
            font=("SF Pro Text", 11),
            bg=self.colors['input'],
            fg=self.colors['text'],
            insertbackground=self.colors['text']
        )
        ped_spin.grid(row=1, column=3, padx=5, pady=5)
        
        # Кнопки управления настройками
        buttons_frame = tk.Frame(settings_frame, bg=self.colors['bg'])
        buttons_frame.pack(pady=10)
        
        apply_btn = tk.Button(
            buttons_frame,
            text="Apply Settings",
            command=self.apply_settings,
            font=("SF Pro Text", 11),
            bg=self.colors['button'],
            fg=self.colors['text'],
            activebackground=self.colors['button_hover'],
            activeforeground=self.colors['text'],
            borderwidth=0,
            width=15
        )
        apply_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = tk.Button(
            buttons_frame,
            text="Save Settings",
            command=self.save_settings,
            font=("SF Pro Text", 11),
            bg=self.colors['button'],
            fg=self.colors['text'],
            activebackground=self.colors['button_hover'],
            activeforeground=self.colors['text'],
            borderwidth=0,
            width=15
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = tk.Button(
            buttons_frame,
            text="Reset to Default",
            command=self.reset_settings,
            font=("SF Pro Text", 11),
            bg=self.colors['button'],
            fg=self.colors['text'],
            activebackground=self.colors['button_hover'],
            activeforeground=self.colors['text'],
            borderwidth=0,
            width=15
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
    
    def create_status_bar(self, parent):
        """Создание статус бара"""
        status_frame = tk.Frame(parent, bg=self.colors['panel'])
        status_frame.pack(fill=tk.X, pady=10, padx=20)
        
        self.status_text = tk.StringVar(value="System: Ready | Mode: Automatic")
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_text,
            font=("SF Pro Text", 10),
            bg=self.colors['panel'],
            fg=self.colors['secondary']
        )
        status_label.pack(pady=5)
    
    def set_manual_state(self, state):
        """Ручное переключение состояния"""
        self.current_state = state
        self.auto_mode = False
        self.auto_var.set(False)
        self.state_start_time = time.time()
        self.update_lights()
        self.update_status(f"Manual control: {state}")
    
    def toggle_auto_mode(self):
        """Переключение автоматического режима"""
        self.auto_mode = self.auto_var.get()
        if self.auto_mode:
            self.state_start_time = time.time()
            self.update_status("Switched to Automatic mode")
        else:
            self.update_status("Switched to Manual mode")
    
    def toggle_emergency_mode(self):
        """Переключение аварийного режима"""
        self.emergency_mode = self.emergency_var.get()
        if self.emergency_mode:
            self.auto_mode = False
            self.auto_var.set(False)
            self.update_status("Emergency mode activated - Blinking Yellow")
        else:
            self.update_status("Emergency mode deactivated")
    
    def toggle_night_mode(self):
        """Переключение ночного режима"""
        self.night_mode = self.night_var.get()
        if self.night_mode:
            # Уменьшаем яркость или меняем тайминги
            self.update_status("Night mode activated - Reduced timings")
        else:
            self.update_status("Night mode deactivated")
    
    def pedestrian_request(self):
        """Запрос пешеходного перехода"""
        if not self.pedestrian_mode and self.current_state == "RED":
            self.pedestrian_mode = True
            self.ped_button.config(state=tk.DISABLED, bg='#555555')
            self.ped_status.config(text="Crossing in progress...")
            self.update_status("Pedestrian crossing requested")
    
    def apply_settings(self):
        """Применение настроек времени"""
        try:
            self.timings['RED'] = int(self.red_time_var.get())
            self.timings['YELLOW'] = int(self.yellow_time_var.get())
            self.timings['GREEN'] = int(self.green_time_var.get())
            self.timings['PEDESTRIAN'] = int(self.ped_time_var.get())
            
            self.state_start_time = time.time()
            self.update_status("Settings applied successfully")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
    
    def save_settings(self):
        """Сохранение настроек в файл"""
        settings = {
            'timings': self.timings,
            'auto_mode': self.auto_mode,
            'night_mode': self.night_mode
        }
        
        try:
            with open('traffic_settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
            self.update_status("Settings saved to file")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def load_settings(self):
        """Загрузка настроек из файла"""
        try:
            if os.path.exists('traffic_settings.json'):
                with open('traffic_settings.json', 'r') as f:
                    settings = json.load(f)
                    self.timings.update(settings.get('timings', {}))
                    self.auto_mode = settings.get('auto_mode', True)
                    self.night_mode = settings.get('night_mode', False)
        except:
            pass  # Используем настройки по умолчанию
    
    def reset_settings(self):
        """Сброс настроек к значениям по умолчанию"""
        self.timings = {
            'RED': 5,
            'RED_YELLOW': 2,
            'GREEN': 5,
            'YELLOW': 2,
            'GREEN_BLINK': 3,
            'PEDESTRIAN': 10
        }
        
        self.red_time_var.set('5')
        self.yellow_time_var.set('2')
        self.green_time_var.set('5')
        self.ped_time_var.set('10')
        
        self.update_status("Settings reset to defaults")
    
    def update_lights(self):
        """Обновление состояния светофора"""
        # Сбрасываем все цвета
        self.red_light.itemconfig(self.red_circle, fill='#330000')
        self.yellow_light.itemconfig(self.yellow_circle, fill='#333300')
        self.green_light.itemconfig(self.green_circle, fill='#003300')
        self.ped_light.itemconfig(self.ped_circle, fill='#330000')
        
        if self.emergency_mode:
            # Аварийный режим - мигающий желтый
            if int(time.time()) % 2 == 0:
                self.yellow_light.itemconfig(self.yellow_circle, fill=self.colors['yellow'])
                self.status_label.config(text="EMERGENCY", fg=self.colors['yellow'])
            else:
                self.status_label.config(text="CAUTION", fg=self.colors['secondary'])
            return
        
        # Нормальный режим
        if self.current_state == "RED":
            self.red_light.itemconfig(self.red_circle, fill=self.colors['red'])
            self.status_label.config(text="STOP", fg=self.colors['red'])
            
        elif self.current_state == "RED_YELLOW":
            self.red_light.itemconfig(self.red_circle, fill=self.colors['red'])
            self.yellow_light.itemconfig(self.yellow_circle, fill=self.colors['yellow'])
            self.status_label.config(text="PREPARE", fg=self.colors['yellow'])
            
        elif self.current_state == "GREEN":
            self.green_light.itemconfig(self.green_circle, fill=self.colors['green'])
            self.status_label.config(text="GO", fg=self.colors['green'])
            
        elif self.current_state == "YELLOW":
            self.yellow_light.itemconfig(self.yellow_circle, fill=self.colors['yellow'])
            self.status_label.config(text="CAUTION", fg=self.colors['yellow'])
        
        # Пешеходный свет
        if self.pedestrian_mode and self.current_state == "RED":
            self.ped_light.itemconfig(self.ped_circle, fill=self.colors['green'])
    
    def update_timer(self):
        """Обновление таймера"""
        elapsed = time.time() - self.state_start_time
        
        if self.current_state == "RED":
            time_left = self.timings['RED'] - elapsed
        elif self.current_state == "RED_YELLOW":
            time_left = self.timings['RED_YELLOW'] - elapsed
        elif self.current_state == "GREEN":
            time_left = self.timings['GREEN'] - elapsed
        elif self.current_state == "YELLOW":
            time_left = self.timings['YELLOW'] - elapsed
        else:
            time_left = 0
        
        if time_left > 0:
            self.timer_label.config(text=f"Time left: {time_left:.1f}s")
        else:
            self.timer_label.config(text="Changing...")
    
    def update_pedestrian_timer(self):
        """Обновление таймера пешехода"""
        if self.pedestrian_mode:
            elapsed = time.time() - self.pedestrian_start_time
            time_left = max(0, self.timings['PEDESTRIAN'] - elapsed)
            
            if time_left > 0:
                self.ped_timer.config(text=f"Cross: {time_left:.0f}s")
            else:
                self.pedestrian_mode = False
                self.ped_button.config(state=tk.NORMAL, bg=self.colors['green'])
                self.ped_status.config(text="Press button to cross")
                self.ped_timer.config(text="Wait: --")
                self.ped_light.itemconfig(self.ped_circle, fill='#330000')
    
    def update_status(self, message):
        """Обновление статус бара"""
        mode = "Automatic" if self.auto_mode else "Manual"
        if self.emergency_mode:
            mode = "Emergency"
        elif self.night_mode:
            mode = "Night"
        
        self.status_text.set(f"Status: {message} | Mode: {mode}")
    
    def auto_cycle(self):
        """Автоматический цикл светофора"""
        if not self.auto_mode or self.emergency_mode:
            return
        
        elapsed = time.time() - self.state_start_time
        
        if self.current_state == "RED" and elapsed >= self.timings['RED']:
            self.current_state = "RED_YELLOW"
            self.state_start_time = time.time()
            self.update_status("Switching to RED+YELLOW")
            
        elif self.current_state == "RED_YELLOW" and elapsed >= self.timings['RED_YELLOW']:
            self.current_state = "GREEN"
            self.state_start_time = time.time()
            self.update_status("Switching to GREEN")
            
        elif self.current_state == "GREEN" and elapsed >= self.timings['GREEN']:
            self.current_state = "YELLOW"
            self.state_start_time = time.time()
            self.update_status("Switching to YELLOW")
            
        elif self.current_state == "YELLOW" and elapsed >= self.timings['YELLOW']:
            self.current_state = "RED"
            self.state_start_time = time.time()
            self.update_status("Switching to RED")
            
            # Завершаем пешеходный переход если был
            if self.pedestrian_mode:
                self.pedestrian_mode = False
                self.pedestrian_start_time = time.time()
    
    def light_controller(self):
        """Контроллер светофора (работает в отдельном потоке)"""
        while self.running:
            try:
                # Автоматический цикл
                self.auto_cycle()
                
                # Обновление отображения
                self.root.after(0, self.update_lights)
                self.root.after(0, self.update_timer)
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error in light controller: {e}")
                break
    
    def pedestrian_controller(self):
        """Контроллер пешеходного перехода (работает в отдельном потоке)"""
        while self.running:
            try:
                if self.pedestrian_mode:
                    self.root.after(0, self.update_pedestrian_timer)
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error in pedestrian controller: {e}")
                break
    
    def on_close(self):
        """Обработка закрытия окна"""
        self.running = False
        self.save_settings()
        self.root.destroy()

def main():
    """Запуск приложения"""
    root = tk.Tk()
    app = AdvancedTrafficLight(root)
    
    # Обработка закрытия окна
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    
    # Центрирование окна
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()
