###############################################
# IMPORTACIÓN DE LIBRERÍAS
###############################################
#from funciones import start, iniciar_bot, generar_qr, guardar_ultimo_codigo, incrementar_codigo, obtener_ultimo_codigo, procesar_qr
from funciones.generarQR import generar_qr
from funciones.guardarultimo_cod import guardar_ultimo_codigo
from funciones.incrementar_cod import incrementar_codigo
from funciones.obtenerultimo_cod import obtener_ultimo_codigo
from funciones.procesarQR import procesar_qr
from funciones.iniciarBOT import iniciar_bot
from funciones.iniciarTLG import start

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime as dt
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.orm import declarative_base
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from pathlib import Path
from multiprocessing import Process
from PIL import Image, ImageTk
import os
import threading
import asyncio

###############################################
# CONFIGURACIÓN INICIAL Y BASE DE DATOS
###############################################
Base = declarative_base()                               # Se crea una clase base para definir modelos (tablas) en SQLAlchemy.
engine = create_engine('sqlite:///hospital.db')         # Se crea un motor de conexión a la base de datos.
Session = scoped_session(sessionmaker(bind=engine))     # Se prepara una clase de sesión que maneja las conexiones a la base de datos.
session = Session()                                     # Se crea una instancia de sesión.

class Area(Base):                                                           # Se define una tabla llamada "Area" 
    __tablename__ = 'AREAS'                                                 # Se especifica el nombre real de la tabla en la base de datos
    id = Column(Integer, primary_key=True, autoincrement=True)              # Se crea una columna llamada id
    nombre_area = Column(String(50), nullable=False, unique=True)           # Se crea una columna de texto llamada nombre_area
    equipos = relationship("InventarioEquipo", back_populates="area_rel")   # Crea una relación con la tabla InventarioEquipo, para acceder desde un Area a todos los equipos relacionados con esa área, la relación es bidireccional: en la clase InventarioEquipo debe haber un atributo llamado area_rel que apunte de vuelta al área.

class Equipo(Base):     # Tabla equipos, creacion de columnas
    __tablename__ = 'EQUIPOS'
    nombre_equipo = Column(String(50), primary_key=True)
    inventarios = relationship("InventarioEquipo", back_populates="equipo_rel") # relacion con inventario

class InventarioEquipo(Base):       # Tablas inventario, creacion de columnas
    __tablename__ = 'INVENTARIO_EQUIPOS'
    area_id = Column(Integer, ForeignKey('AREAS.id'), primary_key=True) # clave primaria, foranea para la relacion con areas
    nombre_equipo = Column(String(50), ForeignKey('EQUIPOS.nombre_equipo'), primary_key=True) # clave primaria, foranea para la relacion con equipos
    N_item = Column(Integer, primary_key=True) # clave primaria
    codigo = Column(String(20), nullable=False, unique=True) # clave unica
    nombre_estandarizado = Column(String(50), nullable=False)
    marca = Column(String(50), nullable=False)
    modelo = Column(String(50), nullable=False)
    numero_serie = Column(String(50), nullable=False, unique=True) # clave unica
    estado = Column(String(20), nullable=False)
    area_rel = relationship("Area", back_populates="equipos")   # relacion con area
    equipo_rel = relationship("Equipo", back_populates="inventarios") # relacion con equipo

class Prestamo(Base):       # Tabla prestamo, creacion de columnas
    __tablename__ = 'PRESTAMOS'
    id = Column(Integer, primary_key=True, autoincrement=True) # clave primaria, autoincremental
    area_origen = Column(String(50), nullable=False)
    equipo = Column(String(50), nullable=False)
    area_destino = Column(String(50), nullable=False)
    solicitante = Column(String(50), nullable=False)
    fecha_solicitud = Column(DateTime, default=dt.now)
    qr_equipo = Column(String(50), nullable=False)
    estado = Column(String(20), default='Pendiente')  # Pendiente, Aprobado, Rechazado, Devuelto
    usuario_id = Column(Integer)
    username = Column(String(50))
    foto_id = Column(String(100))

class OrdenTrabajo(Base):   # Tabla ordenes_trabajo, creacion de columnas
    __tablename__ = 'ORDENES_TRABAJO'
    id = Column(Integer, primary_key=True, autoincrement=True) # clave primaria, autoincremental
    tipo = Column(String(50), nullable=False)
    area = Column(String(50), nullable=False)
    urgencia = Column(String(20), nullable=False)
    descripcion = Column(String(200), nullable=False)
    fecha_solicitud = Column(DateTime, default=dt.now)
    qr_equipo = Column(String(50), nullable=False)
    estado = Column(String(20), default='Pendiente')  # Pendiente, En proceso, Completada
    usuario_id = Column(Integer)
    username = Column(String(50))
    foto_id = Column(String(100))

Base.metadata.create_all(engine)    # Crea las tablas en la base de datos

###############################################
# CONFIGURACIÓN DE TELEGRAM
###############################################
TOKEN = '7854191859:AAEFK--ZL3_uA6i49h9nfHQcG-LEHJ-gAuY'        # Token unico del bot de telegram
datos_usuario = {}                                              # lista donde se guardaran los datos de los usuarios

# Variables para el manejo de conversationhandler
DETALLES_PRESTAMO = 0
FOTO_PRESTAMO = 1    
DETALLES_ORDEN = 2
FOTO_ORDEN = 3

logging.basicConfig(level=logging.INFO)         # Se activa el sistema de registros (logs) y muestra mensajes informativos.

###############################################
# FUNCIONES PARA EL BOT DE TELEGRAM
###############################################
async def iniciar_prestamo(update: Update, context: ContextTypes.DEFAULT_TYPE):     # El inicio del proceso del prestamo, primero se envia un mensaje de instruccion donde se piden los datos
    await update.message.reply_text(
        "Por favor, escribe el detalle del préstamo con el formato:\n"
        "Área del equipo-Equipo-Área de destino-NombreApellido\n\n"
        "Por ejemplo:\nEnfermería-Monitor fetal-Consultorio 2-JuanPerez"
    )
    return DETALLES_PRESTAMO    # Devuelve un 0, para el proceso de conversation handler

async def recibir_detalles_prestamo(update: Update, context: ContextTypes.DEFAULT_TYPE):    # Recibe los datos del prestamo, 
    user = update.effective_user
    datos = update.message.text.split('-') # se accede al texto recibido, y se divide el substrings con el separador '-' con el comando .split()
    if len(datos) != 4:     #si no se ingresaron los 4 datos requeridos, se vuelve a pedir los datos 
        await update.message.reply_text("Formato incorrecto. Usa: Área-Equipo-ÁreaDestino-Nombre")
        return DETALLES_PRESTAMO    # Devuelve un 0 para el proceso de conversation handler, es decir, vuelve a esperar los datos
    
    area_origen, equipo, area_destino, solicitante = [d.strip() for d in datos] # el comando .strip() elimina espacios en blanco al inicio y al final, para cada elemento en d se aplica
    datos_usuario[user.id] = {      #se rellena la lista de datos de usuario, con el identificador id del usuario de telegram
        "username": user.username,
        "area_origen": area_origen,
        "equipo": equipo,
        "area_destino": area_destino,
        "solicitante": solicitante,
        "fecha": dt.now(),  #fecha y hora actual
        "tipo": "PRESTAMO"
    }
    await update.message.reply_text("Por favor, envía una foto de la etiqueta QR en el equipo.")    #Mensaje de comienzo del siguiente proceso
    return FOTO_PRESTAMO #Devuelve un 1 para el proceso de conversation handler

