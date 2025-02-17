# application.py
# Ce fichier contient l’application Flask ainsi que toutes les routes et la logique de l’application.
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from models import db, Question, Response
import json
from datetime import datetime
import io
import base64
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import matplotlib
matplotlib.use('Agg')
import pandas as pd

# Configuration de l'application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///survey.db'
app.config['SECRET_KEY'] = 'votre_cle_secrete'
app.config['ADMIN_USERNAME'] = 'admin'
app.config['ADMIN_PASSWORD'] = 'admin'  # Compte administrateur prédéfini

# Initialisation de la base de données
db.init_app(app)

# Initialisation de flask-login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Classe utilisateur pour l'administrateur
class AdminUser(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id == app.config['ADMIN_USERNAME']:
        return AdminUser(user_id)
    return None

# Utilisation de before_request pour créer les tables et insérer des données par défaut (si nécessaire)
@app.before_request
def create_tables():
    db.create_all()
    if Question.query.count() == 0:
        q1 = Question(
            titre="Première question : Choisissez plusieurs options",
            type_question="multiple",
            options=json.dumps(["Option A", "Option B", "Option C"])
        )
        q2 = Question(
            titre="Deuxième question : Sélectionnez 9 participants",
            type_question="dropdown9",
            options=json.dumps(["Participant 1", "Participant 2", "Participant 3"])
        )
        q3 = Question(
            titre="Troisième question : Choisissez plusieurs options",
            type_question="multiple",
            options=json.dumps(["Option D", "Option E", "Option F"])
        )
        q4 = Question(
            titre="Quatrième question : Choisissez plusieurs options",
            type_question="multiple",
            options=json.dumps(["Option G", "Option H", "Option I"])
        )
        db.session.add_all([q1, q2, q3, q4])
        db.session.commit()

# Route pour le formulaire de sondage (accessible à tous)
@app.route('/', methods=['GET', 'POST'])
def survey():
    questions = Question.query.all()
    if request.method == 'POST':
        nom = request.form.get('nom')
        departement = request.form.get('departement')
        if not nom:
            flash("Le nom est obligatoire.")
            return redirect(url_for('survey'))
        reponses_obj = {}
        for q in questions:
            if q.type_question == 'multiple':
                reponse = request.form.getlist(f'question_{q.id}')
            elif q.type_question == 'dropdown':
                reponse = request.form.get(f'question_{q.id}')
            elif q.type_question == 'dropdown9':
                reponse = {}
                for i in range(1, 10):
                    reponse[str(i)] = request.form.get(f'question_{q.id}_{i}')
            else:
                # Pour les types 'texte', 'numerique', 'date', etc.
                reponse = request.form.get(f'question_{q.id}')
            reponses_obj[str(q.id)] = reponse
        nouvelle_reponse = Response(
            nom=nom,
            departement=departement,
            reponses=json.dumps(reponses_obj)
        )
        db.session.add(nouvelle_reponse)
        db.session.commit()
        flash("Merci pour votre réponse !")
        return redirect(url_for('survey'))
    return render_template('survey.html', questions=questions)

# Route de connexion pour l'administrateur
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            user = AdminUser(username)
            login_user(user)
            flash("Connexion réussie.")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect.")
            return redirect(url_for('login'))
    return render_template('login.html')

# Route de déconnexion
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Vous avez été déconnecté.")
    return redirect(url_for('login'))

# Tableau de bord de l'administrateur
@app.route('/admin')
@login_required
def admin_dashboard():
    questions = Question.query.all()
    responses = Response.query.all()
    return render_template('admin.html', questions=questions, responses=responses)

# Route pour ajouter une question
@app.route('/admin/ajouter_question', methods=['GET', 'POST'])
@login_required
def ajouter_question():
    if request.method == 'POST':
        titre = request.form.get('titre')
        type_question = request.form.get('type_question')
        options = request.form.get('options')
        options_list = [opt.strip() for opt in options.split(',')] if options else []
        nouvelle_question = Question(
            titre=titre,
            type_question=type_question,
            options=json.dumps(options_list)
        )
        db.session.add(nouvelle_question)
        db.session.commit()
        flash("Question ajoutée avec succès.")
        return redirect(url_for('admin_dashboard'))
    return render_template('ajouter_question.html')

# Route pour modifier une question
@app.route('/admin/modifier_question/<int:question_id>', methods=['GET', 'POST'])
@login_required
def modifier_question(question_id):
    question = Question.query.get_or_404(question_id)
    if request.method == 'POST':
        question.titre = request.form.get('titre')
        question.type_question = request.form.get('type_question')
        options = request.form.get('options')
        options_list = [opt.strip() for opt in options.split(',')] if options else []
        question.options = json.dumps(options_list)
        db.session.commit()
        flash("Question modifiée avec succès.")
        return redirect(url_for('admin_dashboard'))
    options_str = ', '.join(question.get_options())
    return render_template('modifier_question.html', question=question, options_str=options_str)

# Route pour supprimer une question
@app.route('/admin/supprimer_question/<int:question_id>', methods=['POST'])
@login_required
def supprimer_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash("Question supprimée avec succès.")
    return redirect(url_for('admin_dashboard'))

# Route pour supprimer toutes les réponses
@app.route('/admin/supprimer_toutes_reponses', methods=['POST'])
@login_required
def supprimer_toutes_reponses():
    try:
        num = Response.query.delete()
        db.session.commit()
        flash(f"{num} réponses supprimées avec succès.")
    except Exception as e:
        db.session.rollback()
        flash("Erreur lors de la suppression des réponses.")
    return redirect(url_for('admin_dashboard'))

# --- Visualisations par question dans l'administration ---

# Graphique en Barres
@app.route('/graphique_barre/<int:question_id>')
@login_required
def graphique_barre(question_id):
    question = Question.query.get_or_404(question_id)
    responses = Response.query.all()
    comptages = {}
    for r in responses:
        data = json.loads(r.reponses)
        rep = data.get(str(question.id))
        if rep:
            if question.type_question in ['multiple', 'dropdown']:
                if isinstance(rep, list):
                    for ans in rep:
                        comptages[ans] = comptages.get(ans, 0) + 1
                else:
                    comptages[rep] = comptages.get(rep, 0) + 1
            elif question.type_question == 'dropdown9':
                for key, val in rep.items():
                    if val:
                        comptages[val] = comptages.get(val, 0) + 1
            else:
                # Pour les types 'texte', 'numerique', 'date', etc.
                comptages[rep] = comptages.get(rep, 0) + 1
    plt.figure(figsize=(12,8))
    plt.bar(list(comptages.keys()), list(comptages.values()), color='skyblue')
    plt.title("Graphique en Barres - " + question.titre)
    plt.xlabel("Options")
    plt.ylabel("Nombre de réponses")
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return render_template('graph.html', graph_url=graph_url, titre=question.titre, type_graph="Barres")

# Graphique en Secteurs (Pie)
@app.route('/graphique_secteurs/<int:question_id>')
@login_required
def graphique_secteurs(question_id):
    question = Question.query.get_or_404(question_id)
    responses = Response.query.all()
    comptages = {}
    for r in responses:
        data = json.loads(r.reponses)
        rep = data.get(str(question.id))
        if rep:
            if question.type_question in ['multiple', 'dropdown']:
                if isinstance(rep, list):
                    for ans in rep:
                        comptages[ans] = comptages.get(ans, 0) + 1
                else:
                    comptages[rep] = comptages.get(rep, 0) + 1
            elif question.type_question == 'dropdown9':
                for key, val in rep.items():
                    if val:
                        comptages[val] = comptages.get(val, 0) + 1
            else:
                comptages[rep] = comptages.get(rep, 0) + 1
    plt.figure(figsize=(12,8))
    plt.pie(list(comptages.values()), labels=list(comptages.keys()), autopct='%1.1f%%', startangle=140)
    plt.title("Graphique en Secteurs - " + question.titre)
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return render_template('graph.html', graph_url=graph_url, titre=question.titre, type_graph="Secteurs")

# Sociogramme
@app.route('/sociogramme/<int:question_id>')
@login_required
def sociogramme(question_id):
    question = Question.query.get_or_404(question_id)
    responses = Response.query.all()
    # Création d'un graphe biparti : répondants et options
    G = nx.Graph()
    options = question.get_options()
    for opt in options:
        G.add_node(opt, bipartite='answers')
    for r in responses:
        data = json.loads(r.reponses)
        rep = data.get(str(question.id))
        if rep:
            G.add_node(r.nom, bipartite='respondents')
            if isinstance(rep, list):
                for answer in rep:
                    if answer:
                        G.add_edge(r.nom, answer)
            elif isinstance(rep, dict):
                for key, answer in rep.items():
                    if answer:
                        G.add_edge(r.nom, answer)
            else:
                G.add_edge(r.nom, rep)
    pos = nx.spring_layout(G)
    plt.figure(figsize=(12,8))
    respondents = [n for n, d in G.nodes(data=True) if d.get('bipartite')=='respondents']
    answers = [n for n, d in G.nodes(data=True) if d.get('bipartite')=='answers']
    nx.draw_networkx_nodes(G, pos, nodelist=respondents, node_color='lightblue', node_size=300, label="Répondants")
    nx.draw_networkx_nodes(G, pos, nodelist=answers, node_color='lightgreen', node_size=500, label="Options")
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_labels(G, pos, font_size=8)
    plt.title("Sociogramme pour: " + question.titre)
    plt.axis('off')
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return render_template('sociogramme.html', graph_url=graph_url, question=question)

# Route pour voir la réponse individuelle d'un utilisateur
@app.route('/reponse/<int:response_id>')
@login_required
def voir_reponse(response_id):
    response = Response.query.get_or_404(response_id)
    data = json.loads(response.reponses)
    return render_template('voir_reponse.html', response=response, data=data)

if __name__ == '__main__':
    app.run(host='X.X.X.X', port=5000, debug=True)
