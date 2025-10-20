# Sistema de Gerência de Equipamentos - Fullstack Web Application

Sistema completo para gerenciamento de equipamentos com backend Python/Flask e frontend vanilla JavaScript.

## 📋 Características

- **Backend**: Python 3.10+ com Flask e SQLite
- **Frontend**: HTML5 + CSS3 + JavaScript (vanilla)
- **Banco de Dados**: SQLite (arquivo local, sem instalação necessária)
- **API REST**: Endpoints JSON para todas as operações
- **Importação de Dados**: Suporte para CSV e Excel (.xlsx)
- **Relatórios**: Dashboard com estatísticas e relatórios customizados

## 🚀 Funcionalidades

### Gestão de Equipamentos
- Cadastro de tipos de equipamentos
- Controle de estoque por nota fiscal
- Rastreamento individual (patrimonial/serial)
- Status: disponível, alocado, em manutenção, baixado

### Gestão de Usuários
- Importação de funcionários via CSV
- Busca e filtros por cidade, cargo, setor
- Visualização de equipamentos por usuário

### Destinação e Movimentação
- Destinação de equipamentos a usuários
- Devolução de equipamentos
- Histórico completo de movimentações

### Relatórios
- Resumo de estoque (disponíveis, alocados, etc)
- Valores investidos por tipo
- Equipamentos por usuário
- Histórico de movimentações

### Importação de Dados
- **CSV de Usuários**: colunas esperadas: nome, cpf, cargo, cidade, setor, matricula, email
- **Excel/CSV de Equipamentos**: colunas esperadas: nome, marca, modelo, patrimonial, serial, valor, data_aquisicao, status

## 📦 Estrutura do Projeto

```
project/
├── backend/
│   ├── app.py                 # Aplicação Flask principal
│   ├── models.py              # Modelos SQLAlchemy
│   ├── db_init.py            # Inicialização do banco
│   ├── config.py             # Configurações
│   ├── requirements.txt      # Dependências Python
│   ├── import_service.py     # Serviço de importação
│   └── utils.py              # Utilitários
├── frontend/
│   ├── index.html            # Interface principal
│   ├── app.js                # Lógica JavaScript
│   └── styles.css            # Estilos
├── uploads/                  # Arquivos importados
├── scripts/
│   └── backup.py             # Script de backup
└── README.md                 # Esta documentação
```

## 🛠️ Instalação e Configuração

### Pré-requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)

### Passo 1: Clonar ou criar a estrutura

Crie uma pasta para o projeto e organize os arquivos conforme a estrutura acima.

### Passo 2: Criar ambiente virtual (recomendado)

```bash
# No diretório do projeto
python -m venv venv

# Ativar o ambiente virtual
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### Passo 3: Instalar dependências

```bash
cd backend
pip install -r requirements.txt
```

**Dependências instaladas:**
- Flask: Framework web
- Flask-Cors: Habilitar CORS
- SQLAlchemy: ORM para banco de dados
- pandas: Manipulação de dados CSV/Excel
- openpyxl: Leitura de arquivos Excel
- reportlab: Geração de PDFs (opcional)

### Passo 4: Inicializar o banco de dados

```bash
# Ainda na pasta backend
python db_init.py
```

Isso criará o arquivo `database.db` com todas as tabelas necessárias.

### Passo 5: Executar o servidor backend

```bash
python app.py
```

O servidor estará disponível em: `http://127.0.0.1:5000`

### Passo 6: Abrir o frontend

Abra o arquivo `frontend/index.html` no navegador, ou use um servidor local:

**Opção 1 - Diretamente:**
- Navegue até a pasta `frontend` e abra `index.html` em um navegador

**Opção 2 - Com Python (recomendado):**
```bash
# Em outro terminal, na pasta frontend
python -m http.server 5500
```
Acesse: `http://127.0.0.1:5500`

**Opção 3 - Com VSCode Live Server:**
- Instale a extensão "Live Server"
- Clique com botão direito em `index.html` > "Open with Live Server"

## 🔑 API Key

A aplicação usa uma API key simples para proteger endpoints de escrita.

**API Key padrão de desenvolvimento:** `dev-key-12345`

Para alterar, edite o arquivo `backend/config.py` ou defina a variável de ambiente:
```bash
export API_KEY=sua-chave-personalizada
```

## 📊 Usando o Sistema

### 1. Importar Dados

**Importar Usuários:**
1. Prepare um arquivo CSV com as colunas: `nome`, `cpf`, `cargo`, `cidade`, `setor`, `matricula`, `email`
2. Vá para a aba "Importar Dados"
3. Selecione o arquivo CSV de usuários
4. Clique em "Importar Usuários"

**Importar Equipamentos:**
1. Prepare um arquivo Excel (.xlsx) ou CSV com as colunas: `nome`, `marca`, `modelo`, `patrimonial`, `serial`, `valor`, `data_aquisicao`, `status`
2. Vá para a aba "Importar Dados"
3. Selecione o arquivo
4. Clique em "Importar Equipamentos"

### 2. Cadastrar Nova Entrada de Estoque

1. Vá para a aba "Estoque"
2. Clique em "+ Adicionar Entrada"
3. Preencha os dados da nota fiscal
4. Salve

