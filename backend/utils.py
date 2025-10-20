from functools import wraps
from flask import request, jsonify
from config import Config

def require_api_key(f):
    """Decorator para proteger endpoints com API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        if api_key and api_key == Config.API_KEY:
            return f(*args, **kwargs)
        return jsonify({'error': 'API key inválida ou ausente'}), 401
    return decorated_function

def allowed_file(filename):
    """Verificar se extensão de arquivo é permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def format_currency(value):
    """Formatar valor monetário"""
    if not value:
        return "R$ 0,00"
    return f"R$ {value:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
