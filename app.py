from flask import Flask, render_template, jsonify, request, Response
import time
import json
from tsp_solver import carregar_problema, algoritmo_colonia_formigas_sse, visualizar_grafo_json, \
    visualizar_melhor_rota_json

app = Flask(__name__)

# Variáveis globais para armazenar o problema e a melhor rota
problem_instance = None
melhor_rota = None
G = None
problem = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/load_instance', methods=['POST'])
def load_instance():
    global G, problem
    instance_name = request.json['instance']

    try:
        G, problem = carregar_problema(instance_name)
        if G is None or problem is None:
            raise ValueError("Erro ao carregar o problema.")
    except Exception as e:
        return jsonify({"error": f"Falha ao carregar a instância {instance_name}: {str(e)}"}), 400

    return jsonify({"message": f"Instância {instance_name} carregada com sucesso."})


@app.route('/get_graph', methods=['GET'])
def get_graph():
    if G is not None and problem is not None:
        # Retorna o HTML do gráfico usando Plotly
        return visualizar_grafo_json(G, problem)  # Retorna o HTML do gráfico
    else:
        return jsonify({"error": "Grafo não carregado!"}), 400


@app.route('/get_best_route', methods=['GET'])
def get_best_route():
    global melhor_rota
    print(f"Melhor rota: {melhor_rota}")  # Verificação para garantir que a melhor rota está sendo passada
    if melhor_rota is not None:
        return visualizar_melhor_rota_json(G, problem, melhor_rota)
    else:
        return jsonify({"error": "Nenhuma melhor rota encontrada!"}), 400


@app.route('/run_aco_with_solution_sse', methods=['GET'])
def run_aco_with_solution_sse():
    global melhor_rota
    try:
        solucao_inicial = json.loads(request.args.get('solution'))
    except Exception as e:
        return jsonify({'error': f'Erro ao processar a solução inicial: {str(e)}'}), 400

    # Captura os parâmetros da query string
    alfa = float(request.args.get('alpha', 1))
    beta = float(request.args.get('beta', 2))
    evaporacao = float(request.args.get('evaporation', 0.5))
    Q = float(request.args.get('Q', 10))
    num_formigas = int(request.args.get('numAnts', 100))
    num_iteracoes = int(request.args.get('numIterations', 100))

    def iteracoes():
        global melhor_rota
        try:
            if G is not None and problem is not None and solucao_inicial is not None:
                melhor_rota = solucao_inicial

                # Passa os parâmetros e a solução inicial ao algoritmo ACO
                for iteracao, fitness, rota_atual in algoritmo_colonia_formigas_sse(
                        G, problem, solucao_inicial=solucao_inicial, alfa=alfa, beta=beta, evaporacao=evaporacao, Q=Q,
                        num_formigas=num_formigas, num_iteracoes=num_iteracoes):
                    melhor_rota = rota_atual
                    yield f"data: {json.dumps({'iteracao': iteracao, 'fitness': fitness})}\n\n"
                    time.sleep(0.1)

                yield f"data: {json.dumps({'final': True, 'mensagem': 'Execução concluída com sucesso', 'melhor_rota': melhor_rota})}\n\n"
            else:
                yield "data: {'error': 'Carregue uma instância e forneça uma solução inicial válida!'}\n\n"
        except Exception as e:
            yield f"data: {{'error': 'Erro no servidor: {str(e)}'}}\n\n"

    return Response(iteracoes(), content_type='text/event-stream')


@app.route('/run_aco_sse', methods=['GET'])
def run_aco_sse():
    global melhor_rota

    # Captura os parâmetros da query string
    alfa = float(request.args.get('alpha', 1))
    beta = float(request.args.get('beta', 2))
    evaporacao = float(request.args.get('evaporation', 0.5))
    Q = float(request.args.get('Q', 10))
    num_formigas = int(request.args.get('numAnts', 100))
    num_iteracoes = int(request.args.get('numIterations', 100))

    def iteracoes():
        global melhor_rota
        try:
            if G is not None and problem is not None:
                melhor_rota = None

                # Passa os parâmetros ao algoritmo ACO
                for iteracao, fitness, rota_atual in algoritmo_colonia_formigas_sse(
                        G, problem, alfa=alfa, beta=beta, evaporacao=evaporacao, Q=Q,
                        num_formigas=num_formigas, num_iteracoes=num_iteracoes):
                    melhor_rota = rota_atual
                    yield f"data: {json.dumps({'iteracao': iteracao, 'fitness': fitness})}\n\n"
                    time.sleep(0.1)

                yield f"data: {json.dumps({'final': True, 'mensagem': 'Execução concluída com sucesso', 'melhor_rota': melhor_rota})}\n\n"
            else:
                yield "data: {'error': 'Carregue uma instância primeiro!'}\n\n"
        except Exception as e:
            yield f"data: {{'error': 'Erro no servidor: {str(e)}'}}\n\n"

    return Response(iteracoes(), content_type='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True)
