import pandas as pd
from datetime import datetime
from models import User, EquipmentType, StockItem, EquipmentInstance, StatusEnum
from sqlalchemy.exc import IntegrityError
import json

class ImportService:
    """Serviço de importação de dados"""
    
    def __init__(self, session):
        self.session = session
        
    def normalize_cpf(self, cpf):
        """Normalizar CPF"""
        if pd.isna(cpf) or not cpf:
            return None
        cpf_str = str(cpf).strip()
        # Remover caracteres não numéricos
        cpf_clean = ''.join(filter(str.isdigit, cpf_str))
        if len(cpf_clean) == 11:
            return f"{cpf_clean[:3]}.{cpf_clean[3:6]}.{cpf_clean[6:9]}-{cpf_clean[9:]}"
        return cpf_clean if cpf_clean else None
    
    def import_users_from_csv(self, file_path):
        """
        Importar usuários do CSV
        Esperado: colunas como nome, cpf, cargo, cidade, setor, matricula, email
        """
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='latin-1')
        
        # Normalizar nomes de colunas (minúsculas, sem espaços)
        df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
        
        stats = {'created': 0, 'updated': 0, 'errors': 0}
        
        for idx, row in df.iterrows():
            try:
                # Extrair dados
                cpf = self.normalize_cpf(row.get('cpf'))
                nome = str(row.get('nome', '')).strip()
                cargo = str(row.get('cargo', '')).strip() if pd.notna(row.get('cargo')) else None
                cidade = str(row.get('cidade', '')).strip() if pd.notna(row.get('cidade')) else None
                setor = str(row.get('setor', '')).strip() if pd.notna(row.get('setor')) else None
                email = str(row.get('email', '')).strip() if pd.notna(row.get('email')) else None
                matricula = str(row.get('matricula', '')).strip() if pd.notna(row.get('matricula')) else None
                
                if not nome:
                    continue
                
                # Buscar por CPF ou matrícula
                user = None
                if cpf:
                    user = self.session.query(User).filter_by(cpf=cpf).first()
                if not user and matricula:
                    user = self.session.query(User).filter_by(matricula=matricula).first()
                
                if user:
                    # Atualizar
                    user.nome = nome
                    user.cargo = cargo
                    user.cidade = cidade
                    user.setor = setor
                    user.email = email
                    if cpf and not user.cpf:
                        user.cpf = cpf
                    if matricula and not user.matricula:
                        user.matricula = matricula
                    user.updated_at = datetime.now()
                    stats['updated'] += 1
                else:
                    # Criar novo
                    user = User(
                        cpf=cpf,
                        nome=nome,
                        cargo=cargo,
                        cidade=cidade,
                        setor=setor,
                        email=email,
                        matricula=matricula
                    )
                    self.session.add(user)
                    stats['created'] += 1
                
            except Exception as e:
                stats['errors'] += 1
                print(f"Erro na linha {idx}: {e}")
        
        self.session.commit()
        return stats
    
    def import_equipment_from_excel(self, file_path):
        """
        Importar equipamentos do Excel
        Esperado: colunas como nome, marca, modelo, patrimonial, serial, data_aquisicao, status
        """
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
        except Exception as e:
            # Fallback: tentar ler como CSV
            try:
                df = pd.read_csv(file_path)
            except:
                raise Exception(f"Não foi possível ler o arquivo: {e}")
        
        # Normalizar nomes de colunas
        df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
        
        stats = {'equipment_types_created': 0, 'instances_created': 0, 'errors': 0}
        
        for idx, row in df.iterrows():
            try:
                # Extrair dados
                nome = str(row.get('nome', '')).strip() if pd.notna(row.get('nome')) else None
                marca = str(row.get('marca', '')).strip() if pd.notna(row.get('marca')) else None
                modelo = str(row.get('modelo', '')).strip() if pd.notna(row.get('modelo')) else None
                patrimonial = str(row.get('patrimonial', '')).strip() if pd.notna(row.get('patrimonial')) else None
                serial = str(row.get('serial', '')).strip() if pd.notna(row.get('serial')) else None
                data_aquisicao = row.get('data_aquisicao')
                status_str = str(row.get('status', 'disponível')).strip().lower() if pd.notna(row.get('status')) else 'disponível'
                valor = float(row.get('valor', 0)) if pd.notna(row.get('valor')) else 0.0
                
                if not nome:
                    continue
                
                # Buscar ou criar tipo de equipamento
                eq_type = self.session.query(EquipmentType).filter_by(
                    nome=nome, 
                    marca=marca, 
                    modelo=modelo
                ).first()
                
                if not eq_type:
                    eq_type = EquipmentType(
                        nome=nome,
                        marca=marca,
                        modelo=modelo,
                        especificacoes=json.dumps({'imported': True})
                    )
                    self.session.add(eq_type)
                    self.session.flush()
                    stats['equipment_types_created'] += 1
                
                # Criar item de estoque
                stock_item = StockItem(
                    equipment_type_id=eq_type.id,
                    nota_numero=None,
                    nota_data=pd.to_datetime(data_aquisicao).date() if pd.notna(data_aquisicao) else None,
                    quantidade=1,
                    valor_unitario=valor,
                    valor_total=valor,
                    origem='import_excel'
                )
                self.session.add(stock_item)
                self.session.flush()
                
                # Mapear status
                status_map = {
                    'disponível': StatusEnum.disponivel,
                    'disponivel': StatusEnum.disponivel,
                    'alocado': StatusEnum.alocado,
                    'em manutenção': StatusEnum.em_manutencao,
                    'em manutencao': StatusEnum.em_manutencao,
                    'baixado': StatusEnum.baixado
                }
                status = status_map.get(status_str, StatusEnum.disponivel)
                
                # Criar instância de equipamento
                instance = EquipmentInstance(
                    stock_item_id=stock_item.id,
                    patrimonial=patrimonial,
                    serial=serial,
                    status=status
                )
                self.session.add(instance)
                stats['instances_created'] += 1
                
            except Exception as e:
                stats['errors'] += 1
                print(f"Erro na linha {idx}: {e}")
        
        self.session.commit()
        return stats
    
    def import_equipment_from_csv(self, file_path):
        """Importar equipamentos de CSV (alternativa ao Excel)"""
        # Mesma lógica, mas lê CSV
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='latin-1')
        
        df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
        
        stats = {'equipment_types_created': 0, 'instances_created': 0, 'errors': 0}
        
        for idx, row in df.iterrows():
            try:
                nome = str(row.get('nome', '')).strip() if pd.notna(row.get('nome')) else None
                marca = str(row.get('marca', '')).strip() if pd.notna(row.get('marca')) else None
                modelo = str(row.get('modelo', '')).strip() if pd.notna(row.get('modelo')) else None
                patrimonial = str(row.get('patrimonial', '')).strip() if pd.notna(row.get('patrimonial')) else None
                serial = str(row.get('serial', '')).strip() if pd.notna(row.get('serial')) else None
                valor = float(row.get('valor', 0)) if pd.notna(row.get('valor')) else 0.0
                
                if not nome:
                    continue
                
                eq_type = self.session.query(EquipmentType).filter_by(
                    nome=nome, marca=marca, modelo=modelo
                ).first()
                
                if not eq_type:
                    eq_type = EquipmentType(nome=nome, marca=marca, modelo=modelo)
                    self.session.add(eq_type)
                    self.session.flush()
                    stats['equipment_types_created'] += 1
                
                stock_item = StockItem(
                    equipment_type_id=eq_type.id,
                    quantidade=1,
                    valor_unitario=valor,
                    valor_total=valor,
                    origem='import_csv'
                )
                self.session.add(stock_item)
                self.session.flush()
                
                instance = EquipmentInstance(
                    stock_item_id=stock_item.id,
                    patrimonial=patrimonial,
                    serial=serial,
                    status=StatusEnum.disponivel
                )
                self.session.add(instance)
                stats['instances_created'] += 1
                
            except Exception as e:
                stats['errors'] += 1
                print(f"Erro na linha {idx}: {e}")
        
        self.session.commit()
        return stats
