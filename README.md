# Ant Colony Optimization for TSP - Flask Application

Este projeto implementa uma aplicação web utilizando o algoritmo de otimização colônia de formigas ACO para resolver o problema do caixeiro viajante TSP − TravelingSalesmanProblem. A aplicação é desenvolvida com o framework Flask, e o processamento do algoritmo é visualizado através de gráficos e dados transmitidos em tempo real para o frontend.

## Requisitos

Antes de rodar a aplicação, você precisará instalar os seguintes softwares e bibliotecas:

### Dependências do Sistema:

Python 3.10+ 
pip para o gerenciamento de pacotes do Python

### Pacotes Python: As seguintes bibliotecas Python são necessárias para rodar o projeto:

Flask
Matplotlib
NetworkX
Tsplib95
NumPy
Base64 gerenciamento de encoding
io para manipulação de arquivos sem memória
random para gerar números aleatórios 
json para manipulação de dados json
time para manipulação de tempo e delays

Você pode instalar todos os pacotes necessários com os comandos de pip install descritos abaixo.

## Instalação

### 1. Clonando o repositório Primeiro, clone o repositório em sua máquina local 

```bash git clone https://github.com/MatheusGarvao/ACOproblem-Sergio-Tanaka.git```

### 2. Criação de ambiente virtual 

É altamente recomendado criar um ambiente virtual para o projeto. Para criar e ativar o ambiente, use os seguintes comandos:

#### No Windows: ```bash python -m venv venv venv\Scripts\activate ```

#### No Linux/Mac: ```bash python3 -m venv venv source venv/bin/activate ```

### 3. Instalação das dependências

Com o ambiente virtual ativado, instale as dependências necessárias usando os seguintes comandos, um para cada biblioteca:

#### Instalar Flask: ```bash pip install Flask ```

#### Instalar Matplotlib: ```bash pip install matplotlib ```

#### Instalar NetworkX: ```bash pip install networkx ```

#### Instalar Tsplib95: ```bash pip install tsplib95 ```

#### Instalar NumPy: ```bash pip install numpy ```

## Como Executar

Certifique-se de que você está no diretório do projeto.
Ative o ambiente virtua (se necessário).
Execute o comando abaixo para iniciar o servidor Flask:
```bash python app.py ```

Se tudo estiver configurado corretamente, você verá a mensagem indicando que o servidor Flask está rodando:

```bash * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit) ```

Agora, abra seu navegador e acesse http://127.0.0.1:5000/ para interagir com a interface web.

Para rodar, selecione a instância do problema e clique em Carregar Instância, após isso clique em Executar ACO, caso queira customizar, a partir disso você consegue rodar multiplos ACO ou rodar ACO com solução inicial pré-carregada.
