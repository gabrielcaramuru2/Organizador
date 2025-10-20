import sqlite3
import json
from datetime import datetime

def backup_database():
    """Fazer backup do banco de dados em formato JSON"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    backup_data = {
        'backup_date': datetime.now().isoformat(),
        'tables': {}
    }
    
    # Lista de tabelas
    tables = ['users', 'equipment_types', 'stock_items', 'equipment_instances', 'movements', 'invoices']
    
    for table in tables:
        try:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            backup_data['tables'][table] = [dict(row) for row in rows]
            print(f"✓ Backup de {table}: {len(rows)} registros")
        except sqlite3.Error as e:
            print(f"✗ Erro ao fazer backup de {table}: {e}")
    
    conn.close()
    
    # Salvar em arquivo JSON
    filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Backup salvo em: {filename}")
    return filename

if __name__ == '__main__':
    backup_database()
