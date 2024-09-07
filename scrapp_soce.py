# Importation des modules nécessaires
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from Log_scraper_soce import *  # Import des logs
import time
import pandas as pd
from openpyxl import Workbook
import datetime

print("[#] - Modules importés avec succès")

# Fonction pour initialiser le webdriver et se connecter au site
def init_and_connect(usr, pswd, spec_metier): 
    print("[#] - Initialisation du webdriver et connexion au site")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("window-size=1400,1500")
    options.add_argument("--disable-gpu")
    options.add_argument("enable-automation")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--no-sandbox')  # Désactiver le sandboxing
    options.add_argument('--disable-extensions')  # Désactiver les extensions pour réduire la charge
    options.add_argument('--single-process')  # Exécuter Chrome en un seul processus
    options.add_argument('--start-maximized')

    driver = webdriver.Chrome(options=options)

    
    print("[#] - Webdriver initialisé")

    driver.get("https://www.arts-et-metiers.asso.fr/")
    print("[#] - Page d'accueil chargée")
    time.sleep(5)  # Augmentez le temps d'attente

    # Vérifiez si vous êtes sur la bonne page de connexion
    if "login" not in driver.current_url:
        print("[#] - Navigation vers la page de connexion...")
        login_link = driver.find_element(By.LINK_TEXT, "Se connecter")
        login_link.click()
        time.sleep(5)

    username = driver.find_element(By.XPATH, "//input[@name='user']")
    password = driver.find_element(By.XPATH, "//input[@name='password']")
    
    print("[#] - Champs de connexion trouvés")

    # Effacez d'abord les champs
    username.clear()
    password.clear()
    
    time.sleep(2)
    username.send_keys(usr)
    time.sleep(1)
    password.send_keys(pswd)
    time.sleep(2)

    print("[#] - Identifiants saisis")

    submit = driver.find_element(By.XPATH, "//button[@type='submit']")
    submit.click()

    print("[#] - Formulaire de connexion soumis")

    time.sleep(10)  # Attendez plus longtemps après la soumission

    # Vérifiez si la connexion a réussi
   
    print("[#] - Connexion réussie!")
    

    # Naviguer vers la page spécifique après la connexion
    driver.get("https://www.arts-et-metiers.asso.fr/people?who="+spec_metier)
    print(f"[#] - Navigation vers la page des profils pour le métier: {spec_metier}")

    return driver


def scrap_links(driver):
    links_global = []
    time.sleep(10)
    driver.find_elements(By.CSS_SELECTOR, '.sc-iSnsYj.biVAyv')[0].click()
    for i in range(1):  # Parcourir toutes les pages
        try:
            time.sleep(10)  # Attente pour le chargement des éléments
            print("[#] - scrapping links from page " + str(i+1))
            elements = driver.find_elements(By.CSS_SELECTOR, '.sc-dkjaqt.goKSRo.sc-cBYhjr.iKMYhH')
            # Extraire les attributs href de ces éléments
            links_page = [element.get_attribute('href') for element in elements]

            # Ajouter les deux premiers liens à la liste globale
            for link in links_page:
                if "messaging" in link:
                    pass
                else:
                    links_global.append(link)
                    print("[#] - Adding "+link+" to the list")

            # Passer à la page suivante
            try:
                driver.find_element(By.CSS_SELECTOR, '.sc-knesRu.cecfjh')[0].click()
            except:
                print("Pas d'autre page")
                pass

        except Exception as e:
            print("Erreur lors du scraping des liens : ", e)
            break
        
    return links_global
