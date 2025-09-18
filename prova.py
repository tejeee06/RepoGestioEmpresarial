import tkinter as tk

def mostrar_entrada():
    entrada_usuario = entrada.get()
    etiqueta.config(text=entrada_usuario)

# Crear una ventana raíz
root = tk.Tk()
root.title("Interacción con el Usuario")
root.geometry("400x200")

# Campo de entrada
entrada = tk.Entry(root)
entrada.pack()

# Botón para actualizar la etiqueta
boton = tk.Button(root, text="Mostrar Entrada", command=mostrar_entrada)
boton.pack()

# Etiqueta para mostrar la entrada
etiqueta = tk.Label(root, text="Aquí se mostrará tu texto")
etiqueta.pack()

# Iniciar el bucle de eventos
root.mainloop()
