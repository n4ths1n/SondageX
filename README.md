# Documentation du Projet Sondage

## Introduction

Ce projet est une application web de sondage conçue pour permettre aux utilisateurs de répondre à des questionnaires et aux administrateurs de gérer dynamiquement les questions et de visualiser les réponses sous différents formats graphiques (graphique en barres, graphique en secteurs, sociogramme). L'application est construite avec **Python** et **Flask**, utilise **SQLAlchemy** pour la gestion de la base de données et **Flask-Login** pour l'authentification de l'administrateur. L'interface est réalisée avec **Bootstrap** (pour une expérience responsive) et **Font Awesome** (pour les icônes).

---

## Structure du Projet

Le projet est organisé comme suit :

```
projet/
├── application.py         # Fichier principal de l'application Flask
├── models.py              # Définition des modèles de données (Question, Response)
├── README.md              # Documentation complète (ce fichier)
└── templates/             # Dossier contenant tous les fichiers HTML
    ├── base.html          # Template de base (inclus les liens vers Bootstrap, Font Awesome, favicon, etc.)
    ├── survey.html        # Formulaire de sondage accessible aux utilisateurs (mode "wizard")
    ├── login.html         # Formulaire de connexion pour l'administrateur
    ├── admin.html         # Tableau de bord de l'administrateur (gestion des questions, réponses et visualisations)
    ├── ajouter_question.html  # Formulaire pour ajouter une question
    ├── modifier_question.html # Formulaire pour modifier une question existante
    ├── graph.html         # Page d'affichage d'un graphique (barres ou secteurs)
    ├── sociogramme.html   # Page d'affichage du sociogramme d'une question
    └── voir_reponse.html  # Page d'affichage détaillé d'une réponse individuelle
└── static/                # Dossier pour les fichiers statiques
    ├── logo.ico    # Favicon
    └── logo.jpg    # Logo de l'entreprise
```

---

## Prérequis

- **Python 3.x** installé sur votre machine.
- Les modules Python suivants doivent être installés :

```bash
pip install flask flask_sqlalchemy flask_login matplotlib networkx pandas
```

---

## Installation et Configuration

1. **Cloner le projet** dans votre répertoire de travail.

2. **Créer un environnement virtuel** (optionnel, mais recommandé) :

   - Sous Windows :
     ```batch
     python -m venv env
     env\Scripts\activate
     ```
   - Sous Linux/Mac :
     ```bash
     python3 -m venv env
     source env/bin/activate
     ```

