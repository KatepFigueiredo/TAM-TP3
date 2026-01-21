from flask import Flask, jsonify
from models import db
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from datetime import timedelta
from auth_routes import auth_bp
from quiz_routes import quiz_bp
from question_routes import question_bp
import os

# Carrega as variáveis do ficheiro .env
load_dotenv()

app = Flask(__name__)

# Configuração usando as variáveis de ambiente
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=5)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=1)

# Define o debug mode com base na variável de ambiente (False por padrão para produção)
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# OTIMIZAÇÃO DE CONEXÕES (Requisito para bases de dados remotas com limites)
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_size": 2,          # Mantém apenas 2 ligações abertas
    "max_overflow": 0,       # Não permite criar mais do que o limite
    "pool_recycle": 300,     # Recicla a ligação a cada 5 minutos
    "pool_pre_ping": True    # Verifica se a ligação está viva antes de usar
}

db.init_app(app)
jwt = JWTManager(app)

# --- Handlers de Erro Globais para retornar JSON ---
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"message": "Recurso não encontrado"}), 404

@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({"message": "Método HTTP não permitido para este recurso"}), 405

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback() # Garante que a sessão da BD é revertida em caso de erro
    return jsonify({"message": "Ocorreu um erro interno no servidor"}), 500

@app.route('/')
def home():
    return jsonify({"message": "Bem-vindo à API do LetsQuiz (Segura)!"})

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(quiz_bp, url_prefix='/quizzes')
app.register_blueprint(question_bp, url_prefix='/questions')

if __name__ == '__main__':
    with app.app_context():
        # db.create_all() # Comentado porque as tabelas já devem existir na BD da escola
        pass
    app.run(debug=app.config['DEBUG'], host='0.0.0.0')