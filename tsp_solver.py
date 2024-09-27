import networkx as nx #Biblioteca para interpretação do dataset, contendo a estrutura de dados para ele (um grafo)
import tsplib95 #Biblioteca para leitura dos datasets
import numpy as np #Biblioteca numpy para realizar a raiz quadrada na função de custo
import random #Biblioteca de randomização
from flask import jsonify #Biblioteca para interface, neste caso especificamente para trabalhar com json.

def carregar_problema(nome_arquivo): #Função para carregar e interpretar o dataset.
    problem = tsplib95.load(nome_arquivo) #Ele armazena dentro de problem o arquivo carregado de acordo com o nome selecionado
    G = nx.Graph() #Gera a estrutura em grafo

    for i, j in problem.get_edges(): #loop entre todas as combinações entre todos os pontos, o objetivo é mapear todas as arestas existentes
        G.add_edge(i, j, weight=problem.get_weight(i, j)) #e aqui adiciona o peso, no momento, é null, mas será direcionado futuramente

    return G, problem #retorna o grafo e o problema.


def calculo_distancia_euclidiana(coord1, coord2): #função para o cálculo da distância euclidiana dita no enunciado do algoritmo
    return np.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)


#Para calcular a distancia total, ele deve percorrer por todos os itens do array rota
#o array rota contém a ordem de acesso das cidades, no final ele pega o ultimo elemento do array e o primeiro
#para completar o loop.
def calcular_distancia_total(rota, coordenadas):
    distancia_total = 0
    n = len(rota)
    for i in range(n - 1):
        cidade_atual = rota[i]
        proxima_cidade = rota[i + 1]
        distancia_total += calculo_distancia_euclidiana(coordenadas[cidade_atual], coordenadas[proxima_cidade])
    distancia_total += calculo_distancia_euclidiana(coordenadas[rota[-1]], coordenadas[rota[0]])
    return distancia_total

#Essa é a função para construir a rota da formiga, ela tem como influência o feromonio deixado pelas outras
#iterações, o alfa qu é o quanto elas serão influenciadas pelo feromonio (valor de 0,1 até 5), e o beta
# que é um valor que influência se a escolha irá para rotas mais curtas ou mais longas.
def construir_rota(cidades, feromonio, coordenadas, alfa, beta):
    rota = []
    cidades_nao_visitadas = set(cidades)
    cidade_atual = random.choice(list(cidades_nao_visitadas)) #inicializa a formiga em algum local aleatório.
    rota.append(cidade_atual) #primeira cidade.
    cidades_nao_visitadas.remove(cidade_atual) #remoção da cidade inicial, já que ela já foi visitada.

    #enquanto existir cidades que não foram visitadas, ele irá realizar o loop.
    while cidades_nao_visitadas:
        #Ele seleciona a próxima cidade, passando como parâmetros qual a cidade que a formiga está, a lista das
        #cidades que não foram visitadas, o feromonio de todas as arestas, as coordenadas dos nós, alfa e beta.
        proxima_cidade = escolher_proxima_cidade(cidade_atual, cidades_nao_visitadas, feromonio, coordenadas, alfa, beta)
        #adiciona no array de rota
        rota.append(proxima_cidade)
        #remove da lista de não visitadas
        cidades_nao_visitadas.remove(proxima_cidade)
        #atualiza a cidade atual, já que a formiga acabou de andar.
        cidade_atual = proxima_cidade
    return rota


#Aqui é a lógica para escolha das cidades, recebendo qual a cidade que a formiga tá, quais as opções
#de caminho que ela pode ir, quais são os feromonios de todas as arestas, as coordenadas existentes
#alfa e beta.

#este algoritmo utiliza de uma função heurística, uma medida de qualidade baseada na distância entre
#as cidades, é o inverso da distância euclidiana, cidades mais próximas terão uma heurística maior
#cidades mais distantes terão uma heurística menor.

