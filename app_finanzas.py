import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageOps
import datetime
import json
import os
import shutil
from tkinter import filedialog, messagebox

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
        self.geometry("400x550")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.parent = parent
        self.ruta_foto_seleccionada = None
        
        try:
            img_logo = ctk.CTkImage(light_image=Image.open("assets/logo.png"), 
                                    dark_image=Image.open("assets/logo.png"), 
                                    size=(80, 80))
            ctk.CTkLabel(self, image=img_logo, text="").pack(pady=(20, 0))
        except Exception:
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
        self.attributes("-topmost", False) 
        ruta = filedialog.askopenfilename(title="Seleccionar foto", filetypes=[("Archivos de imagen", "*.jpg *.jpeg *.png")])
        self.attributes("-topmost", True) 
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
            "billetera_total": salario_float, 
            "transacciones": [],
            "metas": []
        }
        
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
            
        self.parent.cargar_datos()
        self.destroy()


class FinanzasApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Dashboard Financiero")
        self.geometry("1100x700")
        self.minsize(950, 600)
        
        ctk.set_appearance_mode("dark")
        self.modo_actual = "dark"
        
        self.fuente_titulos = ctk.CTkFont(family="Inter", size=28, weight="bold")
        self.fuente_subtitulos = ctk.CTkFont(family="Inter", size=18, weight="bold")
        self.fuente_normal = ctk.CTkFont(family="Inter", size=13, weight="bold")
        self.fuente_pequena = ctk.CTkFont(family="Inter", size=12)

        self.datos_usuario = {}
        self.main_area = None
        self.sidebar = None
        self.verificar_primer_inicio()

    def verificar_primer_inicio(self):
        if not os.path.exists(ARCHIVO_DATOS):
            self.withdraw()
            SetupWindow(self)
        else:
            self.cargar_datos()

    def cargar_datos(self):
        self.deiconify()
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            self.datos_usuario = json.load(f)
        self.construir_esqueleto_ui()
        self.mostrar_vista("billetera") 

    def guardar_datos(self):
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
            json.dump(self.datos_usuario, f, ensure_ascii=False, indent=4)

    def obtener_saludo(self):
        hora = datetime.datetime.now().hour
        if hora < 12: return "¡Buenos días,"
        elif hora < 18: return "¡Buenas tardes,"
        else: return "¡Buenas noches,"

    def crear_imagen_circular(self, ruta, tamano):
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
        try:
            ruta_light = f"assets/{nombre_base}_light.png"
            ruta_dark = f"assets/{nombre_base}_dark.png"
            return ctk.CTkImage(light_image=Image.open(ruta_light), dark_image=Image.open(ruta_dark), size=tamano)
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

    def construir_esqueleto_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = ctk.CTkFrame(self, fg_color=COLOR_PANELES, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        self.perfil_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.perfil_container.pack(fill="x", pady=(30, 20), padx=10)

        self.actualizar_bloque_perfil_sidebar()

        ctk.CTkButton(self.sidebar, text="Mi Perfil", fg_color=COLOR_PRIMARIO, text_color="#FFFFFF", font=self.fuente_normal, command=lambda: self.mostrar_vista("perfil")).pack(pady=(0, 10), padx=20, fill="x")
        ctk.CTkButton(self.sidebar, text="Billetera", fg_color=COLOR_FONDO_PRINCIPAL, text_color=COLOR_TEXTO, hover_color=COLOR_BARRAS_GRISES, font=self.fuente_normal, command=lambda: self.mostrar_vista("billetera")).pack(pady=(0, 20), padx=20, fill="x")

        opciones_nav = [
            ("Ingresos", "ingresos", lambda: self.mostrar_vista("ingresos")),
            ("Gastos", "gastos", lambda: self.mostrar_vista("gastos")),
            ("Metas", "metas", lambda: self.mostrar_vista("metas")),
            ("Historial", "historial", lambda: self.mostrar_vista("historial"))
        ]

        for texto, nombre_icono, comando in opciones_nav:
            img_icono = self.cargar_icono_dinamico(nombre_icono, (20, 20))
            btn = ctk.CTkButton(self.sidebar, text=f"   {texto}", image=img_icono, anchor="w", fg_color="transparent", text_color=COLOR_TEXTO, hover_color=COLOR_BARRAS_GRISES, font=self.fuente_normal, command=comando)
            btn.pack(pady=5, padx=20, fill="x")

        img_theme = self.cargar_icono_dinamico("theme_icon", (24, 24))
        btn_theme = ctk.CTkButton(self.sidebar, text="", image=img_theme, width=40, fg_color="transparent", hover_color=COLOR_BARRAS_GRISES, command=self.toggle_theme)
        btn_theme.pack(side="bottom", anchor="w", pady=20, padx=20)

        self.main_area = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)

    def actualizar_bloque_perfil_sidebar(self):

        for widget in self.perfil_container.winfo_children():
            widget.destroy()
        
        img_perfil = self.crear_imagen_circular(self.datos_usuario.get("foto", "assets/default_profile.png"), (45, 45))
        lbl_foto = ctk.CTkLabel(self.perfil_container, image=img_perfil, text="")
        lbl_foto.pack(side="left", padx=(10, 10))
        
        frame_saludo = ctk.CTkFrame(self.perfil_container, fg_color="transparent")
        frame_saludo.pack(side="left", fill="x")
        
        ctk.CTkLabel(frame_saludo, text=self.obtener_saludo(), font=self.fuente_pequena, text_color=COLOR_TEXTO).pack(anchor="w")
        nombre_display = self.datos_usuario.get("nombre", "Usuario").split()[0]
        ctk.CTkLabel(frame_saludo, text=f"{nombre_display}!", font=self.fuente_normal, text_color=COLOR_TEXTO).pack(anchor="w")

    def limpiar_pantalla_principal(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()

    def mostrar_vista(self, vista):
        self.limpiar_pantalla_principal()
        
        if vista == "perfil":
            self.render_perfil()
        elif vista == "billetera":
            self.render_billetera()
        elif vista == "ingresos":
            self.render_ingresos_gastos("Ingreso")
        elif vista == "gastos":
            self.render_ingresos_gastos("Gasto")
        elif vista == "metas":
            self.render_metas()
        elif vista == "historial":
            self.render_historial()

    def render_perfil(self):
        container = ctk.CTkFrame(self.main_area, fg_color="transparent")
        container.pack(expand=True, fill="both", pady=40)

        img_perfil = self.crear_imagen_circular(self.datos_usuario.get("foto", "assets/default_profile.png"), (130, 130))
        btn_foto = ctk.CTkButton(container, image=img_perfil, text="", fg_color="transparent", hover=False, command=self.cambiar_foto_desde_perfil)
        btn_foto.pack(pady=10)
        
        ctk.CTkLabel(container, text="Click en la foto para cambiarla", font=self.fuente_pequena, text_color=COLOR_TEXTO_SECUNDARIO).pack(pady=(0, 20))

        ctk.CTkLabel(container, text="Nombre de Usuario", font=self.fuente_subtitulos, text_color=COLOR_TEXTO).pack(pady=5)
        self.entry_cambiar_nombre = ctk.CTkEntry(container, width=300, font=self.fuente_normal)
        self.entry_cambiar_nombre.insert(0, self.datos_usuario.get("nombre", ""))
        self.entry_cambiar_nombre.pack(pady=10)

        ctk.CTkLabel(container, text="Salario Base Mensual (COP)", font=self.fuente_subtitulos, text_color=COLOR_TEXTO).pack(pady=5)
        self.entry_cambiar_salario = ctk.CTkEntry(container, width=300, font=self.fuente_normal)
        self.entry_cambiar_salario.insert(0, str(self.datos_usuario.get("salario_base", 0.0)))
        self.entry_cambiar_salario.pack(pady=10)

        ctk.CTkButton(container, text="Guardar Cambios", fg_color=COLOR_PRIMARIO, text_color="#FFFFFF", font=self.fuente_normal, command=self.actualizar_datos_perfil).pack(pady=30)

    def cambiar_foto_desde_perfil(self):
        ruta = filedialog.askopenfilename(title="Cambiar foto de perfil", filetypes=[("Archivos de imagen", "*.jpg *.jpeg *.png")])
        if ruta:
            foto_destino = "assets/user_profile.png"
            if not os.path.exists("assets"): os.makedirs("assets")
            shutil.copy(ruta, foto_destino)
            self.datos_usuario["foto"] = foto_destino
            self.guardar_datos()
            self.actualizar_bloque_perfil_sidebar()
            self.mostrar_vista("perfil")

    def actualizar_datos_perfil(self):
        nuevo_nombre = self.entry_cambiar_nombre.get()
        nuevo_salario = self.entry_cambiar_salario.get()
        if not nuevo_nombre or not nuevo_salario:
            messagebox.showerror("Error", "Los campos no pueden estar vacíos.")
            return
        try:
            self.datos_usuario["nombre"] = nuevo_nombre
            self.datos_usuario["salario_base"] = float(nuevo_salario)
            self.guardar_datos()
            self.actualizar_bloque_perfil_sidebar()
            messagebox.showinfo("Éxito", "Perfil actualizado correctamente.")
        except ValueError:
            messagebox.showerror("Error", "El salario debe ser un número válido.")


    def render_billetera(self):
        img_billetera = self.cargar_icono_dinamico("billetera_centrada", (70, 70))
        ctk.CTkLabel(self.main_area, image=img_billetera, text="").pack(pady=(10, 5))
        
        ctk.CTkLabel(self.main_area, text="Billetera", font=self.fuente_titulos, text_color=COLOR_TEXTO).pack()
        
        total = self.datos_usuario.get("billetera_total", 0.0)
        ctk.CTkLabel(self.main_area, text=f"COP {total:,.0f}".replace(",", "."), font=self.fuente_titulos, text_color=COLOR_PRIMARIO).pack(pady=(0, 20))

        self.render_modulo_ultimos_movimientos()

    def render_modulo_ultimos_movimientos(self):
        frame_movimientos = ctk.CTkFrame(self.main_area, fg_color="transparent")
        frame_movimientos.pack(fill="x", padx=40, pady=10)


        transacciones = self.datos_usuario.get("transacciones", [])
        entradas = [t for t in transacciones if t["tipo"] == "Ingreso"]
        salidas = [t for t in transacciones if t["tipo"] == "Gasto"]


        self.crear_fila_movimiento(frame_movimientos, "Última Entrada", entradas[-1] if entradas else None, "trend_up")

        self.crear_fila_movimiento(frame_movimientos, "Última Salida", salidas[-1] if salidas else None, "trend_down")

    def crear_fila_movimiento(self, parent, titulo_bloque, transaccion, icono_nombre):
        container_fila = ctk.CTkFrame(parent, fg_color=COLOR_PANELES, height=75, corner_radius=12)
        container_fila.pack(fill="x", pady=8)
        container_fila.pack_propagate(False)

     
        img_ico = self.cargar_icono_dinamico(icono_nombre, (24, 24))
        lbl_ico = ctk.CTkLabel(container_fila, image=img_ico, text="")
        lbl_ico.pack(side="left", padx=20)

        lbl_tit = ctk.CTkLabel(container_fila, text=titulo_bloque, font=self.fuente_subtitulos, text_color=COLOR_TEXTO)
        lbl_tit.pack(side="left")

        frame_derecho = ctk.CTkFrame(container_fila, fg_color="transparent")
        frame_derecho.pack(side="right", padx=20, fill="y")

        if transaccion:
            monto_str = f"COP {transaccion['monto']:,.0f}".replace(",", ".")
            desc_str = transaccion['descripcion']
            ctk.CTkLabel(frame_derecho, text=monto_str, font=self.fuente_normal, text_color=COLOR_TEXTO, anchor="e").pack(side="top", pady=(15,0))
            ctk.CTkLabel(frame_derecho, text=desc_str, font=self.fuente_pequena, text_color=COLOR_TEXTO_SECUNDARIO, anchor="e").pack(side="top")
        else:
            ctk.CTkLabel(frame_derecho, text="Sin registros", font=self.fuente_normal, text_color=COLOR_TEXTO_SECUNDARIO).pack(side="right", pady=20)

    def render_ingresos_gastos(self, tipo):
        icono_central = "ingresos_centrados" if tipo == "Ingreso" else "gastos_centrados"
        img_central = self.cargar_icono_dinamico(icono_central, (70, 70))
        ctk.CTkLabel(self.main_area, image=img_central, text="").pack(pady=(10, 5))

        ctk.CTkLabel(self.main_area, text=f"Registrar {tipo}", font=self.fuente_titulos, text_color=COLOR_TEXTO).pack(pady=10)


        form_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        form_frame.pack(pady=10)

        entry_monto = ctk.CTkEntry(form_frame, placeholder_text="Monto (COP)", width=250, font=self.fuente_normal)
        entry_monto.pack(pady=5)

        entry_desc = ctk.CTkEntry(form_frame, placeholder_text="Razón / Descripción", width=250, font=self.fuente_normal)
        entry_desc.pack(pady=5)

        def ejecutar_registro():
            monto = entry_monto.get()
            desc = entry_desc.get()
            if not monto or not desc:
                messagebox.showerror("Error", "Rellene todos los campos.")
                return
            try:
                monto_f = float(monto)
           
                if tipo == "Ingreso":
                    self.datos_usuario["billetera_total"] += monto_f
                else:
                    self.datos_usuario["billetera_total"] -= monto_f

            
                self.datos_usuario["transacciones"].append({
                    "tipo": tipo,
                    "monto": monto_f,
                    "descripcion": desc,
                    "fecha": datetime.date.today().strftime("%Y-%m-%d")
                })
                self.guardar_datos()
                messagebox.showinfo("Éxito", f"{tipo} añadido correctamente.")
                self.mostrar_vista("ingresos" if tipo == "Ingreso" else "gastos")
            except ValueError:
                messagebox.showerror("Error", "Monto inválido.")

        ctk.CTkButton(self.main_area, text=f"Añadir {tipo}", fg_color=COLOR_PRIMARIO, text_color="#FFFFFF", font=self.fuente_normal, command=ejecutar_registro).pack(pady=15)

        ctk.CTkLabel(self.main_area, text="Historial Reciente de esta Categoría", font=self.fuente_subtitulos, text_color=COLOR_TEXTO).pack(pady=(20, 5))
        
        frame_historial_interno = ctk.CTkFrame(self.main_area, fg_color="transparent")
        frame_historial_interno.pack(fill="x", padx=40)

        transacciones_filtradas = [t for t in self.datos_usuario.get("transacciones", []) if t["tipo"] == str(tipo)]
        ultimas_dos = transacciones_filtradas[-2:] if len(transacciones_filtradas) >= 2 else transacciones_filtradas
        ultimas_dos.reverse()

        icono_nombre = "trend_up" if tipo == "Ingreso" else "trend_down"
        if ultimas_dos:
            for index, trans in enumerate(ultimas_dos):
                self.crear_fila_movimiento(frame_historial_interno, f"Registro #{index+1}", trans, icono_nombre)
        else:
            ctk.CTkLabel(frame_historial_interno, text=f"No hay {tipo.lower()}s registrados todavía.", font=self.fuente_normal, text_color=COLOR_TEXTO_SECUNDARIO).pack(pady=10)

  
    def render_metas(self):
        img_metas = self.cargar_icono_dinamico("metas_centradas", (65, 65))
        ctk.CTkLabel(self.main_area, image=img_metas, text="").pack(pady=(10, 5))

        ctk.CTkLabel(self.main_area, text="Mis Metas Financieras", font=self.fuente_titulos, text_color=COLOR_TEXTO).pack()

        form_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        form_frame.pack(pady=10)

        entry_meta_nombre = ctk.CTkEntry(form_frame, placeholder_text="Nombre de la meta (Ej: Comprar laptop)", width=240, font=self.fuente_normal)
        entry_meta_nombre.pack(side="left", padx=5)

        entry_meta_monto = ctk.CTkEntry(form_frame, placeholder_text="Monto objetivo", width=140, font=self.fuente_normal)
        entry_meta_monto.pack(side="left", padx=5)

        def registrar_meta():
            nom = entry_meta_nombre.get()
            mon = entry_meta_monto.get()
            if not nom or not mon:
                return
            try:
                self.datos_usuario["metas"].append({
                    "nombre": nom,
                    "monto": float(mon),
                    "completada": False
                })
                self.guardar_datos()
                self.mostrar_vista("metas")
            except ValueError:
                messagebox.showerror("Error", "Monto inválido.")

        ctk.CTkButton(form_frame, text="Añadir Meta", fg_color=COLOR_PRIMARIO, width=100, font=self.fuente_normal, command=registrar_meta).pack(side="left", padx=5)

        ctk.CTkLabel(self.main_area, text="Lista de Metas Activas", font=self.fuente_subtitulos, text_color=COLOR_TEXTO).pack(pady=(15, 5))

        scroll_metas = ctk.CTkScrollableFrame(self.main_area, fg_color="transparent", height=250)
        scroll_metas.pack(fill="x", padx=40)

        metas_lista = self.datos_usuario.get("metas", [])
        metas_activas = [m for m in metas_lista if not m.get("completada", False)]

        if metas_activas:
            for idx, meta in enumerate(metas_lista):
                if meta.get("completada", False): continue
                
                row = ctk.CTkFrame(scroll_metas, fg_color=COLOR_PANELES, height=60, corner_radius=10)
                row.pack(fill="x", pady=5)
                row.pack_propagate(False)

                img_medal = self.cargar_icono_dinamico("medallita", (22, 22))
                ctk.CTkLabel(row, image=img_medal, text="").pack(side="left", padx=15)

                txt_meta = f"{meta['nombre']} — Objetivo: COP {meta['monto']:,.0f}".replace(",", ".")
                ctk.CTkLabel(row, text=txt_meta, font=self.fuente_normal, text_color=COLOR_TEXTO).pack(side="left", padx=10)

                btn_comp = ctk.CTkButton(row, text="Marcar como Completa", fg_color=COLOR_PRIMARIO, text_color="#FFFFFF", font=self.fuente_pequena, width=140, command=lambda i=idx: self.completar_meta(i))
                btn_comp.pack(side="right", padx=15, pady=15)
        else:
            ctk.CTkLabel(scroll_metas, text="No tienes metas activas pendientes.", font=self.fuente_normal, text_color=COLOR_TEXTO_SECUNDARIO).pack(pady=20)

    def completar_meta(self, indice):
        self.datos_usuario["metas"][indice]["completada"] = True
        self.guardar_datos()
        messagebox.showinfo("¡Felicidades!", f"¡Meta '{self.datos_usuario['metas'][indice]['nombre']}' completada con éxito!")
        self.mostrar_vista("metas")

    def render_historial(self):
        img_hist = self.cargar_icono_dinamico("historial_centrado", (65, 65))
        ctk.CTkLabel(self.main_area, image=img_hist, text="").pack(pady=(10, 5))

        ctk.CTkLabel(self.main_area, text="Historial de Movimientos", font=self.fuente_titulos, text_color=COLOR_TEXTO).pack(pady=5)
        ctk.CTkLabel(self.main_area, text="Mostrando las últimas 5 entradas o salidas unificadas", font=self.fuente_pequena, text_color=COLOR_TEXTO_SECUNDARIO).pack(pady=(0, 15))

        scroll_historial = ctk.CTkScrollableFrame(self.main_area, fg_color="transparent", height=380)
        scroll_historial.pack(fill="x", padx=40)

        transacciones = self.datos_usuario.get("transacciones", [])
        ultimas_cinco = transacciones[-5:] if len(transacciones) >= 5 else transacciones
        ultimas_cinco.reverse()

        if ultimas_cinco:
            for idx, trans in enumerate(ultimas_cinco):
                icono_nombre = "trend_up" if trans["tipo"] == "Ingreso" else "trend_down"
                
                row = ctk.CTkFrame(scroll_historial, fg_color=COLOR_PANELES, height=65, corner_radius=10)
                row.pack(fill="x", pady=5)
                row.pack_propagate(False)

                img_ico = self.cargar_icono_dinamico(icono_nombre, (22, 22))
                ctk.CTkLabel(row, image=img_ico, text="").pack(side="left", padx=15)

                info_izq = f"{trans['tipo']} — {trans['fecha']}"
                ctk.CTkLabel(row, text=info_izq, font=self.fuente_normal, text_color=COLOR_TEXTO).pack(side="left", padx=5)

                frame_derecho = ctk.CTkFrame(row, fg_color="transparent")
                frame_derecho.pack(side="right", padx=20, fill="y")

                monto_str = f"COP {trans['monto']:,.0f}".replace(",", ".")
                ctk.CTkLabel(frame_derecho, text=monto_str, font=self.fuente_normal, text_color=COLOR_TEXTO, anchor="e").pack(side="top", pady=(10,0))
                ctk.CTkLabel(frame_derecho, text=trans['descripcion'], font=self.fuente_pequena, text_color=COLOR_TEXTO_SECUNDARIO, anchor="e").pack(side="top")
        else:
            ctk.CTkLabel(scroll_historial, text="No hay registros globales guardados en el historial.", font=self.fuente_normal, text_color=COLOR_TEXTO_SECUNDARIO).pack(pady=40)


if __name__ == "__main__":
    app = FinanzasApp()
    app.mainloop()