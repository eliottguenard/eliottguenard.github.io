import mysql.connector
from tkinter import *
from tkinter import ttk, messagebox
import csv
from datetime import datetime

# Connexion à la base de données
user = "root"
password = ""
nom_base_principal = "selmarin_tda"
params = {"host": "localhost", "user": user, "password": password, "database": nom_base_principal}
db = mysql.connector.connect(**params)

def recuperer_donnees(db):
    try:
        cursor = db.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        # Créer une fenêtre Tkinter
        root = Tk()
        root.title("Modifier une Ligne de Valeur")

        # Créer un menu déroulant pour choisir une table
        label = Label(root, text="Choisissez une table:")
        label.pack(pady=10)

        table_names = [table[0] for table in tables]
        table_combobox = ttk.Combobox(root, values=table_names)
        table_combobox.pack(pady=10)

        # Variables pour le Treeview et les boutons
        tree = None
        modify_button = None
        add_button = None
        delete_button = None
        columns = []  # Define columns globally for later use

        # Créer un frame pour les boutons (pour les aligner sur la même ligne)
        buttons_frame = Frame(root)
        buttons_frame.pack(pady=10)

        # Fonction pour afficher les données d'une table dans un Treeview
        def afficher_donnees():
            nonlocal tree, modify_button, add_button, delete_button, columns

            selected_table = table_combobox.get()

            # Si un Treeview existe déjà, le supprimer
            if tree:
                tree.destroy()

            # Si un bouton de modification existe déjà, le supprimer
            if modify_button:
                modify_button.destroy()

            # Si un bouton d'ajout existe déjà, le supprimer
            if add_button:
                add_button.destroy()

            # Si un bouton de suppression existe déjà, le supprimer
            if delete_button:
                delete_button.destroy()

            # Récupérer toutes les lignes de la table sélectionnée
            cursor.execute(f"SELECT * FROM {selected_table}")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]  # Update columns list

            # Créer un Treeview pour afficher les résultats
            tree = ttk.Treeview(root, columns=columns, show="headings")
            tree.pack(fill=BOTH, expand=True, pady=20)

            # Ajouter des colonnes
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)

            # Insérer les lignes de données dans le Treeview
            for row in rows:
                tree.insert("", "end", values=row)

            # Fonction pour modifier une ligne sélectionnée
            def modifier_ligne():
                selected_item = tree.selection()  # Sélectionner la ligne
                if not selected_item:
                    messagebox.showwarning("Sélectionnez une ligne", "Veuillez sélectionner une ligne à modifier.")
                    return

                # Extraire les valeurs de la ligne sélectionnée
                values = tree.item(selected_item)['values']

                # Fenêtre de modification
                def appliquer_modifications():
                    updated_values = [entry.get() for entry in entry_fields]
                    if not all(updated_values):
                        messagebox.showwarning("Entrées manquantes", "Veuillez remplir toutes les cases.")
                        return

                    try:
                        # Requête UPDATE pour appliquer les modifications
                        set_clause = ", ".join([f"{columns[i]} = %s" for i in range(len(columns))])
                        update_query = f"UPDATE {selected_table} SET {set_clause} WHERE {columns[0]} = %s"
                        
                        # Mise à jour des données dans la base de données
                        cursor.execute(update_query, (*updated_values, values[0]))  # Utilise la première colonne (ID) pour WHERE
                        db.commit()

                        # Mise à jour du Treeview avec les nouvelles données
                        tree.item(selected_item, values=updated_values)

                        messagebox.showinfo("Succès", "Les données ont été modifiées avec succès.")
                        modify_window.destroy()

                    except Exception as e:
                        messagebox.showerror("Erreur", f"Erreur lors de la modification : {e}")

                # Créer une fenêtre de modification
                modify_window = Toplevel(root)
                modify_window.title("Modifier la ligne")

                entry_fields = []
                for idx, value in enumerate(values):
                    label = Label(modify_window, text=columns[idx])
                    label.grid(row=idx, column=0, padx=5, pady=5)
                    entry = Entry(modify_window)
                    entry.insert(0, value)
                    entry.grid(row=idx, column=1, padx=5, pady=5)
                    entry_fields.append(entry)

                # Bouton pour appliquer les modifications
                apply_button = Button(modify_window, text="Appliquer", command=appliquer_modifications)
                apply_button.grid(row=len(values), column=0, columnspan=2, pady=10)

            # Bouton pour modifier la ligne sélectionnée
            modify_button = Button(buttons_frame, text="Modifier la ligne", command=modifier_ligne)
            modify_button.pack(side=LEFT, padx=5)

            # Fonction pour supprimer une ligne sélectionnée
            def supprimer_ligne():
                selected_item = tree.selection()  # Sélectionner la ligne
                if not selected_item:
                    messagebox.showwarning("Sélectionnez une ligne", "Veuillez sélectionner une ligne à supprimer.")
                    return

                # Extraire les valeurs de la ligne sélectionnée (ici, on prend la première colonne comme identifiant)
                values = tree.item(selected_item)['values']
                row_id = values[0]  # Assuming the first column is the primary key

                # Demander confirmation avant de supprimer
                confirmation = messagebox.askyesno("Confirmer la suppression", "Êtes-vous sûr de vouloir supprimer cette ligne ?")
                if confirmation:
                    try:
                        # Requête DELETE pour supprimer la ligne
                        delete_query = f"DELETE FROM {selected_table} WHERE {columns[0]} = %s"
                        cursor.execute(delete_query, (row_id,))
                        db.commit()

                        # Supprimer la ligne dans le Treeview
                        tree.delete(selected_item)

                        messagebox.showinfo("Succès", "La ligne a été supprimée avec succès.")
                    except Exception as e:
                        messagebox.showerror("Erreur", f"Erreur lors de la suppression : {e}")

            # Bouton pour supprimer la ligne sélectionnée
            delete_button = Button(buttons_frame, text="Supprimer la ligne", command=supprimer_ligne)
            delete_button.pack(side=LEFT, padx=5)

            # Dynamically add "Ajouter une ligne" button next to modify and delete buttons
            add_button = Button(buttons_frame, text="Ajouter une ligne", command=ajouter_ligne)
            add_button.pack(side=LEFT, padx=5)

        # Fonction pour ajouter une nouvelle ligne
        def ajouter_ligne():
            selected_table = table_combobox.get()
            
            # Vérifier que la table est sélectionnée
            if not selected_table:
                messagebox.showwarning("Sélection Table", "Veuillez choisir une table.")
                return

            # Fenêtre pour saisir les données de la nouvelle ligne
            def ajouter_donnees():
                new_data = [entry.get() for entry in entry_fields]
                if not all(new_data):
                    messagebox.showwarning("Entrées manquantes", "Veuillez remplir toutes les cases.")
                    return

                # Requête d'insertion
                try:
                    columns_str = ", ".join(columns)
                    placeholders = ", ".join(["%s"] * len(columns))
                    insert_query = f"INSERT INTO {selected_table} ({columns_str}) VALUES ({placeholders})"

                    cursor.execute(insert_query, new_data)
                    db.commit()

                    messagebox.showinfo("Succès", "Donnée ajoutée avec succès.")
                    add_window.destroy()

                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de l'ajout de la ligne : {e}")

            # Ouvrir la fenêtre pour ajouter une nouvelle ligne
            add_window = Toplevel(root)
            add_window.title("Ajouter une nouvelle ligne")

            entry_fields = []
            for idx, col in enumerate(columns):
                label = Label(add_window, text=col)
                label.grid(row=idx, column=0, padx=5, pady=5)
                entry = Entry(add_window)
                entry.grid(row=idx, column=1, padx=5, pady=5)
                entry_fields.append(entry)

            # Bouton pour ajouter les données à la table
            add_button = Button(add_window, text="Ajouter", command=ajouter_donnees)
            add_button.grid(row=len(columns), column=0, columnspan=2, pady=10)

        # Bouton pour afficher les données
        afficher_button = Button(root, text="Afficher les Données", command=afficher_donnees)
        afficher_button.pack(pady=10)

        # Fonction pour exécuter une requête SQL personnalisée
        def executer_requete_sql():
            nonlocal tree  # Ensure tree is accessible in this function
            custom_query = sql_entry.get()  # Récupérer la requête SQL entrée par l'utilisateur
            if not custom_query:
                messagebox.showwarning("Entrée vide", "Veuillez entrer une requête SQL.")
                return

            # Désactiver les boutons Modifier, Supprimer et Ajouter
            if modify_button:
                modify_button.config(state=DISABLED)
            if delete_button:
                delete_button.config(state=DISABLED)
            if add_button:
                add_button.config(state=DISABLED)

            try:
                cursor.execute(custom_query)
                columns = [desc[0] for desc in cursor.description]  # Retrieve column names
                rows = cursor.fetchall()

                # Si un Treeview existe déjà, le supprimer
                if tree:
                    tree.destroy()

                # Créer un Treeview pour afficher les résultats de la requête personnalisée
                tree = ttk.Treeview(root, columns=columns, show="headings")
                tree.pack(fill=BOTH, expand=True, pady=20)

                for col in columns:
                    tree.heading(col, text=col)
                    tree.column(col, width=100)

                for row in rows:
                    tree.insert("", "end", values=row)

            except mysql.connector.Error as err:
                messagebox.showerror("Erreur SQL", f"Erreur lors de l'exécution de la requête : {err}")
            finally:
                # Réactiver les boutons Modifier, Supprimer et Ajouter après l'exécution de la requête
                if modify_button:
                    modify_button.config(state=DISABLED)
                if delete_button:
                    delete_button.config(state=DISABLED)
                if add_button:
                    add_button.config(state=DISABLED)

        # Champ d'entrée pour la requête SQL personnalisée
        sql_label = Label(root, text="Entrez votre requête SQL:")
        sql_label.pack(pady=10)

        sql_entry = Entry(root, width=50)
        sql_entry.pack(pady=5)

        # Bouton pour exécuter la requête SQL personnalisée
        execute_button = Button(root, text="Exécuter la requête", command=executer_requete_sql)
        execute_button.pack(pady=10)

        predefined_queries = {
    "Vente Produit 2024": """
        SELECT p.numPdt, p.libPdt, SUM(c.qteSort) AS total_vendu 
        FROM PRODUIT p 
        JOIN CONCERNER c ON p.numPdt = c.numPdt 
        JOIN SORTIE s ON c.numSort = s.numSort 
        WHERE YEAR(s.dateSort) = 2024 
        GROUP BY p.numPdt, p.libPdt
    """,

    "Produits à faible stock": """
        SELECT numPdt, libPdt, stockPdt 
        FROM PRODUIT 
        WHERE stockPdt < 1500
    """,

    "Client Achats": """
        SELECT client.NumCli, client.nomCli, count(concerner.numPdt) as Nb_Achats, produit.libPdt 
        FROM CLIENT, SORTIE, CONCERNER, PRODUIT 
        WHERE client.NumCli = sortie.NumCli 
        AND sortie.NumSort = concerner.NumSort 
        AND produit.numPdt = concerner.numPdt 
        GROUP BY produit.libPdt, client.numCli, client.nomCli
    """,

    "Insertion Client": """
        INSERT INTO `client`(`numCli`, `nomCli`, `precisionCli`, `villeCli`) 
        VALUES (12, 'CHIROLE', 'Quentin', 'BORDEAUX')
    """,

    "Update Client": """
        UPDATE `client` 
        SET `numCli`=12, `nomCli`='CHIROL', `precisionCli`='Quentin', `villeCli`='TOULOUSE' 
        WHERE nomCli = 'CHIROLE'
    """,

    "Delete Client": """
        DELETE FROM CLIENT 
        WHERE numCli = 12
    """,

    "Produits Achetes Plus De Deux Fois": """
        SELECT client.NumCli, client.nomCli, count(concerner.numPdt) as Nb_Achats, produit.libPdt 
        FROM CLIENT 
        JOIN SORTIE ON client.NumCli = sortie.NumCli 
        JOIN CONCERNER ON sortie.NumSort = concerner.NumSort 
        JOIN PRODUIT ON produit.numPdt = concerner.numPdt 
        GROUP BY produit.libPdt, client.numCli, client.nomCli 
        HAVING Nb_Achats >= 2
    """,

    "Produits Non Achetes En 2024": """
        SELECT p.numPdt, p.libPdt 
        FROM PRODUIT p 
        WHERE p.numPdt NOT IN (
            SELECT c.numPdt 
            FROM CONCERNER c 
            JOIN SORTIE S ON c.numSort = s.numSort 
            WHERE YEAR(s.dateSort) = 2024
        )
    """,

    "Produits Vendu En 2024": """
        SELECT p.numPdt, p.libPdt, SUM(c.qteSort) AS total_vendu 
        FROM PRODUIT p 
        JOIN CONCERNER c ON p.numPdt = c.numPdt 
        JOIN SORTIE s ON c.numSort = s.numSort 
        WHERE YEAR(s.dateSort) = 2024 
        GROUP BY p.numPdt, p.libPdt
    """,

    "Produits Faible Stock": """
        SELECT numPdt, libPdt, stockPdt 
        FROM PRODUIT 
        WHERE stockPdt < 1500
    """,

    "Vente Produit 2024 View": """
        CREATE OR REPLACE VIEW VenteProduit2024 AS
        SELECT p.numPdt, p.libPdt, IFNULL(SUM(c.qteSort), 0) AS total_vendu 
        FROM PRODUIT p 
        LEFT JOIN CONCERNER c ON p.numPdt = c.numPdt 
        LEFT JOIN SORTIE s ON c.numSort = s.numSort 
        LEFT JOIN PRIX pr ON p.numPdt = pr.numPdt 
        WHERE (YEAR(s.dateSort) = 2024 OR s.dateSort IS NULL) 
        AND (pr.Annee = 2024 OR pr.Annee IS NULL) 
        GROUP BY p.numPdt, p.libPdt
    """,

    "Produits Vendu Plus Que 700": """
        SELECT numPdt, libPdt, total_vendu 
        FROM VenteProduit2024 
        WHERE total_vendu > 700
    """
    }

        # Liste déroulante pour choisir une requête prédéfinie
        def executer_requete_predefinie(event):
            query_name = query_combobox.get()
            if query_name in predefined_queries:
                custom_query = predefined_queries[query_name]
                #executer_requete_sql(custom_query)
                sql_entry.delete(0, END)  # Efface le texte existant avant d'ajouter
                sql_entry.insert(END, custom_query)  # Insère la requête à la fin
                executer_requete_sql()

        query_label = Label(root, text="Choisissez une requête prédéfinie:")
        query_label.pack(pady=10)

        query_combobox = ttk.Combobox(root, values=list(predefined_queries.keys()))
        query_combobox.pack(pady=10)

        query_combobox.bind("<<ComboboxSelected>>", executer_requete_predefinie)

        def executer_code():
            def insert_sql(requete, db, valeurs):
                try:
                    c = db.cursor()
                    c.execute(requete, valeurs)
                    db.commit() 
                    print("Insertion réussie !")
                except Exception as e:
                    print(f"Erreur: {e}")
                    
            requete_format = {
                "entree" : "INSERT INTO {} VALUES (%s, %s, %s, %s, %s)",
                "saunier" : "INSERT INTO {} VALUES (%s, %s, %s, %s)",
                "client" : "INSERT INTO {} VALUES (%s, %s, %s, %s)",
                "sortie" : "INSERT INTO {} VALUES (%s, %s, %s)",
                "concerner" : "INSERT INTO {} VALUES (%s, %s, %s)",
            }

            fichier = ["client", "entree", "saunier", "sortie"]

            for i in range(len(fichier)):
                print(fichier[i])
                with open(fichier[i] + ".csv", mode='r', encoding='utf-8') as file:
                    csv_reader = csv.reader(file, delimiter=';')
                    requete = requete_format[fichier[i]].format(fichier[i].upper())
                    next(csv_reader)
                    for row in csv_reader:
                        if fichier[i] == "entree" :
                            row[1] = datetime.strptime(row[1], "%d/%m/%Y").strftime("%Y-%m-%d %H:%M:%S")
                        if fichier[i] == "sortie" :
                            row[1] = datetime.strptime(row[1], "%d/%m/%Y").strftime("%Y-%m-%d %H:%M:%S")
                            tuple1 = [row[0], row[1], row[2]] 
                            tuple2 = [row[3], row[0], row[4]] 
                            insert_sql(requete_format["sortie"].format("SORTIE"), db, tuple(tuple1))
                            insert_sql(requete_format["concerner"].format("CONCERNER"), db, tuple(tuple2))
                        else :
                            insert_sql(requete, db, tuple(row)) 
            messagebox.showinfo("Succès", "Insertion réussie")
            

        # Créez un bouton qui appelle la fonction 'executer_code' lorsqu'il est cliqué
        bouton = Button(root, text="Insertion csv", command=executer_code)
        bouton.pack(pady=20)

        # Lancer l'interface Tkinter
        root.mainloop()

    except mysql.connector.Error as err:
        messagebox.showerror("Erreur MySQL", f"Erreur de connexion à la base de données: {err}")
    finally:
        if db.is_connected():
            db.close()

# Appeler la fonction pour récupérer et afficher les données
recuperer_donnees(db)

