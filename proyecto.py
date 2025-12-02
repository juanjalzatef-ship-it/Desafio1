import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt


# COLOR DE LA INTERFAZ

COLOR_FONDO = "#E6EEF7"     
COLOR_TEXTO = "#052E64"     
COLOR_BOTON ="#55A0F0"     
COLOR_BOTON_TEXTO = "white"

# ARCHIVO EXCEL
ARCHIVO = r"GESTION DE PRODUCTOS .xlsx"

# Cargar Excel → ahora sí se usa en la interfaz
try:
    df = pd.read_excel(ARCHIVO)
    # Aseguramos que existan las columnas correctas
    columnas = [
        "CODIGO","CODIGO CIUDAD", "PRODUCTO", "CATEGORIA", "PRECIO", "STOCK",
        "PROVEEDOR", "DEMANDA", "CIUDAD", "FECHA/INGRESO",
        "ESTADO", "PESO", "CALIDAD "
    ]
    for col in columnas:
        if col not in df.columns:
            df[col] = ""    # Si falta alguna, la crea
except:
    messagebox.showerror("Error", "El archivo Excel no se pudo cargar.")
    # Si no existe, lo crea vacío
    columnas = [
        "CODIGO", "CODIGO CIUDAD" ,"PRODUCTO", "CATEGORIA", "PRECIO", "STOCK",
        "PROVEEDOR", "DEMANDA", "CIUDAD", "FECHA/INGRESO",
        "ESTADO", "PESO", "CALIDAD "
    ]
    df = pd.DataFrame(columns=columnas)


df["PRECIO"] = pd.to_numeric(
    df["PRECIO"]
    .astype(str)
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .str.replace(".", "", regex=False),
    errors="coerce"
)

df["STOCK"] = pd.to_numeric(df["STOCK"], errors="coerce")  # Convierte texto a número y NaN los errores
df["STOCK"] = df["STOCK"].fillna(0).astype(int)  

# FUNCIONES PRINCIPALES

def guardar_excel():
    """Guarda cambios en el archivo original"""
    df.to_excel(ARCHIVO, index=False)


def guardar_producto(datos):
    global df
    df.loc[len(df)] = datos
    guardar_excel()
    messagebox.showinfo("¡Éxito!", "Producto agregado correctamente.")


def buscar_producto(CODIGO):
    CODIGO = str(CODIGO).strip()
    resultado = df[df["CODIGO"] == CODIGO]
    return resultado if not resultado.empty else None


def actualizar_producto(CODIGO, nuevos_datos):
    global df
    CODIGO = str(CODIGO).strip()
    idx = df.index[df["CODIGO"] == CODIGO]

    if len(idx) > 0:
        df.loc[idx[0]] = nuevos_datos
        guardar_excel()
        return True
    return False
# VENTANA AGREGAR

def ventana_agregar():
    win = tk.Toplevel()
    win.title("Agregar Producto")
    win.configure(bg=COLOR_FONDO)

    entradas = {}

    for i, col in enumerate(columnas):
        tk.Label(win, text=col, bg=COLOR_FONDO, fg=COLOR_TEXTO).grid(row=i, column=0, padx=5, pady=5)
        entry = tk.Entry(win)
        entry.grid(row=i, column=1)
        entradas[col] = entry

    def guardar():
        datos = [entradas[col].get() for col in columnas]
        guardar_producto(datos)
        win.destroy()

    tk.Button(win, text="Guardar", bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO,
              command=guardar).grid(row=len(columnas)+1, column=0, columnspan=2)
    
# VENTANA CONSULTAR/MODIFICAR

def ventana_consultar():
    win = tk.Toplevel()
    win.title("Consultar Y/O Modificar Producto")
    win.configure(bg=COLOR_FONDO)

    tk.Label(win, text="CODIGO DE PRODUCTO:", bg=COLOR_FONDO, fg=COLOR_TEXTO).grid(row=0, column=0)
    entry_codigo = tk.Entry(win)
    entry_codigo.grid(row=0, column=1)

    entradas = {}

    def buscar():
        CODIGO= entry_codigo.get()
        producto = buscar_producto(CODIGO)

        if producto is None:
            messagebox.showerror("Error", "Producto no encontrado.")
            return

        for i, col in enumerate(columnas):
            tk.Label(win, text=col, bg=COLOR_FONDO, fg=COLOR_TEXTO).grid(row=i+2, column=0)
            entrada = tk.Entry(win)
            entrada.insert(0, str(producto.iloc[0][col]))
            entrada.grid(row=i+2, column=1)
            entradas[col] = entrada

    def actualizar():
        CODIGO = entry_codigo.get()
        nuevos = [entradas[col].get() for col in columnas]
        if actualizar_producto(CODIGO, nuevos):
            messagebox.showinfo("¡Listo!", "Producto actualizado.")
        else:
            messagebox.showerror("Error", "No se pudo actualizar.")

    tk.Button(win, text="Buscar", bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO,
              command=buscar).grid(row=1, column=0)

    tk.Button(win, text="Actualizar", bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO,
              command=actualizar).grid(row=1, column=1)



