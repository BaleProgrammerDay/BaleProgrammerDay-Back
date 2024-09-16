from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Question(db.Model):
    __tablename__ = 'question'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    text = db.Column(db.Text, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    is_starred = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    zip_file_name = db.Column(db.String, nullable=True) 
    answer = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Question {self.id} - {self.title}>"


class Submit(db.Model):
    __tablename__ = 'submit'
    
    id = db.Column(db.Integer, primary_key=True)
    submit_time = db.Column(db.DateTime, default=datetime.utcnow)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    result = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"<Submit {self.id} - Group {self.group_id} - Question {self.question_id}>"


class Group(db.Model):
    __tablename__ = 'group'
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    correct_submits = db.Column(db.Integer, nullable=False, default=0)
    total_submits = db.Column(db.Integer, nullable=False, default=0)
    keys = db.Column(db.Integer, nullable=False, default=0)

class Purchase(db.Model):
    __tablename__ = 'purchase'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
