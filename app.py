from flask import Flask, render_template, jsonify, request, Response, send_file
import matplotlib.pyplot as plt
import io
import time
import json
import base64
from tsp_solver import carregar_problema, algoritmo_colonia_formigas_sse, visualizar_grafo_json, \
    visualizar_melhor_rota_json

app = Flask(__name__)

# Variables for problem and solution data
problem_instance = None
melhor_rota = None
G = None
problem = None

# Global variables for fitness and iteration data
iteration_counts = []
best_fitnesses = []
worst_fitnesses = []
avg_fitnesses = []

@app.route('/')
def index():
    print("[INFO] Index page accessed.")
    return render_template('index.html')


@app.route('/load_instance', methods=['POST'])
def load_instance():
    global G, problem
    instance_name = request.json['instance']
    print(f"[INFO] Attempting to load instance: {instance_name}")

    try:
        G, problem = carregar_problema(instance_name)
        if G is None or problem is None:
            raise ValueError("Erro ao carregar o problema.")
    except Exception as e:
        print(f"[ERROR] Failed to load instance {instance_name}: {str(e)}")
        return jsonify({"error": f"Falha ao carregar a instância {instance_name}: {str(e)}"}), 400

    print(f"[SUCCESS] Instance {instance_name} loaded successfully.")
    return jsonify({"message": f"Instância {instance_name} carregada com sucesso."})


@app.route('/get_graph', methods=['GET'])
def get_graph():
    print("[INFO] Generating graph for the problem instance.")
    if G is not None and problem is not None:
        return visualizar_grafo_json(G, problem)
    else:
        print("[ERROR] Graph not generated because the problem or graph is not loaded.")
        return jsonify({"error": "Grafo não carregado!"}), 400


@app.route('/get_best_route', methods=['GET'])
def get_best_route():
    global melhor_rota
    print(f"[INFO] Fetching the best route: {melhor_rota}")
    if melhor_rota is not None:
        return visualizar_melhor_rota_json(G, problem, melhor_rota)
    else:
        print("[ERROR] No best route found.")
        return jsonify({"error": "Nenhuma melhor rota encontrada!"}), 400


@app.route('/run_aco_sse', methods=['GET'])
def run_aco_sse():
    global melhor_rota, iteration_counts, best_fitnesses, worst_fitnesses, avg_fitnesses

    # Reset fitness and iteration data for a new run
    iteration_counter = 0
    best_fitnesses.clear()
    worst_fitnesses.clear()
    avg_fitnesses.clear()
    iteration_counts.clear()

    alfa = float(request.args.get('alpha', 1))
    beta = float(request.args.get('beta', 2))
    evaporacao = float(request.args.get('evaporation', 0.5))
    Q = float(request.args.get('Q', 10))
    num_formigas = int(request.args.get('numAnts', 100))
    num_iteracoes = int(request.args.get('numIterations', 100))

    def iteracoes():
        global melhor_rota
        nonlocal iteration_counter

        try:
            if G is not None and problem is not None:
                melhor_rota = None

                # Pass fitness lists explicitly
                for iteracao, fitness, rota_atual in algoritmo_colonia_formigas_sse(
                        G, problem, best_fitnesses, worst_fitnesses, avg_fitnesses,
                        alfa=alfa, beta=beta, evaporacao=evaporacao, Q=Q,
                        num_formigas=num_formigas, num_iteracoes=num_iteracoes):
                    melhor_rota = rota_atual
                    iteration_counter += 1
                    yield f"data: {json.dumps({'iteracao': iteracao, 'fitness': fitness})}\n\n"
                    time.sleep(0.1)

                iteration_counts.append(iteration_counter)
                yield f"data: {json.dumps({'final': True, 'mensagem': 'Execução concluída com sucesso', 'melhor_rota': melhor_rota})}\n\n"
            else:
                yield "data: {'error': 'Carregue uma instância primeiro!'}\n\n"
        except Exception as e:
            yield f"data: {{'error': 'Erro no servidor: {str(e)}'}}\n\n"

    return Response(iteracoes(), content_type='text/event-stream')


@app.route('/plot_iterations_boxplot', methods=['GET'])
def plot_iterations_boxplot():
    print("[INFO] Generating boxplot for iteration counts.")
    if not iteration_counts:
        print("[ERROR] No iteration data available for plotting.")
        return jsonify({'error': 'No iteration data available to plot.'}), 400

    # Create the boxplot
    plt.figure()
    plt.boxplot(iteration_counts)
    plt.title("Boxplot of Iterations Until Convergence")
    plt.xlabel("Run")
    plt.ylabel("Number of Iterations")

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    print("[SUCCESS] Boxplot generated and sent.")
    return send_file(img, mimetype='image/png')


@app.route('/plot_fitness_evolution', methods=['GET'])
def plot_fitness_evolution():
    global best_fitnesses, worst_fitnesses, avg_fitnesses
    print("[INFO] Generating fitness evolution plot.")
    if not best_fitnesses:
        print("[ERROR] No fitness data available for plotting.")
        return jsonify({'error': 'No fitness data available to plot.'}), 400

    plt.figure()
    plt.plot(best_fitnesses, label='Best Fitness')
    plt.plot(worst_fitnesses, label='Worst Fitness')
    plt.plot(avg_fitnesses, label='Average Fitness')
    plt.title("Fitness Evolution Over Time")
    plt.xlabel("Iteration")
    plt.ylabel("Fitness")
    plt.legend()

    # Save the plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    print("[SUCCESS] Fitness evolution plot generated and sent.")
    return send_file(img, mimetype='image/png')

@app.route('/run_multiple_aco', methods=['GET'])
def run_multiple_aco():
    global iteration_counts, best_fitnesses, worst_fitnesses, avg_fitnesses

    # Reset iteration counts
    iteration_counts.clear()

    alfa = float(request.args.get('alpha', 1))
    beta = float(request.args.get('beta', 2))
    evaporacao = float(request.args.get('evaporation', 0.5))
    Q = float(request.args.get('Q', 10))
    num_formigas = int(request.args.get('numAnts', 100))
    num_iteracoes = int(request.args.get('numIterations', 100))
    num_runs = int(request.args.get('numRuns', 10))  # Number of runs, default to 10

    def run_multiple_aco_stream():
        for run_num in range(num_runs):
            iteration_counter = 0
            best_fitnesses.clear()
            worst_fitnesses.clear()
            avg_fitnesses.clear()

            for iteracao, fitness, rota_atual in algoritmo_colonia_formigas_sse(
                    G, problem, best_fitnesses, worst_fitnesses, avg_fitnesses,
                    alfa=alfa, beta=beta, evaporacao=evaporacao, Q=Q,
                    num_formigas=num_formigas, num_iteracoes=num_iteracoes):
                iteration_counter += 1

            iteration_counts.append(iteration_counter)
            yield f"data: {json.dumps({'run': run_num + 1, 'iterations': iteration_counter})}\n\n"
            time.sleep(0.1)

        # Send the final boxplot image after all runs
        plt.figure()
        plt.boxplot(iteration_counts)
        plt.title("Boxplot of Iterations Until Convergence")
        plt.xlabel("Run")
        plt.ylabel("Number of Iterations")

        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        img_url = f"data:image/png;base64,{base64.b64encode(img.getvalue()).decode()}"

        yield f"data: {json.dumps({'final': True, 'message': 'Execução múltipla concluída com sucesso', 'boxplot_url': img_url})}\n\n"

    return Response(run_multiple_aco_stream(), content_type='text/event-stream')





if __name__ == '__main__':
    app.run(debug=True)