3. **Installer les dépendances** (si ce n'est pas déjà fait) :
   ```bash
   pip install flask flask_sqlalchemy flask_login matplotlib networkx pandas
   ```

4. **Placer les fichiers statiques** :
   - Copiez le fichier `logo.ico` dans le dossier `static/` (ce sera votre favicon).
   - Copiez le fichier `logo.jpg` dans le dossier `static/` (ce sera le logo de l'entreprise).

5. **Exécuter l'application** :

   Depuis la racine du projet, lancez :
   ```bash
   python application.py
   ```
   L'application sera accessible à l'adresse [http://X.X.X.X:5000](http://X.X.X.X:5000).

6. **Accéder à l'interface administrateur** :

   Rendez-vous sur [http://X.X.X.X:5000/login](http://X.X.X.X:5000/login)  
   (Identifiant : **admin**, Mot de passe : **admin**).

---

## Description des Fichiers Clés

### 1. `application.py`

- **Configuration de Flask et SQLAlchemy** :  
  Initialise l'application avec la base de données SQLite et définit la clé secrète.

- **Gestion de l'authentification** :  
  Utilise **Flask-Login** pour gérer l'administrateur (compte prédéfini `admin`/`admin`).

- **Routes Principales** :
  - `/` : Affiche le formulaire de sondage accessible à tous les utilisateurs.
  - `/login` et `/logout` : Gèrent la connexion/déconnexion de l'administrateur.
  - `/admin` : Tableau de bord de l'administrateur permettant de gérer les questions et de visualiser les réponses.
  - Routes pour ajouter, modifier et supprimer des questions.
  - Routes pour afficher les visualisations (graphique en barres, graphique en secteurs, sociogramme) pour chaque question.
  - Route pour afficher une réponse individuelle (`/reponse/<int:response_id>`).

- **Note sur `@app.before_request`** :  
  La fonction décorée par `@app.before_request` est utilisée pour créer les tables et insérer des données par défaut si aucune question n'existe.

### 2. `models.py`

- **Modèle `Question`** :
  - `titre` : Le texte de la question.
  - `type_question` : Le type de réponse attendu (par exemple : `multiple`, `dropdown`, `dropdown9`, `texte`, `numerique`, `date`).
  - `options` : Options de réponse au format JSON (utilisé pour certains types comme `multiple` ou `dropdown`).

- **Modèle `Response`** :
  - `nom` : Nom et prénom du répondant.
  - `departement` : Département du répondant.
  - `reponses` : Réponses données par le répondant (stockées en JSON).
  - `timestamp` : Date et heure de la réponse.

### 3. Templates HTML

- **`base.html`** :  
  Le template de base qui inclut :
  - La balise meta viewport pour rendre le site responsive.
  - Liens vers Bootstrap et Font Awesome.
  - Le favicon (affiché via `logo.ico`).
  - Une structure de base pour afficher les messages flash et le contenu des autres templates.

- **`survey.html`** :  
  Le formulaire de sondage pour les utilisateurs en mode "wizard" (multi-étapes) :
  - Étape 0 : Informations personnelles (Nom, Prénom et Département via un dropdown).
  - Étapes suivantes : Une étape par question. Le type de champ affiché dépend du `type_question` de chaque question (checkbox, dropdown, champ texte, numérique, date, etc.).
  - Étape finale : Message de remerciement et bouton "Fermer la fenêtre" centré.
  
- **`login.html`** :  
  Formulaire de connexion pour l'administrateur.

- **`admin.html`** :  
  Tableau de bord de l'administrateur permettant de :
  - Gérer les questions (ajouter, modifier, supprimer).
  - Visualiser les options de visualisation pour chaque question (graphique en barres, en secteurs, sociogramme) via des boutons avec icônes Font Awesome.
  - Visualiser la liste des réponses et accéder à une vue détaillée pour chaque réponse.
  - Supprimer toutes les réponses avec un bouton dédié.

- **`ajouter_question.html` et `modifier_question.html`** :  
  Formulaires pour créer ou modifier une question. L'administrateur peut choisir le `type_question` parmi plusieurs options (`multiple`, `dropdown`, `dropdown9`, `texte`, `numerique`, `date`) et saisir les options de réponse (si applicable).

- **`graph.html`** :  
  Affiche un graphique généré (barres ou secteurs) pour une question donnée.

- **`sociogramme.html`** :  
  Affiche le sociogramme pour une question donnée (représentation graphique des relations entre répondants et options de réponse).

- **`voir_reponse.html`** :  
  Affiche en détail les réponses fournies par un utilisateur.

### 4. Fichier Static

- **`logo.ico`** :  
  Le favicon du site.
- **`logo.jpg`** :  
  Le logo de l'entreprise affiché dans le formulaire de sondage.

---

## Responsive Design

Le fichier **`base.html`** inclut la balise meta viewport :

```html
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
```

Grâce à Bootstrap, l'application est responsive et s'affiche correctement sur mobiles, tablettes et ordinateurs.

---

## Utilisation et Navigation

1. **Accès au Formulaire Utilisateur** :
   - Rendez-vous sur [http://X.X.X.X:5000](http://X.X.X.X:5000).
   - Le formulaire en mode "wizard" vous demandera vos informations personnelles, puis vous guidera question par question.
   - Une fois terminé, un message de remerciement s'affiche avec un bouton "Fermer la fenêtre" centré.

2. **Accès à l'Administration** :
   - Rendez-vous sur [http://X.X.X.X:5000/login](http://X.X.X.X:5000/login) pour vous connecter en tant qu'administrateur (identifiant: **admin**, mot de passe: **admin**).
   - Dans le tableau de bord, vous pouvez :
     - Gérer les questions (ajouter, modifier, supprimer).
     - Visualiser les réponses avec différents types de graphiques (barres, secteurs, sociogramme).
     - Supprimer toutes les réponses via un bouton dédié.
     - Voir le détail d'une réponse individuelle en cliquant sur l'icône "oeil".

---

## Personnalisation des Types de Questions

Lors de la création ou modification d'une question, l'administrateur peut choisir le type de question parmi :

- **multiple** : Plusieurs réponses possibles (checkboxes).
- **dropdown** : Choix unique dans un menu déroulant.
- **dropdown9** : Neuf menus déroulants pour une question nécessitant plusieurs sélections distinctes.
- **texte** : Champ de texte libre.
- **numerique** : Champ de saisie numérique.
- **date** : Sélecteur de date.

Les options de réponse sont saisies dans un champ (pour les types `multiple`, `dropdown` et `dropdown9`) en les séparant par des virgules.

---

## Visualisations Graphiques

Pour chaque question, trois options de visualisation sont disponibles dans l'administration :

- **Graphique en Barres** : Affiche le nombre de réponses pour chaque option.
- **Graphique en Secteurs** : Affiche la répartition en pourcentages des réponses.
- **Sociogramme** : Représente graphiquement les relations entre les répondants et les options de réponse (utilise NetworkX).

Ces visualisations sont générées à la volée et affichées via des pages dédiées.

---

## Sécurité et Authentification

L'authentification est gérée via **Flask-Login**. Seul l'administrateur (compte prédéfini) peut accéder aux pages d'administration et gérer les questions/réponses.

---

## Mise en Production

Pour déployer ce projet en production, il est recommandé d'utiliser un serveur WSGI (par exemple, **Gunicorn** ou **uWSGI**) et éventuellement de configurer un proxy inversé (avec **Nginx** ou **Apache**) pour gérer les requêtes et le domaine (vous pouvez remplacer l'IP par un nom de domaine).

---

## Conclusion

Ce projet offre une solution complète pour la réalisation et la gestion de sondages en ligne. Il intègre :

- Un formulaire utilisateur responsive et moderne.
- Un tableau de bord administrateur complet avec gestion dynamique des questions et visualisations graphiques.
- La possibilité de choisir différents types de réponses et d'afficher des visualisations détaillées.

Nous espérons que cette documentation détaillée vous aidera à comprendre, déployer et personnaliser le projet selon vos besoins.  
