# Utiliser une image de base officielle de Python
FROM python:3.8-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /Scrapper_AMJE

# Copier le fichier de dépendances et installer les dépendances
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l'application
COPY . .

# Exposer le port sur lequel l'application va s'exécuter
EXPOSE 8501

# Définir la commande par défaut pour exécuter l'application
CMD ["streamlit", "run", "scrapp_soce.py"]