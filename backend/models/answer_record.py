from datetime import datetime
from backend.models import db


class AnswerRecord(db.Model):
    """答题记录模型"""
    __tablename__ = 'answer_records'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联题目
    question = db.relationship('Question', back_populates='records')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'question_id': self.question_id,
            'is_correct': self.is_correct,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
