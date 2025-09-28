import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "erp_demo",
    "port": "3306",
}

def get_conn() :
    return mysql.connector.connect(**DB_CONFIG)

# Recupera les files de la taula Client
def fetch_clients() :
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT ClientId, nom, email, telefon, ciutat FROM client ORDER BY ClientId;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# Recarrega les dades de la BD
def refresh_tree(tree: ttk.Treeview) :
    for item in tree.get_children():
        tree.delete(item)
    try:
        for row in fetch_clients():
            tree.insert("", tk.END, values=row)
    except Error as e:
        messagebox.showerror("Error MySQL", str(e))

def main():
    root = tk.Tk()
    root.title("Clients — Tkinter + MySQL")
    root.geometry("800x420")

    # Marc principal
    frame = ttk.Frame(root, padding=12)
    frame.pack(fill="both", expand=True)

    # Definició de columnes del Treeview
    cols = ("ClientId", "Nom", "Email", "Telèfon", "Ciutat")
    tree = ttk.Treeview(frame, columns=cols, show="headings")
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=120 if c != "Email" else 220, anchor="w")

    # Scrollbars
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    # Disposició amb grid
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    # Botonera inferior
    btns = ttk.Frame(root, padding=(12, 0, 12, 12))
    btns.pack(fill="x")
    ttk.Button(btns, text="Actualitza", command=lambda: refresh_tree(tree)).pack(side="left")
    ttk.Button(btns, text="Sortir", command=root.destroy).pack(side="right")

    # Carrega inicial
    refresh_tree(tree)
    root.mainloop()


if __name__ == "__main__":
    main()
