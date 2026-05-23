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


// ============================ 
// PLUGIN PARA GRAFICOS (Chart.js) 
// ============================ 
// Esse plugin desenha os valores sobre os gráficos automaticamente 
const pluginValoresGraficos = { 
    id: "pluginValoresGraficos", 
    afterDatasetsDraw(chart) { 
        const { ctx } = chart; 
 
        ctx.save(); 
        ctx.font = "bold 12px Arial"; 
        ctx.fillStyle = "#111"; 
        ctx.textAlign = "center"; 
        ctx.textBaseline = "middle"; 
 
        chart.data.datasets.forEach((dataset, datasetIndex) => { 
            const meta = chart.getDatasetMeta(datasetIndex); 
 
            meta.data.forEach((element, index) => { 
                const valor = Number(dataset.data[index]); 
                if (valor <= 0) return; 
 
                const texto = `R$ ${valor.toFixed(2)}`; 
 
                let position; 
                if (chart.config.type === "doughnut") { 
                    position = element.tooltipPosition(); 
                } else { 
                    position = element.tooltipPosition(); 
                    position.y -= 12; 
                } 

 
                ctx.fillText(texto, position.x, position.y); 
            }); 
        }); 
 
        ctx.restore(); 
    } 
}; 

 
// ============================ 
// FUNÇÃO: CARREGAR GRÁFICO DE CATEGORIAS DE DESPESAS 
// ============================ 
async function carregarGraficoCategoria() { 
    const canvas = document.getElementById("graficoCategoria"); 
    if (!canvas) return; 
 
    const response = await fetch("/dashboard/despesas-categorias/"); 
    const dados = await response.json(); 
 
    if (!response.ok || !dados.length) return; 
 
    const labels = dados.map(item => item.categoria || "Sem categoria"); 
    const valores = dados.map(item => Number(item.total)); 
 
    new Chart(canvas, { 
        type: "bar", 
        data: { 
            labels: labels, 
            datasets: [{ 
                label: "Valor gasto", 
                data: valores, 
                backgroundColor: [ 
                    "#1e88e5", "#43a047", "#fb8c00", "#8e24aa", 
                    "#e53935", "#00897b", "#3949ab", "#6d4c41" 
                ], 
                borderRadius: 10, 
                borderSkipped: false 
            }] 
        }, 
        plugins: [pluginValoresGraficos], 
        options: { 
            responsive: true, 
            maintainAspectRatio: false, 
            plugins: { 
                legend: { display: false }, 
                tooltip: { 
                    callbacks: { 
                        label: function(context) { 
                            return ` R$ ${Number(context.raw).toFixed(2)}`; 
                        } 
                    } 
                } 
            }, 
            scales: { 
                x: { grid: { display: false } }, 
                y: { 
                    beginAtZero: true, 
                    ticks: { 
                        callback: function(value) { return "R$ " + value; } 
                    } 
                } 
            }, 
            animation: { duration: 1000, easing: "easeOutQuart" } 
        } 
    }); 
}


