"""QuickReview - 刷题小网页主应用"""
import os
from flask import Flask, render_template
from backend.models import db
from backend.models.question_bank import QuestionBank
from backend.models.question import Question
from backend.models.answer_record import AnswerRecord
from backend.routes.bank_routes import bank_bp
from backend.routes.question_routes import question_bp
from backend.routes.stats_routes import stats_bp


def create_app():
    """创建Flask应用"""
    app = Flask(__name__)

    # 配置数据库
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "data", "quickreview.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 初始化数据库
    db.init_app(app)

    # 注册路由
    app.register_blueprint(bank_bp)
    app.register_blueprint(question_bp)
    app.register_blueprint(stats_bp)

    # 创建数据库表
    with app.app_context():
        os.makedirs(os.path.join(basedir, 'data'), exist_ok=True)
        db.create_all()

    # 前端页面路由
    @app.route('/')
    def index():
        """刷题主页"""
        return render_template('index.html')

    @app.route('/stats')
    def stats():
        """统计页面"""
        return render_template('stats.html')

    @app.route('/upload')
    def upload_page():
        """上传页面"""
        return render_template('upload.html')

    @app.route('/banks')
    def banks_page():
        """题库管理页面"""
        return render_template('banks.html')

    return app


if __name__ == '__main__':
    app = create_app()
    print('QuickReview 启动成功！')
    print('访问地址: http://127.0.0.1:5001')
    print('- 刷题页面: http://127.0.0.1:5001')
    print('- 题库管理: http://127.0.0.1:5001/banks')
    print('- 统计页面: http://127.0.0.1:5001/stats')
    print('- 上传页面: http://127.0.0.1:5001/upload')
    print('')
    print('VSCode SSH用户：在VSCode中设置端口转发 5001，然后访问 http://localhost:5001')
    app.run(debug=True, host='0.0.0.0', port=5001)