async def recibir_foto_prestamo(update: Update, context: ContextTypes.DEFAULT_TYPE):    #Recibe la foto del qr y decodifica su informacion
    user_id = update.effective_user.id
    user_data = datos_usuario.get(user_id, {})  # Obtiene los datos para el usuario actual
    
    if not user_data:   # si no hay datos en dicho usuario, se envia un mensaje de error
        await update.message.reply_text("Error: No se encontraron datos. Por favor inicia nuevamente con /prestamo")
        return ConversationHandler.END # se termina el conversation handler para el usuario, es decir se vuelve a antes del inicio

    if not update.message.photo:    # si no se responde con una foto, se envia un mensaje de error
        await update.message.reply_text("Por favor, envía una foto válida del QR.")
        return FOTO_PRESTAMO    # se devuelve un 1 para el conversation handler

    foto = update.message.photo[-1]     # se obtiene la foto con la mayor calidad (parametro -1), enviada por el usuario
    file = await context.bot.get_file(foto.file_id) # obtiene el objeto file de telegram utilizando la id del archivo.
    ruta_temporal = f"temp_{user_id}.jpg"   # genera una ruta, con nombre unico para el archivo temporal
    await file.download_to_drive(ruta_temporal) # se descarga la imagen del qr obtenida desde los servidores de telegram
    datos_qr = procesar_qr(ruta_temporal)   # se llama la funcion para procesar el qr, y obtener su contenido, en base a la ruta_temporal
    Path(ruta_temporal).unlink() # elimina el archivo temporal del sistema con el comando path().unlink()

    if "QR no detectado" in datos_qr: # si se envia un error desde la funcion de procesamiento de qr, se 
        await update.message.reply_text("No se pudo detectar el código QR. Por favor, vuelve a enviar la foto del QR o /cancelar.")
        return FOTO_PRESTAMO    #Devuelve un 1 para el proceso de conversation handler

    # Registrar en base de datos
    nuevo_prestamo = Prestamo(      # se crea una instancia llamada prestamo, con los datos que se recolectaron durante el proceso del prestamo
        area_origen=user_data['area_origen'],
        equipo=user_data['equipo'],
        area_destino=user_data['area_destino'],
        solicitante=user_data['solicitante'],
        fecha_solicitud=user_data['fecha'],
        qr_equipo=datos_qr,
        usuario_id=user_id,
        username=user_data['username'],
        foto_id=foto.file_id
    )
    
    session.add(nuevo_prestamo)     # agrega el objeto nuevo prestamo a la base de datos
    session.commit()                # confirma y ejecuta todas las operaciones pendientes
    
    await update.message.reply_text(   # se envia un texto de confirmacion del ingreso de los datos a la bd, y se esperará su confirmación desde la interfaz central
        "Solicitud de préstamo registrada.\nEspera la aprobación de un administrador.",
#        reply_markup=ReplyKeyboardRemove()
    )
    datos_usuario.pop(user_id, None)
    return ConversationHandler.END      # termina el conversation handler con el usuario


# se repite el proceso con el comando orden_trabajo
async def iniciar_orden(update: Update, context: ContextTypes.DEFAULT_TYPE):        
    await update.message.reply_text(
        "Por favor, escribe los detalles de la orden con el formato:\n"
        "Tipo de trabajo-Área-Urgencia-Descripción\n\n"
        "Por ejemplo:\nMantenimiento-Enfermería-Alta-Reparación monitor fetal"
    )
    return DETALLES_ORDEN # devuelve esta un 2 para el conversation handler

