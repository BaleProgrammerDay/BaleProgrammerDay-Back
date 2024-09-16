from flask import Blueprint, jsonify, request, session

# from group import Group
from models import Group, db
from utility import authentication_required, get_key_from_json_request, get_object_or_404

auth_bp = Blueprint('auth', __name__)

@auth_bp.get("/authenticated-hello")
def auth_hello():
    group = authentication_required(request)
    return "hiii " + group.group_name + "\n"

@auth_bp.post("/login")
def login():
    a = request.json
    group_name = get_key_from_json_request(a, "group_name")
    password = get_key_from_json_request(a, "password")
    gr = Group.query.filter_by(group_name=group_name, password=password).first()
    if gr == None:
        return "groupname or password is incorrect", 404

    session["group_id"] = gr.id 
    return jsonify(group_id=gr.id), 200

@auth_bp.post("/new-group")
def create_group():
    data = request.json
    if Group.query.filter_by(id=int(data['id'])).first() != None:
        return "group id already exits", 400
    
    new_group = Group(
        id=int(data['id']),
        score=0,
        correct_submits=0,
        total_submits=0,
        group_name=data['group_name'],
        password=data['password'],
        keys=int(data['keys'])
    )

    db.session.add(new_group)
    db.session.commit()
    group_id = Group.query.filter_by(group_name=data['group_name']).first().id
    return jsonify({"id": group_id}), 201

@auth_bp.get("/group-info")
def group_info():
    group = authentication_required(request)
    info = {
        'group_name': group.group_name,
        'keys': group.keys,
        'score': group.score,
        'correct_submits': group.correct_submits
    }
    return jsonify(info), 200

@auth_bp.get("/ranking")
def ranking():
    group = authentication_required(request)
    groups_query = db.session.query(
        Group.group_name,
        Group.score,
        Group.correct_submits,
        Group.id
    ).all()

    group_list = [
        {'group_name': g.group_name,
         'score': g.score,
         'correct_submits': g.correct_submits,
         'self': g.id == group.id}
         
         for g in groups_query
    ]
    group_list.sort(key=lambda g: g['score'], reverse=True)

    return jsonify(group_list), 200