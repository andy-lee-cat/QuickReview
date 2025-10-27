"""数据库操作封装层"""
import random
from datetime import datetime, timezone
from typing import List, Optional, Dict
from sqlalchemy import func
from backend.models import db
from backend.models.question_bank import QuestionBank
from backend.models.question import Question
from backend.models.answer_record import AnswerRecord


class QuestionBankRepository:
    """题库数据库操作封装"""

    @staticmethod
    def create_bank(name: str, description: str = None) -> QuestionBank:
        """创建题库"""
        bank = QuestionBank(name=name, description=description)
        db.session.add(bank)
        db.session.commit()
        return bank

    @staticmethod
    def get_bank_by_id(bank_id: int) -> Optional[QuestionBank]:
        """根据ID获取题库"""
        return db.session.get(QuestionBank, bank_id)

    @staticmethod
    def get_bank_by_name(name: str) -> Optional[QuestionBank]:
        """根据名称获取题库"""
        return db.session.query(QuestionBank).filter_by(name=name).first()

    @staticmethod
    def get_all_banks() -> List[QuestionBank]:
        """获取所有题库"""
        return db.session.query(QuestionBank).order_by(QuestionBank.created_at.desc()).all()

    @staticmethod
    def delete_bank(bank_id: int) -> bool:
        """删除题库"""
        bank = db.session.get(QuestionBank, bank_id)
        if bank:
            db.session.delete(bank)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_or_create_default_bank() -> QuestionBank:
        """获取或创建默认题库"""
        bank = QuestionBankRepository.get_bank_by_name("默认题库")
        if not bank:
            bank = QuestionBankRepository.create_bank("默认题库", "系统默认题库")
        return bank


class QuestionRepository:
    """题目数据库操作封装"""

    @staticmethod
    def create_question(bank_id: int, question: str, answer: str) -> Question:
        """创建题目"""
        q = Question(bank_id=bank_id, question=question, answer=answer)
        db.session.add(q)
        db.session.commit()
        return q

    @staticmethod
    def bulk_create_questions(bank_id: int, questions_data: List[Dict]) -> List[Question]:
        """批量创建题目"""
        questions = []
        for data in questions_data:
            q = Question(
                bank_id=bank_id,
                question=data.get('question'),
                answer=data.get('answer')
            )
            questions.append(q)
            db.session.add(q)
        db.session.commit()
        return questions

    @staticmethod
    def get_question_by_id(question_id: int) -> Optional[Question]:
        """根据ID获取题目"""
        return db.session.get(Question, question_id)

    @staticmethod
    def get_all_questions(bank_id: Optional[int] = None) -> List[Question]:
        """获取所有题目"""
        query = db.session.query(Question)
        if bank_id:
            query = query.filter_by(bank_id=bank_id)
        return query.all()

    @staticmethod
    def get_random_question(bank_id: int, prioritize_wrong: bool = True) -> Optional[Question]:
        """
        获取随机题目
        bank_id: 题库ID
        prioritize_wrong: 是否优先选择错误率高的题目

        新算法：
        1. 按正确率分档：<50%, 50%-80%, 80%-100%
        2. 按5:3:2的概率随机选择档位
        3. 在选中的档位中，选择最久没做过的题目
        """
        if prioritize_wrong:
            questions = db.session.query(Question).filter_by(bank_id=bank_id).all()
            if not questions:
                return None

            # 将题目按正确率分档
            low_accuracy = []    # <50%
            mid_accuracy = []    # 50%-80%
            high_accuracy = []   # 80%-100%

            for q in questions:
                correct_count = sum(1 for r in q.records if r.is_correct)
                total_count = len(q.records)

                # 计算最后答题时间
                last_review = max((r.created_at for r in q.records), default=None) if q.records else None

                if total_count == 0:
                    # 从未做过的题目，归入低正确率档（优先做）
                    accuracy = 0.0
                    low_accuracy.append((q, last_review, accuracy))
                else:
                    accuracy = correct_count / total_count

                    if accuracy < 0.5:
                        low_accuracy.append((q, last_review, accuracy))
                    elif accuracy < 0.8:
                        mid_accuracy.append((q, last_review, accuracy))
                    else:
                        high_accuracy.append((q, last_review, accuracy))

            # 按5:3:2的概率选择档位
            tier_weights = [5, 3, 2]
            available_tiers = []

            if low_accuracy:
                available_tiers.append(('low', low_accuracy, tier_weights[0]))
            if mid_accuracy:
                available_tiers.append(('mid', mid_accuracy, tier_weights[1]))
            if high_accuracy:
                available_tiers.append(('high', high_accuracy, tier_weights[2]))

            if not available_tiers:
                return None

            # 根据权重随机选择档位
            total_weight = sum(t[2] for t in available_tiers)
            rand_val = random.uniform(0, total_weight)
            cumulative = 0
            selected_tier = None

            for tier_name, tier_questions, weight in available_tiers:
                cumulative += weight
                if rand_val <= cumulative:
                    selected_tier = tier_questions
                    break

            if not selected_tier:
                selected_tier = available_tiers[0][1]

            # 在选中的档位中，按最后答题时间排序，选择最久没做过的
            # None (从未做过) 视为最早，排在最前面
            selected_tier.sort(key=lambda x: (x[1] is not None, x[1] if x[1] else datetime.min))

            # 返回最久未做的题目
            return selected_tier[0][0]
        else:
            # 完全随机
            return db.session.query(Question).filter_by(bank_id=bank_id).order_by(func.random()).first()

    @staticmethod
    def delete_question(question_id: int) -> bool:
        """删除题目"""
        question = db.session.get(Question, question_id)
        if question:
            db.session.delete(question)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_question_count(bank_id: Optional[int] = None) -> int:
        """获取题目总数"""
        query = db.session.query(Question)
        if bank_id:
            query = query.filter_by(bank_id=bank_id)
        return query.count()


class AnswerRecordRepository:
    """答题记录数据库操作封装"""

    @staticmethod
    def create_record(question_id: int, is_correct: bool) -> AnswerRecord:
        """创建答题记录"""
        record = AnswerRecord(
            question_id=question_id,
            is_correct=is_correct
        )
        db.session.add(record)
        db.session.commit()
        return record

    @staticmethod
    def get_records_by_question(question_id: int) -> List[AnswerRecord]:
        """获取某题目的所有记录"""
        return db.session.query(AnswerRecord).filter_by(question_id=question_id).all()

    @staticmethod
    def get_all_records() -> List[AnswerRecord]:
        """获取所有答题记录"""
        return db.session.query(AnswerRecord).all()

    @staticmethod
    def get_statistics(bank_id: Optional[int] = None) -> Dict:
        """获取总体统计信息"""
        if bank_id:
            # 获取该题库的所有题目ID
            question_ids = [q.id for q in db.session.query(Question.id).filter_by(bank_id=bank_id).all()]
            total_records = db.session.query(AnswerRecord).filter(AnswerRecord.question_id.in_(question_ids)).count()
            correct_records = db.session.query(AnswerRecord).filter(
                AnswerRecord.question_id.in_(question_ids),
                AnswerRecord.is_correct == True
            ).count()
        else:
            total_records = db.session.query(AnswerRecord).count()
            correct_records = db.session.query(AnswerRecord).filter_by(is_correct=True).count()

        wrong_records = total_records - correct_records

        return {
            'total_records': total_records,
            'correct_records': correct_records,
            'wrong_records': wrong_records,
            'accuracy': correct_records / total_records if total_records > 0 else 0
        }
