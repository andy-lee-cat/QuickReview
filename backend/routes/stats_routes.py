"""统计相关路由"""
from flask import Blueprint, jsonify, request
from backend.repository import QuestionRepository, AnswerRecordRepository

stats_bp = Blueprint('stats', __name__, url_prefix='/api/stats')


@stats_bp.route('/', methods=['GET'])
def get_overall_stats():
    """获取总体统计信息"""
    bank_id = request.args.get('bank_id', type=int)
    stats = AnswerRecordRepository.get_statistics(bank_id=bank_id)
    question_count = QuestionRepository.get_question_count(bank_id=bank_id)

    return jsonify({
        **stats,
        'total_questions': question_count
    })


@stats_bp.route('/questions', methods=['GET'])
def get_questions_stats():
    """获取所有题目的详细统计"""
    bank_id = request.args.get('bank_id', type=int)
    questions = QuestionRepository.get_all_questions(bank_id=bank_id)

    questions_stats = []
    for q in questions:
        stats = q.get_stats()
        questions_stats.append({
            'id': q.id,
            'question': q.question,
            **stats
        })

    # 按正确率排序（错误率高的排前面）
    questions_stats.sort(key=lambda x: (x['accuracy'], -x['total_count']))

    return jsonify(questions_stats)
