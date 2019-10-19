# dockerfile

# préparation de l'environnement
# ce fichier est appelé par docker-compose pour fabriquer l'image utilisée par l'environnement

# version python utilisée
FROM python:3.6

# variable d'environnement pour python
ENV PYTHONUNBUFFERED 1

# préparation de l'environnement
# le répertoire de travail de l'application
WORKDIR /usr/src/app

# installation des requirements
COPY /config/requirements.txt ./
RUN pip install -r requirements.txt

# installation des fichiers de l'application dans le container
COPY . .

## première migration pour utiliser l'admin du django
RUN python3 manage.py migrate

# le port utilisé
EXPOSE 8000

# lancement du server dans le container
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]
