

from app import create_app


app = create_app(env='production')  # 生产环境: production(默认), 测试环境: test 开发: development

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=app.config['DEBUG'], port=3002)
