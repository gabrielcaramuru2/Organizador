// Configuração da API
const API_URL = 'https://organizador-ctxb.onrender.com/api';
const API_KEY = 'dev-key-12345';

// Estado global
let currentView = 'dashboard';
let allUsers = [];
let allEquipmentTypes = [];
let allStockItems = [];
let allEquipmentInstances = [];

// ============== INICIALIZAÇÃO ==============

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    loadDashboard();
    
    // Event listeners para busca
    document.getElementById('stock-search')?.addEventListener('input', filterStock);
    document.getElementById('users-search')?.addEventListener('input', filterUsers);
    
    // Forms
    document.getElementById('assign-form')?.addEventListener('submit', handleAssign);
    document.getElementById('add-stock-form')?.addEventListener('submit', handleAddStock);
});

// ============== NAVEGAÇÃO ==============

function initNavigation() {
    const navBtns = document.querySelectorAll('.nav-btn');
    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const view = btn.dataset.view;
            switchView(view);
        });
    });
}

function switchView(view) {
    // Atualizar botões
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === view);
    });
    
    // Atualizar views
    document.querySelectorAll('.view').forEach(v => {
        v.classList.remove('active');
    });
    document.getElementById(`${view}-view`).classList.add('active');
    
    currentView = view;
    
    // Carregar dados da view
    switch(view) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'stock':
            loadStock();
            break;
        case 'users':
            loadUsers();
            break;
        case 'assign':
            loadAssignView();
            break;
        case 'reports':
            break;
        case 'import':
            break;
    }
}

// ============== DASHBOARD ==============

async function loadDashboard() {
    try {
        const response = await fetch(`${API_URL}/reports/stock-summary`);
        const data = await response.json();
        
        document.getElementById('stat-total').textContent = data.total || 0;
        document.getElementById('stat-disponivel').textContent = data.disponivel || 0;
        document.getElementById('stat-alocado').textContent = data.alocado || 0;
        document.getElementById('stat-manutencao').textContent = data.em_manutencao || 0;
        document.getElementById('stat-valor').textContent = formatCurrency(data.valor_total_investido);
    } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
        showNotification('Erro ao carregar dashboard', 'error');
    }
}

// ============== ESTOQUE ==============

async function loadStock() {
    try {
        const response = await fetch(`${API_URL}/stock`);
        const data = await response.json();
        allStockItems = data;
        renderStockTable(data);
    } catch (error) {
        console.error('Erro ao carregar estoque:', error);
        showNotification('Erro ao carregar estoque', 'error');
    }
}

function renderStockTable(items) {
    const tbody = document.getElementById('stock-tbody');
    tbody.innerHTML = '';
    
    items.forEach(item => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${item.id}</td>
            <td>${item.equipment_type?.nome || '-'}</td>
            <td>${item.equipment_type?.marca || '-'}</td>
            <td>${item.equipment_type?.modelo || '-'}</td>
            <td>${item.nota_numero || '-'}</td>
            <td>${item.nota_data || '-'}</td>
            <td>${item.quantidade}</td>
            <td>${formatCurrency(item.valor_total)}</td>
        `;
    });
}

function filterStock() {
    const query = document.getElementById('stock-search').value.toLowerCase();
    const filtered = allStockItems.filter(item => {
        const nome = item.equipment_type?.nome?.toLowerCase() || '';
        const marca = item.equipment_type?.marca?.toLowerCase() || '';
        const modelo = item.equipment_type?.modelo?.toLowerCase() || '';
        return nome.includes(query) || marca.includes(query) || modelo.includes(query);
    });
    renderStockTable(filtered);
}

// ============== USUÁRIOS ==============

async function loadUsers() {
    try {
        const response = await fetch(`${API_URL}/users`);
        const data = await response.json();
        allUsers = data;
        renderUsersTable(data);
        populateCityFilter(data);
    } catch (error) {
        console.error('Erro ao carregar usuários:', error);
        showNotification('Erro ao carregar usuários', 'error');
    }
}

function renderUsersTable(users) {
    const tbody = document.getElementById('users-tbody');
    tbody.innerHTML = '';
    
    users.forEach(user => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${user.id}</td>
            <td>${user.nome}</td>
            <td>${user.cpf || '-'}</td>
            <td>${user.cargo || '-'}</td>
            <td>${user.cidade || '-'}</td>
            <td>${user.setor || '-'}</td>
            <td>
                <button class="btn btn-small" onclick="viewUserEquipment(${user.id})">Ver Equipamentos</button>
            </td>
        `;
    });
}

