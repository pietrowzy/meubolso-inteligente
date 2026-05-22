// ============================ 
// Configuração da API 
// ============================ 
// Define a URL base da nossa API para requisições 
const API_URL = "http://127.0.0.1:5000"; 
// ============================ 
// FUNÇÃO: PROTEGER PÁGINAS INTERNAS 
// ============================ 
// Verifica se o usuário está logado 
// Retorna o ID do usuário se estiver logado ou null caso contrário 
function getUsuarioLogado() { 
if (window.USUARIO_ID) { 
return { 
id: window.USUARIO_ID 
}; 
} 
return null; 
} 
// ============================ 
// FUNÇÃO: CARREGAR CATEGORIAS 
// ============================ 
// Função assíncrona para carregar categorias do tipo informado 
// e popular um <select> no HTML 
async function carregarCategorias(tipo, selectId) { 
const select = document.getElementById(selectId); 
if (!select) return; // Se o select não existe, não faz nada 
// Requisição para a API para pegar categorias 
const response = await fetch(`${API_URL}/categorias?tipo=${tipo}`); 
    const categorias = await response.json(); 
 
    // Cria <option> para cada categoria 
    categorias.forEach(categoria => { 
        const option = document.createElement("option"); 
        option.value = categoria.id; 
        option.textContent = categoria.nome; 
        select.appendChild(option); 
    }); 
} 
 
// ============================ 
// FUNÇÃO: CARREGAR RELATÓRIOS 
// ============================ 
// Carrega dados de relatórios financeiros 
async function carregarRelatorios() { 
    const usuario = getUsuarioLogado(); 
 
    if (!usuario) { 
        alert("Faça login novamente."); 
        window.location.href = "/login"; // Redireciona para login se não estiver logado 
        return; 
    } 
 
    // Chama funções para carregar cada relatório 
    await carregarRelatorioCategorias(); 
    await carregarHistoricoReceitas(); 
    await carregarHistoricoDespesas(); 
} 
 
// ============================ 
// FUNÇÃO: CARREGAR DASHBOARD 
// ============================ 
// Puxa os dados do dashboard (totais de receitas, despesas e saldo) 
async function carregarDashboard() { 
    const response = await fetch("/dashboard/dados"); 
    const data = await response.json(); 
 
    if (!response.ok) { 
        window.location.href = "/login"; // Redireciona se não autorizado 
        return; 
    } 
 
    // Atualiza os elementos do HTML com os valores formatados 
    document.getElementById("totalReceitas").innerText = 
        `R$ ${Number(data.total_receitas).toFixed(2)}`; 
 
    document.getElementById("totalDespesas").innerText = 
        `R$ ${Number(data.total_despesas).toFixed(2)}`; 
 
    document.getElementById("saldo").innerText = 
        `R$ ${Number(data.saldo).toFixed(2)}`; 
} 
 
// ============================ 
// INICIALIZA DASHBOARD AUTOMATICAMENTE 
// ============================ 
if (document.getElementById("saldo")) { 
    carregarDashboard(); 
    carregarGraficoResumo(); 
    carregarGraficoCategoria(); 
}


