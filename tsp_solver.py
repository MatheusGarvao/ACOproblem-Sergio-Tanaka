import networkx as nx
import tsplib95
import numpy as np
import random
import plotly.graph_objs as go
import plotly.io as pio
from flask import jsonify


def carregar_problema(nome_arquivo):
    problem = tsplib95.load(nome_arquivo)
    G = nx.Graph()

    for i, j in problem.get_edges():
        G.add_edge(i, j, weight=problem.get_weight(i, j))

    return G, problem


def calculo_distancia_euclidiana(coord1, coord2):
    return np.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)


def calcular_distancia_total(rota, coordenadas):
    distancia_total = 0
    n = len(rota)
    for i in range(n - 1):
        cidade_atual = rota[i]
        proxima_cidade = rota[i + 1]
        distancia_total += calculo_distancia_euclidiana(coordenadas[cidade_atual], coordenadas[proxima_cidade])
    distancia_total += calculo_distancia_euclidiana(coordenadas[rota[-1]], coordenadas[rota[0]])
    return distancia_total


def construir_rota(cidades, feromonio, coordenadas, alfa, beta):
    rota = []
    cidades_nao_visitadas = set(cidades)
    cidade_atual = random.choice(list(cidades_nao_visitadas))
    rota.append(cidade_atual)
    cidades_nao_visitadas.remove(cidade_atual)
    while cidades_nao_visitadas:
        proxima_cidade = escolher_proxima_cidade(cidade_atual, cidades_nao_visitadas, feromonio, coordenadas, alfa, beta)
        rota.append(proxima_cidade)
        cidades_nao_visitadas.remove(proxima_cidade)
        cidade_atual = proxima_cidade
    return rota


def escolher_proxima_cidade(cidade_atual, cidades_nao_visitadas, feromonio, coordenadas, alfa, beta):
    probabilidades = []
    somatorio = 0
    for cidade in cidades_nao_visitadas:
        feromonio_atual = feromonio.get((min(cidade_atual, cidade), max(cidade_atual, cidade)), 1)
        heuristica = 1.0 / calculo_distancia_euclidiana(coordenadas[cidade_atual], coordenadas[cidade])
        valor = (feromonio_atual ** alfa) * (heuristica ** beta)
        somatorio += valor
        probabilidades.append((cidade, valor))

    # Verificar se o somatório é zero
    if somatorio == 0:
        # Probabilidade uniforme entre as cidades restantes
        probabilidades = [(cidade, 1.0 / len(cidades_nao_visitadas)) for cidade in cidades_nao_visitadas]
    else:
        probabilidades = [(cidade, valor / somatorio) for cidade, valor in probabilidades]

    # Escolher a próxima cidade
    proxima_cidade = random.choices([cidade for cidade, _ in probabilidades], weights=[p for _, p in probabilidades])[0]
    return proxima_cidade


def atualizar_feromonios(feromonio, todas_rotas, todas_distancias, evaporacao, Q):
    for edge in feromonio:
        feromonio[edge] *= (1 - evaporacao)
    for rota, distancia in zip(todas_rotas, todas_distancias):
        for i in range(len(rota) - 1):
            edge = (min(rota[i], rota[i + 1]), max(rota[i + 1], rota[i]))
            feromonio[edge] += Q / distancia
    return feromonio


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


def visualizar_melhor_rota_json(G, problem, melhor_rota):
    pos = {i: (problem.node_coords[i][0], problem.node_coords[i][1]) for i in G.nodes}

    # Criar os nós
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

    # Criar as arestas da melhor rota
    edge_x = []
    edge_y = []
    for i in range(len(melhor_rota) - 1):
        x0, y0 = pos[melhor_rota[i]]
        x1, y1 = pos[melhor_rota[i + 1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    # Conectar o último nó ao primeiro
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



def algoritmo_colonia_formigas_sse(G, problem, solucao_inicial=None, alfa=1, beta=2, evaporacao=0.5, Q=10,
                                   num_formigas=100, num_iteracoes=100):
    coordenadas = problem.node_coords
    feromonio = {edge: 1.0 for edge in G.edges}
    cidades = list(G.nodes)
    melhor_rota = None
    melhor_distancia = float('inf')

    if solucao_inicial:
        melhor_rota = solucao_inicial
        melhor_distancia = calcular_distancia_total(melhor_rota, coordenadas)

    for iteracao in range(num_iteracoes):
        todas_rotas = []
        todas_distancias = []
        for _ in range(num_formigas):
            rota = construir_rota(cidades, feromonio, coordenadas, alfa, beta)
            distancia_rota = calcular_distancia_total(rota, coordenadas)
            todas_rotas.append(rota)
            todas_distancias.append(distancia_rota)
            if distancia_rota < melhor_distancia:
                melhor_rota = rota
                melhor_distancia = distancia_rota

        feromonio = atualizar_feromonios(feromonio, todas_rotas, todas_distancias, evaporacao, Q)

        # Emite a iteração e o fitness a cada loop
        yield iteracao + 1, melhor_distancia, melhor_rota
