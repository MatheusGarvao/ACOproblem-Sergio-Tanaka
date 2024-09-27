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
        document.getElementById('runMultipleACO').disabled = false; // Enable multiple ACO button after instance loads
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

    eventSource.onmessage = function (event) {
        const data = JSON.parse(event.data);
        if (data.iteracao && data.fitness) {
            const iterationsDiv = document.getElementById('iterations');
            iterationsDiv.innerHTML += `Iteração: ${data.iteracao}, Fitness: ${data.fitness}<br>`;
        }

        if (data.final) {
            logMessage(data.mensagem);
            logMessage("Melhor solução encontrada: " + JSON.stringify(data.melhor_rota));
            document.getElementById('viewBestRoute').disabled = false;
            document.getElementById('plotBoxplot').disabled = false; // Enable boxplot button
            document.getElementById('plotFitnessEvolution').disabled = false; // Enable fitness evolution button
            eventSource.close();
        }
    };

    eventSource.onerror = function () {
        logMessage("Erro na execução em tempo real.");
        eventSource.close();
    };
});
// Executar múltiplos ACOs e visualizar logs e boxplot em tempo real
document.getElementById('runMultipleACO').addEventListener('click', function () {
    logMessage("Executando múltiplos ACOs em tempo real...");

    const params = getParameters();
    const queryString = new URLSearchParams(params).toString();
    const eventSource = new EventSource(`/run_multiple_aco?${queryString}`);

    eventSource.onmessage = function (event) {
        const data = JSON.parse(event.data);

        // Log each run's result
        if (data.run && data.iterations) {
            logMessage(`Execução: ${data.run}, Iterações: ${data.iterations}`);
        }

        // Display the boxplot when the process is complete
        if (data.final) {
            logMessage(data.message);

            // Render the boxplot image
            const img = new Image();
            img.src = data.boxplot_url;
            const canvas = document.getElementById('canvas');
            canvas.innerHTML = '';  // Clear previous content
            canvas.appendChild(img);  // Add the new boxplot image

            eventSource.close();  // Close the SSE connection
        }
    };

    eventSource.onerror = function () {
        logMessage("Erro na execução múltipla em tempo real.");
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

// Visualizar Boxplot de Iterações
document.getElementById('plotBoxplot').addEventListener('click', function () {
    fetch('/plot_iterations_boxplot')
        .then(response => response.blob())
        .then(blob => {
            const imgUrl = URL.createObjectURL(blob);
            const img = new Image();
            img.src = imgUrl;
            const canvas = document.getElementById('canvas');
            canvas.innerHTML = ''; // Limpar canvas
            canvas.appendChild(img); // Adicionar imagem do boxplot
        }).catch(error => {
            console.error('Erro ao carregar boxplot:', error);
        });
});

// Visualizar Evolução do Fitness
document.getElementById('plotFitnessEvolution').addEventListener('click', function () {
    fetch('/plot_fitness_evolution')
        .then(response => response.blob())
        .then(blob => {
            const imgUrl = URL.createObjectURL(blob);
            const img = new Image();
            img.src = imgUrl;
            const canvas = document.getElementById('canvas');
            canvas.innerHTML = ''; // Limpar canvas
            canvas.appendChild(img); // Adicionar imagem da evolução do fitness
        }).catch(error => {
            console.error('Erro ao carregar evolução do fitness:', error);
        });
});

function logMessage(message) {
    const logDiv = document.getElementById('log');
    logDiv.innerHTML += message + '<br>';
}
