from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

# Instance de SQLAlchemy pour gérer la base de données
db = SQLAlchemy()

# Modèle représentant une question du sondage
class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)  # Identifiant unique de la question
    titre = db.Column(db.String(200), nullable=False)  # Texte de la question
    type_question = db.Column(db.String(50), nullable=False)  # Type de question (ex: multiple, dropdown, texte, etc.)
    options = db.Column(db.Text, nullable=True)  # Options de la question au format JSON (pour les types concernés)
    ordre = db.Column(db.Integer, nullable=False, default=0)  # Ordre d'affichage de la question

    def get_options(self):
        """Retourne la liste des options sous forme de liste Python."""
        return json.loads(self.options) if self.options else []

# Modèle représentant une réponse fournie par un utilisateur
class Response(db.Model):
    __tablename__ = 'responses'
    id = db.Column(db.Integer, primary_key=True)  # Identifiant unique de la réponse
    nom = db.Column(db.String(100), nullable=False)  # Nom de l'utilisateur qui a répondu
    departement = db.Column(db.String(100), nullable=True)  # Département ou pôle de l'utilisateur
    reponses = db.Column(db.Text, nullable=False)  # Réponses de l'utilisateur, enregistrées en JSON
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Date et heure de la soumission de la réponse