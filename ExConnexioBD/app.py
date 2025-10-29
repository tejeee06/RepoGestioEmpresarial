import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import errors

#  Configuració de la Connexió a la Base de Dades
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "erp_demo",
    "port": "3306",
}

#  Funcions de Base de Dades

def get_conn():
    """Estableix connexió amb la BD."""
    try:
        return mysql.connector.connect(**DB_CONFIG, connect_timeout=5)
    except mysql.connector.Error as e:
        messagebox.showerror("Error de Connexió MySQL",
                             f"No s'ha pogut connectar:\n{e}")
        raise

def fetch_clients():
    """Recupera tots els clients de la base de dades."""
    conn = None
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT ClientId, Nom, Email, Telefon, Ciutat FROM client ORDER BY ClientId;")
            return cur.fetchall()
    finally:
        if conn:
            conn.close()

#  Funcions de la Interfície Gràfica (GUI) --

def refresh_tree(tree: ttk.Treeview):
    """
    Neteja el Treeview i el torna a poblar des de la BD.
    (Versió de la Secció 6, sense cerca).
    """
    for item in tree.get_children():
        tree.delete(item)
    try:
        clients = fetch_clients()
        if clients:
            for row in clients:
                tree.insert("", tk.END, values=row)
    except mysql.connector.Error as e:
        messagebox.showerror("Error de Càrrega de Dades", str(e))
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperat en carregar dades: {e}")


def open_client_form(tree: ttk.Treeview, client_data=None):
    """
    Obre el formulari per AFEGIR (client_data=None) o
    MODIFICAR (client_data=tupla) un client. (Secció 4 i 5.2)
    """
    form_window = tk.Toplevel()
    form_window.title("Modificar Client" if client_data else "Nou Client")
    form_window.geometry("420x260")
    form_window.resizable(False, False)
    form_window.transient(tree.winfo_toplevel())
    form_window.grab_set()

    frame = ttk.Frame(form_window, padding="15")
    frame.pack(fill="both", expand=True)

    fields = [
        ("Nom", "Nom"),
        ("Email", "Email"),
        ("Telèfon", "Telefon"),
        ("Ciutat", "Ciutat"),
    ]
    entries = {}

    for i, (label_text, key) in enumerate(fields):
        ttk.Label(frame, text=label_text + ":").grid(row=i, column=0, sticky="w", pady=5, padx=5)
        entry = ttk.Entry(frame, width=36)
        entry.grid(row=i, column=1, sticky="ew", pady=5, padx=5)
        if client_data:
            mapping = {"Nom": 1, "Email": 2, "Telefon": 3, "Ciutat": 4}
            entry.insert(0, client_data[mapping[key]] or "")
        entries[key] = entry

    client_id = int(client_data[0]) if client_data else None

    def on_enter(event):
        save_or_update_client(entries, form_window, tree, client_id)

    save_button = ttk.Button(
        frame,
        text="Desar Canvis" if client_data else "Desar",
        command=lambda: save_or_update_client(entries, form_window, tree, client_id)
    )
    save_button.grid(row=len(fields), column=0, columnspan=2, pady=16)

    entries["Nom"].focus_set()
    form_window.bind("<Return>", on_enter)

def save_or_update_client(entries, window, tree, client_id=None):
    """
    Desa un client NOU (INSERT) o existent (UPDATE). (Secció 4 i 5.2)
    """
    nom = entries["Nom"].get().strip()
    email = entries["Email"].get().strip()
    telefon = entries["Telefon"].get().strip()
    ciutat = entries["Ciutat"].get().strip()

    if not nom or not email:
        messagebox.showwarning("Camps Obligatoris", "El nom i l'email són camps obligatoris.", parent=window)
        return

    if "@" not in email or "." not in email.split("@")[-1]:
        if not messagebox.askyesno("Possible email invàlid",
                                     "L'email no sembla vàlid. Vols desar igualment?",
                                     parent=window):
            return

    conn = None
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            if client_id is None:
                # Create
                sql = "INSERT INTO client (Nom, Email, Telefon, Ciutat) VALUES (%s, %s, %s, %s)"
                cur.execute(sql, (nom, email, telefon, ciutat))
                message = "Client afegit correctament."
            else:
                # Update
                sql = "UPDATE client SET Nom=%s, Email=%s, Telefon=%s, Ciutat=%s WHERE ClientId=%s"
                cur.execute(sql, (nom, email, telefon, ciutat, client_id))
                message = "Client actualitzat correctament."
            
            conn.commit()
            messagebox.showinfo("Èxit", message, parent=window)
            window.destroy()
            
            refresh_tree(tree) 

    except errors.IntegrityError:
        messagebox.showerror("Error de Dades",
                             f"No s'ha pogut desar el client.\nPossiblement l'email '{email}' ja existeix.",
                             parent=window)
    except mysql.connector.Error as e:
        if conn:
            conn.rollback()
        messagebox.showerror("Error de Base de Dades", f"Hi ha hagut un error: {e}", parent=window)
    except Exception as e:
        if conn:
            conn.rollback()
        messagebox.showerror("Error", f"Hi ha hagut un error inesperat: {e}", parent=window)
    finally:
        if conn:
            conn.close()

