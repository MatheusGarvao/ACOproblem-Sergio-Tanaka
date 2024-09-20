// Carregar instância TSP
document.getElementById('loadInstance').addEventListener('click', function () {
    const instance = document.getElementById('problemInstance').value;
    fetch('/load_instance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ instance: instance })
    }).then(response => response.json()).then(data => {
        logMessage(data.message);
        document.getElementById('runACO').disabled = false;
        document.getElementById('runACOWithSolution').disabled = false;
        document.getElementById('viewGraph').disabled = false;
    });
});

function getParameters() {
    return {
        alpha: parseFloat(document.getElementById('alpha').value),
        beta: parseFloat(document.getElementById('beta').value),
        evaporation: parseFloat(document.getElementById('evaporation').value),
        Q: parseFloat(document.getElementById('Q').value),
        numAnts: parseInt(document.getElementById('numAnts').value),
        numIterations: parseInt(document.getElementById('numIterations').value)
    };
}

// Executar ACO
document.getElementById('runACO').addEventListener('click', function () {
     const params = getParameters();

    logMessage("Rodando algoritmo em tempo real...");

    const queryString = new URLSearchParams(params).toString();

    const eventSource = new EventSource(`/run_aco_sse?${queryString}`);

    // Receber as mensagens do servidor (iterações e fitness)
eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);

    if (data.iteracao && data.fitness) {
        const iterationsDiv = document.getElementById('iterations');
        iterationsDiv.innerHTML += `Iteração: ${data.iteracao}, Fitness: ${data.fitness}<br>`;
    }

    if (data.final) {
        logMessage(data.mensagem);  // Exibe a mensagem de conclusão
        logMessage("Melhor solução encontrada: " + JSON.stringify(data.melhor_rota));  // Exibe a melhor rota

        // Habilita o botão para visualizar a melhor rota
        document.getElementById('viewBestRoute').disabled = false;

        eventSource.close();  // Fechar SSE quando o processo terminar
    }
};





    eventSource.onerror = function() {
        logMessage("Erro na execução em tempo real.");
        eventSource.close();
    };
});



document.getElementById('runACOWithSolution').addEventListener('click', function () {
    const params = getParameters();
    const solution = document.getElementById('initialSolution').value;

    if (!solution) {
        logMessage("Por favor, insira uma solução inicial.");
        return;
    }

    let parsedSolution;
    try {
        parsedSolution = JSON.parse(solution);
    } catch (error) {
        logMessage("Formato de solução inicial inválido. Use um array JSON.");
        return;
    }

    logMessage("Rodando algoritmo em tempo real com solução inicial...");

    params.solution = JSON.stringify(parsedSolution);
    const queryString = new URLSearchParams(params).toString();

    const eventSource = new EventSource(`/run_aco_with_solution_sse?${queryString}`);

    // Receber as mensagens do servidor (iterações e fitness)
eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);

    if (data.iteracao && data.fitness) {
        const iterationsDiv = document.getElementById('iterations');
        iterationsDiv.innerHTML += `Iteração: ${data.iteracao}, Fitness: ${data.fitness}<br>`;
    }

    if (data.final) {
        logMessage(data.mensagem);  // Exibe a mensagem de conclusão
        logMessage("Melhor solução encontrada: " + JSON.stringify(data.melhor_rota));  // Exibe a melhor rota

        // Habilita o botão para visualizar a melhor rota
        document.getElementById('viewBestRoute').disabled = false;

        eventSource.close();  // Fechar SSE quando o processo terminar
    }
};


    eventSource.onerror = function() {
        logMessage("Erro na execução em tempo real com solução inicial.");
        eventSource.close();
    };
});






// Visualizar Grafo
document.getElementById('viewGraph').addEventListener('click', function () {
    fetch('/get_graph')
    .then(response => response.json())
    .then(data => {
        const canvas = document.getElementById('canvas');
        Plotly.newPlot(canvas, [data.edge_trace, data.node_trace], data.layout);
    }).catch(error => {
        console.error('Error loading graph:', error);
    });
});


// Visualizar Melhor Rota
document.getElementById('viewBestRoute').addEventListener('click', function () {
    fetch('/get_best_route')
    .then(response => response.json())
    .then(data => {
        const canvas = document.getElementById('canvas');
        Plotly.newPlot(canvas, [data.edge_trace, data.node_trace], data.layout);
    }).catch(error => {
        console.error('Error loading best route:', error);
    });
});


function logMessage(message) {
    const logDiv = document.getElementById('log');
    logDiv.innerHTML += message + '<br>';
}