// ============================ 
// FUNÇÃO: CARREGAR GRÁFICO RESUMO FINANCEIRO 
// ============================ 
async function carregarGraficoResumo() { 
    const canvas = document.getElementById("graficoResumo"); 
    if (!canvas) return; 
 
    const response = await fetch("/dashboard/dados"); 
    const dados = await response.json(); 
    if (!response.ok) return; 
 
    const receitas = Number(dados.total_receitas); 
    const despesas = Number(dados.total_despesas); 
 
    const valores = [receitas, despesas]; 
    const total = valores.reduce((acc, item) => acc + item, 0); 
 
    new Chart(canvas, { 
        type: "doughnut", 
        data: { 
            labels: ["Receitas", "Despesas"], 
            datasets: [{ 
                data: valores, 
                backgroundColor: ["#43a047", "#e53935"], 
                borderWidth: 2, 
                borderColor: "#ffffff", 
                hoverOffset: 12 
            }] 
        }, 
        plugins: [pluginValoresGraficos], 
        options: { 
            responsive: true, 
            maintainAspectRatio: false, 
            cutout: "55%", 
            plugins: { 
                legend: { 
                    position: "bottom", 
                    labels: { padding: 18, font: { size: 13 } } 
                }, 
                tooltip: { 
                    callbacks: { 
                        label: function(context) { 
                            const valor = Number(context.raw); 
                            const porcentagem = total > 0 
                                ? ((valor / total) * 100).toFixed(1) 
                                : "0.0"; 
                            return ` ${context.label}: R$ ${valor.toFixed(2)} (${porcentagem}%)`; 
                        } 
                    } 
                } 
            }, 
            animation: { animateRotate: true, animateScale: true } 
        } 
    }); 
} 

 
// ============================ 
// FUNÇÃO: CARREGAR RELATÓRIO DE DESPESAS POR CATEGORIA 
// ============================ 
async function carregarRelatorioCategorias() { 
    const container = document.getElementById("relatorioCategorias"); 
    if (!container) return; 
 
    const response = await fetch("/relatorios/despesas-categorias"); 
    const dados = await response.json(); 
 
    container.innerHTML = ""; 
 
    if (dados.length === 0) { 
        container.innerHTML = "<p>Nenhuma despesa cadastrada ainda.</p>"; 
        return; 
    } 
 
    const maiorValor = Math.max(...dados.map(item => item.total)); 
 
    dados.forEach(item => { 
        const porcentagem = (item.total / maiorValor) * 100; 
 
        const div = document.createElement("div"); 
        div.className = "item-lista"; 
 
        div.innerHTML = ` 
            <div style="width:100%"> 
                <strong>${item.categoria || "Sem categoria"}</strong> 
                <p>R$ ${item.total.toFixed(2)}</p> 
                <div class="barra"> 
                    <div class="barra-preenchida" style="width:${porcentagem}%"></div> 
                </div> 
            </div> 
        `; 
 
        container.appendChild(div); 
    }); 
}


// ============================ 
// FUNÇÕES: HISTÓRICO DE RECEITAS E DESPESAS 
// ============================ 
// Essas funções carregam listas de receitas e despesas e populam o HTML 
async function carregarHistoricoReceitas() { 
    const container = document.getElementById("listaReceitas"); 
    if (!container) return; 
 
    const response = await fetch(`${API_URL}/receitas/listar`); 
    const receitas = await response.json(); 
 
    container.innerHTML = ""; 
 
    if (receitas.length === 0) { 
        container.innerHTML = "<p>Nenhuma receita cadastrada ainda.</p>"; 
        return; 
    } 
 
    receitas.forEach(item => { 
        const div = document.createElement("div"); 
        div.className = "item-lista"; 
 
        div.innerHTML = ` 
            <div> 
                <strong>${item.descricao}</strong> 
                <p>${item.categoria || "Sem categoria"} - ${item.data_receita}</p> 
            </div> 
            <span class="valor-receita">R$ ${item.valor.toFixed(2)}</span> 
        `; 
        container.appendChild(div); 
    }); 
} 

 
async function carregarHistoricoDespesas() { 
    const container = document.getElementById("listaDespesas"); 
    if (!container) return; 
 
    const response = await fetch(`${API_URL}/despesas/listar`); 
    const despesas = await response.json(); 
 
    container.innerHTML = ""; 
 
    if (despesas.length === 0) { 
        container.innerHTML = "<p>Nenhuma despesa cadastrada ainda.</p>"; 
        return; 
    } 
 
    despesas.forEach(item => { 
        const div = document.createElement("div"); 
        div.className = "item-lista"; 
 
        div.innerHTML = ` 
            <div> 
                <strong>${item.descricao}</strong> 
                <p>${item.categoria || "Sem categoria"} - ${item.data_despesa}</p> 
            </div> 
            <span class="valor-despesa">R$ ${item.valor.toFixed(2)}</span> 
        `; 
        container.appendChild(div); 
    }); 
} 

 
// Executa relatórios apenas na página de relatórios 
if (document.getElementById("relatorioCategorias")) { 
    carregarRelatorios(); 
} 

 
// ============================ 
// FUNÇÃO: CARREGAR FEEDBACKS 
// ============================ 
async function carregarFeedbacks() { 
    const container = document.getElementById("listaFeedbacks"); 
    if (!container) return; 
 
    const response = await fetch("/feedbacks"); 
    const feedbacks = await response.json(); 
 
    container.innerHTML = ""; 
 
    if (!response.ok || !feedbacks.length) { 
        container.innerHTML = ` 
            <div class="feedback-vazio"> 
                Nenhum feedback enviado ainda. 
            </div> 
        `; 
        return; 
    } 
 
    feedbacks.forEach(item => { 
        let estrelas = ""; 
        for (let i = 0; i < Number(item.nota); i++) estrelas += "   "; 
 
        const div = document.createElement("div"); 
        div.className = "feedback-card"; 
 
        div.innerHTML = ` 
            <div class="feedback-topo"> 
                <div class="feedback-nota">${estrelas}</div> 
                <div class="feedback-data">${item.criado_em}</div> 
            </div> 
            <div class="feedback-comentario"> 
                ${item.comentario || "Sem comentário."} 
            </div> 
        `; 
 
        container.appendChild(div); 
    }); 
} 
 
