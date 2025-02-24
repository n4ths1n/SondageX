from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from models import db, Question, Response as DBResponse
import json
from datetime import datetime
import io
import base64
import csv
import math

# Configuration pour générer des graphiques PDF sans affichage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx

# Utilisé pour convertir du HTML en PDF
from weasyprint import HTML

# Pour créer des graphiques interactifs avec Plotly
import plotly
import plotly.graph_objs as go

# Initialisation de l'application Flask et configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///survey.db'
app.config['SECRET_KEY'] = 'votre_cle_secrete'
app.config['ADMIN_USERNAME'] = 'admin'
app.config['ADMIN_PASSWORD'] = 'admin'  # Identifiants administrateur

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Classe représentant l'utilisateur administrateur
class AdminUser(UserMixin):
    def __init__(self, id):
        self.id = id

# Charge l'utilisateur administrateur pour la session de connexion
@login_manager.user_loader
def load_user(user_id):
    if user_id == app.config['ADMIN_USERNAME']:
        return AdminUser(user_id)
    return None

# Avant chaque requête, créer les tables et insérer des questions par défaut si nécessaire
@app.before_request
def create_tables():
    db.create_all()
    if Question.query.count() == 0:
        q1 = Question(
            titre="Question très longue pour tester l'affichage : Choisissez plusieurs options si vous le souhaitez, c'est un test",
            type_question="multiple",
            options=json.dumps(["Option A", "Option B", "Option C", "Option D"]),
            ordre=0
        )
        q2 = Question(
            titre="Question 2 : Sélectionnez 9 participants",
            type_question="dropdown9",
            options=json.dumps(["Participant 1", "Participant 2", "Participant 3"]),
            ordre=1
        )
        db.session.add_all([q1, q2])
        db.session.commit()

# Route pour afficher et traiter le sondage (accessible à tous)
@app.route('/', methods=['GET', 'POST'])
def survey():
    questions = Question.query.order_by(Question.ordre).all()
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
                reponse = request.form.get(f'question_{q.id}')
            reponses_obj[str(q.id)] = reponse
        nouvelle_reponse = DBResponse(
            nom=nom,
            departement=departement,
            reponses=json.dumps(reponses_obj),
            timestamp=datetime.utcnow()
        )
        db.session.add(nouvelle_reponse)
        db.session.commit()
        flash("Merci pour votre réponse !")
        return redirect(url_for('survey'))
    return render_template('survey.html', questions=questions)

# Routes d'authentification pour l'administrateur
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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Vous avez été déconnecté.")
    return redirect(url_for('login'))

# Tableau de bord administrateur : affichage des questions et des réponses
@app.route('/admin')
@login_required
def admin_dashboard():
    questions = Question.query.order_by(Question.ordre).all()
    responses = DBResponse.query.order_by(DBResponse.timestamp.desc()).all()
    return render_template('admin.html', questions=questions, responses=responses)

# Route pour ajouter une nouvelle question
@app.route('/admin/ajouter_question', methods=['GET', 'POST'])
@login_required
def ajouter_question():
    if request.method == 'POST':
        titre = request.form.get('titre')
        type_question = request.form.get('type_question')
        options = request.form.get('options')
        options_list = [opt.strip() for opt in options.split(',')] if options else []
        dernier = Question.query.order_by(Question.ordre.desc()).first()
        nouvel_ordre = dernier.ordre + 1 if dernier else 0
        nouvelle_question = Question(
            titre=titre,
            type_question=type_question,
            options=json.dumps(options_list),
            ordre=nouvel_ordre
        )
        db.session.add(nouvelle_question)
        db.session.commit()
        flash("Question ajoutée avec succès.")
        return redirect(url_for('admin_dashboard'))
    return render_template('ajouter_question.html')

# Route pour modifier une question existante
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
        num = DBResponse.query.delete()
        db.session.commit()
        flash(f"{num} réponses supprimées avec succès.")
    except Exception:
        db.session.rollback()
        flash("Erreur lors de la suppression des réponses.")
    return redirect(url_for('admin_dashboard'))

# Route pour supprimer une réponse spécifique
@app.route('/admin/supprimer_reponse/<int:response_id>', methods=['POST'])
@login_required
def supprimer_reponse(response_id):
    reponse = DBResponse.query.get_or_404(response_id)
    db.session.delete(reponse)
    db.session.commit()
    flash("Réponse supprimée avec succès.")
    return redirect(url_for('admin_dashboard'))

# Route pour afficher une réponse détaillée
@app.route('/reponse/<int:response_id>')
@login_required
def voir_reponse(response_id):
    reponse = DBResponse.query.get_or_404(response_id)
    data = json.loads(reponse.reponses)
    return render_template('voir_reponse.html', response=reponse, data=data)