def delete_client(tree: ttk.Treeview):
    """
    Elimina el client seleccionat (Delete). (Secció 5.3)
    """
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showwarning("Cap Selecció", "Si us plau, seleccioneu un client per eliminar.")
        return

    confirm = messagebox.askyesno(
        "Confirmar Eliminació",
        "Està segur que vol eliminar el client seleccionat?\nAquesta acció no es pot desfer."
    )
    if not confirm:
        return

    selected_iid = selected_items[0]
    client_values = tree.item(selected_iid, "values")
    if not client_values:
        messagebox.showerror("Error", "No s'han pogut obtenir les dades del client seleccionat.")
        return

    client_id = int(client_values[0])

    conn = None
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            sql = "DELETE FROM client WHERE ClientId=%s"
            cur.execute(sql, (client_id,))
            conn.commit()

        messagebox.showinfo("Èxit", "Client eliminat correctament.")
        refresh_tree(tree)

    except mysql.connector.Error as e:
        if conn:
            conn.rollback()
        messagebox.showerror("Error de Base de Dades", f"No s'ha pogut eliminar el client: {e}")
    except Exception as e:
        if conn:
            conn.rollback()
        messagebox.showerror("Error", f"No s'ha pogut eliminar el client: {e}")
    finally:
        if conn:
            conn.close()

# Funció Principal

def main():
    root = tk.Tk()
    root.title("Gestió de Clients — CRUD amb Tkinter + MySQL")
    root.geometry("850x450")

    main_frame = ttk.Frame(root, padding=12)
    main_frame.pack(fill="both", expand=True)

    cols = ("ClientId", "Nom", "Email", "Telèfon", "Ciutat")
    tree = ttk.Treeview(main_frame, columns=cols, show="headings", selectmode="browse")

    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=100 if c == "ClientId" else (120 if c != "Email" else 220), anchor="w")

    vsb = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(main_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")

    main_frame.rowconfigure(0, weight=1)
    main_frame.columnconfigure(0, weight=1)

    btns_frame = ttk.Frame(root, padding=(12, 12, 12, 12)) 
    btns_frame.pack(fill="x")

    btn_new = ttk.Button(btns_frame, text="Nou Client", command=lambda: open_client_form(tree))
    btn_new.pack(side="left")

    def on_edit():
        sel = tree.selection()
        if not sel:
            return
        iid = sel[0]
        values = tree.item(iid, "values")
        open_client_form(tree, values)

    btn_edit = ttk.Button(btns_frame, text="Modificar Client", state="disabled", command=on_edit)
    btn_edit.pack(side="left", padx=5)

    btn_delete = ttk.Button(btns_frame, text="Eliminar Client", state="disabled", command=lambda: delete_client(tree))
    btn_delete.pack(side="left")

    ttk.Button(btns_frame, text="Sortir", command=root.destroy).pack(side="right")
    
    ttk.Button(btns_frame, text="Refresca Llista",
               command=lambda: refresh_tree(tree)).pack(side="right", padx=5)

    def on_tree_select(event):
        if tree.selection():
            btn_edit.config(state="normal")
            btn_delete.config(state="normal")
        else:
            btn_edit.config(state="disabled")
            btn_delete.config(state="disabled")

    tree.bind("<<TreeviewSelect>>", on_tree_select)

    try:
        refresh_tree(tree)
    except mysql.connector.Error as e:
        messagebox.showerror("Error de Càrrega Inicial", f"No s'han pogut carregar els clients:\n{e}")
    except Exception as e:
         messagebox.showerror("Error", f"Error inesperat en la càrrega inicial: {e}")

    root.mainloop()

if __name__ == "__main__":
    main()