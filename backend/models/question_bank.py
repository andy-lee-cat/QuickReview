from datetime import datetime
from backend.models import db


class QuestionBank(db.Model):
    """题库模型"""
    __tablename__ = 'question_banks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联题目
    questions = db.relationship('Question', back_populates='bank', cascade='all, delete-orphan')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'question_count': len(self.questions)
        }