# VENTANA FILTROS

def ventana_filtros():
    win = tk.Toplevel()
    win.title("Filtros Interactivos")
    win.configure(bg=COLOR_FONDO)

    tabla = ttk.Treeview(win, columns=columnas, show="headings")
    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=100)
    tabla.grid(row=3, column=0, columnspan=4)

    def actualizar_tabla(data):
        tabla.delete(*tabla.get_children())
        for _, row in data.iterrows():
            tabla.insert("", tk.END, values=list(row))

    tk.Button(win, text="PRECIO > PROMEDIO", bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO,
              command=lambda: actualizar_tabla(
    df[
        df["PRECIO"] > df["PRECIO"].mean()
    ]
)
              ).grid(row=0, column=0)

    tk.Button(win, text="STOCK < 10", bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO,
              command=lambda: actualizar_tabla(df[df["STOCK"] < 10])
              ).grid(row=0, column=1)

    tk.Button(win, text="ALTA DEMANDA + STOCK>20", bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO,
           command=lambda: actualizar_tabla(df[(df["DEMANDA"] == "Alto") & (df["STOCK"] > 20)])
              ).grid(row=0, column=2)

    tk.Label(win, text="CODIGO:", bg=COLOR_FONDO, fg=COLOR_TEXTO).grid(row=1, column=0)
    entry_cat = tk.Entry(win)
    entry_cat.grid(row=1, column=1)

    tk.Button(win, text="Filtrar", bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO,
              command=lambda: actualizar_tabla(df[df["CATEGORIA"] == entry_cat.get()])
              ).grid(row=1, column=2)
    
# VENTANA GRAFICOS

def ventana_graficos():
    win = tk.Toplevel()
    win.title("Graficos")

    # Paleta de colores
    tk.Label(win, text="Color:").grid(row=0, column=0)
    color_var = tk.StringVar(value="blue")
    ttk.Combobox(win, textvariable=color_var, values=["blue", "green"]).grid(row=0, column=1)

    # Graficos
    def scatter():
        plt.scatter(df["PRECIO"].astype(float), df["STOCK"].astype(int), color=color_var.get())
        plt.xlabel("PRECIO")
        plt.ylabel("STOCK")
        plt.title("Dispersion PRECIO vs STOCK")
        plt.show()

    def boxplot():
        plt.boxplot(df["PRECIO"].astype(float))
        plt.title("Distribucion de Precios")
        plt.show()

    def hist():
        plt.hist(df["STOCK"].astype(int), color=color_var.get())
        plt.title("Distribucion de STOCK")
        plt.show()

    tk.Button(win, text="Dispersion", command=scatter).grid(row=2, column=0)
    tk.Button(win, text="Boxplot", command=boxplot).grid(row=2, column=1)
    tk.Button(win, text="Histograma", command=hist).grid(row=2, column=2)



# VENTANA ESTADISTICAS

def ventana_estadisticas():
    win = tk.Toplevel()
    win.title("Estadisticas")
    win.configure(bg=COLOR_FONDO)

    def barras():
        df.groupby("CATEGORIA")["PRECIO"].mean().plot(kind="bar")
        plt.title("Promedio de PRECIOS por CATEGORIA")
        plt.show()

    tk.Button(win, text="Barras", bg=COLOR_BOTON, fg=COLOR_BOTON_TEXTO,
              command=barras).grid(row=0, column=0)


# VENTANA PRINCIPAL

def ventana_principal():
    root = tk.Tk()
    root.title("Sistema de Gestion de Productos")
    root.geometry("600x400")
    root.configure(bg=COLOR_FONDO)

    tk.Label(root, text="GESTION DE PRODUCTOS",
             font=("Arial", 18, "bold"),
             bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=20)

    tk.Button(root, text="Agregar Producto", width=25, bg=COLOR_BOTON,
              fg=COLOR_BOTON_TEXTO, command=ventana_agregar).pack(pady=5)

    tk.Button(root, text="Consultar/Modificar", width=25, bg=COLOR_BOTON,
              fg=COLOR_BOTON_TEXTO, command=ventana_consultar).pack(pady=5)

    tk.Button(root, text="Aplicar Filtros", width=25, bg=COLOR_BOTON,
              fg=COLOR_BOTON_TEXTO, command=ventana_filtros).pack(pady=5)

    tk.Button(root, text="Visualizar Graficos", width=25, bg=COLOR_BOTON,
              fg=COLOR_BOTON_TEXTO, command=ventana_graficos).pack(pady=5)

    tk.Button(root, text="Ver Estadisticas", width=25, bg=COLOR_BOTON,
              fg=COLOR_BOTON_TEXTO, command=ventana_estadisticas).pack(pady=5)

    tk.Button(root, text="Salir", width=25, bg="red", fg="white",
              command=root.destroy).pack(pady=10)

    root.mainloop()


ventana_principal()