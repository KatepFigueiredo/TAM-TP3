from flask import Blueprint, request, jsonify
from models import db, Quiz, Question
from flask_jwt_extended import jwt_required, get_jwt_identity

quiz_bp = Blueprint('quiz', __name__)

# Listar quizzes (com suporte a filtro ?mine=true)
@quiz_bp.route('', methods=['GET'])
@jwt_required()
def get_all_quizzes():
    current_user_id = int(get_jwt_identity())
    # Obtém o parâmetro da query string (?mine=true)
    mine = request.args.get('mine', 'false').lower() == 'true'
    
    if mine:
        # Filtra apenas quizzes do utilizador logado
        quizzes = Quiz.query.filter_by(user_id=current_user_id).all()
    else:
        # Retorna todos os quizzes
        quizzes = Quiz.query.all()
        
    output = []
    for quiz in quizzes:
        quiz_data = {
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'max_time': quiz.max_time,
            'author': quiz.user_id,
            'author_name': quiz.author.username,
            'active_sessions': quiz.active_sessions
        }
        output.append(quiz_data)
    return jsonify({'quizzes': output}), 200

# Criar um novo Quiz
@quiz_bp.route('/', methods=['POST'])
@jwt_required()
def create_quiz():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    title_to_check = data.get('title', '').strip()

    if not title_to_check:
        return jsonify({'message': 'O título do quiz não pode estar vazio'}), 400

    # Validação: Não devem existir dois quizzes com o mesmo título
    existing_quiz = Quiz.query.filter_by(title=title_to_check).first()
    if existing_quiz:
        return jsonify({'message': f'Já existe um quiz com o título "{title_to_check}"'}), 400

    new_quiz = Quiz(
        title=title_to_check, 
        description=data.get('description', ''), 
        max_time=data.get('max_time', 60), 
        user_id=user_id
    )
    db.session.add(new_quiz)
    db.session.commit()

    return jsonify({
        'id': new_quiz.id,
        'title': new_quiz.title,
        'message': 'Quiz criado com sucesso!'
    }), 201

# Eliminar um Quiz
@quiz_bp.route('/<int:quiz_id>', methods=['DELETE'])
@jwt_required()
def delete_quiz(quiz_id):
    current_user_id = int(get_jwt_identity())
    quiz = Quiz.query.get_or_404(quiz_id)

    if quiz.user_id != current_user_id:
        return jsonify({'message': 'Não é permitido eliminar um quiz que não é seu'}), 403

    # Validação: não deve ser permitida a remoção se houver utilizadores a executá-lo
    if quiz.active_sessions > 0:
        return jsonify({'message': 'Não é permitido eliminar um quiz que está a ser executado por utilizadores'}), 400

    db.session.delete(quiz)
    db.session.commit()
    return jsonify({'message': 'Quiz eliminado com sucesso!'}), 200

# Editar um Quiz
@quiz_bp.route('/<int:quiz_id>', methods=['PUT'])
@jwt_required()
def update_quiz(quiz_id):
    current_user_id = int(get_jwt_identity())
    quiz = Quiz.query.get_or_404(quiz_id)

    if quiz.user_id != current_user_id:
        return jsonify({'message': 'Não é permitido editar um quiz que não é seu'}), 403

    # Validação: não deve ser permitida a alteração se houver utilizadores a executá-lo
    if quiz.active_sessions > 0:
        return jsonify({'message': 'Não é permitido editar um quiz que está a ser executado por utilizadores'}), 400

    data = request.get_json()
    new_title = data.get('title', quiz.title).strip()

    if new_title != quiz.title:
        if Quiz.query.filter_by(title=new_title).first():
            return jsonify({'message': f'Já existe outro quiz com o título "{new_title}"'}), 400
        quiz.title = new_title

    quiz.description = data.get('description', quiz.description)
    quiz.max_time = data.get('max_time', quiz.max_time)

    db.session.commit()
    return jsonify({'message': 'Quiz atualizado com sucesso!'}), 200

# Iniciar sessão
@quiz_bp.route('/<int:quiz_id>/start', methods=['POST'])
@jwt_required()
def start_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    quiz.active_sessions += 1
    db.session.commit()
    return jsonify({'message': 'Sessão iniciada', 'active_sessions': quiz.active_sessions}), 200

# Terminar sessão
@quiz_bp.route('/<int:quiz_id>/end', methods=['POST'])
@jwt_required()
def end_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.active_sessions > 0:
        quiz.active_sessions -= 1
        db.session.commit()
    return jsonify({'message': 'Sessão terminada', 'active_sessions': quiz.active_sessions}), 200
