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
    global melhor_rota  # Use a variável global para armazenar a melhor rota
    try:
        solucao_inicial = request.args.get('solution')  # Captura a solução inicial da query string
        solucao_inicial = json.loads(solucao_inicial)  # Converte a solução inicial de string para JSON
        print(f"Solução inicial recebida: {solucao_inicial}")  # Log para verificar a solução recebida
    except Exception as e:
        return jsonify({'error': f'Erro ao processar a solução inicial: {str(e)}'}), 400

    def iteracoes():
        global melhor_rota  # Use a variável global para garantir que melhor_rota seja armazenada corretamente
        try:
            if G is not None and problem is not None and solucao_inicial is not None:
                melhor_rota = solucao_inicial  # Inicializa a melhor rota com a solução inicial

                # Chama o algoritmo com solução inicial
                for iteracao, fitness, rota_atual in algoritmo_colonia_formigas_sse(G, problem, solucao_inicial=solucao_inicial):
                    melhor_rota = rota_atual  # Atualiza a melhor rota se encontrar uma melhor
                    print(f"Iteração: {iteracao}, Melhor rota atual: {melhor_rota}")  # Log para cada iteração
                    yield f"data: {json.dumps({'iteracao': iteracao, 'fitness': fitness})}\n\n"
                    time.sleep(0.1)  # Controle do tempo entre iterações

                # Armazena a melhor rota globalmente para ser usada na visualização
                yield f"data: {json.dumps({'final': True, 'mensagem': 'Execução concluída com sucesso', 'melhor_rota': melhor_rota})}\n\n"
            else:
                yield "data: {'error': 'Carregue uma instância e forneça uma solução inicial válida!'}\n\n"
        except Exception as e:
            print(f"Erro no SSE: {str(e)}")
            yield f"data: {{'error': 'Erro no servidor: {str(e)}'}}\n\n"

    return Response(iteracoes(), content_type='text/event-stream')


@app.route('/run_aco_sse', methods=['GET'])
def run_aco_sse():
    global melhor_rota  # Use a variável global para armazenar a melhor rota

    def iteracoes():
        global melhor_rota  # Garante que a melhor rota seja global
        try:
            if G is not None and problem is not None:
                melhor_rota = None  # Inicializa a melhor rota como None

                for iteracao, fitness, rota_atual in algoritmo_colonia_formigas_sse(G, problem):
                    melhor_rota = rota_atual  # Atualiza a melhor rota a cada iteração
                    yield f"data: {json.dumps({'iteracao': iteracao, 'fitness': fitness})}\n\n"
                    time.sleep(0.1)

                # Armazena a melhor rota globalmente ao final da execução
                yield f"data: {json.dumps({'final': True, 'mensagem': 'Execução concluída com sucesso', 'melhor_rota': melhor_rota})}\n\n"
            else:
                yield "data: {'error': 'Carregue uma instância primeiro!'}\n\n"
        except Exception as e:
            print(f"Erro no SSE: {str(e)}")
            yield f"data: {'error': 'Erro no servidor: {str(e)}'}\n\n"

    return Response(iteracoes(), content_type='text/event-stream')



if __name__ == '__main__':
    app.run(debug=True)
