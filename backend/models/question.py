from datetime import datetime
from backend.models import db


class Question(db.Model):
    """题目模型"""
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    bank_id = db.Column(db.Integer, db.ForeignKey('question_banks.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联题库
    bank = db.relationship('QuestionBank', back_populates='questions')
    # 关联答题记录
    records = db.relationship('AnswerRecord', back_populates='question', cascade='all, delete-orphan')

    def to_dict(self, include_answer=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'bank_id': self.bank_id,
            'question': self.question,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_answer:
            data['answer'] = self.answer
        return data

    def get_stats(self):
        """获取题目统计信息"""
        correct_count = sum(1 for r in self.records if r.is_correct)
        wrong_count = sum(1 for r in self.records if not r.is_correct)
        last_review = max((r.created_at for r in self.records), default=None)

        return {
            'correct_count': correct_count,
            'wrong_count': wrong_count,
            'total_count': len(self.records),
            'last_review': last_review.isoformat() if last_review else None,
            'accuracy': correct_count / len(self.records) if self.records else 0
        }
