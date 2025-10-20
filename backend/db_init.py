from models import init_db, Base
from sqlalchemy import create_engine

def create_database():
    """Criar banco de dados e todas as tabelas"""
    print("Criando banco de dados...")
    engine = init_db('sqlite:///database.db')
    print("✓ Banco de dados database.db criado com sucesso!")
    print("✓ Tabelas criadas:")
    print("  - users")
    print("  - equipment_types")
    print("  - stock_items")
    print("  - equipment_instances")
    print("  - movements")
    print("  - invoices")
    return engine

if __name__ == '__main__':
    create_database()
