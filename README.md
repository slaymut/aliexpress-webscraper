# Mon Projet

## Description
Ce projet est une application web développée avec Docker.

## Prérequis
Assurez-vous d'avoir Docker et Docker Compose installés sur votre machine.

## Installation
1. Clonez ce dépôt sur votre machine.
2. Naviguez vers le répertoire du projet.
3. Exécutez la commande suivante pour démarrer l'application :
  ```shell
  docker-compose up -d
  ```
4. Arrêtez la avec:
  ```shell
  docker-compose down
  ```

## Utilisation
Une fois l'application lancée, vous pouvez accéder à celle-ci dans votre navigateur en utilisant l'adresse suivante : `http://localhost:8000` ou `http://127.0.0.1:8000`.

Vous trouverez trois composants:
- le principale conntenant le formulaire ainsi que la méthode de scraping
- un bouton de recherche des meilleurs items dans la base de données
- un bouton de recherche des meilleurs magasins dans la base de données

