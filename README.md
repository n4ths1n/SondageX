# Projet Sondage - Gestion de Projets

Une application web Flask pour gérer des sondages interactifs dans le cadre de la gestion de projets. Ce projet permet aux utilisateurs de répondre à un formulaire interactif et offre une interface administrateur pour gérer les questions, analyser les réponses et exporter les données sous divers formats (CSV, HTML interactif et PDF).

---

## Fonctionnalités

- **Sondage interactif** :
  - Formulaire public avec navigation étape par étape (wizard).
  - Collecte des informations personnelles (nom, département) et réponses aux questions (types multiples, dropdown, texte, numérique, date).

- **Interface administrateur** :
  - Connexion sécurisée via Flask-Login.
  - Tableau de bord pour gérer les questions et visualiser les réponses.
  - Possibilité d'ajouter, modifier, supprimer et réorganiser les questions (glisser-déposer).

- **Visualisations interactives** :
  - Graphiques en barres et en secteurs interactifs créés avec Plotly.
  - Sociogramme interactif pour visualiser les relations entre répondants et options.

- **Exportation des données** :
  - Export CSV des réponses.
  - Rapport interactif en HTML (avec graphiques Plotly).
  - Rapport statique en PDF généré avec Matplotlib et WeasyPrint.

---

## Technologies Utilisées

- **Flask** -- Framework web Python léger.
- **Flask-SQLAlchemy** -- Gestion de la base de données avec SQLAlchemy.
- **Flask-Login** -- Authentification et gestion des sessions.
- **Plotly** -- Création de graphiques interactifs.
- **Matplotlib** -- Génération de graphiques statiques pour le PDF.
- **WeasyPrint** -- Conversion de HTML en PDF.
- **Bootstrap** -- Framework CSS pour une interface réactive.
- **Font Awesome** -- Collection d'icônes.

---

## Installation

1. **Cloner le dépôt GitHub :**

```
   git clone https://github.com/n4ths1n/SondageX
```

2.  **Créer un environnement virtuel et installer les dépendances :**

```
python3 -m venv venv
source venv/bin/activate   # Sur Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3.  **Configurer la base de données :**

Par défaut, l'application utilise SQLite (fichier survey.db). Vous pouvez adapter la configuration dans application.py.

4.  **Lancer l'application :**

```
python application.py
```

L'application sera accessible à l'adresse <http://X.X.X.X:5000>.

**Structure du Projet**

```bash
.
├── application.py         # Point d'entrée et logique serveur de l'application Flask
├── models.py              # Définition des modèles de données (Question et Response)
├── templates/             # Dossier contenant tous les fichiers de templates HTML
│   ├── admin.html         # Tableau de bord administrateur
│   ├── ajouter_question.html   # Formulaire d'ajout de question
│   ├── base.html          # Template de base pour l'ensemble des pages
│   ├── graph_ploty_bar.html     # Graphique interactif en barres (Plotly)
│   ├── graph_plotly_pie.html    # Graphique interactif en secteurs (Plotly)
│   ├── graph_plotly_sociogram.html  # Sociogramme interactif (Plotly)
│   ├── graph.html         # Affichage statique d'un graphique (image Base64)
│   ├── login.html         # Formulaire de connexion pour l'administrateur
│   ├── modifier_question.html   # Formulaire de modification de question
│   ├── rapport_export_interactif.html  # Rapport interactif en HTML
│   ├── rapport_export_pdf.html  # Rapport statique en PDF
│   ├── rapport_export.html      # Rapport détaillé avec téléchargement des graphiques
│   ├── sociogramme.html   # Affichage statique du sociogramme (image Base64)
│   ├── survey.html        # Formulaire public du sondage (wizard)
│   └── voir_reponse.html  # Affichage détaillé d'une réponse
└── README.md              # Documentation et instructions (ce fichier)
```

**Utilisation**

**Sondage Public**

-  Rendez-vous sur l'URL racine pour accéder au formulaire du sondage.

-  Remplissez le formulaire en fournissant vos informations personnelles et vos réponses aux questions.

-  Utilisez les boutons "Précédent" et "Suivant" pour naviguer entre les étapes.

-  Une fois le formulaire soumis, un message de remerciement s'affiche.

**Interface Administrateur**

-  Accédez à /login pour vous connecter en tant qu'administrateur (identifiants par défaut : admin / admin).

-  Une fois connecté, le tableau de bord vous permet de :

-  Gérer les questions (ajouter, modifier, supprimer, réorganiser).

-  Visualiser et supprimer les réponses.

-  Exporter les données sous différents formats (CSV, HTML interactif, PDF).

-  Afficher des graphiques interactifs pour analyser les réponses.

**Remarques**

-  **Configuration par défaut :**

L'application est configurée pour s'exécuter sur l'hôte X.X.X.X et le port 5000. Vous pouvez modifier ces paramètres dans application.py.

-  **Initialisation de la Base de Données :**

Lors de la première exécution, si aucune question n'est présente, des questions par défaut seront insérées automatiquement dans la base de données.

-  **Dépendances :**

Assurez-vous d'avoir installé toutes les dépendances listées dans le fichier requirements.txt.
