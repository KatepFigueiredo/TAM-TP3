from flask import Blueprint, request, jsonify
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data=request.get_json()

    # 1. Verificar se o utilizador já existe
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Utilizador ja existe'}), 400

    # 2. Encriptar a password
    hashed_pw = generate_password_hash(data['password'])

    # 3. Guardar na Base de Dados
    new_user = User(username=data['username'], password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()

    # 4. Criar o token de acesso e refresh
    access_token = create_access_token(identity=str(new_user.id))
    refresh_token = create_refresh_token(identity=str(new_user.id))

    # 5. Devolver os tokens
    return jsonify({
        'access_token': access_token, 
        'refresh_token': refresh_token,
        'username': new_user.username
    }), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    data=request.get_json()

    # 1. Verificar se o utilizador existe
    user = User.query.filter_by(username=data['username']).first()
    if not user:
        return jsonify({'error': 'Utilizador nao encontrado'}), 404

    # 2. Verificar a password
    if not check_password_hash(user.password, data['password']):
        return jsonify({'error': 'Password incorrecta'}), 401

    # 3. Criar os tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    # 4. Devolver os tokens
    return jsonify({
        'access_token': access_token, 
        'refresh_token': refresh_token,
        'username': user.username
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify({'access_token': new_access_token}), 200
