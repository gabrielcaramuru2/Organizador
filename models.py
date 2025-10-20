from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import enum

Base = declarative_base()

class StatusEnum(enum.Enum):
    """Status do equipamento"""
    disponivel = "disponível"
    alocado = "alocado"
    em_manutencao = "em manutenção"
    baixado = "baixado"

class MovementTypeEnum(enum.Enum):
    """Tipo de movimentação"""
    destinacao = "destinação"
    devolucao = "devolução"
    transferencia = "transferência"
    baixa = "baixa"

class User(Base):
    """Funcionários/Usuários"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cpf = Column(String(14), unique=True, nullable=True, index=True)
    nome = Column(String(200), nullable=False)
    cargo = Column(String(100))
    cidade = Column(String(100))
    setor = Column(String(100))
    email = Column(String(200))
    matricula = Column(String(50), unique=True, nullable=True, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relacionamentos
    equipment_instances = relationship("EquipmentInstance", back_populates="current_user")
    movements_from = relationship("Movement", foreign_keys="Movement.from_user_id")
    movements_to = relationship("Movement", foreign_keys="Movement.to_user_id")
    
    def to_dict(self):
        return {
            'id': self.id,
            'cpf': self.cpf,
            'nome': self.nome,
            'cargo': self.cargo,
            'cidade': self.cidade,
            'setor': self.setor,
            'email': self.email,
            'matricula': self.matricula,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class EquipmentType(Base):
    """Tipos/Modelos de equipamentos"""
    __tablename__ = 'equipment_types'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(200), nullable=False)
    marca = Column(String(100))
    modelo = Column(String(100))
    especificacoes = Column(Text)  # JSON ou texto livre
    created_at = Column(DateTime, default=datetime.now)
    
    # Relacionamentos
    stock_items = relationship("StockItem", back_populates="equipment_type")
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'marca': self.marca,
            'modelo': self.modelo,
            'especificacoes': self.especificacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class StockItem(Base):
    """Item de estoque (entrada por nota fiscal)"""
    __tablename__ = 'stock_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_type_id = Column(Integer, ForeignKey('equipment_types.id'), nullable=False)
    nota_numero = Column(String(50))
    nota_data = Column(Date)
    quantidade = Column(Integer, default=1)
    valor_unitario = Column(Float, default=0.0)
    valor_total = Column(Float, default=0.0)
    origem = Column(String(200))  # Importação, compra, doação, etc
    created_at = Column(DateTime, default=datetime.now)
    
    # Relacionamentos
    equipment_type = relationship("EquipmentType", back_populates="stock_items")
    equipment_instances = relationship("EquipmentInstance", back_populates="stock_item")
    
    def to_dict(self):
        return {
            'id': self.id,
            'equipment_type_id': self.equipment_type_id,
            'equipment_type': self.equipment_type.to_dict() if self.equipment_type else None,
            'nota_numero': self.nota_numero,
            'nota_data': self.nota_data.isoformat() if self.nota_data else None,
            'quantidade': self.quantidade,
            'valor_unitario': self.valor_unitario,
            'valor_total': self.valor_total,
            'origem': self.origem,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class EquipmentInstance(Base):
    """Instância individual de equipamento (com serial/patrimonial)"""
    __tablename__ = 'equipment_instances'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_item_id = Column(Integer, ForeignKey('stock_items.id'), nullable=False)
    patrimonial = Column(String(50), unique=True, nullable=True, index=True)
    serial = Column(String(100), nullable=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.disponivel)
    current_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    assigned_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relacionamentos
    stock_item = relationship("StockItem", back_populates="equipment_instances")
    current_user = relationship("User", back_populates="equipment_instances")
    movements = relationship("Movement", back_populates="equipment_instance")
    
    def to_dict(self):
        return {
            'id': self.id,
            'stock_item_id': self.stock_item_id,
            'stock_item': self.stock_item.to_dict() if self.stock_item else None,
            'patrimonial': self.patrimonial,
            'serial': self.serial,
            'status': self.status.value if self.status else None,
            'current_user_id': self.current_user_id,
            'current_user': self.current_user.to_dict() if self.current_user else None,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Movement(Base):
    """Histórico de movimentações"""
    __tablename__ = 'movements'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_instance_id = Column(Integer, ForeignKey('equipment_instances.id'), nullable=False)
    from_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    to_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    type = Column(Enum(MovementTypeEnum), nullable=False)
    date = Column(DateTime, default=datetime.now)
    note = Column(Text)
    
    # Relacionamentos
    equipment_instance = relationship("EquipmentInstance", back_populates="movements")
    
    def to_dict(self):
        return {
            'id': self.id,
            'equipment_instance_id': self.equipment_instance_id,
            'from_user_id': self.from_user_id,
            'to_user_id': self.to_user_id,
            'type': self.type.value if self.type else None,
            'date': self.date.isoformat() if self.date else None,
            'note': self.note
        }

class Invoice(Base):
    """Notas fiscais (opcional - agrupador)"""
    __tablename__ = 'invoices'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String(50), unique=True, nullable=False)
    data = Column(Date)
    fornecedor = Column(String(200))
    valor_total = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero': self.numero,
            'data': self.data.isoformat() if self.data else None,
            'fornecedor': self.fornecedor,
            'valor_total': self.valor_total,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

def init_db(database_url='sqlite:///database.db'):
    """Inicializar banco de dados"""
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    """Obter sessão do banco"""
    Session = sessionmaker(bind=engine)
    return Session()
