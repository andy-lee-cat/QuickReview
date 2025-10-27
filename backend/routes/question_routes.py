"""题目相关路由"""
import json
from flask import Blueprint, request, jsonify
from backend.repository import QuestionRepository, AnswerRecordRepository, QuestionBankRepository

question_bp = Blueprint('questions', __name__, url_prefix='/api/questions')


@question_bp.route('/', methods=['GET'])
def get_all_questions():
    """获取所有题目列表"""
    bank_id = request.args.get('bank_id', type=int)
    questions = QuestionRepository.get_all_questions(bank_id=bank_id)
    return jsonify([{
        **q.to_dict(),
        'stats': q.get_stats()
    } for q in questions])


@question_bp.route('/<int:question_id>', methods=['GET'])
def get_question(question_id):
    """获取指定题目（包含答案）"""
    question = QuestionRepository.get_question_by_id(question_id)
    if not question:
        return jsonify({'error': '题目不存在'}), 404
    return jsonify(question.to_dict(include_answer=True))


@question_bp.route('/random', methods=['GET'])
def get_random_question():
    """获取随机题目（不含答案）"""
    bank_id = request.args.get('bank_id', type=int)
    if not bank_id:
        return jsonify({'error': '请指定题库ID'}), 400

    question = QuestionRepository.get_random_question(bank_id=bank_id, prioritize_wrong=True)
    if not question:
        return jsonify({'error': '该题库没有题目'}), 404
    return jsonify(question.to_dict(include_answer=False))


@question_bp.route('/<int:question_id>/answer', methods=['GET'])
def get_answer(question_id):
    """获取题目答案（包含统计信息）"""
    question = QuestionRepository.get_question_by_id(question_id)
    if not question:
        return jsonify({'error': '题目不存在'}), 404

    stats = question.get_stats()

    return jsonify({
        'id': question.id,
        'answer': question.answer,
        'stats': stats
    })


@question_bp.route('/<int:question_id>/record', methods=['POST'])
def record_answer(question_id):
    """记录答题结果"""
    data = request.get_json()
    is_correct = data.get('is_correct')

    if is_correct is None:
        return jsonify({'error': '缺少is_correct参数'}), 400

    question = QuestionRepository.get_question_by_id(question_id)
    if not question:
        return jsonify({'error': '题目不存在'}), 404

    record = AnswerRecordRepository.create_record(question_id, is_correct)
    return jsonify(record.to_dict()), 201


@question_bp.route('/upload', methods=['POST'])
def upload_questions():
    """上传题目（JSON格式）"""
    data = request.get_json()

    if not data:
        return jsonify({'error': '请提供数据'}), 400

    bank_name = data.get('bank_name')
    questions_data = data.get('questions')

    if not bank_name:
        return jsonify({'error': '请提供题库名称'}), 400

    if not questions_data or not isinstance(questions_data, list):
        return jsonify({'error': '请提供题目数组'}), 400

    # 验证数据格式
    for item in questions_data:
        if 'question' not in item or 'answer' not in item:
            return jsonify({'error': '每道题必须包含question和answer字段'}), 400

    # 获取或创建题库
    bank = QuestionBankRepository.get_bank_by_name(bank_name)
    if not bank:
        bank = QuestionBankRepository.create_bank(bank_name)

    # 批量创建题目
    QuestionRepository.bulk_create_questions(bank.id, questions_data)

    return jsonify({
        'message': f'成功上传{len(questions_data)}道题目到题库"{bank_name}"',
        'count': len(questions_data),
        'bank_id': bank.id,
        'bank_name': bank.name
    }), 201


@question_bp.route('/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    """删除题目"""
    success = QuestionRepository.delete_question(question_id)
    if success:
        return jsonify({'message': '删除成功'})
    return jsonify({'error': '题目不存在'}), 404