#a ideia é que cidades mais longes recebam um valor menor, enquanto cidades próximas recebam um valor maior
#priorizando as cidades mais próximas, porém mantendo o valor de influência.
def escolher_proxima_cidade(cidade_atual, cidades_nao_visitadas, feromonio, coordenadas, alfa, beta):
    probabilidades = [] #array que armazenará as probabilidades de acesso, ele é relativo a posição exata em cidades não visitadas.
    somatorio = 0
    for cidade in cidades_nao_visitadas:

        #primeiramente antes de calcular o quanto eles vão influênciar, tem que fazer os calculos deles.
        #então primeiro busca o feromonio, min e max servem para manter as chaves independente da ordem, ou seja
        # 2, 5 é o mesmo que 5, 2, evitando valores de feromonio diferentes já que o caminho dos grafos não importa
        feromonio_atual = feromonio.get((min(cidade_atual, cidade), max(cidade_atual, cidade)), 1)
        #agora vem o valor entre 0 e 1, cidades com distância menor tem um valor mais próximo de 1, enquanto
        #cidades com distância maior, tem valores mais próximos de 0
        heuristica = 1.0 / calculo_distancia_euclidiana(coordenadas[cidade_atual], coordenadas[cidade])
        #e aqui é o gatilho, a formula trabalhada aqui é o valor do feromonio^2 * heurística^2
        # se o valor de beta for maior ou igual a 1, a influência entre as cidades será maior!
        # já se for menor, ainda terá uma influência, mas é bem menos relevante entre as outras.
        valor = (feromonio_atual ** alfa) * (heuristica ** beta)
        # O somatório irá servir como uma forma de normalização, já que a soma das probabilidades de todos os caminhos
        # tem que dar no máximo 1, ou seja, 100%.
        somatorio += valor
        probabilidades.append((cidade, valor))
    #se o somatório for 0, ou seja, beta muito grande e alfa muito pequeno, ele considera 1.0 como valor.
    #e divide pela quantidade de cidades, igualando a probabilidade para cada cidade.

    # essa parte é equivalente a criação de um array normalizado das proabilidades, para cada cidade não visitada,
    # ele pega o valor que foi retirado e divide pelo somatório de todos os valores.

    #para exemplificar, vamos supor que o somatório de probabilidade de escolha entre 2 cidades deu 11.
    # uma cidade o valor é 5 a outra é 6, a probabilidade de escolher após realizar esse calculo, a cidade
    # com o valor 5 é de 0,45, já a com valor 6, a probabilidade é de 0,54, ou seja, 45% e 54% respectivamente.
    # por causa dessa divisão, os valores foram normalizados para probabilidades.
    if somatorio == 0:
        probabilidades = [(cidade, 1.0 / len(cidades_nao_visitadas)) for cidade in cidades_nao_visitadas]
    else:
        probabilidades = [(cidade, valor / somatorio) for cidade, valor in probabilidades]

    #e aqui é a linha onde faz a escolha propriamente dita, levando em consideração o peso em weights.
    proxima_cidade = random.choices([cidade for cidade, _ in probabilidades], weights=[p for _, p in probabilidades])[0]
    return proxima_cidade

#função responsável por atualizar os feromonios no final, de acordo com a taxa de evaporação e o valor Q.
#a evaporação é responsável por retirar os feromonios, o valor de Q é relativo a quantidade de feromonio que vai ser
#depositado. é realmente para atualizar esses feromonios mesmo.

#O calculo para cada aresta, ele multipica o valor atual do feromonio por 1-a taxa de evaporação.
#a taxa de evaporação é entre 0 e 1, quanto mais próximo de 1, mais rápido o feromonio desaparece
#e quanto mais próximo de 0, ele demora mais para sumir. (por que ele está diminuindo 1 pela taxa e guardando
#a multiplicação pelo anterior.

