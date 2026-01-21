from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable = False, unique = True)
    password = db.Column(db.String(255), nullable = False)
    # Relação: Um utilizador pode ter vários quizzes
    quizzes = db.relationship('Quiz', backref='author', lazy=True)

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique = True, nullable = False)
    description = db.Column(db.String(255))
    max_time = db.Column(db.Integer, default = 60)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    active_sessions = db.Column(db.Integer, default = 0)
    # Relação: Um quiz pode ter várias questões
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable = False)
    # Vamos guardar como string separada por | ou JSON
    answers = db.Column(db.Text, nullable = False)
    correct_answer_index = db.Column(db.Integer, nullable = False)
    url_image = db.Column(db.String(255))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable = False)