### 3. Destinar Equipamento

1. Vá para a aba "Destinações"
2. Selecione um equipamento disponível
3. Selecione o usuário
4. Adicione observações (opcional)
5. Clique em "Destinar Equipamento"

### 4. Devolver Equipamento

1. Na aba "Destinações", veja a lista de equipamentos alocados
2. Clique em "Devolver" no equipamento desejado
3. Confirme a devolução

### 5. Gerar Relatórios

1. Vá para a aba "Relatórios"
2. Escolha o tipo de relatório:
   - Resumo de Estoque
   - Resumo de Valores
   - Histórico de Movimentações
   - Equipamentos por Usuário (digite o ID)
3. Clique em "Gerar Relatório"

## 🗄️ Modelo de Dados

### Tabelas Principais

**users** - Funcionários
- id, cpf, nome, cargo, cidade, setor, email, matricula

**equipment_types** - Tipos de equipamentos
- id, nome, marca, modelo, especificacoes

**stock_items** - Entradas de estoque
- id, equipment_type_id, nota_numero, nota_data, quantidade, valor_unitario, valor_total, origem

**equipment_instances** - Instâncias individuais
- id, stock_item_id, patrimonial, serial, status, current_user_id, assigned_at

**movements** - Histórico de movimentações
- id, equipment_instance_id, from_user_id, to_user_id, type, date, note

**invoices** - Notas fiscais (opcional)
- id, numero, data, fornecedor, valor_total

## 🔌 API Endpoints

### Importação
- `POST /api/import/users` - Importar usuários (CSV)
- `POST /api/import/equipment` - Importar equipamentos (Excel/CSV)

### Usuários
- `GET /api/users` - Listar usuários (filtros: ?city=&cargo=&setor=&q=)
- `GET /api/users/<id>` - Detalhes de um usuário
- `POST /api/users` - Criar usuário

### Tipos de Equipamentos
- `GET /api/equipment-types` - Listar tipos (filtro: ?q=)
- `POST /api/equipment-types` - Criar tipo

### Estoque
- `GET /api/stock` - Listar estoque (filtros: ?type_id=)
- `POST /api/stock` - Adicionar entrada

### Instâncias de Equipamentos
- `GET /api/equipment-instances` - Listar instâncias (filtros: ?status=&user_id=)

### Destinação
- `POST /api/assign` - Destinar equipamento
- `POST /api/return` - Devolver equipamento

### Relatórios
- `GET /api/reports/stock-summary` - Resumo do estoque
- `GET /api/reports/user/<id>` - Equipamentos por usuário
- `GET /api/reports/value-summary` - Resumo de valores
- `GET /api/reports/movements` - Histórico (parâmetro: ?limit=)

### Utilitários
- `GET /api/health` - Health check da API

**Nota:** Endpoints de escrita (POST) requerem o header `X-API-Key` com a chave configurada.

## 🔐 Segurança

- **API Key**: Proteção básica com chave configurável
- **CORS**: Configurado para origens locais (localhost:3000, localhost:5500)
- **Validação**: Tipos de arquivo permitidos: .csv, .xlsx, .xls
- **Tamanho**: Upload limitado a 16MB

**⚠️ Aviso**: Este sistema é para uso local/desenvolvimento. Para produção, implemente:
- Autenticação robusta (JWT, OAuth)
- HTTPS
- Validação de entrada mais rigorosa
- Rate limiting
- Logs de auditoria

## 🛡️ Backup

Para fazer backup do banco de dados:

```bash
cd scripts
python backup.py
```

Isso gerará um arquivo JSON com todos os dados: `backup_YYYYMMDD_HHMMSS.json`

## 🐛 Troubleshooting

### Problema: Erro ao instalar pandas/openpyxl

**Solução**: Se não conseguir instalar as bibliotecas para Excel:
1. Converta seus arquivos .xlsx para .csv
2. Use apenas arquivos CSV
3. Remova `openpyxl` do `requirements.txt`

### Problema: CORS bloqueando requisições

**Solução**: 
1. Verifique se o frontend está rodando nas portas configuradas (3000 ou 5500)
2. Adicione a origem do seu frontend em `backend/config.py` → `CORS_ORIGINS`

### Problema: Banco de dados não criado

**Solução**:
```bash
cd backend
python db_init.py
```

### Problema: "Module not found"

**Solução**: Certifique-se de estar no ambiente virtual e ter instalado as dependências:
```bash
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt
```

## 📈 Melhorias Futuras

- [ ] Autenticação de usuários
- [ ] Geração de PDF dos relatórios
- [ ] Upload de múltiplos arquivos simultâneos
- [ ] Gráficos interativos (Chart.js)
- [ ] Filtros avançados
- [ ] Exportação de dados
- [ ] Notificações por email
- [ ] Histórico de alterações (audit log)
- [ ] Agendamento de alertas
- [ ] Dashboard com métricas em tempo real

## 📄 Licença

Este projeto é de código aberto para fins educacionais e pode ser modificado conforme necessário.

## 🤝 Contribuições

Sinta-se livre para sugerir melhorias, reportar bugs ou contribuir com código!

---

**Desenvolvido com ❤️ usando Flask + JavaScript**