function populateCityFilter(users) {
    const cities = [...new Set(users.map(u => u.cidade).filter(c => c))];
    const select = document.getElementById('users-city-filter');
    select.innerHTML = '<option value="">Todas as cidades</option>';
    cities.forEach(city => {
        const option = document.createElement('option');
        option.value = city;
        option.textContent = city;
        select.appendChild(option);
    });
    
    select.addEventListener('change', filterUsers);
}

function filterUsers() {
    const query = document.getElementById('users-search').value.toLowerCase();
    const city = document.getElementById('users-city-filter').value;
    
    const filtered = allUsers.filter(user => {
        const matchQuery = user.nome.toLowerCase().includes(query) || 
                          (user.cpf && user.cpf.includes(query)) ||
                          (user.matricula && user.matricula.includes(query));
        const matchCity = !city || user.cidade === city;
        return matchQuery && matchCity;
    });
    
    renderUsersTable(filtered);
}

// ============== DESTINAÇÕES ==============

async function loadAssignView() {
    await loadAvailableEquipment();
    await loadUsersForAssign();
    await loadAllocatedEquipment();
}

async function loadAvailableEquipment() {
    try {
        const response = await fetch(`${API_URL}/equipment-instances?status=disponivel`);
        const data = await response.json();
        
        const select = document.getElementById('assign-equipment');
        select.innerHTML = '<option value="">Selecione um equipamento</option>';
        
        data.forEach(eq => {
            const option = document.createElement('option');
            option.value = eq.id;
            option.textContent = `${eq.stock_item?.equipment_type?.nome || 'Equipamento'} - ${eq.patrimonial || eq.serial || eq.id}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Erro ao carregar equipamentos disponíveis:', error);
    }
}

async function loadUsersForAssign() {
    try {
        const response = await fetch(`${API_URL}/users`);
        const data = await response.json();
        
        const select = document.getElementById('assign-user');
        select.innerHTML = '<option value="">Selecione um usuário</option>';
        
        data.forEach(user => {
            const option = document.createElement('option');
            option.value = user.id;
            option.textContent = `${user.nome} - ${user.cargo || ''} (${user.cidade || ''})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Erro ao carregar usuários:', error);
    }
}

async function loadAllocatedEquipment() {
    try {
        const response = await fetch(`${API_URL}/equipment-instances?status=alocado`);
        const data = await response.json();
        
        const container = document.getElementById('allocated-list');
        container.innerHTML = '';
        
        data.forEach(eq => {
            const div = document.createElement('div');
            div.className = 'allocated-item';
            div.innerHTML = `
                <strong>${eq.stock_item?.equipment_type?.nome || 'Equipamento'}</strong><br>
                <small>Usuário: ${eq.current_user?.nome || 'N/A'}</small><br>
                <small>Desde: ${new Date(eq.assigned_at).toLocaleDateString()}</small><br>
                <button class="btn btn-small" onclick="returnEquipment(${eq.id})">Devolver</button>
            `;
            container.appendChild(div);
        });
    } catch (error) {
        console.error('Erro ao carregar equipamentos alocados:', error);
    }
}

async function handleAssign(e) {
    e.preventDefault();
    
    const equipmentId = document.getElementById('assign-equipment').value;
    const userId = document.getElementById('assign-user').value;
    const note = document.getElementById('assign-note').value;
    
    if (!equipmentId || !userId) {
        showNotification('Selecione equipamento e usuário', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/assign`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_KEY
            },
            body: JSON.stringify({
                equipment_instance_id: parseInt(equipmentId),
                to_user_id: parseInt(userId),
                note: note
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Equipamento destinado com sucesso!', 'success');
            document.getElementById('assign-form').reset();
            loadAssignView();
        } else {
            showNotification(data.error || 'Erro ao destinar equipamento', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showNotification('Erro ao destinar equipamento', 'error');
    }
}

async function returnEquipment(instanceId) {
    if (!confirm('Deseja realmente devolver este equipamento?')) return;
    
    try {
        const response = await fetch(`${API_URL}/return`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_KEY
            },
            body: JSON.stringify({
                equipment_instance_id: instanceId
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Equipamento devolvido com sucesso!', 'success');
            loadAssignView();
        } else {
            showNotification(data.error || 'Erro ao devolver equipamento', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showNotification('Erro ao devolver equipamento', 'error');
    }
}

// ============== RELATÓRIOS ==============

async function generateStockReport() {
    try {
        const response = await fetch(`${API_URL}/reports/stock-summary`);
        const data = await response.json();
        
        const output = document.getElementById('report-output');
        output.innerHTML = `
            <h3>Resumo de Estoque</h3>
            <div class="report-content">
                <p><strong>Total de Equipamentos:</strong> ${data.total}</p>
                <p><strong>Disponíveis:</strong> ${data.disponivel}</p>
                <p><strong>Alocados:</strong> ${data.alocado}</p>
                <p><strong>Em Manutenção:</strong> ${data.em_manutencao}</p>
                <p><strong>Baixados:</strong> ${data.baixado}</p>
                <p><strong>Valor Total Investido:</strong> ${formatCurrency(data.valor_total_investido)}</p>
            </div>
        `;
    } catch (error) {
        showNotification('Erro ao gerar relatório', 'error');
    }
}

async function generateValueReport() {
    try {
        const response = await fetch(`${API_URL}/reports/value-summary`);
        const data = await response.json();
        
        const output = document.getElementById('report-output');
        let html = '<h3>Resumo de Valores por Tipo</h3><table class="report-table"><thead><tr><th>Nome</th><th>Marca</th><th>Modelo</th><th>Quantidade</th><th>Valor Total</th></tr></thead><tbody>';
        
        data.forEach(item => {
            html += `<tr>
                <td>${item.nome}</td>
                <td>${item.marca || '-'}</td>
                <td>${item.modelo || '-'}</td>
                <td>${item.quantidade}</td>
                <td>${formatCurrency(item.valor_total)}</td>
            </tr>`;
        });
        
        html += '</tbody></table>';
        output.innerHTML = html;
    } catch (error) {
        showNotification('Erro ao gerar relatório', 'error');
    }
}

async function generateMovementsReport() {
    try {
        const response = await fetch(`${API_URL}/reports/movements?limit=50`);
        const data = await response.json();
        
        const output = document.getElementById('report-output');
        let html = '<h3>Histórico de Movimentações (Últimas 50)</h3><table class="report-table"><thead><tr><th>Data</th><th>Tipo</th><th>Equipamento ID</th><th>Observações</th></tr></thead><tbody>';
        
        data.forEach(mov => {
            html += `<tr>
                <td>${new Date(mov.date).toLocaleString()}</td>
                <td>${mov.type}</td>
                <td>${mov.equipment_instance_id}</td>
                <td>${mov.note || '-'}</td>
            </tr>`;
        });
        
        html += '</tbody></table>';
        output.innerHTML = html;
    } catch (error) {
        showNotification('Erro ao gerar relatório', 'error');
    }
}

async function generateUserReport() {
    const userId = document.getElementById('report-user-id').value;
    if (!userId) {
        showNotification('Digite o ID do usuário', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/reports/user/${userId}`);
        const data = await response.json();
        
        const output = document.getElementById('report-output');
        let html = `<h3>Equipamentos de ${data.user.nome}</h3>`;
        html += `<p><strong>CPF:</strong> ${data.user.cpf || '-'} | <strong>Cargo:</strong> ${data.user.cargo || '-'} | <strong>Cidade:</strong> ${data.user.cidade || '-'}</p>`;
        
        if (data.equipment.length > 0) {
            html += '<table class="report-table"><thead><tr><th>ID</th><th>Equipamento</th><th>Patrimonial</th><th>Serial</th><th>Desde</th></tr></thead><tbody>';
            
            data.equipment.forEach(eq => {
                html += `<tr>
                    <td>${eq.id}</td>
                    <td>${eq.stock_item?.equipment_type?.nome || '-'}</td>
                    <td>${eq.patrimonial || '-'}</td>
                    <td>${eq.serial || '-'}</td>
                    <td>${eq.assigned_at ? new Date(eq.assigned_at).toLocaleDateString() : '-'}</td>
                </tr>`;
            });
            
            html += '</tbody></table>';
        } else {
            html += '<p>Nenhum equipamento alocado.</p>';
        }
        
        output.innerHTML = html;
    } catch (error) {
        showNotification('Erro ao gerar relatório', 'error');
    }
}

// ============== IMPORTAÇÃO ==============

async function importUsers() {
    const fileInput = document.getElementById('import-users-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showNotification('Selecione um arquivo', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_URL}/import/users`, {
            method: 'POST',
            headers: {
                'X-API-Key': API_KEY
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('import-result').innerHTML = `
                <div class="success-message">
                    <p>Importação concluída com sucesso!</p>
                    <p>Criados: ${data.stats.created} | Atualizados: ${data.stats.updated} | Erros: ${data.stats.errors}</p>
                </div>
            `;
            fileInput.value = '';
        } else {
            showNotification(data.error || 'Erro ao importar', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showNotification('Erro ao importar usuários', 'error');
    }
}

async function importEquipment() {
    const fileInput = document.getElementById('import-equipment-file');
    const file = fileInput.files[0];
    
    if (!file) {
        showNotification('Selecione um arquivo', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_URL}/import/equipment`, {
            method: 'POST',
            headers: {
                'X-API-Key': API_KEY
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('import-result').innerHTML = `
                <div class="success-message">
                    <p>Importação concluída com sucesso!</p>
                    <p>Tipos criados: ${data.stats.equipment_types_created} | Instâncias: ${data.stats.instances_created} | Erros: ${data.stats.errors}</p>
                </div>
            `;
            fileInput.value = '';
        } else {
            showNotification(data.error || 'Erro ao importar', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showNotification('Erro ao importar equipamentos', 'error');
    }
}

// ============== MODAL DE ESTOQUE ==============

async function showAddStockModal() {
    // Carregar tipos de equipamentos
    try {
        const response = await fetch(`${API_URL}/equipment-types`);
        const types = await response.json();
        
        const select = document.getElementById('stock-type-id');
        select.innerHTML = '<option value="">Selecione o tipo</option>';
        
        types.forEach(type => {
            const option = document.createElement('option');
            option.value = type.id;
            option.textContent = `${type.nome} - ${type.marca || ''} ${type.modelo || ''}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Erro ao carregar tipos:', error);
    }
    
    document.getElementById('add-stock-modal').style.display = 'block';
}

function closeAddStockModal() {
    document.getElementById('add-stock-modal').style.display = 'none';
    document.getElementById('add-stock-form').reset();
}

async function handleAddStock(e) {
    e.preventDefault();
    
    const typeId = document.getElementById('stock-type-id').value;
    const notaNumero = document.getElementById('stock-nota-numero').value;
    const notaData = document.getElementById('stock-nota-data').value;
    const quantidade = parseInt(document.getElementById('stock-quantidade').value);
    const valorUnitario = parseFloat(document.getElementById('stock-valor-unitario').value);
    const origem = document.getElementById('stock-origem').value;
    
    if (!typeId) {
        showNotification('Selecione o tipo de equipamento', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/stock`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_KEY
            },
            body: JSON.stringify({
                equipment_type_id: parseInt(typeId),
                nota_numero: notaNumero,
                nota_data: notaData,
                quantidade: quantidade,
                valor_unitario: valorUnitario,
                valor_total: valorUnitario * quantidade,
                origem: origem,
                instances: []
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Entrada adicionada com sucesso!', 'success');
            closeAddStockModal();
            loadStock();
        } else {
            showNotification(data.error || 'Erro ao adicionar entrada', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showNotification('Erro ao adicionar entrada', 'error');
    }
}

// ============== UTILIDADES ==============

function formatCurrency(value) {
    if (!value) return 'R$ 0,00';
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type} show`;
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

async function viewUserEquipment(userId) {
    try {
        const response = await fetch(`${API_URL}/reports/user/${userId}`);
        const data = await response.json();
        
        if (data.equipment.length === 0) {
            showNotification('Usuário não possui equipamentos alocados', 'info');
            return;
        }
        
        let message = `Equipamentos de ${data.user.nome}:\n\n`;
        data.equipment.forEach(eq => {
            message += `- ${eq.stock_item?.equipment_type?.nome || 'Equipamento'} (${eq.patrimonial || eq.serial || eq.id})\n`;
        });
        
        alert(message);
    } catch (error) {
        showNotification('Erro ao buscar equipamentos', 'error');
    }
}

// Fechar modal ao clicar fora
window.onclick = function(event) {
    const modal = document.getElementById('add-stock-modal');
    if (event.target === modal) {
        closeAddStockModal();
    }
}
