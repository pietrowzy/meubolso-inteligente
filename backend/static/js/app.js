const API_URL = "http://127.0.0.1:5000";

// ============================
// PROTEGER PÁGINAS INTERNAS
// ============================
function getUsuarioLogado() {
    if (window.USUARIO_ID) {
        return {
            id: window.USUARIO_ID
        };
    }
    return null;
}

// ============================
// CARREGAR CATEGORIAS
// ============================
async function carregarCategorias(tipo, selectId) {

    const select = document.getElementById(selectId);

    if (!select) return;

    const response = await fetch(`${API_URL}/categorias?tipo=${tipo}`);

    const categorias = await response.json();

    categorias.forEach(categoria => {
        const option = document.createElement("option");
        option.value = categoria.id;
        option.textContent = categoria.nome;
        select.appendChild(option);
    });

}

// ============================
// RELATÓRIOS
// ============================
async function carregarRelatorios() {

    const usuario = getUsuarioLogado();

    if (!usuario) {
        alert("Faça login novamente.");
        window.location.href = "/login";
        return;
    }

    await carregarRelatorioCategorias();
    await carregarHistoricoReceitas();
    await carregarHistoricoDespesas();
}

// ============================
// DASHBOARD
// ============================
async function carregarDashboard() {
    const response = await fetch("/dashboard/dados");
    const data = await response.json();

    if (!response.ok) {
        window.location.href = "/login";
        return;
    }

    document.getElementById("totalReceitas").innerText =
        `R$ ${Number(data.total_receitas).toFixed(2)}`;

    document.getElementById("totalDespesas").innerText =
        `R$ ${Number(data.total_despesas).toFixed(2)}`;

    document.getElementById("saldo").innerText =
        `R$ ${Number(data.saldo).toFixed(2)}`;
}

// ============================
// INICIAR DASHBOARD
// ============================
if (document.getElementById("saldo")) {
    carregarDashboard();
    carregarGraficoResumo();
    carregarGraficoCategoria();
}
