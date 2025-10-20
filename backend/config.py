import os

class Config:
    """Configuração da aplicação"""
    
    # Banco de dados
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Segurança - API Key simples
    API_KEY = os.environ.get('API_KEY', 'dev-key-12345')
    
    # Upload de arquivos
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    
    # CORS
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000', 
                    'http://localhost:5500', 'http://127.0.0.1:5500']
    
    # Timezone
    TIMEZONE = 'America/Sao_Paulo'
    
    @staticmethod
    def init_app(app):
        """Inicializar configurações do app"""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
