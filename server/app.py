from flask import Flask, jsonify
from models import db
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from datetime import timedelta
from auth_routes import auth_bp
from quiz_routes import quiz_bp
from question_routes import question_bp
import os
from sqlalchemy.pool import NullPool

# Carrega as variáveis do ficheiro .env
load_dotenv()

app = Flask(__name__)

# Configuração usando as variáveis de ambiente
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=5)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=1)

# OTIMIZAÇÃO PARA SERVERLESS (Vercel)
# Usamos NullPool para fechar as conexões imediatamente após cada pedido, 
# evitando o erro "too many connections" no servidor da ESTGOH.
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "poolclass": NullPool,
}

db.init_app(app)
jwt = JWTManager(app)

# Handlers de Erro
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"message": "Recurso não encontrado no Vercel"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"message": "Método HTTP não permitido para este recurso"}), 405

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"message": "Erro interno no servidor (Verifique a ligação à Base de Dados no Vercel)"}), 500

@app.route('/')
def home():
    return jsonify({"message": "Bem-vindo à API do LetsQuiz (Segura)!"})

# Registo de Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(quiz_bp, url_prefix='/quizzes')
app.register_blueprint(question_bp, url_prefix='/questions')

if __name__ == '__main__':
    app.run(debug=True)