async def recibir_detalles_orden(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    datos = update.message.text.split('-')
    if len(datos) != 4:
        await update.message.reply_text("Formato incorrecto. Usa: Tipo-Área-Urgencia-Descripción")
        return DETALLES_ORDEN   # devuelve esta un 2 para el conversation handler
    
    tipo, area, urgencia, descripcion = [d.strip() for d in datos]
    
    datos_usuario[user.id] = {
        "username": user.username,
        "tipo": tipo,
        "area": area,
        "urgencia": urgencia,
        "descripcion": descripcion,
        "fecha": dt.now(),
        "tipo_solicitud": "ORDEN_TRABAJO"
    }
    
    await update.message.reply_text("Por favor, envía una foto de la etiqueta QR del equipo relacionado.")
    return FOTO_ORDEN   #Devuelve un 3 para el proceso de conversation handler

async def recibir_foto_orden(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = datos_usuario.get(user_id, {})
    
    if not user_data:
        await update.message.reply_text("Error: No se encontraron datos. Por favor inicia nuevamente con /ordentrabajo")
        return ConversationHandler.END

    if not update.message.photo:
        await update.message.reply_text("Por favor, envía una foto válida del QR.")
        return FOTO_ORDEN

    foto = update.message.photo[-1]
    file = await context.bot.get_file(foto.file_id)
    ruta_temporal = f"temp_{user_id}_orden.jpg"
    await file.download_to_drive(ruta_temporal)
    datos_qr = procesar_qr(ruta_temporal)
    Path(ruta_temporal).unlink()

    if "QR no detectado" in datos_qr:
        await update.message.reply_text("No se pudo detectar el código QR. Por favor, vuelve a enviar la foto del QR o /cancelar.")
        return FOTO_ORDEN   #Devuelve un 3 para el proceso de conversation handler

    # Registrar en base de datos
    nueva_orden = OrdenTrabajo(
        tipo=user_data['tipo'],
        area=user_data['area'],
        urgencia=user_data['urgencia'],
        descripcion=user_data['descripcion'],
        fecha_solicitud=user_data['fecha'],
        qr_equipo=datos_qr,
        usuario_id=user_id,
        username=user_data['username'],
        foto_id=foto.file_id
    )
    
    session.add(nueva_orden)
    session.commit()
    await update.message.reply_text(
        "Orden de trabajo registrada.\nUn técnico revisará tu solicitud pronto.",
    )
    datos_usuario.pop(user_id, None)
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):     # comando para cancelar el proceso en cualquier momento
    user_id = update.effective_user.id  # se obtiene el id de telegram del usuario
    datos_usuario.pop(user_id, None)    # elimina la entrada correspondiente a user_id del diccionario datos_usuario y devuelve el valor eliminado
    await update.message.reply_text(    # se envia un mensaje de informacion
        "Operación cancelada.",
    )
    return ConversationHandler.END  # termina el conversation handler

###############################################
# INTERFAZ GRÁFICA DE ESCRITORIO
###############################################
letra = "Arial"

##############################
# 1. CREACIÓN DE LA APLICACIÓN

class App(tk.Tk):               # Define la clase principal de la aplicación que hereda de tk.Tk (ventana principal)
    def __init__(self):
        super().__init__()  # Llama al constructor de la clase padre (tk.Tk)

        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)   # Configura el comportamiento al cerrar la ventana
        self.title("PROGRAMA DE GESTIÓN DE INVENTARIO, ORDEN DE TRABAJO Y PRÉSTAMOS")   # Título de la ventana
        self.geometry("1000x800")   # Tamaño inicial de la ventana (ancho x alto)
        self.config(bg="#F4F4F4")   # Color de fondo (gris claro)

        container = tk.Frame(self)  # Crea un frame contenedor
        container.pack(side="top", fill="both", expand=True)    # Empaqueta el contenedor para que ocupe todo el espacio
        container.grid_rowconfigure(0, weight=1)                # Hace que la fila 0 se expanda
        container.grid_columnconfigure(0, weight=1)             # Hace que la columna 0 se expanda
        self.frames = {}    # Diccionario para almacenar todos los frames (pantallas) de la aplicación

        for F in (Frame_Principal, Frame_Areas, Frame_Registro_Area, Frame_Inventario_General, Frame_Registro_Nuevo,    # Crea instancias de cada frame y las almacena en el diccionario
                  Frame_Equipo_Modificar, Frame_Prestamos, Frame_Ordenes):
            frame = F(container, self)      # Crea una instancia del frame
            self.frames[F] = frame          # Almacena el frame en el diccionario
            frame.grid(row=0, column=0, sticky="nsew")      # Coloca todos los frames en la misma posición

        self.show_frame(Frame_Principal)    # Muestra el frame principal al iniciar
        self.bot_process = None     # Variable para almacenar el proceso del bot de Telegram

    def show_frame(self, cont):
        frame = self.frames[cont]   # Obtiene el frame solicitado del diccionario
        if hasattr(frame, 'actualizar_areas'): frame.actualizar_areas()     # Comprueba si el frame tiene este método y actualiza la lista de áreas
        if hasattr(frame, 'actualizar_equipos'): frame.actualizar_equipos() # Comprueba si el frame tiene este método y actualiza la lista de equipos
        if hasattr(frame, 'actualizar_prestamos'): frame.actualizar_prestamos() # Comprueba si el frame tiene este método y actualiza la lista de préstamos
        if hasattr(frame, 'actualizar_ordenes'): frame.actualizar_ordenes() # Comprueba si el frame tiene este método y actualiza la lista de órdenes de trabajo
        frame.tkraise() # Trae el frame al frente (lo hace visible)
        
    def set_bot_process(self, process):
        self.bot_process = process  # Almacena la referencia al proceso del bot de Telegram
        
    def cerrar_aplicacion(self):    #Maneja el cierre limpio de toda la aplicación
        try:
            try:
                session.close() # Cierra la sesión de SQLAlchemy
                engine.dispose()    # Libera los recursos de conexión de la base de datos
            except Exception as db_error:
                print(f"Error al cerrar recursos de DB: {db_error}")

            if hasattr(self, 'bot_process') and self.bot_process:   # Detener el bot de Telegram si está en ejecución
                try:
                    self.bot_process.terminate()    # Solicita terminación del proceso
                    self.bot_process.join(timeout=2)    # Espera hasta 2 segundos
                    if self.bot_process.is_alive(): # Si aún sigue vivo después de 2 segundos
                        self.bot_process.kill() # Fuerza la terminación
                except Exception as bot_error:
                    print(f"Error al cerrar el bot: {bot_error}")

            self.destroy()  # Cierra la ventana principal de Tkinter
            
        except Exception as e:
            print(f"Error al cerrar la aplicación: {e}")
        finally:
            os._exit(0) # Termina el proceso completamente (código de salida 0 = éxito)

####################
# 2. FRAME PRINCIPAL