if (document.getElementById("listaFeedbacks")) { 
    carregarFeedbacks(); 
} 


// ============================
// FUNÇÔES DA PÁGINA IA
// ============================
carregarSugestoesIA();

const btnGerarAnalise = document.getElementById("btnGerarAnalise");
if (btnGerarAnalise) {
    btnGerarAnalise.addEventListener("click", gerarAnaliseFinanceira);
}

async function gerarAnaliseFinanceira() {
    const resultado = document.getElementById("resultadoIA");
    const botao = document.getElementById("btnGerarAnalise");

    resultado.style.display = "block";
    resultado.innerHTML = "<p>Gerando análise financeira...</p>";

    botao.disabled = true;
    botao.innerText = "Aguarde...";

    try {
        const response = await fetch("/ia/analise-financeira");
        const data = await response.json();

        if (response.ok) {
            resultado.innerHTML = `
                <strong>Nova análise da IA:</strong>
                <p>${data.analise.replace(/\n/g, "<br>")}</p>
            `;

            carregarSugestoesIA();
        } else {
            resultado.innerHTML = `<p>${data.erro}</p>`;
        }

    } catch (error) {
        resultado.innerHTML = "<p>Erro ao gerar análise. Tente novamente.</p>";
    }

    botao.disabled = false;
    botao.innerText = "Gerar análise com IA";
}

async function carregarSugestoesIA() {
    const container = document.getElementById("listaSugestoesIA");

    if (!container) return;

    container.innerHTML = "<p>Carregando análises...</p>";

    try {
        const response = await fetch("/ia/sugestoes");
        const sugestoes = await response.json();

        container.innerHTML = "";

        if (!response.ok) {
            container.innerHTML = `<p>${sugestoes.erro}</p>`;
            return;
        }

        if (sugestoes.length === 0) {
            container.innerHTML = "<p>Nenhuma análise gerada ainda.</p>";
            return;
        }

        sugestoes.forEach(item => {
            const div = document.createElement("div");
            div.className = "feedback-card";

            div.innerHTML = `
                <div class="feedback-topo">
                    <strong>Análise financeira</strong>
                    <span class="feedback-data">${item.criado_em}</span>
                </div>

                <div class="feedback-comentario">
                    ${item.resposta.replace(/\n/g, "<br>")}
                </div>
            `;

            container.appendChild(div);
        });

    } catch (error) {
        container.innerHTML = "<p>Erro ao carregar análises anteriores.</p>";
    }
}
