from sqlalchemy.orm import aliased
import os
from flask import Blueprint, jsonify, request, current_app, session, Response

from models import Question, Submit, db, Purchase
from utility import *
question_bp = Blueprint('question', __name__)

@question_bp.route('/new-question', methods=['POST'])
def create_question():
    if Question.query.filter_by(id=int(request.form['id'])).first() != None:
        return "question id already exits", 400
    
    zip_file = request.files.get('zip_file')
    if zip_file:
        zip_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], zip_file.filename)
        zip_file.save(zip_file_path)

    new_question = Question(
        id=int(request.form['id']),
        title=request.form['title'],
        text=request.form['text'],
        cost=int(request.form['cost']),
        score=int(request.form['score']),
        is_starred=request.form.get('is_starred', '0') == '1',
        zip_file_name=zip_file.filename,
        answer=request.form['answer']
    )

    db.session.add(new_question)
    db.session.commit()

    return jsonify({"question_id": new_question.id})

@question_bp.route('/purchase-question', methods=['POST'])
def purchase_question():
    group = authentication_required(request)
    data = request.json
    question = get_object_or_404(Question, id=int(decrypt_id(data['question_id'], group.id)))
    if not question.is_active:
        return "question is not active", 400
    if Purchase.query.filter_by(question_id=question.id, group_id=group.id).first() != None:
        return "question is already purchased", 400
    if group.keys < question.cost:
        return "not enough keys", 400
    
    new_purchase = Purchase(
        group_id=group.id,
        question_id=question.id
    )

    db.session.add(new_purchase)
    group.keys = group.keys - question.cost
    db.session.commit()
    return {'left_keys': group.keys}, 200

@question_bp.route('/all-questions', methods=['GET'])
def all_questions():
    group = authentication_required(request)

    purchase_alias = aliased(Purchase)
    submit_alias = aliased(Submit)

    questions_query = db.session.query(
        Question.id,
        Question.is_starred,
        Question.is_active,
        Question.cost,
        Question.score,
    ).all()

    questions_list = [
        {
            'id': encrypt_id(question.id, group.id),
            'is_starred': question.is_starred,
            'is_active': question.is_active,
            'cost': question.cost,
            'score': question.score,
            'is_purchased': is_purchased(question.id, group.id),
            'is_answerd': is_answerd(question.id, group.id)
        }
        for question in questions_query
    ]
    questions_list.sort(key=lambda a: a['id'])

    return jsonify(questions_list), 200




@question_bp.post('/question-details')
def question_details():
    group = authentication_required(request)
    data = request.json
    question = get_object_or_404(Question, id=int(decrypt_id(data['id'], group.id)))
    if not is_purchased(question.id, group.id):
        return "question is not purchased", 403
    
    question_dict = {
        'id': encrypt_id(question.id, group.id),
        'title': question.title,
        'text': question.text,
        'is_starred': question.is_starred,
        'is_active': question.is_active,
        'cost': question.cost,
        'score': question.score,
        'has_zip': question.zip_file_name != '',
        'zip_file_url': f"/assets/{data['id']}/{group.id}",
        'is_purchased': is_purchased(question.id, group.id),
        'is_answerd': is_answerd(question.id, group.id)
    }

    return jsonify(question_dict), 200



@question_bp.get('/assets/<path:question_id>/<path:gid>')
def question_assets(question_id, gid):
    question = get_object_or_404(Question, id=int(decrypt_id(question_id, gid)))
    if not is_purchased(question.id, gid):
        return "question is not purchased", 403
    
    response = Response()
    response.headers['X-Accel-Redirect'] = f'/protected/{question.zip_file_name}'
    return response

