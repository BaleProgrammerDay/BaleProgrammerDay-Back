from flask import Blueprint, jsonify, request, session

from models import Question, Submit, db
from utility import *
submit_bp = Blueprint('submit', __name__)

@submit_bp.route('/submit', methods=['POST'])
def submit_answer():
    group = authentication_required(request)
    data = request.json
    question = get_object_or_404(Question, id=decrypt_id(data['question_id'], group.id))
    if not question.is_active:
        return "question is not active", 400
    submitted_answer = data['answer']

    if not is_purchased(question.id, group.id):
        return "question is not purchased", 403
    if is_answerd(question.id, group.id):
        return "question is already answered", 400
    
    is_correct = (submitted_answer == question.answer)
    
    new_submit = Submit(
        group_id=group.id,
        question_id=question.id,
        answer=submitted_answer,
        result=is_correct
    )
    db.session.add(new_submit)
    db.session.commit()

    group.total_submits += 1
    if is_correct:
        group.correct_submits += 1
        group.score += question.score
        if num_correct_answers(question.id) == 2:
            question.is_active = False
    
    db.session.commit()
    
    return jsonify({"result": is_correct})