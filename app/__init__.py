# app/__init__.py
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

# Настройки Flask, такие как SECRET_KEY, загружаются из переменных окружения
app.config.from_mapping(
    SECRET_KEY='your_secret_key'
)

from app.routes import list_routes, user_routes, report_routes

# Регистрация маршрутов
app.register_blueprint(list_routes.bp)
app.register_blueprint(user_routes.bp)
app.register_blueprint(report_routes.bp)
