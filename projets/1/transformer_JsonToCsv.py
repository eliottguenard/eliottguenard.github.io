# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import csv
import json
from datetime import datetime


def nettoyerTexte(texte):
    if isinstance(texte, str):  # Vérifie si le champ est une chaîne de caractères
        if len(texte)> 30000:
            # on prend les 30000 premiers caractères car une cellule excel ne peut contenir plus de caractères que ça
            texte = texte[:30000]
        return texte.replace("\n", " ")  # Remplace les \n par des espaces pour pas qu'il n'y ai de retour de lignes en trop
    elif texte is None:
        return ""
    return str(texte)
    # renvoie le texte en chaine si c'est ni de la chaine ni None

colonne  = ["id","url","title","lead_text","description","tags","date_start","date_end","address_name","address_street","address_zipcode","address_city","lat_lon","pmr","blind","deaf","transport","contact_phone","contact_mail","contact_url","access_type","price_detail","cover_url"]
entete = ["ID","URL","Titre","Chapeau","Description","Mots clés","Date de début","Heure de début","Date de fin","Heure de Fin","Nom du lieu","Adresse du lieu","Code Postal","Ville","Coordonnées géographiques","Accès PMR","Accès mal voyant","Accès mal entendant","Transport","Téléphone de contact","Email de contact","Url de contact","Type d’accès","Détail du prix","URL de l’image de couverture"]
# pour remplacer les noms des colonnes par les noms en français plus tard
try:
    
    fichier = open("que-faire-a-paris-.json","r", encoding = "utf-8")
    # ouverture avec le bon encodage pour les caractères spéciaux
    tousLesDico = json.loads(fichier.read())
    # ouverture du dossier json a transformer
    fichier.close()
    try:
            
        fichierCSV = open("CSV.csv","w",encoding = "utf-8-sig", newline = '')
        ecritCSV = csv.writer(fichierCSV,delimiter  = ";")
        ecritCSV.writerow(entete)
        # ouverture du fichier csv dans lequel on va écrire avec écriture des noms de colonnes (la liste au dessus)
        
        for j in range(len(tousLesDico)):
            ligne = []
            # on crée un liste vide dans laquelle on va rentrer chaque élément un a un
            evenement = tousLesDico[j]
            # on parcours la liste des dictionnaires un a un
            
            if not isinstance(evenement, dict):
              print(f"L'élément à l'indice {j} n'est pas un dictionnaire.")
              continue 
            # regarder si c'est bien un dico, sinon on le passe
            
            for i in range(len(colonne)):
                dedans = False
                # on initialise un booléen qui permet de vérifier si la clé qu'on cherche est bien là
                
                for cle, valeur in evenement.items():
                    
                    if cle == colonne[i]:
                        dedans = True
                        # check si la valeur de la clé correspond a la colonne pour que les valeurs aillent dans les bonnes colonnes
                        
                        if (cle == 'date_start' or cle == 'date_end'):
                            # dates et heures sont sous un format particulier donc on les gère séparement, ca les cherche
                            # on s'occupe des dates en premier
                            if valeur == None or valeur == '':
                                # regarde si la valeur est vide ou égale à None
                                ligne.append("")
                                ligne.append("")
                                # met un espace pour laisser la place vide si il n'y a pas de date ou pas d'heure
                                
                            else:
                                
                                try:
                                    date = datetime.fromisoformat(valeur.split('T')[0])
                                    # le T sépare la date et l'heure avec le T qui est au milieu
                                    # le [O] indique qu'on prend la première partie de ce qui a été séparé donc la date
                                    dateFr = date.strftime("%d/%m/%Y")
                                    # transforme la date en format francais
                                    heure = str(valeur[11:19])
                                    # s'occupe des heures ensuite
                                    ligne.append(dateFr)
                                    ligne.append(heure)
                                    # sépare correctement les dates et les heures séparément
                                    
                                except ValueError:
                                    ligne.append("")
                                    ligne.append("")
                                    # sinon ca mets des espaces pour que ca soit vide
                                    
                        # on a fait les dates donc on fait le reste
                        else:
                            
                            if valeur == None:
                                ligne.append("")
                                # si c'est vide (none) alors on laisse un espace pour que la case soit vide
                                
                            else:
                                if isinstance(valeur,str):
                                    if "<"  in valeur and ">"  in valeur:
                                        soup = BeautifulSoup(valeur, "html.parser")
                                        valeur = soup.getText()
                                    # ca permet de nettoyer le texte et d'enlever les balises html
                                        
                                    if  valeur and (valeur[0] == '0' or valeur[0] == '+'):
                                        valeur = f"'{valeur}"
                                        # pour garder les 0 non-significatifs 
                                        # garder le + devant les numéros de téléphone aussi
                                ligne.append(nettoyerTexte(valeur))
                                
                if dedans == False:
                    # si il n'ya pas de 'datestart' on met des cases vides grâce aux espaces
                    if i == 6  or i == 8:
                        # le 6 et le 8 sont les indices de date_start et date_end
                        ligne.append("")
                        
                    ligne.append("")
                    
            ecritCSV.writerow(ligne)
            # écrit les lignes 
        fichierCSV.close()
        # pour fermer le fichier
    except PermissionError:
        print("Vous n'avez pas la permission")
        # au cas ou on ne peut pas écrire dans le répertoire ou si le fichier est déjà ouvert, lecture seule, etc.
    except OSError:
        print("Erreur du système de fichiers")
        # au cas erreur du systeme d'exploitation
except FileNotFoundError:
    print('Fichier "que-faire-a-paris-.json" introuvable')
    # si on ne trouve pas le fichier
except json.JSONDecodeError:
    print("Erreur de décodage JSON, le fichier n'est pas correctement formaté.")
    # au cas ou le fichier importé n'est pas en json ou mal formaté
    # par exemple pas d'accolade fermante etc.
except UnicodeDecodeError:
    print("Erreur d'encodage lors de la lecture du fichier JSON.")
    # au cas l'encodage ne fonctionne pas correctement