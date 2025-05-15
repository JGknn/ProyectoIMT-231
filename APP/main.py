import tkinter as tk
from tkinter import ttk

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GESTION DE HOSPITAL")
        self.geometry("800x800")
        self.config(bg="#F4F4F4")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        
        # Lista de todos los frames de la aplicación
        for F in (Frame1, Frame2, Frame3, Frame4, Frame5, Frame6, Frame7, FrameInventario):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(Frame1)

    # CORRECCIÓN PRINCIPAL: show_frame debe ser un método de la clase, no estar dentro de __init__
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
class Frame1(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#F4F4F4")
        
        # Título principal
        tk.Label(
            self, 
            text="SISTEMA DE GESTIÓN HOSPITALARIA",
            font=("Gotham", 20, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).place(relx=0.5, rely=0.2, anchor="center")
        
        # Botón de inventario
        boton_inventario = tk.Button(
            self,
            text="INVENTARIO",
            font=("Gotham", 15),
            bg="#012E40", 
            fg="white",
            command=lambda: controller.show_frame(Frame7)
        )
        boton_inventario.place(
            relx=0.5,
            rely=0.5,
            relheight=0.07,
            relwidth=0.3,
            anchor="center"
        )
        
        # Botón de ficha técnica
        boton_ficha_tecnica = tk.Button(
            self,
            text="FICHA TÉCNICA",
            font=("Gotham", 15),
            bg="#012E40", 
            fg="white",
            command=lambda: controller.show_frame(Frame3)
        )
        boton_ficha_tecnica.place(
            relx=0.5,
            rely=0.6,
            relheight=0.07,
            relwidth=0.3,
            anchor="center"
        )

class Frame2(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#F4F4F4")
        
        # Título del frame
        tk.Label(
            self, 
            text="INVENTARIO",
            font=("Gotham", 20, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).pack(pady=30)
        
        # Botón para volver al inicio
        tk.Button(
            self, 
            text="VOLVER AL ANTERIOR",
            font=("Gotham", 12),
            bg="#012E40",
            fg="white",
            command=lambda: controller.show_frame(Frame7)
        ).place(
            relx=0.15,
            rely=0.97,
            relheight=0.05,
            relwidth=0.24,
            anchor="center"
        )
        tk.Button(
            self, 
            text="REGISTRAR NUEVO",
            font=("Gotham", 12),
            bg="#012E40",
            fg="white",
            command=lambda: controller.show_frame(Frame4)
        ).place(
            relx=0.68,
            rely=0.97,
            relheight=0.05,
            relwidth=0.2,
            anchor="center"
        )
        tk.Button(
            self, 
            text="MODIFICAR",
            font=("Gotham", 12),
            bg="#012E40",
            fg="white",
            command=lambda: controller.show_frame(Frame5)
        ).place(
            relx=0.89,
            rely=0.97,
            relheight=0.05,
            relwidth=0.2,
            anchor="center"
        )
        #tabla donde se añadiran los equipos 
        
class Frame3(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#F4F4F4")
        
        # Título del frame
        tk.Label(
            self, 
            text="FICHA TÉCNICA",
            font=("Gotham", 20, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).pack(pady=30)
        
        # Botón para volver al inicio
        tk.Button(
            self, 
            text="VOLVER AL ANTERIOR",
            font=("Gotham", 12),
            bg="#012E40",
            fg="white",
            command=lambda: controller.show_frame(Frame2)
        ).pack(pady=20)
#FRAME4=REGISTRAR NUEVO EQUIPO


class FrameInventario(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#F4F4F4")
        
        self.tree = ttk.Treeview(self, columns=("#", "CODIGO", "NOMBRE", "MARCA", "MODELO","SERIE"), show="headings")
        
        self.style = ttk.Style()
        self.style.configure(
            "Treeview.Heading",
            bg="#012E40",
            fg="white",
            font=('Gotham', 14, 'bold'),
            rowheight=25,
            fieldbackground="#012E40"
        )

        # Configurar las columnas
        self.tree.heading("#", text="#")
        self.tree.heading("CODIGO", text="CODIGO")
        self.tree.heading("NOMBRE", text="NOMBRE ESTANDARIZADO")
        self.tree.heading("MARCA", text="MARCA")
        self.tree.heading("MODELO", text="MODELO")
        self.tree.heading("SERIE", text="SERIE")

        # Ajustar el ancho de las columnas

        self.tree.column("#", width=50)
        self.tree.column("CODIGO", width=120)
        self.tree.column("NOMBRE", width=170)
        self.tree.column("MARCA", width=170)
        self.tree.column("MODELO", width=170)
        self.tree.column("SERIE", width=120)
        
        #ARREGLAR LA POSICION DE MANERA QUE SE VEA BIEN
        # Posicionar elementos
        self.tree.place(
            relx=0.5,
            rely=0.5,
            relheight=0.9,
            relwidth=1,
            anchor="center"
        )
        
        
        
        # Botones de control
        
        tk.Button(
            self,
            text="Agregar",
            command=self.agregar_item
            ).pack(
                side="left",
                padx=5
            )
        tk.Button(
            self,
            text="Editar", 
            command=self.editar_item
            ).pack(
                side="left", 
                padx=5
            )
        tk.Button(
            self, 
            text="Eliminar", 
            command=self.eliminar_item
        ).pack(
            side="left", 
            padx=5
        )
        tk.Button(
            self, 
            text="Actualizar", 
            command=self.actualizar_tabla
        ).pack(
            side="left", 
            padx=5
        )
        tk.Button(
            self, 
            text="Volver", 
            command=lambda: controller.show_frame(Frame1)
        ).pack(
            side="left", 
            padx=5
        )
        
        # Llenar la tabla con datos de ejemplo (luego lo cambiarás por tu BD)
        self.actualizar_tabla()

    def actualizar_tabla(self):
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Aquí iría la conexión a tu base de datos
        # Ejemplo con datos ficticios
        datos = [
            (1, "13123", "incubadora", "GE", "45646", "4656a5a"),
        ]
        
        for dato in datos:
            self.tree.insert("", "end", values=dato)
    
    def agregar_item(self):
        # Crear ventana emergente para agregar nuevo ítem
        self.ventana_agregar = tk.Toplevel(self)
        self.ventana_agregar.title("Agregar nuevo ítem")
        
        # Campos del formulario
        tk.Label(self.ventana_agregar, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
        nombre_entry = tk.Entry(self.ventana_agregar)
        nombre_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(self.ventana_agregar, text="Cantidad:").grid(row=1, column=0, padx=5, pady=5)
        cantidad_entry = tk.Entry(self.ventana_agregar)
        cantidad_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(self.ventana_agregar, text="Proveedor:").grid(row=2, column=0, padx=5, pady=5)
        proveedor_entry = tk.Entry(self.ventana_agregar)
        proveedor_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Botón para guardar
        tk.Button(self.ventana_agregar, text="Guardar", 
                 command=lambda: self.guardar_nuevo_item(
                     nombre_entry.get(),
                     cantidad_entry.get(),
                     proveedor_entry.get()
                 )).grid(row=3, columnspan=2, pady=10)
    
    def guardar_nuevo_item(self, nombre, cantidad, proveedor):
        # Aquí iría el código para guardar en la base de datos
        print(f"Guardando: {nombre}, {cantidad}, {proveedor}")
        self.actualizar_tabla()
        self.ventana_agregar.destroy()
    
    def editar_item(self):
        seleccionado = self.tree.selection()
        if seleccionado:
            item = self.tree.item(seleccionado)
            # Implementar lógica de edición similar a agregar_item
            print(f"Editando: {item['values']}")
    
    def eliminar_item(self):
        seleccionado = self.tree.selection()
        if seleccionado:
            # Aquí iría el código para eliminar de la base de datos
            self.tree.delete(seleccionado)

            
class Frame4(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#F4F4F4")
        
        # Título del frame
        tk.Label(
            self, 
            text="EQUIPO NUEVO",
            font=("Gotham", 24, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).place(
            relx=0.28,
            rely=0.02,
            relheight=0.07,
            relwidth=0.4,
            anchor="w"

        )
        #lugar de colocar el area
        tk.Label(
            self, 
            text="AREA",
            font=("Gotham", 20, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).place(
            relx=0,
            rely=0.15,
            relheight=0.07,
            relwidth=0.3,
            anchor="w"
        )
        tk.Entry(
            self,
            font=("Gotham", 15),
            bg="#012E40",
            fg="white"
        ).place(
            relx=0.7,
            rely=0.15,
            relheight=0.07,
            relwidth=0.4,
            anchor="center"
        )
         #lugar de colocar el NUMERO DE ITEM
        tk.Label(
            self, 
            text="N ITEM",
            font=("Gotham", 20, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).place(
            relx=0,
            rely=0.25,
            relheight=0.07,
            relwidth=0.3,
            anchor="w")
        tk.Entry(
            self,
            font=("Gotham", 15),
            bg="#012E40",
            fg="white"
        ).place(
            relx=0.7,
            rely=0.25,
            relheight=0.07,
            relwidth=0.4,
            anchor="center"
        )
         #lugar de colocar el CODIGO DEL EQUIPO
        tk.Label(
            self, 
            text="CODIGO",
            font=("Gotham", 20, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).place(
            relx=0,
            rely=0.35,
            relheight=0.07,
            relwidth=0.3,
            anchor="w")
        tk.Entry(
            self,
            font=("Gotham", 15),
            bg="#012E40",
            fg="white"
        ).place(
            relx=0.7,
            rely=0.35,
            relheight=0.07,
            relwidth=0.4,
            anchor="center"
        )
         #lugar de colocar el NOMBRE ESTANDARIZADO
        tk.Label(
            self, 
            text="NOMBRE ESTANDARIZADO",
            font=("Gotham", 20, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).place(
            relx=0,
            rely=0.45,
            relheight=0.07,
            relwidth=0.4,
            anchor="w")
        tk.Entry(
            self,
            font=("Gotham", 15),
            bg="#012E40",
            fg="white"
        ).place(
            relx=0.7,
            rely=0.45,
            relheight=0.07,
            relwidth=0.4,
            anchor="center"
        )
         #lugar de colocar el MARCA
        tk.Label(
            self, 
            text="MARCA",
            font=("Gotham", 20, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).place(
            relx=0,
            rely=0.55,
            relheight=0.07,
            relwidth=0.3,
            anchor="w")
        tk.Entry(
            self,
            font=("Gotham", 15),
            bg="#012E40",
            fg="white"
        ).place(
            relx=0.7,
            rely=0.55,
            relheight=0.07,
            relwidth=0.4,
            anchor="center"
        )
         #lugar de colocar el MODELO
        tk.Label(
            self, 
            text="MODELO",
            font=("Gotham", 20, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).place(
            relx=0,
            rely=0.65,
            relheight=0.07,
            relwidth=0.3,
            anchor="w")
        tk.Entry(
            self,
            font=("Gotham", 15),
            bg="#012E40",
            fg="white"
        ).place(
            relx=0.7,
            rely=0.65,
            relheight=0.07,
            relwidth=0.4,
            anchor="center"
        )
         #lugar de colocar el SERIE
        tk.Label(
            self, 
            text="SERIE",
            font=("Gotham", 20, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).place(
            relx=0,
            rely=0.75,
            relheight=0.07,
            relwidth=0.3,
            anchor="w")
        tk.Entry(
            self,
            font=("Gotham", 15),
            bg="#012E40",
            fg="white"
        ).place(
            relx=0.7,
            rely=0.75,
            relheight=0.07,
            relwidth=0.4,
            anchor="center"
        )
         #lugar de colocar el ESTADO
        tk.Label(
            self, 
            text="ESTADO",
            font=("Gotham", 20, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).place(
            relx=0,
            rely=0.85,
            relheight=0.07,
            relwidth=0.3,
            anchor="w")
        tk.Entry(
            self,
            font=("Gotham", 15),
            bg="#012E40",
            fg="white"
        ).place(
            relx=0.7,
            rely=0.85,
            relheight=0.07,
            relwidth=0.4,
            anchor="center"
        )
        
        # Botón para volver al inicio
        tk.Button(
            self, 
            text="VOLVER AL ANTERIOR",
            font=("Gotham", 12),
            bg="#012E40",
            fg="white",
            command=lambda: controller.show_frame(Frame2)
        ).place(
            relx=0.15,
            rely=0.97,
            relheight=0.05,
            relwidth=0.24,
            anchor="center"
        )
        # Botón para AGREGAR
        tk.Button(
            self, 
            text="AGREGAR",
            font=("Gotham", 12),
            bg="#012E40",
            fg="white",
            command=...
        ).place(
            relx=0.5,
            rely=0.97,
            relheight=0.05,
            relwidth=0.24,
            anchor="center")
#FRAME5=EQUIPO A MDIFICAR
class Frame5(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#F4F4F4")
        
        # Título del frame
        tk.Label(
            self, 
            text="QUE EQUIPO MODIFICAR",
            font=("Gotham", 20, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).pack(pady=30)
        tk.Button(
            self, 
            text="MONITOR FETAL",
            font=("Gotham", 20, "bold"),
            bg="#012E40",
            fg="#F4F4F4",
            command=lambda: controller.show_frame(Frame6)
        ).place(
            relx=0.05,
            rely=0.15,
            relheight=0.07,
            relwidth=0.3,
            anchor="w"
        )
        
        # Botón para volver al inicio
        tk.Button(
            self, 
            text="VOLVER AL ANTERIOR",
            font=("Gotham", 12),
            bg="#012E40",
            fg="white",
            command=lambda: controller.show_frame(Frame2)
        ).place(
            relx=0.15,
            rely=0.97,
            relheight=0.05,
            relwidth=0.24,
            anchor="center"
        )
class Frame6(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#F4F4F4")

         #lugar de colocar el area
        tk.Label(
            self, 
            text="AREA",
            font=("Gotham", 20, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).place(
            relx=0,
            rely=0.15,
            relheight=0.07,
            relwidth=0.3,
            anchor="w"
        )
        tk.Entry(
            self,
            font=("Gotham", 15),
            bg="#012E40",
            fg="white"
        ).place(
            relx=0.7,
            rely=0.15,
            relheight=0.07,
            relwidth=0.4,
            anchor="center"
        )
         #lugar de colocar el NUMERO DE ITEM
        tk.Label(
            self, 
            text="N ITEM",
            font=("Gotham", 20, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).place(
            relx=0,
            rely=0.25,
            relheight=0.07,
            relwidth=0.3,
            anchor="w")
        tk.Entry(
            self,
            font=("Gotham", 15),
            bg="#012E40",
            fg="white"
        ).place(
            relx=0.7,
            rely=0.25,
            relheight=0.07,
            relwidth=0.4,
            anchor="center"
        )
         #lugar de colocar el CODIGO DEL EQUIPO
        tk.Label(
            self, 
            text="CODIGO",
            font=("Gotham", 20, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).place(
            relx=0,
            rely=0.35,
            relheight=0.07,
            relwidth=0.3,
            anchor="w")
        tk.Entry(
            self,
            font=("Gotham", 15),
            bg="#012E40",
            fg="white"
        ).place(
            relx=0.7,
            rely=0.35,
            relheight=0.07,
            relwidth=0.4,
            anchor="center"
        )
         #lugar de colocar el NOMBRE ESTANDARIZADO
        tk.Label(
            self, 
            text="NOMBRE ESTANDARIZADO",
            font=("Gotham", 20, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).place(
            relx=0,
            rely=0.45,
            relheight=0.07,
            relwidth=0.4,
            anchor="w")
        tk.Entry(
            self,
            font=("Gotham", 15),
            bg="#012E40",
            fg="white"
        ).place(
            relx=0.7,
            rely=0.45,
            relheight=0.07,
            relwidth=0.4,
            anchor="center"
        )
         #lugar de colocar el MARCA
        tk.Label(
            self, 
            text="MARCA",
            font=("Gotham", 20, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).place(
            relx=0,
            rely=0.55,
            relheight=0.07,
            relwidth=0.3,
            anchor="w")
        tk.Entry(
            self,
            font=("Gotham", 15),
            bg="#012E40",
            fg="white"
        ).place(
            relx=0.7,
            rely=0.55,
            relheight=0.07,
            relwidth=0.4,
            anchor="center"
        )
         #lugar de colocar el MODELO
        tk.Label(
            self, 
            text="MODELO",
            font=("Gotham", 20, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).place(
            relx=0,
            rely=0.65,
            relheight=0.07,
            relwidth=0.3,
            anchor="w")
        tk.Entry(
            self,
            font=("Gotham", 15),
            bg="#012E40",
            fg="white"
        ).place(
            relx=0.7,
            rely=0.65,
            relheight=0.07,
            relwidth=0.4,
            anchor="center"
        )
         #lugar de colocar el SERIE
        tk.Label(
            self, 
            text="SERIE",
            font=("Gotham", 20, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).place(
            relx=0,
            rely=0.75,
            relheight=0.07,
            relwidth=0.3,
            anchor="w")
        tk.Entry(
            self,
            font=("Gotham", 15),
            bg="#012E40",
            fg="white"
        ).place(
            relx=0.7,
            rely=0.75,
            relheight=0.07,
            relwidth=0.4,
            anchor="center"
        )
         #lugar de colocar el ESTADO
        tk.Label(
            self, 
            text="ESTADO",
            font=("Gotham", 20, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).place(
            relx=0,
            rely=0.85,
            relheight=0.07,
            relwidth=0.3,
            anchor="w")
        tk.Entry(
            self,
            font=("Gotham", 15),
            bg="#012E40",
            fg="white"
        ).place(
            relx=0.7,
            rely=0.85,
            relheight=0.07,
            relwidth=0.4,
            anchor="center"
        )
        # Botón para volver al inicio
        tk.Button(
            self, 
            text="VOLVER AL ANTERIOR",
            font=("Gotham", 12),
            bg="#012E40",
            fg="white",
            command=lambda: controller.show_frame(Frame5)
        ).place(
            relx=0.15,
            rely=0.97,
            relheight=0.05,
            relwidth=0.24,
            anchor="center"
        )  
class Frame7(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#F4F4F4")
        
        # Título del frame
        tk.Label(
            self, 
            text="AREAS",
            font=("Gotham", 20, "bold"),
            bg="#F4F4F4",
            fg="#012E40"
        ).pack(pady=30)
        tk.Button(
            self, 
            text="ENFERMERIA",
            font=("Gotham", 20, "bold"),
            bg="#012E40",
            fg="#F4F4F4",
            command=lambda: controller.show_frame(Frame2)
        ).place(
            relx=0.05,
            rely=0.15,
            relheight=0.07,
            relwidth=0.3,
            anchor="w"
        )
        
        # Botón para volver al inicio
        tk.Button(
            self, 
            text="VOLVER AL INICIO",
            font=("Gotham", 12),
            bg="#012E40",
            fg="white",
            command=lambda: controller.show_frame(Frame1)
        ).place(
            relx=0.15,
            rely=0.97,
            relheight=0.05,
            relwidth=0.24,
            anchor="center"
        )
app = App()
app.mainloop()