#O zip ele junta todas as rotas com todas as distâncias, criando um par de chaves associado, em rota ele
#guarda a rota, em distância ele guarda a distância relativo a rota que está trabalhando.
#para cada rota, ele joga um feromonio em cada aresta, o calculo é Q dividido pela distância.
#Q é um valor de 1 a 1000, quanto mais próximo de 1 a taxa de feromonio depositado será menor
#já quanto mais próximo de 1000, ele deposita muito mais feromonio.

#esses parâmetros normalmente devem ser ajustados para cada problema.
def atualizar_feromonios(feromonio, todas_rotas, todas_distancias, evaporacao, Q):
    for edge in feromonio:
        feromonio[edge] *= (1 - evaporacao)
    for rota, distancia in zip(todas_rotas, todas_distancias):
        for i in range(len(rota) - 1):
            edge = (min(rota[i], rota[i + 1]), max(rota[i + 1], rota[i]))
            feromonio[edge] += Q / distancia
    return feromonio

#função usada para gerar o grafo, realmente essa eu fiz com chatgpt puro.
def visualizar_grafo_json(G, problem):
    pos = {i: (problem.node_coords[i][0], problem.node_coords[i][1]) for i in G.nodes}
    edges = list(G.edges)

    node_x = [pos[i][0] for i in G.nodes]
    node_y = [pos[i][1] for i in G.nodes]

    node_trace = {
        'x': node_x,
        'y': node_y,
        'mode': 'markers+text',
        'text': [str(i) for i in G.nodes],
        'textposition': 'top center',
        'marker': {
            'size': 10,
            'color': 'blue',
            'line': {'width': 2}
        }
    }

    edge_x = []
    edge_y = []
    for edge in edges:
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = {
        'x': edge_x,
        'y': edge_y,
        'line': {'width': 1, 'color': '#888'},
        'mode': 'lines'
    }

    layout = {
        'title': 'Visualização do Grafo TSP',
        'showlegend': False,
        'hovermode': 'closest',
        'margin': {'b': 0, 'l': 0, 'r': 0, 't': 40},
        'xaxis': {'showgrid': False, 'zeroline': False},
        'yaxis': {'showgrid': False, 'zeroline': False},
        'height': 600
    }

    return jsonify({'node_trace': node_trace, 'edge_trace': edge_trace, 'layout': layout})

#mesma coisa, chatgpt puro.
def visualizar_melhor_rota_json(G, problem, melhor_rota):
    pos = {i: (problem.node_coords[i][0], problem.node_coords[i][1]) for i in G.nodes}

    node_x = [pos[i][0] for i in G.nodes]
    node_y = [pos[i][1] for i in G.nodes]

    node_trace = {
        'x': node_x,
        'y': node_y,
        'mode': 'markers+text',
        'text': [str(i) for i in G.nodes],
        'textposition': 'top center',
        'marker': {
            'size': 10,
            'color': 'blue',
            'line': {'width': 2}
        }
    }

    edge_x = []
    edge_y = []
    for i in range(len(melhor_rota) - 1):
        x0, y0 = pos[melhor_rota[i]]
        x1, y1 = pos[melhor_rota[i + 1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    x0, y0 = pos[melhor_rota[-1]]
    x1, y1 = pos[melhor_rota[0]]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])

    edge_trace = {
        'x': edge_x,
        'y': edge_y,
        'line': {'width': 2, 'color': 'red'},
        'mode': 'lines'
    }

    layout = {
        'title': 'Melhor Rota Encontrada',
        'showlegend': False,
        'hovermode': 'closest',
        'margin': {'b': 0, 'l': 0, 'r': 0, 't': 40},
        'xaxis': {'showgrid': False, 'zeroline': False},
        'yaxis': {'showgrid': False, 'zeroline': False},
        'height': 600
    }

    return jsonify({'node_trace': node_trace, 'edge_trace': edge_trace, 'layout': layout})

#Esse aqui é a primeira função do algoritmo em si, ela recebe o grafo, o problema, o melhor fitness (se tiver), o pior fitness (se tiver)
#e a média, isso somente para fins de caso haja solução inicial instanciada.
#Ela também recebe o alfa, beta, evaporação, Q, a quantidade de formigas, o número máximo de iteracoes e
#o limite de iterações sem melhora (caso queria passar).

