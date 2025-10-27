"""题库相关路由"""
from flask import Blueprint, request, jsonify
from backend.repository import QuestionBankRepository

bank_bp = Blueprint('banks', __name__, url_prefix='/api/banks')


@bank_bp.route('/', methods=['GET'])
def get_all_banks():
    """获取所有题库"""
    banks = QuestionBankRepository.get_all_banks()
    return jsonify([bank.to_dict() for bank in banks])


@bank_bp.route('/<int:bank_id>', methods=['GET'])
def get_bank(bank_id):
    """获取指定题库"""
    bank = QuestionBankRepository.get_bank_by_id(bank_id)
    if not bank:
        return jsonify({'error': '题库不存在'}), 404
    return jsonify(bank.to_dict())


@bank_bp.route('/', methods=['POST'])
def create_bank():
    """创建题库"""
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')

    if not name:
        return jsonify({'error': '题库名称不能为空'}), 400

    # 检查是否已存在同名题库
    existing = QuestionBankRepository.get_bank_by_name(name)
    if existing:
        return jsonify({'error': '题库名称已存在'}), 400

    bank = QuestionBankRepository.create_bank(name, description)
    return jsonify(bank.to_dict()), 201


@bank_bp.route('/<int:bank_id>', methods=['DELETE'])
def delete_bank(bank_id):
    """删除题库"""
    success = QuestionBankRepository.delete_bank(bank_id)
    if success:
        return jsonify({'message': '删除成功'})
    return jsonify({'error': '题库不存在'}), 404
