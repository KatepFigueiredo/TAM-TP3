import json
from flask import Blueprint, request, jsonify 
from models import db, Question, Quiz
from flask_jwt_extended import jwt_required, get_jwt_identity

question_bp = Blueprint('question', __name__)

# Listar perguntas de um Quiz Específico
@question_bp.route('/<int:quiz_id>', methods=['GET'])
@jwt_required()
def get_questions_by_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = []
    for q in quiz.questions:
        answers_list = []
        if q.answers:
            try:
                answers_list = json.loads(q.answers)
            except json.JSONDecodeError:
                if '|' in q.answers:
                    answers_list = q.answers.split('|')
                else:
                    try:
                        answers_list = json.loads(q.answers.replace("'", '"'))
                    except:
                        answers_list = []

        questions.append({
            'id': q.id,
            'question_text': q.question_text,
            'answers': answers_list,
            'correct_answer_index': q.correct_answer_index,
            'url_image': q.url_image,
            'quiz_id': q.quiz_id
        })
    return jsonify({'questions': questions}), 200

# Adicionar uma pergunta a um Quiz
@question_bp.route('/<int:quiz_id>', methods=['POST'])
@jwt_required()
def add_question(quiz_id):
    current_user_id = int(get_jwt_identity())
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if quiz.user_id != current_user_id:
        return jsonify({'message': 'Não é permitido adicionar perguntas a um quiz que não é seu'}), 403

    # Validação: Impedir modificação se houver jogadores ativos
    if quiz.active_sessions > 0:
        return jsonify({'message': 'Não é permitido alterar questões de um quiz que está a ser executado'}), 400

    data = request.get_json()
    new_question = Question(
        question_text=data['question_text'],
        answers=json.dumps(data['answers']),
        correct_answer_index=data['correct_answer_index'],
        url_image=data.get('url_image'),
        quiz_id=quiz_id
    )
    db.session.add(new_question)
    db.session.commit()
    return jsonify({'message': 'Pergunta adicionada com sucesso!', 'id': new_question.id}), 201

# Editar uma Pergunta
@question_bp.route('/<int:question_id>', methods=['PUT'])
@jwt_required()
def update_question(question_id):
    current_user_id = int(get_jwt_identity())
    question = Question.query.get_or_404(question_id)
    quiz = Quiz.query.get(question.quiz_id)

    if quiz.user_id != current_user_id:
        return jsonify({'message': 'Não é permitido editar perguntas de um quiz que não é seu'}), 403

    # Validação: Impedir modificação se houver jogadores ativos
    if quiz.active_sessions > 0:
        return jsonify({'message': 'Não é permitido editar questões de um quiz que está a ser executado'}), 400

    data = request.get_json()
    question.question_text = data.get('question_text', question.question_text)
    if 'answers' in data:
        question.answers = json.dumps(data['answers'])
    question.correct_answer_index = data.get('correct_answer_index', question.correct_answer_index)
    question.url_image = data.get('url_image', question.url_image)

    db.session.commit()
    return jsonify({'message': 'Pergunta atualizada com sucesso!'}), 200

# Remover uma Pergunta
@question_bp.route('/<int:question_id>', methods=['DELETE'])
@jwt_required()
def delete_question(question_id):
    current_user_id = int(get_jwt_identity())
    question = Question.query.get_or_404(question_id)
    quiz = Quiz.query.get(question.quiz_id)

    if quiz.user_id != current_user_id:
        return jsonify({'message': 'Não é permitido remover perguntas de um quiz que não é seu'}), 403

    # Validação: Impedir modificação se houver jogadores ativos
    if quiz.active_sessions > 0:
        return jsonify({'message': 'Não é permitido remover questões de um quiz que está a ser executado'}), 400

    db.session.delete(question)
    db.session.commit()
    return jsonify({'message': 'Pergunta removida com sucesso!'}), 200