# Fonction pour récupérer des données à partir de chaque profil
def scrap_data(driver, list_of_links, User_name):
    print("[#] - Début du scraping des données des profils")
    data = [["Nom", "Prénom", "Propriétaire du contact", "Type de contact", "Statut du lead", "Nom de l'entreprise", "Intitulé du poste", "Adresse Mail", "Numéro de téléphone", "Profil Linkedin", "Source du contact", "Gadzart", "Secteur"]]
    
    for index, link in enumerate(list_of_links[3:]):
        if "messaging" in link:
            break
        try:
            driver.get(link)
            print(f"[#] - Scraping du profil {index+1}/{len(list_of_links)} : {link}")
            time.sleep(10)  # Attente pour le chargement de la page
            
            info = {
                "Name_prospect": (".sc-braxZu.DwTMa", "nom"),
                "Job_prospect": (".sc-braxZu.jcqcYi", "poste", 0),
                "Company_prospect": (".sc-braxZu.jcqcYi", "entreprise", 1),
                "Mail_prospect": (".sc-dnaUSb.gNFqS", "adresse e-mail"),
                "Number_prospect": (".sc-braxZu.sc-1tp6r43-1.eeDMBt.iFUuNQ", "numéro de téléphone")
            }
            
            profile_data = {}
            for key, (selector, desc, *index) in info.items():
                try:
                    element = driver.find_elements(By.CSS_SELECTOR, selector)[index[0] if index else 0] if index else driver.find_element(By.CSS_SELECTOR, selector)
                    profile_data[key] = element.text
                    print(f"[#] - {desc.capitalize()} récupéré : {profile_data[key]}")
                except Exception as e:
                    print(f"[#] - Erreur lors de la récupération de {desc} : {e}")
                    profile_data[key] = ""
            
            if profile_data["Name_prospect"]:
                parts = profile_data["Name_prospect"].split()
                First_name, Last_name = parts[0], " ".join(parts[1:])
                print(f"[#] - Prénom : {First_name}, Nom : {Last_name}")
                
                data.append([Last_name, First_name, User_name, "Prospect/client", "Nouveau", 
                             profile_data["Company_prospect"], profile_data["Job_prospect"], 
                             profile_data["Mail_prospect"], profile_data["Number_prospect"], 
                             "", "Soce", "Oui", ""])
                print(f"[#] - {profile_data['Name_prospect']} ajouté à la base de données. {len(data)} profils sur {len(list_of_links)} scrapés.")
            
        except Exception as e:
            print(f"[#] - Erreur lors du scraping du profil : {e}")
    
    print(f"[#] - Fin du scraping des données. Total de profils scrapés : {len(data)-1}")
    return data

# Fonction pour créer un fichier Excel et y écrire les données
def create_xlsx(data, name): 
    
    print(f"[#] - Création du tableau pour {name}")
    df = pd.DataFrame(data[1:], columns=data[0])
    st.write(f"Résultats pour {name}:")
    st.dataframe(df)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"Télécharger les résultats pour {name} (CSV)",
        data=csv,
        file_name=f"{name}.csv",
        mime="text/csv",
    )
    print(f"[#] - Tableau affiché et option de téléchargement ajoutée pour {name}")

# Interface Streamlit
def main():
    print("[#] - Démarrage de l'interface Streamlit")
    st.title("Scrapper de profils SOCE")

    # Champs pour le nom d'utilisateur et le mot de passe
    username = st.text_input("Nom d'utilisateur SOCE")
    password = st.text_input("Mot de passe SOCE", type="password")

    # Liste des métiers à scrapper
    # Champ de texte pour entrer les rôles personnalisés
    custom_roles = st.text_area("Entrez les rôles à scrapper (un par ligne)")
    
    # Conversion du texte en liste de rôles
    roles = [role.strip() for role in custom_roles.split('\n') if role.strip()]
    
    # Sélection multiple des métiers à scrapper
    selected_roles = st.multiselect("Sélectionnez les métiers à scrapper", roles)
    
    # Message d'information pour l'utilisateur
    st.info("Vous pouvez ajouter vos propres rôles dans le champ de texte ci-dessus.")

    if st.button("Lancer le scrapping"):
        print("[#] - Bouton de lancement du scraping cliqué")
        if not username or not password:
            st.error("Veuillez entrer votre nom d'utilisateur et votre mot de passe.")
            print("[#] - Erreur : Nom d'utilisateur ou mot de passe manquant")
        elif not selected_roles:
            st.error("Veuillez sélectionner au moins un métier à scrapper.")
            print("[#] - Erreur : Aucun métier sélectionné")
        else:
            total_scrap = 0
            for spec in selected_roles:
                print(f"[#] - Début du scraping pour le métier : {spec}")
                driver = init_and_connect(username, password, spec)
                list_of_links = scrap_links(driver)
                data = scrap_data(driver, list_of_links, User_name=username)
                create_xlsx(data, spec)
                driver.quit()
                print(f"[#] - Fin du scraping pour le métier : {spec}")

                total_scrap += len(data)
                st.write(f"[#] - Total des profils scrapés pour {spec}: {len(data)}")

            print(f"[#] - Scraping terminé. Total des profils scrapés : {total_scrap}")
            st.success(f"Scraping terminé. Total des profils scrapés : {total_scrap}")

if __name__ == "__main__":
    print("[#] - Démarrage du programme")
    main()
    print("[#] - Fin du programme")