class Frame_Principal(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#F4F4F4")   # Inicializa el frame con el elemento padre y color de fondo

        title_frame = tk.Frame(self, bg="#F4F4F4")      # Crea un frame para el título
        title_frame.pack(pady=(40, 30), fill="x")       # Empaqueta el frame del título con márgenes verticales

        tk.Label(title_frame, text="SISTEMA DE GESTIÓN DE EQUIPOS MÉDICOS", font=("Arial", 24, "bold"), bg="#F4F4F4", fg="#012E40").pack(pady=(0, 10))  # Crea y empaqueta la etiqueta del título principal
        tk.Label(title_frame, text="Administración de inventario, ordenes de trabajo y préstamos", font=("Arial", 14), bg="#F4F4F4", fg="#555555").pack()   # Crea y empaqueta la etiqueta del subtítulo

        cards_frame = tk.Frame(self, bg="#F4F4F4")  # Crea un frame para contener las tarjetas de opciones
        cards_frame.pack(pady=20, padx=40, fill="both", expand=True)    # Empaqueta el frame de tarjetas con márgenes y expansión

        # Tarjeta Inventario
        inventario_card = tk.Frame(cards_frame, bg="white", bd=2, relief="groove", highlightbackground="#E0E0E0")   # Crea el frame para la tarjeta de inventario
        inventario_card.pack(fill="x", pady=15, padx=20, ipady=15, ipadx=10)    # Empaqueta la tarjeta con márgenes y relleno interno
        tk.Button(  # Botón para salir de la aplicación (ERROR: falta especificar el padre)
            
            text="SALIR",
            font=("Arial", 14, "bold"),
            bg="#1EC2BA",
            fg="white",
            command=controller.cerrar_aplicacion  
        ).pack(pady=(5, 10), padx=20, side="right")

        tk.Button(  # Botón para acceder al inventario
            inventario_card,
            text="INVENTARIO",
            font=("Arial", 14, "bold"),
            bg="#012E40",
            fg="white",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=lambda: controller.show_frame(Frame_Areas)
        ).pack(pady=(5, 10), padx=20, fill="x")

        tk.Label(   # Etiqueta descriptiva para la tarjeta de inventario
            inventario_card,
            text="Gestionar el inventario.",
            font=("Arial", 11),
            bg="white",
            fg="#444444",
            wraplength=600,
            justify="left"
        ).pack(pady=(0, 10), padx=20, fill="x")

        # Se repite para la Tarjeta Orden de Trabajo
        ficha_card = tk.Frame(cards_frame, bg="white", bd=2, relief="groove", highlightbackground="#E0E0E0")
        ficha_card.pack(fill="x", pady=15, padx=20, ipady=15, ipadx=10)
        tk.Button(
            ficha_card,
            text="ORDENES DE TRABAJO",
            font=("Arial", 14, "bold"),
            bg="#025159",
            fg="white",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=lambda: controller.show_frame(Frame_Ordenes)
        ).pack(pady=(5, 10), padx=20, fill="x")
        tk.Label(
            ficha_card,
            text="Gestionar ordenes de trabajo para equipos.",
            font=("Arial", 11),
            bg="white",
            fg="#444444",
            wraplength=600,
            justify="left"
        ).pack(pady=(0, 10), padx=20, fill="x")

        # Se repite para la Tarjeta Préstamos
        prestamo_card = tk.Frame(cards_frame, bg="white", bd=2, relief="groove", highlightbackground="#E0E0E0")
        prestamo_card.pack(fill="x", pady=15, padx=20, ipady=15, ipadx=10)
        tk.Button(
            prestamo_card,
            text="PRÉSTAMOS",
            font=("Arial", 14, "bold"),
            bg="#038C8C",
            fg="white",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=lambda: controller.show_frame(Frame_Prestamos)
        ).pack(pady=(5, 10), padx=20, fill="x")
        tk.Label(
            prestamo_card,
            text="Gestionar préstamos de equipos.",
            font=("Arial", 11),
            bg="white",
            fg="#444444",
            wraplength=600,
            justify="left"
        ).pack(pady=(0, 10), padx=20, fill="x")

        # Pie de frame
        footer_frame = tk.Frame(self, bg="#F4F4F4") # Crea un frame para el pie de página
        footer_frame.pack(side="bottom", fill="x", pady=20) # Empaqueta en la parte inferior con margen
        tk.Label(footer_frame, text="2025 - Sistema de Gestión de Equipos Médicos", font=("Arial", 9), bg="#F4F4F4", fg="#777777").pack()   # Nota de pie

################
# 3. FRAME ÁREAS

class Frame_Areas(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#F4F4F4")
        self.controller = controller
        self.area_seleccionada = None
        
        # Título
        tk.Label(
            self, 
            text="AREAS",
            font=(letra, 20, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).pack(pady=30)
        
        # Frame para la lista de áreas
        self.frame_areas = tk.Frame(self, bg="#F4F4F4")
        self.frame_areas.pack(fill="both", expand=True, padx=20)
        
        # Frame para botones globales
        frame_botones = tk.Frame(self, bg="#F4F4F4")
        frame_botones.pack(fill="x", padx=20, pady=10)
        
        # Botón Volver
        tk.Button(
            frame_botones, 
            text="Volver",
            font=(letra, 12),
            bg="#012E40",
            fg="white",
            command=lambda: controller.show_frame(Frame_Principal)
        ).pack(side="left")
        
        # Botón Agregar Área
        tk.Button(
            frame_botones, 
            text="Agregar Área",
            font=(letra, 12),
            bg="#012E40",
            fg="white",
            command=lambda: controller.show_frame(Frame_Registro_Area)
        ).pack(side="left", padx=10)
        
        # Botón Eliminar (global)
        self.btn_eliminar = tk.Button(
            frame_botones, 
            text="Eliminar Área",
            font=(letra, 12),
            bg="#FF0000",
            fg="white",
            state="disabled",
            command=self.eliminar_area
        )
        self.btn_eliminar.pack(side="right")
        
        # Botón Ingresar (global)
        self.btn_ingresar = tk.Button(
            frame_botones, 
            text="Ingresar al Área",
            font=(letra, 12),
            bg="#038C8C",
            fg="white",
            state="disabled",
            command=self.ingresar_area
        )
        self.btn_ingresar.pack(side="right", padx=10)
        self.actualizar_areas()

    def actualizar_areas(self):
        for widget in self.frame_areas.winfo_children():
            widget.destroy()
            
        areas = session.query(Area).order_by(Area.nombre_area).all()
        
        for area in areas:
            btn = tk.Button(
                self.frame_areas,
                text=area.nombre_area,
                font=(letra, 16),
                bg="#012E40",
                fg="white",
                command=lambda a=area: self.seleccionar_area(a)
            )
            btn.pack(fill="x", pady=5, padx=20)

    def seleccionar_area(self, area):
        self.area_seleccionada = area
        
        # Resaltar botón seleccionado
        for widget in self.frame_areas.winfo_children():
            if isinstance(widget, tk.Button):
                if widget['text'] == area.nombre_area:
                    widget.config(bg="#025E73")
                else:
                    widget.config(bg="#012E40")
        
        # Activar botones de acción
        self.btn_eliminar.config(state="normal")
        self.btn_ingresar.config(state="normal")

    def ingresar_area(self):
        if self.area_seleccionada:
            self.controller.frames[Frame_Inventario_General].set_area(self.area_seleccionada.id)
            self.controller.show_frame(Frame_Inventario_General)
            nombre_area_seleccionada = self.area_seleccionada.nombre_area

    def eliminar_area(self):
        if not self.area_seleccionada:
            return
            
        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar el área '{self.area_seleccionada.nombre_area}'?\n"
            "¡Se borrarán todos sus equipos!"
        )
        
        if confirmacion:
            try:
                # Eliminar equipos primero
                session.query(InventarioEquipo).filter_by(area_id=self.area_seleccionada.id).delete()
                # Luego eliminar el área
                session.delete(self.area_seleccionada)
                session.commit()
                
                messagebox.showinfo("Éxito", "Área eliminada")
                self.area_seleccionada = None
                self.btn_eliminar.config(state="disabled")
                self.btn_ingresar.config(state="disabled")
                self.actualizar_areas()
                
            except Exception as e:
                session.rollback()
                messagebox.showerror("Error", f"No se pudo eliminar: {str(e)}")

###########################
# 4. FRAME REGISTRO DE AREA

class Frame_Registro_Area(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#F4F4F4")
        
        self.controller = controller
        
        tk.Label(
            self, 
            text="AREA NUEVA",
            font=(letra, 24, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).place(
            relx=0.28,
            rely=0.02,
            relheight=0.07,
            relwidth=0.4,
            anchor="w"
        )
        
        tk.Label(
            self, 
            text="NOMBRE DEL AREA",
            font=(letra, 20, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).place(
            relx=0,
            rely=0.45,
            relheight=0.07,
            relwidth=0.4,
            anchor="w")
        self.nombre_entry = tk.Entry(
            self,
            font=(letra, 15),
            bg="#012E40",
            fg="white"
        )
        self.nombre_entry.place(
            relx=0.7,
            rely=0.45,
            relheight=0.07,
            relwidth=0.4,
            anchor="center"
        )
        
        tk.Button(
            self, 
            text="VOLVER AL ANTERIOR",
            font=(letra, 12),
            bg="#012E40",
            fg="white",
            command=lambda: controller.show_frame(Frame_Areas)
        ).place(
            relx=0.15,
            rely=0.97,
            relheight=0.05,
            relwidth=0.24,
            anchor="center"
        )
        
        tk.Button(
            self, 
            text="AGREGAR",
            font=(letra, 12),
            bg="#012E40",
            fg="white",
            command=self.agregar_area
        ).place(
            relx=0.5,
            rely=0.97,
            relheight=0.05,
            relwidth=0.24,
            anchor="center"
        )
    
    def agregar_area(self):
        nombre = self.nombre_entry.get().strip()
        
        if not nombre:
            messagebox.showerror("Error", "El nombre del área no puede estar vacío")
            return
            
        try:
            nueva_area = Area(nombre_area=nombre)
            session.add(nueva_area)
            session.commit()
            
            messagebox.showinfo("Éxito", "Área agregada correctamente")
            self.controller.frames[Frame_Areas].actualizar_areas()
            self.controller.show_frame(Frame_Areas)
            
        except Exception as e:
            session.rollback()
            messagebox.showerror("Error", f"No se pudo agregar el área: {str(e)}")

#############################
# 5. FRAME INVENTARIO GENERAL

class Frame_Inventario_General(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#F4F4F4")
        self.controller = controller
        self.area_id = None
        
        tk.Label(self, text="INVENTARIO GENERAL", font=(letra, 20, "bold"), bg="#F4F4F4", fg="#012E40").pack(pady=20)
        self.frame_lista = tk.Frame(self, bg="#F4F4F4")
        self.frame_lista.pack(fill="both", expand=True, padx=20, pady=10)

        frame_botones = tk.Frame(self, bg="#F4F4F4")
        frame_botones.pack(fill="x", padx=20, pady=10)

        tk.Button(frame_botones,
            text="Volver",
            font=(letra,12),
            bg="#012E40",
            fg="white",
            command=lambda: controller.show_frame(Frame_Areas)
        ).pack(side="left")
        tk.Button(
            frame_botones,
            text="Registrar Nuevo",
            font=(letra,12),
            bg="#012E40",
            fg="white",
            command=self.ir_a_registro_nuevo
        ).pack(side="left", padx=5)

        tk.Button(
            frame_botones,
            text="Modificar",
            font=(letra,12),
            bg="#012E40",
            fg="white",
            command=lambda: self.modificar_equipo()
        ).pack(side="left", padx=5)


        tk.Button(
            frame_botones,
            text="Mostrar QR",
            font=(letra,12),
            bg="#012E40",
            fg="white",
            command=lambda: self.mostrar_qr()
        ).pack(side="left", padx=5)
    def ir_a_registro_nuevo(self):
        self.controller.frames[Frame_Registro_Nuevo].set_area_preseleccionada(self.area_id)
        self.controller.show_frame(Frame_Registro_Nuevo)

    def set_area(self, area_id):
        self.area_id = area_id
        self.actualizar_equipos()

    def actualizar_equipos(self):
        for widget in self.frame_lista.winfo_children():
            widget.destroy()
        columnas = ("#1","#2","#3","#4","#5","#6","#7","#8")
        tree = ttk.Treeview(self.frame_lista, columns=columnas, show="headings")
        tree.heading("#1", text="Area ID")
        tree.heading("#2", text="N_Item")
        tree.heading("#3", text="Código")
        tree.heading("#4", text="Nombre")
        tree.heading("#5", text="Marca")
        tree.heading("#6", text="Modelo")
        tree.heading("#7", text="N° Serie")
        tree.heading("#8", text="Estado")
        tree.column("#1", width=60, anchor="center")

        for i in range(2,9):
            tree.column(f"#{i}", width=100, anchor="w")

        equipos = session.query(InventarioEquipo).filter_by(area_id=self.area_id).all()

        for e in equipos:
            tree.insert("", "end", values=(e.area_id, e.N_item, e.codigo, e.nombre_estandarizado, e.marca, e.modelo, e.numero_serie, e.estado))

        scrollbar = ttk.Scrollbar(self.frame_lista, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree = tree

    def modificar_equipo(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Seleccion", "Selecciona un equipo.")
            return
        item = self.tree.item(seleccion[0])
        area_id, n_item, codigo, nombre, marca, modelo, serie, estado = item['values']
        equipo = session.query(InventarioEquipo).filter_by(area_id=area_id, N_item=n_item).first()
        if equipo:
            self.controller.frames[Frame_Equipo_Modificar].cargar_equipo(equipo)
            self.controller.show_frame(Frame_Equipo_Modificar)

    def mostrar_qr(self):
        try:
            seleccion = self.tree.selection()
            item = self.tree.item(seleccion[0])
            area_id, n_item, codigo, nombre, marca, modelo, serie, estado = item['values']
            nombre_archivo = f"{codigo}.png"

            # Se crea una nueva ventana
            ventana_qr = tk.Toplevel(self)
            ventana_qr.title("Código QR")
            ventana_qr.configure(bg="#F4F4F4")

            # Se carga imagen con PIL
            imagen = Image.open(nombre_archivo)
            imagen = imagen.resize((300, 300), Image.Resampling.LANCZOS)  # Escalar si es necesario
            imagen_tk = ImageTk.PhotoImage(imagen)

            # Se muestra la imagen en un Label
            etiqueta = tk.Label(ventana_qr, image=imagen_tk, bg="#F4F4F4")
            etiqueta.image = imagen_tk  # ← mantener referencia para evitar que se borre
            etiqueta.pack(padx=20, pady=20)

        except FileNotFoundError:
            print("Error: No se encontró la imagen")
        except Exception as e:
            print(f"Error al mostrar QR: {e}")


#########################
# 6. FRAME REGISTRO NUEVO

class Frame_Registro_Nuevo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#F4F4F4")
        self.controller = controller
        self.area_id_preseleccionada = None
        self.area_nombre_preseleccionado = ""
        self.label_area_dinamica = None

        tk.Label(self, text="EQUIPO NUEVO", font=(letra, 24, "bold"), bg="#F4F4F4", fg="#012E40").place(relx=0.3, rely=0.02)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TCombobox',
            fieldbackground='#012E40',
            background='#012E40',
            foreground='white',
            font=(letra, 15),
            selectbackground='#025E73',
            selectforeground='white'
        )

        # Área
        tk.Label(self, text="ÁREA", font=(letra, 20, "bold"), bg="#F4F4F4", fg="#012E40").place(relx=0.20, rely=0.15)
        self.label_area_dinamica = tk.Label(self, text="", font=(letra, 15), bg="#F4F4F4", fg="#012E40")
        self.label_area_dinamica.place(relx=0.35, rely=0.15)

        self.entries = {}

        # N ITEM como Label
        tk.Label(self, text="N ITEM", font=(letra, 20, "bold"), bg="#F4F4F4", fg="#012E40").place(relx=0.20, rely=0.25)
        self.label_n_item = tk.Label(self, text="", font=(letra, 15), bg="#F4F4F4", fg="#012E40", anchor="w")
        self.label_n_item.place(relx=0.35, rely=0.25, relheight=0.07, relwidth=0.4)

        # Otros campos como Entry
        campos = [("NOMBRE", 0.35), ("MARCA", 0.45), ("MODELO", 0.55), ("SERIE", 0.65)]
        for label, ypos in campos:
            tk.Label(self, text=label, font=(letra, 20, "bold"), bg="#F4F4F4", fg="#012E40").place(relx=0.20, rely=ypos)
            entry = tk.Entry(self, font=(letra, 15), bg="#012E40", fg="white")
            entry.place(relx=0.35, rely=ypos, relheight=0.07, relwidth=0.4)
            self.entries[label] = entry

        # Estado
        tk.Label(self, text="ESTADO", font=(letra, 20, "bold"), bg="#F4F4F4", fg="#012E40").place(relx=0.20, rely=0.75)
        self.estado_combobox = ttk.Combobox(self, font=(letra, 15), values=["Nuevo", "Usado"], state="readonly", style='TCombobox')
        self.estado_combobox.place(relx=0.35, rely=0.75, relheight=0.07, relwidth=0.4)

        # Botones
        tk.Button(self, text="VOLVER", font=(letra, 12), bg="#012E40", fg="white",
                  command=lambda: controller.show_frame(Frame_Inventario_General)).place(relx=0.25, rely=0.90, relheight=0.05, relwidth=0.24)
        tk.Button(self, text="GUARDAR", font=(letra, 12), bg="#038C8C", fg="white",
                  command=self.guardar_equipo).place(relx=0.5, rely=0.9, relheight=0.05, relwidth=0.24)

    def set_area_preseleccionada(self, area_id):
        self.area_id_preseleccionada = area_id
        area = session.query(Area).filter_by(id=area_id).first()
        if area:
            self.area_nombre_preseleccionado = area.nombre_area
            self.label_area_dinamica.config(text=self.area_nombre_preseleccionado)
            siguiente_n_item = self.obtener_siguiente_n_item()
            self.label_n_item.config(text=str(siguiente_n_item))
        else:
            self.area_nombre_preseleccionado = ""
            self.label_area_dinamica.config(text="")
            self.label_n_item.config(text="")

    def limpiar_campos(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.estado_combobox.set("")

    def obtener_siguiente_n_item(self):
        if self.area_id_preseleccionada is None:
            return 1
        ultimo_item = (
            session.query(InventarioEquipo)
            .filter_by(area_id=self.area_id_preseleccionada)
            .order_by(InventarioEquipo.N_item.desc())
            .first()
        )
        return (ultimo_item.N_item + 1) if ultimo_item else 1

    def guardar_equipo(self):
        area_nombre = self.area_nombre_preseleccionado
        n_item = self.label_n_item.cget("text")
        nombre = self.entries["NOMBRE"].get()
        marca = self.entries["MARCA"].get()
        modelo = self.entries["MODELO"].get()
        serie = self.entries["SERIE"].get()
        estado = self.estado_combobox.get()

        if not all([area_nombre, n_item, nombre, marca, modelo, serie, estado]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        area = session.query(Area).filter_by(nombre_area=area_nombre).first()
        if not area:
            messagebox.showerror("Error", "Área no encontrada")
            return

        # Verificar si ya existe el número de serie
        serie_existente = session.query(InventarioEquipo).filter_by(numero_serie=serie).first()
        if serie_existente:
            messagebox.showerror("Error", "Ya existe un equipo con ese número de serie")
            return

        # Código QR
        ultimo = obtener_ultimo_codigo()
        nuevo_codigo = incrementar_codigo(ultimo)
        nombre_qr = f"{nuevo_codigo}.png"
        generar_qr(nuevo_codigo, nombre_qr)
        guardar_ultimo_codigo(nuevo_codigo)
        codigo = nuevo_codigo

        equipo_existente = session.query(Equipo).filter_by(nombre_equipo=nombre).first()
        if not equipo_existente:
            equipo_existente = Equipo(nombre_equipo=nombre)
            session.add(equipo_existente)
            session.commit()

        nuevo_equipo = InventarioEquipo(
            area_id=area.id, nombre_equipo=nombre, N_item=int(n_item),
            codigo=codigo, nombre_estandarizado=nombre, marca=marca,
            modelo=modelo, numero_serie=serie, estado=estado
        )

        try:
            session.add(nuevo_equipo)
            session.commit()
        except Exception as e:
            session.rollback()
            messagebox.showerror("Error", f"No se pudo guardar el equipo:\n{e}")
            return

        messagebox.showinfo("Éxito", f"Equipo agregado. QR: {nombre_qr}")
        self.limpiar_campos()
        self.controller.frames[Frame_Inventario_General].set_area(area.id)
        self.controller.show_frame(Frame_Inventario_General)

###########################
# 7. FRAME MODIFICACIÓN EQUIPO

class Frame_Equipo_Modificar(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#F4F4F4")
        self.controller = controller
        self.equipo_actual = None

        tk.Label(self, text="MODIFICAR EQUIPO", font=(letra,20,"bold"), bg="#F4F4F4", fg="#012E40").pack(pady=20)
        self.frame_detalles = tk.Frame(self, bg="#F4F4F4")
        self.frame_detalles.pack(fill="both", expand=True, padx=20)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'TCombobox',
            fieldbackground='#012E40',
            background='#012E40',
            foreground='white',
            font=(letra, 15),
            selectbackground='#025E73',
            selectforeground='white'
        )
        tk.Label(
            self.frame_detalles,
            text="ÁREA",
            font=(letra,20,"bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).place(relx=0.2, rely=0.05)

        self.area_entry = ttk.Combobox(self.frame_detalles, font=(letra,15), values=[a.nombre_area for a in session.query(Area).all()], state="readonly", style='TCombobox')
        self.area_entry.place(relx=0.35, rely=0.05, relheight=0.07, relwidth=0.4)

        campos = [ ("N ITEM",0.15), ("CODIGO",0.25), ("NOMBRE",0.35), ("MARCA",0.45), ("MODELO",0.55), ("SERIE",0.65), ("ESTADO",0.75) ]
        self.mod_entries = {}
        for label, ypos in campos:
            tk.Label(self.frame_detalles, text=label, font=(letra,20,"bold"), bg="#F4F4F4", fg="#012E40").place(relx=0.2, rely=ypos)
            entry = tk.Entry(self.frame_detalles, font=(letra,15), bg="#012E40", fg="white")
            entry.place(relx=0.35, rely=ypos, relheight=0.07, relwidth=0.4)
            self.mod_entries[label] = entry

        tk.Button(
            self,
            text="GUARDAR CAMBIOS",
            font=(letra,12),
            bg="#012E40",
            fg="white",
            command=self.guardar_cambios
        ).place(relx=0.35, rely=0.90, relheight=0.05, relwidth=0.24)

        tk.Button(
            self,
            text="ELIMINAR",
            font=(letra,12),
            bg="#FF0000",
            fg="white",
            command=self.eliminar_equipo
        ).place(relx=0.65, rely=0.90, relheight=0.05, relwidth=0.24)

        tk.Button(
            self,
            text="VOLVER",
            font=(letra,12),
            bg="#012E40",
            fg="white",
            command=lambda: controller.show_frame(Frame_Inventario_General)
        ).place(relx=0.1, rely=0.90, relheight=0.05, relwidth=0.24)

    def cargar_equipo(self, equipo):
        self.equipo_actual = equipo
        area = session.query(Area).filter_by(id=equipo.area_id).first()
        self.area_entry.set(area.nombre_area)
        self.mod_entries["N ITEM"].delete(0, tk.END)
        self.mod_entries["N ITEM"].insert(0, str(equipo.N_item))
        self.mod_entries["CODIGO"].delete(0, tk.END)
        self.mod_entries["CODIGO"].insert(0, equipo.codigo)
        self.mod_entries["NOMBRE"].delete(0, tk.END)
        self.mod_entries["NOMBRE"].insert(0, equipo.nombre_estandarizado)
        self.mod_entries["MARCA"].delete(0, tk.END)
        self.mod_entries["MARCA"].insert(0, equipo.marca)
        self.mod_entries["MODELO"].delete(0, tk.END)
        self.mod_entries["MODELO"].insert(0, equipo.modelo)
        self.mod_entries["SERIE"].delete(0, tk.END)
        self.mod_entries["SERIE"].insert(0, equipo.numero_serie)
        self.mod_entries["ESTADO"].delete(0, tk.END)
        self.mod_entries["ESTADO"].insert(0, equipo.estado)

    def guardar_cambios(self):
        eq = self.equipo_actual
        if not eq:
            return
        area_nombre = self.area_entry.get()
        n_item = self.mod_entries["N ITEM"].get()
        codigo = self.mod_entries["CODIGO"].get()
        nombre = self.mod_entries["NOMBRE"].get()
        marca = self.mod_entries["MARCA"].get()
        modelo = self.mod_entries["MODELO"].get()
        serie = self.mod_entries["SERIE"].get()
        estado = self.mod_entries["ESTADO"].get()
        if not all([area_nombre, n_item, codigo, nombre, marca, modelo, serie, estado]):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return
        area = session.query(Area).filter_by(nombre_area=area_nombre).first()
        if not area:
            messagebox.showerror("Error", "Área no encontrada.")
            return
        eq.area_id = area.id
        eq.N_item = int(n_item)
        eq.codigo = codigo
        eq.nombre_estandarizado = nombre
        eq.marca = marca
        eq.modelo = modelo
        eq.numero_serie = serie
        eq.estado = estado
        session.commit()
        messagebox.showinfo("Éxito", "Cambios guardados.")
        self.controller.frames[Frame_Inventario_General].set_area(area.id)
        self.controller.show_frame(Frame_Inventario_General)

    def eliminar_equipo(self):
        eq = self.equipo_actual
        if not eq:
            return
        confirmar = messagebox.askyesno("Confirmar", "Eliminar equipo?")
        if confirmar:
            session.delete(eq)
            session.commit()
            messagebox.showinfo("Éxito", "Equipo eliminado.")
            self.controller.frames[Frame_Inventario_General].actualizar_equipos()
            self.controller.show_frame(Frame_Inventario_General)

####################
# 8. FRAME PRÉSTAMOS

class Frame_Prestamos(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#F4F4F4")
        self.controller = controller
        tk.Label(self, text="GESTIÓN DE PRÉSTAMOS", font=(letra, 20, "bold"), bg="#F4F4F4", fg="#012E40").pack(pady=20)

        frame_filtros = tk.Frame(self, bg="#F4F4F4")
        frame_filtros.pack(fill="x", padx=20, pady=10)

        # Botones de filtro
        tk.Button(frame_filtros, text="Pendientes", font=(letra, 12), command=lambda: self.actualizar_prestamos("Pendiente")).pack(side="left", padx=5)
        tk.Button(frame_filtros, text="Aprobados", font=(letra, 12), command=lambda: self.actualizar_prestamos("Aprobado")).pack(side="left", padx=5)
        tk.Button(frame_filtros, text="Devueltos", font=(letra, 12), command=lambda: self.actualizar_prestamos("Devuelto")).pack(side="left", padx=5)
        tk.Button(frame_filtros, text="Todos", font=(letra, 12), command=lambda: self.actualizar_prestamos()).pack(side="left", padx=5)

        self.frame_lista = tk.Frame(self, bg="#F4F4F4")
        self.frame_lista.pack(fill="both", expand=True, padx=20, pady=10)

        frame_botones = tk.Frame(self, bg="#F4F4F4")
        frame_botones.pack(fill="x", padx=20, pady=10)
        tk.Button(frame_botones, text="Volver", font=(letra, 12), bg="#012E40", fg="white",
                  command=lambda: controller.show_frame(Frame_Principal)).pack(side="left")

        self.actualizar_prestamos()

    def actualizar_prestamos(self, estado=None):
        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        # Consulta filtrada
        if estado:
            prestamos = session.query(Prestamo).filter_by(estado=estado).order_by(Prestamo.fecha_solicitud.desc()).all()
        else:
            prestamos = session.query(Prestamo).order_by(Prestamo.fecha_solicitud.desc()).all()

        if not prestamos:
            tk.Label(self.frame_lista, text="No hay préstamos", font=(letra, 14), bg="#F4F4F4").pack(pady=50)
            return

        cols = ("#1", "#2", "#3", "#4", "#5", "#6", "#7")
        tree = ttk.Treeview(self.frame_lista, columns=cols, show="headings")
        headings = ["ID", "Equipo", "Área Origen", "Área Destino", "Solicitante", "Fecha", "Estado"]

        for i, h in enumerate(headings, start=1):
            tree.heading(f"#{i}", text=h)
            tree.column(f"#{i}", width=100, anchor="w")

        for p in prestamos:
            tree.insert("", "end", values=(p.id, p.equipo, p.area_origen, p.area_destino, p.solicitante,
                                           p.fecha_solicitud.strftime("%Y-%m-%d %H:%M"), p.estado))

        scrollbar = ttk.Scrollbar(self.frame_lista, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Acciones permitidas si no es historial (Devueltos)
        if estado != "Devuelto":
            frame_acciones = tk.Frame(self.frame_lista, bg="#F4F4F4")
            frame_acciones.pack(fill="x", pady=10)

            tk.Button(frame_acciones, text="Aprobar", font=(letra, 12), bg="green", fg="white",
                      command=lambda: self.cambiar_estado(tree, "Aprobado")).pack(fill='x', padx=5, pady=2)
            tk.Button(frame_acciones, text="Rechazar", font=(letra, 12), bg="red", fg="white",
                      command=lambda: self.cambiar_estado(tree, "Rechazado")).pack(fill='x', padx=5, pady=2)
            tk.Button(frame_acciones, text="Devuelto", font=(letra, 12), bg="blue", fg="white",
                      command=lambda: self.cambiar_estado(tree, "Devuelto")).pack(fill='x', padx=5, pady=2)

        self.prestamo_tree = tree

    def cambiar_estado(self, tree, estado):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Selección", "Selecciona un préstamo.")
            return

        item = tree.item(sel[0])
        pid = item['values'][0]
        p = session.query(Prestamo).get(pid)

        if p:
            p.estado = estado
            session.commit()

            # Enviar mensaje al usuario de Telegram
            if p.usuario_id:
                try:
                    import telegram
                    bot = telegram.Bot(token=TOKEN)
                    mensaje = "Su solicitud fue aprobada." if estado == "Aprobado" else "Su solicitud fue rechazada." if estado == "Rechazado" else None
                    if mensaje:
                        asyncio.run(bot.send_message(chat_id=p.usuario_id, text=mensaje))
                except Exception as e:
                    print(f"Error al enviar mensaje de Telegram: {e}")

            self.actualizar_prestamos()
            messagebox.showinfo("Éxito", f"Estado cambiado a {estado}.")



##################
# 9. FRAME ORDENES

class Frame_Ordenes(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#F4F4F4")
        self.controller = controller
        tk.Label(self, text="ÓRDENES DE TRABAJO", font=(letra, 20, "bold"), bg="#F4F4F4", fg="#012E40").pack(pady=20)

        frame_filtros = tk.Frame(self, bg="#F4F4F4")
        frame_filtros.pack(fill="x", padx=20, pady=10)

        # Filtros por estado
        estados = [("Pendientes", "Pendiente"),("En Proceso", "En proceso"),("Completadas", "Completada"),("Aceptadas", "Aceptada"),("Rechazadas", "Rechazada"),("Todas", None)]
        for texto, valor in estados:
            tk.Button(frame_filtros, text=texto, font=(letra, 12),command=lambda v=valor: self.actualizar_ordenes(v)).pack(side="left", padx=5)

        self.frame_lista = tk.Frame(self, bg="#F4F4F4")
        self.frame_lista.pack(fill="both", expand=True, padx=20, pady=10)

        frame_botones = tk.Frame(self, bg="#F4F4F4")
        frame_botones.pack(fill="x", padx=20, pady=10)

        tk.Button(frame_botones, text="Volver", font=(letra, 12), bg="#012E40", fg="white",
                  command=lambda: controller.show_frame(Frame_Principal)).pack(side="left")

        self.actualizar_ordenes()

    def actualizar_ordenes(self, estado=None):
        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        if estado:
            ordenes = session.query(OrdenTrabajo).filter_by(estado=estado).order_by(OrdenTrabajo.fecha_solicitud.desc()).all()
        else:
            ordenes = session.query(OrdenTrabajo).order_by(OrdenTrabajo.fecha_solicitud.desc()).all()

        if not ordenes:
            tk.Label(self.frame_lista, text="No hay órdenes", font=(letra, 14), bg="#F4F4F4").pack(pady=50)
            return

        cols = ("#1", "#2", "#3", "#4", "#5", "#6", "#7")
        tree = ttk.Treeview(self.frame_lista, columns=cols, show="headings")
        headings = ["ID", "Tipo", "Área", "Urgencia", "Descripción", "Fecha", "Estado"]

        for i, h in enumerate(headings, start=1):
            tree.heading(f"#{i}", text=h)
            tree.column(f"#{i}", width=100, anchor="w")

        for o in ordenes:
            tree.insert("", "end", values=(o.id, o.tipo, o.area, o.urgencia, o.descripcion,
                                           o.fecha_solicitud.strftime("%Y-%m-%d %H:%M"), o.estado))

        scrollbar = ttk.Scrollbar(self.frame_lista, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        frame_acciones = tk.Frame(self.frame_lista, bg="#F4F4F4")
        frame_acciones.pack(fill="x", pady=10)

        # Acciones
        tk.Button(frame_acciones, text="Aceptar", font=(letra, 12), bg="blue", fg="white",
            command=lambda: self.cambiar_estado(tree, "Aceptada")).pack(fill='x', padx=5, pady=2)
        tk.Button(frame_acciones, text="Rechazar", font=(letra, 12), bg="gray", fg="white",
            command=lambda: self.cambiar_estado(tree, "Rechazada")).pack(fill='x', padx=5, pady=2)
        tk.Button(frame_acciones, text="Completar", font=(letra, 12), bg="green", fg="white",
            command=lambda: self.cambiar_estado(tree, "Completada")).pack(fill='x', padx=5, pady=2)
        tk.Button(frame_acciones, text="Cancelar", font=(letra, 12), bg="red", fg="white",
            command=lambda: self.cambiar_estado(tree, "Cancelada")).pack(fill='x', padx=5, pady=2)
        tk.Button(frame_acciones, text="Eliminar", font=(letra, 12), bg="black", fg="white",
            command=lambda: self.eliminar_orden(tree)).pack(fill='x', padx=5, pady=2)
        self.orden_tree = tree

    def cambiar_estado(self, tree, estado):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Selección", "Selecciona una orden.")
            return
        item = tree.item(sel[0])
        oid = item['values'][0]
        o = session.query(OrdenTrabajo).get(oid)
        if o:
            o.estado = estado
            session.commit()

            # Enviar mensaje al usuario de Telegram
            if o.usuario_id:
                try:
                    bot = telegram.Bot(token=TOKEN)
                    mensaje = "Su solicitud fue aprobada." if estado == "Aceptada" else "Su solicitud fue rechazada." if estado == "Rechazada" else None
                    if mensaje: asyncio.run(bot.send_message(chat_id=o.usuario_id, text=mensaje))
                except Exception as e:
                    print(f"Error al enviar mensaje de Telegram: {e}")

            self.actualizar_ordenes()
            messagebox.showinfo("Éxito", f"Estado cambiado a {estado}.")

    def eliminar_orden(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Selección", "Selecciona una orden.")
            return
        item = tree.item(sel[0])
        oid = item['values'][0]
        confirm = messagebox.askyesno("Confirmar eliminación", "¿Estás seguro de que deseas eliminar esta orden?")
        if confirm:
            o = session.query(OrdenTrabajo).get(oid)
            if o:
                session.delete(o)
                session.commit()
                self.actualizar_ordenes()
                messagebox.showinfo("Éxito", "Orden eliminada correctamente.")


###############################################
# PUNTO DE INICIO DE LA APLICACIÓN
###############################################
if __name__ == "__main__":          # Esta parte se ejecuta solo cuando es el script del programa principal 

    app_gui = App() # se crea la instancia de la interfaz grafica del usuario

    bot_process = Process(target=iniciar_bot,args = (TOKEN, start, iniciar_prestamo, recibir_detalles_prestamo, recibir_foto_prestamo, cancelar, iniciar_orden, recibir_detalles_orden, recibir_foto_orden, DETALLES_PRESTAMO, FOTO_PRESTAMO, DETALLES_ORDEN, FOTO_ORDEN))  # Se configura un nuevo proceso hijo, que ejecute la funcion iniciar_bot
    bot_process.start() # Inicia el proceso, para ejecutarse en paralelo con la interfaz

    app_gui.set_bot_process(bot_process) # permite que la interfaz tenga referencia al proceso del bot para poder cerrarlo, guarda bot_process como atributo de la clase app
    app_gui.mainloop()  # inicia el bucle principal de la interfaz grafica
    
    if bot_process.is_alive():  # despues de cerrarse el bucle anterior, se verifica si el bot sigue ejecutandose
        bot_process.terminate() #si es asi, se termina el proceso hijo
        bot_process.join()  # se espera a que el proceso termine completamente antes de salir
