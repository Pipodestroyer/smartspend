import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageOps
import datetime
import json
import os
import shutil
from tkinter import filedialog, messagebox

# --- CONFIGURACIÓN DE PALETA DE COLORES ---
COLOR_PRIMARIO = "#4183FF"
COLOR_FONDO_PRINCIPAL = ("#FFFFFF", "#282828")
COLOR_PANELES = ("#F2F2F2", "#2F2F2F")
COLOR_TEXTO = ("#282828", "#FFFFFF")
COLOR_TEXTO_SECUNDARIO = ("#666666", "#A0A0A0")
COLOR_BARRAS_VERDES = ("#AEDBAB", "#AEDBAB")
COLOR_BARRAS_ROJAS = ("#ECA7A7", "#ECA7A7")
COLOR_BARRAS_GRISES = ("#B3B3B3", "#8C8C8C")

ARCHIVO_DATOS = "datos_financieros.json"

class SetupWindow(ctk.CTkToplevel):
    """Ventana de configuración inicial para usuarios nuevos."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Bienvenido - Configuración Inicial")
        # Aumentamos un poco el alto para que quepa el logo
        self.geometry("400x550")
        self.resizable(False, False) # Bloquear redimensionamiento
        self.attributes("-topmost", True)
        self.parent = parent
        self.ruta_foto_seleccionada = None
        
        # --- CARGAR LOGO DEL PROGRAMA ---
        try:
            img_logo = ctk.CTkImage(light_image=Image.open("assets/logo.png"), 
                                    dark_image=Image.open("assets/logo.png"), 
                                    size=(80, 80))
            ctk.CTkLabel(self, image=img_logo, text="").pack(pady=(20, 0))
        except Exception:
            # Si no encuentra el logo, no crashea, simplemente no muestra imagen
            pass
        
        ctk.CTkLabel(self, text="¡Bienvenido a tu Gestor Financiero!", font=("Inter", 20, "bold")).pack(pady=(20, 10))
        ctk.CTkLabel(self, text="Por favor, ingresa tus datos para comenzar.", text_color=COLOR_TEXTO_SECUNDARIO).pack(pady=(0, 20))
        
        self.entry_nombre = ctk.CTkEntry(self, placeholder_text="Tu nombre", width=250)
        self.entry_nombre.pack(pady=10)
        
        self.entry_salario = ctk.CTkEntry(self, placeholder_text="Salario base mensual (COP)", width=250)
        self.entry_salario.pack(pady=10)
        
        self.btn_foto = ctk.CTkButton(self, text="Seleccionar Foto de Perfil", command=self.seleccionar_foto, fg_color=COLOR_PANELES, text_color=COLOR_TEXTO, hover_color=COLOR_BARRAS_GRISES)
        self.btn_foto.pack(pady=20)
        
        self.lbl_foto_estado = ctk.CTkLabel(self, text="Ninguna foto seleccionada", text_color=COLOR_TEXTO_SECUNDARIO)
        self.lbl_foto_estado.pack()
        
        ctk.CTkButton(self, text="Guardar y Continuar", command=self.guardar_y_cerrar, fg_color=COLOR_PRIMARIO).pack(pady=30)

    def seleccionar_foto(self):
        # Desactivamos topmost temporalmente para que el explorador de archivos se vea por encima
        self.attributes("-topmost", False) 
        ruta = filedialog.askopenfilename(title="Seleccionar foto", filetypes=[("Archivos de imagen", "*.jpg *.jpeg *.png")])
        self.attributes("-topmost", True) # Lo volvemos a activar
        
        if ruta:
            self.ruta_foto_seleccionada = ruta
            self.lbl_foto_estado.configure(text="Foto seleccionada correctamente.")

    def guardar_y_cerrar(self):
        nombre = self.entry_nombre.get()
        salario = self.entry_salario.get()
        
        if not nombre or not salario:
            messagebox.showerror("Error", "Debes ingresar tu nombre y salario.")
            return
            
        try:
            salario_float = float(salario)
        except ValueError:
            messagebox.showerror("Error", "El salario debe ser un número válido.")
            return

        foto_destino = "assets/default_profile.png"
        if self.ruta_foto_seleccionada:
            if not os.path.exists("assets"): os.makedirs("assets")
            foto_destino = "assets/user_profile.png"
            shutil.copy(self.ruta_foto_seleccionada, foto_destino)
            
        datos = {
            "nombre": nombre,
            "foto": foto_destino,
            "salario_base": salario_float,
            "ahorro_mensual": 0.0,
            "transacciones": []
        }
        
        with open(ARCHIVO_DATOS, "w") as f:
            json.dump(datos, f)
            
        self.parent.cargar_datos()
        self.destroy()

class InputModal(ctk.CTkToplevel):
    """Modal reutilizable para agregar ingresos, gastos, etc."""
    def __init__(self, parent, tipo_transaccion):
        super().__init__(parent)
        self.title(f"Nuevo {tipo_transaccion}")
        self.geometry("350x300")
        self.resizable(False, False) # Bloquear redimensionamiento en el modal
        self.attributes("-topmost", True)
        self.parent = parent
        self.tipo = tipo_transaccion
        
        ctk.CTkLabel(self, text=f"Registrar {tipo_transaccion}", font=("Inter", 18, "bold")).pack(pady=20)
        
        self.entry_monto = ctk.CTkEntry(self, placeholder_text="Monto (COP)", width=200)
        self.entry_monto.pack(pady=10)
        
        self.entry_desc = ctk.CTkEntry(self, placeholder_text="Descripción", width=200)
        self.entry_desc.pack(pady=10)
        
        ctk.CTkButton(self, text="Guardar", command=self.guardar_transaccion, fg_color=COLOR_PRIMARIO).pack(pady=30)

    def guardar_transaccion(self):
        messagebox.showinfo("Éxito", f"{self.tipo} registrado. (Lógica de base de datos pendiente)")
        self.destroy()

class FinanzasApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Dashboard Financiero")
        self.geometry("1100x700")
        self.minsize(950, 600) # Bloquear redimensionamiento de la app principal
        
        ctk.set_appearance_mode("dark")
        self.modo_actual = "dark"
        
        # FUENTE PERSONALIZADA INTER
        self.fuente_titulos = ctk.CTkFont(family="inter", size=28, weight="bold")
        self.fuente_subtitulos = ctk.CTkFont(family="inter", size=18)
        self.fuente_normal = ctk.CTkFont(family="inter", size=13, weight="bold")
        self.fuente_pequena = ctk.CTkFont(family="inter", size=12)

        self.datos_usuario = {}
        self.verificar_primer_inicio()

    def verificar_primer_inicio(self):
        if not os.path.exists(ARCHIVO_DATOS):
            self.withdraw()
            SetupWindow(self)
        else:
            self.cargar_datos()

    def cargar_datos(self):
        self.deiconify()
        with open(ARCHIVO_DATOS, "r") as f:
            self.datos_usuario = json.load(f)
        self.construir_ui()

    def obtener_saludo(self):
        hora = datetime.datetime.now().hour
        if hora < 12: return "¡Buenos días,"
        elif hora < 18: return "¡Buenas tardes,"
        else: return "¡Buenas noches,"

    def crear_imagen_circular(self, ruta, tamano):
        """Recorta la imagen en círculo y mantiene el ratio."""
        try:
            img = Image.open(ruta).convert("RGBA")
            img = ImageOps.fit(img, tamano, centering=(0.5, 0.5))
            
            mask = Image.new('L', tamano, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + tamano, fill=255)
            
            img.putalpha(mask)
            return ctk.CTkImage(light_image=img, dark_image=img, size=tamano)
        except Exception:
            img = Image.new('RGB', tamano, color='gray')
            return ctk.CTkImage(light_image=img, dark_image=img, size=tamano)

    def cargar_icono_dinamico(self, nombre_base, tamano):
        """Carga dos versiones del icono para que cambie con el tema."""
        try:
            ruta_light = f"assets/{nombre_base}_light.png"
            ruta_dark = f"assets/{nombre_base}_dark.png"
            
            return ctk.CTkImage(
                light_image=Image.open(ruta_light), 
                dark_image=Image.open(ruta_dark), 
                size=tamano
            )
        except Exception:
            img = Image.new('RGBA', tamano, (0,0,0,0))
            return ctk.CTkImage(light_image=img, dark_image=img, size=tamano)

    def toggle_theme(self):
        if self.modo_actual == "dark":
            ctk.set_appearance_mode("light")
            self.modo_actual = "light"
        else:
            ctk.set_appearance_mode("dark")
            self.modo_actual = "dark"

    def construir_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ==================== BARRA LATERAL ====================
        sidebar = ctk.CTkFrame(self, fg_color=COLOR_PANELES, width=220, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        # Perfil (Ahora circular)
        frame_perfil = ctk.CTkFrame(sidebar, fg_color="transparent")
        frame_perfil.pack(pady=(30, 20), padx=10, fill="x")
        
        img_perfil = self.crear_imagen_circular(self.datos_usuario.get("foto", "assets/default_profile.png"), (45, 45))
        lbl_foto = ctk.CTkLabel(frame_perfil, image=img_perfil, text="")
        lbl_foto.pack(side="left", padx=(10, 10))
        
        frame_saludo = ctk.CTkFrame(frame_perfil, fg_color="transparent")
        frame_saludo.pack(side="left", fill="x")
        ctk.CTkLabel(frame_saludo, text=self.obtener_saludo(), font=self.fuente_pequena, text_color=COLOR_TEXTO).pack(anchor="w")
        nombre_display = self.datos_usuario.get("nombre", "Usuario").split()[0]
        ctk.CTkLabel(frame_saludo, text=f"{nombre_display}!", font=self.fuente_normal, text_color=COLOR_TEXTO).pack(anchor="w")

        # Botones Principales
        ctk.CTkButton(sidebar, text="Mi Perfil", fg_color=COLOR_PRIMARIO, text_color="#FFFFFF", font=self.fuente_normal).pack(pady=(0, 10), padx=20, fill="x")
        btn_billetera = ctk.CTkButton(sidebar, text="Billetera", fg_color=COLOR_FONDO_PRINCIPAL, text_color=COLOR_TEXTO, hover_color=COLOR_BARRAS_GRISES, font=self.fuente_normal)
        btn_billetera.pack(pady=(0, 20), padx=20, fill="x")

        # Navegación
        opciones_nav = [
            ("Ingresos", "ingresos", lambda: InputModal(self, "Ingreso")),
            ("Gastos", "gastos", lambda: InputModal(self, "Gasto")),
            ("Metas", "metas", None),
            ("Proyecciones", "proyecciones", None),
            ("Historial", "historial", None)
        ]

        for texto, nombre_icono, comando in opciones_nav:
            img_icono = self.cargar_icono_dinamico(nombre_icono, (20, 20))
            btn = ctk.CTkButton(sidebar, text=f"   {texto}", image=img_icono, anchor="w", fg_color="transparent", text_color=COLOR_TEXTO, hover_color=COLOR_FONDO_PRINCIPAL, font=self.fuente_normal, command=comando)
            btn.pack(pady=5, padx=20, fill="x")

        # Botón de Tema
        img_theme = self.cargar_icono_dinamico("theme_icon", (24, 24))
        btn_theme = ctk.CTkButton(sidebar, text="", image=img_theme, width=40, fg_color="transparent", hover_color=COLOR_PANELES, command=self.toggle_theme)
        btn_theme.pack(side="bottom", anchor="w", pady=20, padx=20)

        # ==================== ÁREA PRINCIPAL ====================
        main_area = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        main_area.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        main_area.grid_columnconfigure((0, 1), weight=1)
        
        ahorro = self.datos_usuario.get("ahorro_mensual", 0)
        ctk.CTkLabel(main_area, text="Has ahorrado", font=self.fuente_titulos, text_color=COLOR_TEXTO).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        ctk.CTkLabel(main_area, text=f"COP {ahorro:,.0f} este mes.".replace(",", "."), font=self.fuente_titulos, text_color=COLOR_TEXTO).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 30))

        # Tarjetas
        self.crear_tarjeta(main_area, "Ingresos", "COP 500.000", "trend_up", 2, 0)
        self.crear_tarjeta(main_area, "Puntaje crediticio", "129", "trend_up", 2, 1)
        self.crear_tarjeta(main_area, "Proyecciones Q1 2027", "COP 120.000", "trend_down", 3, 0)
        self.crear_tarjeta(main_area, "Gastos", "COP 120.000", "trend_down", 3, 1)

    def crear_tarjeta(self, parent, titulo, subtitulo, icono_tendencia, row, col):
        card = ctk.CTkFrame(parent, fg_color=COLOR_PANELES, corner_radius=15)
        card.grid(row=row, column=col, sticky="nsew", padx=15, pady=15)
        card.grid_propagate(False)
        card.configure(height=240)

        ctk.CTkLabel(card, text=titulo, font=self.fuente_subtitulos, text_color=COLOR_TEXTO).pack(anchor="w", padx=20, pady=(15, 0))
        
        trend_frame = ctk.CTkFrame(card, fg_color="transparent")
        trend_frame.pack(anchor="w", padx=20, pady=(5, 15))
        
        img_trend = self.cargar_icono_dinamico(icono_tendencia, (16, 16))
        ctk.CTkLabel(trend_frame, text="", image=img_trend).pack(side="left", padx=(0, 5))
        ctk.CTkLabel(trend_frame, text=subtitulo, font=self.fuente_pequena, text_color=COLOR_TEXTO_SECUNDARIO).pack(side="left")

        chart_area = ctk.CTkFrame(card, fg_color="transparent")
        chart_area.pack(fill="both", expand=True, padx=20, pady=(0, 20), side="bottom")
        
        import random
        colores = [COLOR_BARRAS_VERDES, COLOR_BARRAS_ROJAS, COLOR_BARRAS_GRISES]
        for i in range(8):
            altura = random.randint(30, 120)
            color = random.choice(colores)
            barra_frame = ctk.CTkFrame(chart_area, width=15, height=altura, fg_color=color, corner_radius=3)
            barra_frame.pack(side="left", padx=4, anchor="s")

if __name__ == "__main__":
    app = FinanzasApp()
    app.mainloop()