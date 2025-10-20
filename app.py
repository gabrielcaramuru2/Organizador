from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func, or_
from datetime import datetime, date
import os

from config import Config
from models import (Base, User, EquipmentType, StockItem, EquipmentInstance, 
                   Movement, Invoice, StatusEnum, MovementTypeEnum, init_db, get_session)
from import_service import ImportService
from utils import require_api_key, allowed_file

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

# Configurar CORS
CORS(app, origins=Config.CORS_ORIGINS)

# Inicializar banco de dados
engine = init_db(app.config['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker(bind=engine)

# ============== ROTAS DE IMPORTAÇÃO ==============

@app.route('/api/import/users', methods=['POST'])
@require_api_key
def import_users():
    """Importar usuários de CSV"""
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
    
    filename = f"users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        session = Session()
        import_service = ImportService(session)
        stats = import_service.import_users_from_csv(filepath)
        session.close()
        
        return jsonify({
            'success': True,
            'message': 'Importação concluída',
            'stats': stats
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/import/equipment', methods=['POST'])
@require_api_key
def import_equipment():
    """Importar equipamentos de Excel ou CSV"""
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
    
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"equipment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        session = Session()
        import_service = ImportService(session)
        
        if ext in ['xlsx', 'xls']:
            stats = import_service.import_equipment_from_excel(filepath)
        else:
            stats = import_service.import_equipment_from_csv(filepath)
        
        session.close()
        
        return jsonify({
            'success': True,
            'message': 'Importação concluída',
            'stats': stats
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== ROTAS DE USUÁRIOS ==============

@app.route('/api/users', methods=['GET'])
def get_users():
    """Listar usuários com filtros"""
    session = Session()
    
    # Parâmetros de filtro
    city = request.args.get('city')
    cargo = request.args.get('cargo')
    setor = request.args.get('setor')
    q = request.args.get('q')  # Busca geral
    
    query = session.query(User)
    
    if city:
        query = query.filter(User.cidade.ilike(f'%{city}%'))
    if cargo:
        query = query.filter(User.cargo.ilike(f'%{cargo}%'))
    if setor:
        query = query.filter(User.setor.ilike(f'%{setor}%'))
    if q:
        query = query.filter(
            or_(
                User.nome.ilike(f'%{q}%'),
                User.cpf.ilike(f'%{q}%'),
                User.matricula.ilike(f'%{q}%')
            )
        )
    
    users = query.all()
    session.close()
    
    return jsonify([user.to_dict() for user in users]), 200

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Obter detalhes de um usuário"""
    session = Session()
    user = session.query(User).get(user_id)
    session.close()
    
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    return jsonify(user.to_dict()), 200

@app.route('/api/users', methods=['POST'])
@require_api_key
def create_user():
    """Criar novo usuário"""
    data = request.json
    session = Session()
    
    try:
        user = User(
            cpf=data.get('cpf'),
            nome=data.get('nome'),
            cargo=data.get('cargo'),
            cidade=data.get('cidade'),
            setor=data.get('setor'),
            email=data.get('email'),
            matricula=data.get('matricula')
        )
        session.add(user)
        session.commit()
        result = user.to_dict()
        session.close()
        return jsonify(result), 201
    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({'error': str(e)}), 400

# ============== ROTAS DE TIPOS DE EQUIPAMENTOS ==============

@app.route('/api/equipment-types', methods=['GET'])
def get_equipment_types():
    """Listar tipos de equipamentos"""
    session = Session()
    q = request.args.get('q')
    
    query = session.query(EquipmentType)
    
    if q:
        query = query.filter(
            or_(
                EquipmentType.nome.ilike(f'%{q}%'),
                EquipmentType.marca.ilike(f'%{q}%'),
                EquipmentType.modelo.ilike(f'%{q}%')
            )
        )
    
    types = query.all()
    session.close()
    
    return jsonify([t.to_dict() for t in types]), 200

@app.route('/api/equipment-types', methods=['POST'])
@require_api_key
def create_equipment_type():
    """Criar novo tipo de equipamento"""
    data = request.json
    session = Session()
    
    try:
        eq_type = EquipmentType(
            nome=data.get('nome'),
            marca=data.get('marca'),
            modelo=data.get('modelo'),
            especificacoes=data.get('especificacoes')
        )
        session.add(eq_type)
        session.commit()
        result = eq_type.to_dict()
        session.close()
        return jsonify(result), 201
    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({'error': str(e)}), 400

# ============== ROTAS DE ESTOQUE ==============

@app.route('/api/stock', methods=['GET'])
def get_stock():
    """Listar estoque"""
    session = Session()
    
    available = request.args.get('available')
    type_id = request.args.get('type_id')
    
    query = session.query(StockItem)
    
    if type_id:
        query = query.filter(StockItem.equipment_type_id == type_id)
    
    items = query.all()
    session.close()
    
    return jsonify([item.to_dict() for item in items]), 200

@app.route('/api/stock', methods=['POST'])
@require_api_key
def create_stock_item():
    """Registrar nova entrada de estoque"""
    data = request.json
    session = Session()
    
    try:
        # Criar item de estoque
        stock_item = StockItem(
            equipment_type_id=data.get('equipment_type_id'),
            nota_numero=data.get('nota_numero'),
            nota_data=datetime.strptime(data.get('nota_data'), '%Y-%m-%d').date() if data.get('nota_data') else None,
            quantidade=data.get('quantidade', 1),
            valor_unitario=data.get('valor_unitario', 0),
            valor_total=data.get('valor_total', 0),
            origem=data.get('origem', 'manual')
        )
        session.add(stock_item)
        session.flush()
        
        # Criar instâncias individuais
        instances_data = data.get('instances', [])
        for inst_data in instances_data:
            instance = EquipmentInstance(
                stock_item_id=stock_item.id,
                patrimonial=inst_data.get('patrimonial'),
                serial=inst_data.get('serial'),
                status=StatusEnum.disponivel
            )
            session.add(instance)
        
        session.commit()
        result = stock_item.to_dict()
        session.close()
        return jsonify(result), 201
    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({'error': str(e)}), 400

# ============== ROTAS DE EQUIPAMENTOS (INSTÂNCIAS) ==============

@app.route('/api/equipment-instances', methods=['GET'])
def get_equipment_instances():
    """Listar instâncias de equipamentos"""
    session = Session()
    
    status = request.args.get('status')
    user_id = request.args.get('user_id')
    
    query = session.query(EquipmentInstance)
    
    if status:
        query = query.filter(EquipmentInstance.status == StatusEnum[status])
    if user_id:
        query = query.filter(EquipmentInstance.current_user_id == user_id)
    
    instances = query.all()
    session.close()
    
    return jsonify([inst.to_dict() for inst in instances]), 200

# ============== ROTAS DE DESTINAÇÃO ==============

@app.route('/api/assign', methods=['POST'])
@require_api_key
def assign_equipment():
    """Destinar equipamento a usuário"""
    data = request.json
    session = Session()
    
    try:
        instance_id = data.get('equipment_instance_id')
        to_user_id = data.get('to_user_id')
        note = data.get('note', '')
        
        # Buscar instância
        instance = session.query(EquipmentInstance).get(instance_id)
        if not instance:
            return jsonify({'error': 'Equipamento não encontrado'}), 404
        
        if instance.status != StatusEnum.disponivel:
            return jsonify({'error': 'Equipamento não está disponível'}), 400
        
        # Buscar usuário
        user = session.query(User).get(to_user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Atualizar instância
        instance.status = StatusEnum.alocado
        instance.current_user_id = to_user_id
        instance.assigned_at = datetime.now()
        
        # Registrar movimento
        movement = Movement(
            equipment_instance_id=instance_id,
            to_user_id=to_user_id,
            type=MovementTypeEnum.destinacao,
            note=note
        )
        session.add(movement)
        
        session.commit()
        result = instance.to_dict()
        session.close()
        
        return jsonify({
            'success': True,
            'message': 'Equipamento destinado com sucesso',
            'equipment': result
        }), 200
    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({'error': str(e)}), 400

@app.route('/api/return', methods=['POST'])
@require_api_key
def return_equipment():
    """Devolver equipamento"""
    data = request.json
    session = Session()
    
    try:
        instance_id = data.get('equipment_instance_id')
        note = data.get('note', '')
        
        # Buscar instância
        instance = session.query(EquipmentInstance).get(instance_id)
        if not instance:
            return jsonify({'error': 'Equipamento não encontrado'}), 404
        
        if instance.status != StatusEnum.alocado:
            return jsonify({'error': 'Equipamento não está alocado'}), 400
        
        from_user_id = instance.current_user_id
        
        # Atualizar instância
        instance.status = StatusEnum.disponivel
        instance.current_user_id = None
        instance.assigned_at = None
        
        # Registrar movimento
        movement = Movement(
            equipment_instance_id=instance_id,
            from_user_id=from_user_id,
            type=MovementTypeEnum.devolucao,
            note=note
        )
        session.add(movement)
        
        session.commit()
        result = instance.to_dict()
        session.close()
        
        return jsonify({
            'success': True,
            'message': 'Equipamento devolvido com sucesso',
            'equipment': result
        }), 200
    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({'error': str(e)}), 400

# ============== ROTAS DE RELATÓRIOS ==============

@app.route('/api/reports/stock-summary', methods=['GET'])
def stock_summary():
    """Resumo do estoque"""
    session = Session()
    
    # Total de equipamentos
    total = session.query(func.count(EquipmentInstance.id)).scalar()
    
    # Por status
    disponivel = session.query(func.count(EquipmentInstance.id)).filter(
        EquipmentInstance.status == StatusEnum.disponivel
    ).scalar()
    
    alocado = session.query(func.count(EquipmentInstance.id)).filter(
        EquipmentInstance.status == StatusEnum.alocado
    ).scalar()
    
    em_manutencao = session.query(func.count(EquipmentInstance.id)).filter(
        EquipmentInstance.status == StatusEnum.em_manutencao
    ).scalar()
    
    baixado = session.query(func.count(EquipmentInstance.id)).filter(
        EquipmentInstance.status == StatusEnum.baixado
    ).scalar()
    
    # Valor total investido
    valor_total = session.query(func.sum(StockItem.valor_total)).scalar() or 0
    
    session.close()
    
    return jsonify({
        'total': total,
        'disponivel': disponivel,
        'alocado': alocado,
        'em_manutencao': em_manutencao,
        'baixado': baixado,
        'valor_total_investido': valor_total
    }), 200

@app.route('/api/reports/user/<int:user_id>', methods=['GET'])
def user_equipment_report(user_id):
    """Equipamentos em uso por um usuário"""
    session = Session()
    
    user = session.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    equipment = session.query(EquipmentInstance).filter(
        EquipmentInstance.current_user_id == user_id
    ).all()
    
    session.close()
    
    return jsonify({
        'user': user.to_dict(),
        'equipment': [eq.to_dict() for eq in equipment]
    }), 200

@app.route('/api/reports/value-summary', methods=['GET'])
def value_summary():
    """Resumo de valores investidos"""
    session = Session()
    
    # Valor total por tipo de equipamento
    summary = session.query(
        EquipmentType.nome,
        EquipmentType.marca,
        EquipmentType.modelo,
        func.sum(StockItem.valor_total).label('total'),
        func.count(StockItem.id).label('quantidade')
    ).join(StockItem).group_by(
        EquipmentType.id
    ).all()
    
    session.close()
    
    result = []
    for item in summary:
        result.append({
            'nome': item.nome,
            'marca': item.marca,
            'modelo': item.modelo,
            'valor_total': item.total,
            'quantidade': item.quantidade
        })
    
    return jsonify(result), 200

@app.route('/api/reports/movements', methods=['GET'])
def movements_report():
    """Histórico de movimentações"""
    session = Session()
    
    limit = int(request.args.get('limit', 100))
    
    movements = session.query(Movement).order_by(
        Movement.date.desc()
    ).limit(limit).all()
    
    session.close()
    
    return jsonify([m.to_dict() for m in movements]), 200

# ============== ROTA DE HEALTH CHECK ==============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verificar saúde da API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    # Criar banco se não existir
    if not os.path.exists('database.db'):
        print("Criando banco de dados...")
        init_db()
    
    print("Servidor rodando em http://127.0.0.1:5000")
    print("API Key para desenvolvimento: dev-key-12345")
    app.run(debug=True, host='0.0.0.0', port=5000)
