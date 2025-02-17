# models.py
# Ce fichier contient les modèles de données pour le projet.
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    type_question = db.Column(db.String(50), nullable=False)  # 'multiple', 'dropdown', 'dropdown9', 'texte', 'numerique', 'date'
    options = db.Column(db.Text, nullable=True)  # Options stockées au format JSON

    def get_options(self):
        # Retourne la liste des options sous forme de liste Python
        return json.loads(self.options) if self.options else []

class Response(db.Model):
    __tablename__ = 'responses'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    departement = db.Column(db.String(100), nullable=True)
    reponses = db.Column(db.Text, nullable=False)  # Stocke les réponses sous forme d'objet JSON
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