# Route pour mettre à jour l'ordre des questions via une requête JSON
@app.route('/admin/mettre_a_jour_ordre_questions', methods=['POST'])
@login_required
def mettre_a_jour_ordre_questions():
    data = request.get_json()
    nouvel_ordre = data.get('order', [])
    for index, question_id in enumerate(nouvel_ordre):
        question = Question.query.get(int(question_id))
        if question:
            question.ordre = index
    db.session.commit()
    return jsonify({'success': True})

# --- EXPORT DES DONNÉES ---

# Export au format CSV
@app.route('/admin/export/csv')
@login_required
def export_csv():
    responses = DBResponse.query.order_by(DBResponse.timestamp.desc()).all()
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(['ID', 'Nom', 'Département', 'Date', 'Reponses(JSON)'])
    for r in responses:
        writer.writerow([
            r.id,
            r.nom,
            r.departement,
            r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            r.reponses
        ])
    output = si.getvalue()
    si.close()
    return Response(output, mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=export_reponses.csv"})

# Export interactif en HTML avec Plotly
@app.route('/admin/export/html')
@login_required
def export_html():
    questions = Question.query.order_by(Question.ordre).all()
    responses = DBResponse.query.order_by(DBResponse.timestamp.desc()).all()
    rapport_data = []
    for q in questions:
        # Calculer le nombre de réponses pour chaque option
        comptages = {}
        for r in responses:
            data = json.loads(r.reponses)
            rep = data.get(str(q.id))
            if rep:
                if q.type_question in ['multiple', 'dropdown']:
                    if isinstance(rep, list):
                        for ans in rep:
                            comptages[ans] = comptages.get(ans, 0) + 1
                    else:
                        comptages[rep] = comptages.get(rep, 0) + 1
                elif q.type_question == 'dropdown9':
                    for _, val in rep.items():
                        if val:
                            comptages[val] = comptages.get(val, 0) + 1
                else:
                    comptages[rep] = comptages.get(rep, 0) + 1
        labels = list(comptages.keys())
        values = list(comptages.values())
        # Création d'un graphique en barres interactif avec Plotly
        bar_fig = go.Figure(data=[go.Bar(x=labels, y=values, marker_color='rgb(0,157,209)')])
        bar_fig.update_layout(
            title=f"Barres - {q.titre}",
            margin=dict(l=60, r=60, t=100, b=80),
            xaxis=dict(title="Options", automargin=True),
            yaxis=dict(title="Nombre de réponses")
        )
        bar_div = bar_fig.to_html(full_html=False)
        # Création d'un graphique en secteurs interactif avec Plotly
        pie_fig = go.Figure(data=[go.Pie(labels=labels, values=values, hoverinfo='label+value+percent')])
        pie_fig.update_layout(
            title=f"Secteurs - {q.titre}",
            margin=dict(l=60, r=60, t=100, b=80)
        )
        pie_div = pie_fig.to_html(full_html=False)
        # Création d'un sociogramme interactif si applicable
        sociogram_div = None
        top_3 = []
        bottom_3 = []
        if q.type_question in ['multiple', 'dropdown', 'dropdown9']:
            nodes_dict = {}
            edges_list = []
            current_id = 0
            for opt in q.get_options():
                nodes_dict[opt] = {'id': current_id, 'label': opt, 'group': 'option'}
                current_id += 1
            for r in responses:
                data = json.loads(r.reponses)
                rep = data.get(str(q.id))
                if rep:
                    if r.nom not in nodes_dict:
                        nodes_dict[r.nom] = {'id': current_id, 'label': r.nom, 'group': 'person'}
                        current_id += 1
                    if isinstance(rep, list):
                        for answer in rep:
                            if answer in nodes_dict:
                                edges_list.append((r.nom, answer))
                    elif isinstance(rep, dict):
                        for _, val in rep.items():
                            if val in nodes_dict:
                                edges_list.append((r.nom, val))
                    else:
                        if rep in nodes_dict:
                            edges_list.append((r.nom, rep))
            sorted_counts = sorted(comptages.items(), key=lambda x: x[1], reverse=True)
            top_3 = sorted_counts[:3] if len(sorted_counts) >= 3 else sorted_counts
            bottom_3 = sorted_counts[-3:] if len(sorted_counts) >= 3 else sorted_counts
            # Positionner les noeuds : les personnes sur un cercle de rayon 1, les options sur un cercle de rayon 2
            person_names = [n for n, info in nodes_dict.items() if info['group'] == 'person']
            option_names = [n for n, info in nodes_dict.items() if info['group'] == 'option']
            angle_step_person = 2 * math.pi / max(1, len(person_names))
            angle_step_option = 2 * math.pi / max(1, len(option_names))
            radius_person = 1.0
            radius_option = 2.0
            node_positions = {}
            i = 0
            for name in person_names:
                angle = i * angle_step_person
                node_positions[name] = (radius_person * math.cos(angle), radius_person * math.sin(angle))
                i += 1
            j = 0
            for name in option_names:
                angle = j * angle_step_option
                node_positions[name] = (radius_option * math.cos(angle), radius_option * math.sin(angle))
                j += 1
            edge_x = []
            edge_y = []
            for (src, dst) in edges_list:
                (x1, y1) = node_positions[src]
                (x2, y2) = node_positions[dst]
                edge_x.extend([x1, x2, None])
                edge_y.extend([y1, y2, None])
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                mode='lines',
                line=dict(width=1, color='#888'),
                hoverinfo='none'
            )
            node_x = []
            node_y = []
            node_text = []
            colors = []
            sizes = []
            for name, info in nodes_dict.items():
                (x, y) = node_positions[name]
                node_x.append(x)
                node_y.append(y)
                node_text.append(info['label'])
                if info['group'] == 'option':
                    colors.append('lightgreen')
                    sizes.append(20)
                else:
                    colors.append('lightblue')
                    sizes.append(12)
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                text=node_text,
                textposition='top center',
                hoverinfo='text',
                marker=dict(color=colors, size=sizes, line=dict(color='#555', width=1))
            )
            layout_socio = go.Layout(
                title=f"Sociogramme - {q.titre}",
                showlegend=False,
                margin=dict(l=60, r=60, t=100, b=80),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
            fig_socio = go.Figure(data=[edge_trace, node_trace], layout=layout_socio)
            sociogram_div = fig_socio.to_html(full_html=False)
        rapport_data.append({
            'question': q,
            'bar_div': bar_div,
            'pie_div': pie_div,
            'sociogram_div': sociogram_div,
            'top_3': top_3,
            'bottom_3': bottom_3
        })
    return render_template('rapport_export_interactif.html', rapport_data=rapport_data)

# Export PDF statique en utilisant Matplotlib et WeasyPrint
@app.route('/admin/export/pdf')
@login_required
def export_pdf():
    questions = Question.query.order_by(Question.ordre).all()
    responses = DBResponse.query.order_by(DBResponse.timestamp.desc()).all()
    pdf_data = []
    for q in questions:
        comptages = {}
        for r in responses:
            data = json.loads(r.reponses)
            rep = data.get(str(q.id))
            if rep:
                if q.type_question in ['multiple', 'dropdown']:
                    if isinstance(rep, list):
                        for ans in rep:
                            comptages[ans] = comptages.get(ans, 0) + 1
                    else:
                        comptages[rep] = comptages.get(rep, 0) + 1
                elif q.type_question == 'dropdown9':
                    for _, val in rep.items():
                        if val:
                            comptages[val] = comptages.get(val, 0) + 1
                else:
                    comptages[rep] = comptages.get(rep, 0) + 1
        plt.figure(figsize=(6, 4))
        if comptages:
            plt.bar(list(comptages.keys()), list(comptages.values()), color='skyblue')
            plt.title(f"Barres - {q.titre}", fontsize=10)
            plt.xlabel("Options")
            plt.ylabel("Nombre de réponses")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
        else:
            plt.text(0.5, 0.5, "Aucune réponse", ha='center', va='center', fontsize=14)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        bar_b64 = base64.b64encode(buf.getvalue()).decode()
        plt.close()
        pdf_data.append({'question': q, 'bar_chart': bar_b64})
    rendered = render_template('rapport_export_pdf.html', pdf_data=pdf_data)
    pdf = HTML(string=rendered).write_pdf()
    return Response(pdf, mimetype='application/pdf',
                    headers={"Content-Disposition": "attachment;filename=export_reponses.pdf"})

# --- GRAPHIQUES INTERACTIFS AVEC PLOTLY ---

# Afficher un graphique en barres interactif pour une question donnée
@app.route('/graphique_barre/<int:question_id>')
@login_required
def graphique_barre(question_id):
    question = Question.query.get_or_404(question_id)
    responses = DBResponse.query.all()
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
                for _, val in rep.items():
                    if val:
                        comptages[val] = comptages.get(val, 0) + 1
            else:
                comptages[rep] = comptages.get(rep, 0) + 1
    labels = list(comptages.keys())
    values = list(comptages.values())
    return render_template('graph_plotly_bar.html', question=question, labels=json.dumps(labels), values=json.dumps(values))

# Afficher un graphique en secteurs interactif pour une question donnée
@app.route('/graphique_secteurs/<int:question_id>')
@login_required
def graphique_secteurs(question_id):
    question = Question.query.get_or_404(question_id)
    responses = DBResponse.query.all()
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
                for _, val in rep.items():
                    if val:
                        comptages[val] = comptages.get(val, 0) + 1
            else:
                comptages[rep] = comptages.get(rep, 0) + 1
    labels = list(comptages.keys())
    values = list(comptages.values())
    return render_template('graph_plotly_pie.html', question=question, labels=json.dumps(labels), values=json.dumps(values))

# Afficher un sociogramme interactif pour une question donnée
@app.route('/sociogramme/<int:question_id>')
@login_required
def sociogramme(question_id):
    question = Question.query.get_or_404(question_id)
    responses = DBResponse.query.all()
    nodes_dict = {}
    edges_list = []
    current_id = 0
    # Ajouter les options comme noeuds
    for opt in question.get_options():
        nodes_dict[opt] = {'id': current_id, 'label': opt, 'group': 'option'}
        current_id += 1
    # Ajouter les répondants et créer les liens entre eux et les options
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
                for _, val in rep.items():
                    if val:
                        comptages[val] = comptages.get(val, 0) + 1
            else:
                comptages[rep] = comptages.get(rep, 0) + 1
            if r.nom not in nodes_dict:
                nodes_dict[r.nom] = {'id': current_id, 'label': r.nom, 'group': 'person'}
                current_id += 1
            if isinstance(rep, list):
                for answer in rep:
                    if answer in nodes_dict:
                        edges_list.append((r.nom, answer))
            elif isinstance(rep, dict):
                for _, val in rep.items():
                    if val in nodes_dict:
                        edges_list.append((r.nom, val))
            else:
                if rep in nodes_dict:
                    edges_list.append((r.nom, rep))
    sorted_counts = sorted(comptages.items(), key=lambda x: x[1], reverse=True)
    top_3 = sorted_counts[:3] if len(sorted_counts) >= 3 else sorted_counts
    bottom_3 = sorted_counts[-3:] if len(sorted_counts) >= 3 else sorted_counts
    # Positionnement des noeuds : répondants sur un cercle de rayon 1, options sur un cercle de rayon 2
    person_names = [name for name, info in nodes_dict.items() if info['group'] == 'person']
    option_names = [name for name, info in nodes_dict.items() if info['group'] == 'option']
    angle_step_person = 2 * math.pi / max(1, len(person_names))
    angle_step_option = 2 * math.pi / max(1, len(option_names))
    radius_person = 1.0
    radius_option = 2.0
    node_positions = {}
    i = 0
    for name in person_names:
        angle = i * angle_step_person
        node_positions[name] = (radius_person * math.cos(angle), radius_person * math.sin(angle))
        i += 1
    j = 0
    for name in option_names:
        angle = j * angle_step_option
        node_positions[name] = (radius_option * math.cos(angle), radius_option * math.sin(angle))
        j += 1
    edge_x = []
    edge_y = []
    for (src, dst) in edges_list:
        (x1, y1) = node_positions[src]
        (x2, y2) = node_positions[dst]
        edge_x.extend([x1, x2, None])
        edge_y.extend([y1, y2, None])
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=1, color='#888'),
        hoverinfo='none'
    )
    node_x = []
    node_y = []
    node_text = []
    colors = []
    sizes = []
    for name, info in nodes_dict.items():
        (x, y) = node_positions[name]
        node_x.append(x)
        node_y.append(y)
        node_text.append(info['label'])
        if info['group'] == 'option':
            colors.append('lightgreen')
            sizes.append(20)
        else:
            colors.append('lightblue')
            sizes.append(12)
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition='top center',
        hoverinfo='text',
        marker=dict(
            color=colors,
            size=sizes,
            line=dict(color='#555', width=1)
        )
    )
    layout_socio = go.Layout(
        title=f"Sociogramme - {question.titre}",
        showlegend=False,
        margin=dict(l=60, r=60, t=100, b=80),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    fig_socio = go.Figure(data=[edge_trace, node_trace], layout=layout_socio)
    sociogram_div = fig_socio.to_html(full_html=False)
    return render_template('graph_plotly_sociogram.html',
                           question=question,
                           nodes=json.dumps(nodes_dict),
                           edges=json.dumps(edges_list),
                           top_3=top_3,
                           bottom_3=bottom_3)

if __name__ == '__main__':
    app.run(host='10.150.6.51', port=5000, debug=True)