def algoritmo_colonia_formigas_sse(G, problem, best_fitnesses, worst_fitnesses, avg_fitnesses,
                                   solucao_inicial=None, alfa=1, beta=2, evaporacao=0.5, Q=10,
                                   num_formigas=100, num_iteracoes=100, max_stagnation=1000):
    coordenadas = problem.node_coords #Guardando as coordenadas dos nós.
    feromonio = {edge: 1.0 for edge in G.edges} #Criação do feromonio inicial sendo de valor 1 para todas as arestas
    cidades = list(G.nodes) #Guardando as cidades
    melhor_rota = None #Variável para guardar a melhor rota encontrada
    melhor_distancia = float('inf') #instanciando como infinito positivo
    stagnation_counter = 0 #contador para manter o track (mapeamento) de quantas iterações foram realizadas sem melhoras
    previous_best_distance = float('inf')  #Melhor distância anterior, para comparar se houve melhora ou não.

    #limpar os antigos melhores resultados.
    best_fitnesses.clear()
    worst_fitnesses.clear()
    avg_fitnesses.clear()

    #se houver uma solução inicial, ele tem que guarda-la para poder trabalhar em cima dela comoo ponto de partida.
    if solucao_inicial:
        melhor_rota = solucao_inicial
        melhor_distancia = calcular_distancia_total(melhor_rota, coordenadas)

    #para cada iteração, ele cria um array vazio de todas as rotas e todas as distâncias
    #além disso, ele cria as formigas que vão explorar, de acordo com a quantidade de formigas que trabalharão.
    #O armazenamento de todas as rotas serve para poder depositar um feromonio ao final dela, feromonio este
    #que é transferido para a próxima iteração de formigas
    for iteracao in range(num_iteracoes):
        todas_rotas = []
        todas_distancias = []

        #cada formiga cria uma rota, e a distância dessa rota, adiciona para a variável de todas as rotas
        #e todas as distâncias também.
        #Se a distancia encontrada pela formiga for melhor, ou seja, a distância seja menor que a melhor distância, então atualiza-se
        #a melhor encontrada.
        for _ in range(num_formigas):
            rota = construir_rota(cidades, feromonio, coordenadas, alfa, beta)
            distancia_rota = calcular_distancia_total(rota, coordenadas)
            todas_rotas.append(rota)
            todas_distancias.append(distancia_rota)

            if distancia_rota < melhor_distancia:
                melhor_rota = rota
                melhor_distancia = distancia_rota

        #Para essa iteração, ou seja, para as 100 formigas, ele guarda o melhor fitness, o pior e a média dos fitness.
        #essa para fins de gráficos.
        best_fitness = min(todas_distancias)
        worst_fitness = max(todas_distancias)
        avg_fitness = sum(todas_distancias) / len(todas_distancias)

        #já essa é global, para construir em torno de todas as iterações.
        best_fitnesses.append(best_fitness)
        worst_fitnesses.append(worst_fitness)
        avg_fitnesses.append(avg_fitness)

        # essa aqui está verificando se está estagnado, para aumentar o contador.
        if melhor_distancia >= previous_best_distance:
            stagnation_counter += 1
        else:
            stagnation_counter = 0

        previous_best_distance = melhor_distancia
        #aqui é para ver se o algoritmo já entrou em convergência.
        if stagnation_counter >= max_stagnation:
            print(f"[INFO] Algorithm converged after {iteracao + 1} iterations.")
            break

        # Essa função no final é extremamente importante, serve para atualizar os feromônios de acordo
        # com os parametros e com as rotas encontradas pelas formigas.
        feromonio = atualizar_feromonios(feromonio, todas_rotas, todas_distancias, evaporacao, Q)

        #aqui ele retorna os valores para construção dos gráficos, mas continua a iteração, sem parar ela.
        yield iteracao + 1, melhor_distancia, melhor_rota



