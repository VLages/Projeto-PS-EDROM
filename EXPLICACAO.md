
# Análise Detalhada de Código (Algoritmo A\*)

Este documento descreve um script em Python que implementa um algoritmo de busca de caminho, especificamente uma variação do \***Algoritmo A* (A-Star)\*\*. O objetivo do código é encontrar o caminho de menor custo entre uma `pos_inicial` e uma `pos_objetivo` em um grid (grade), levando em conta obstáculos, custos de movimento variáveis e zonas de risco.

## Estrutura Geral do Código

O script pode ser dividido nas seguintes seções lógicas:

1.  **Configuração Inicial**: Definição e impressão dos parâmetros do problema.
2.  **Estruturas de Custo**: Definição dos custos de movimento e criação de "zonas de risco" ao redor de obstáculos.
3.  **Inicialização das Variáveis de Busca**: Preparação das variáveis necessárias para o algoritmo A\*.
4.  **Loop Principal de Busca**: O coração do algoritmo, onde os caminhos são explorados iterativamente.
5.  **Resultado**: Apresentação do caminho encontrado.

-----

## Seção 1: Impressão de Parâmetros Iniciais

```python
    print(f"pos_inicial: {pos_inicial}\n")
    print(f"pos_objetivo: {pos_objetivo}\n")
    print(f"obstaculos: {obstaculos}\n")
    print(f"largura_grid: {largura_grid}\n")
    print(f"altura_grid: {altura_grid}\n")
    print(f"tem_bola: {tem_bola}\n")
```

### Explicação

Estas linhas iniciais servem para depuração e registro (logging). Elas imprimem no console os parâmetros de entrada do problema, garantindo que o algoritmo está começando com os dados corretos.

  - `pos_inicial`: A coordenada `(x, y)` de onde o robô começa.
  - `pos_objetivo`: A coordenada `(x, y)` que o robô deve alcançar.
  - `obstaculos`: Uma lista de coordenadas `(x, y)` que o robô não pode atravessar.
  - `largura_grid` / `altura_grid`: As dimensões do mapa ou grade em que o robô se move.
  - `tem_bola`: Uma variável booleana (`True`/`False`) que indica se o robô está carregando um objeto. Isso afetará o custo dos movimentos.

-----

## Seção 2: Estruturas de Custo

### 2.1 - Movimentos Possíveis e Seus Custos

```python
    #movimentos possiveis
    movimentos = {
        "cima": {"direcao": (0, -1), "peso": {"N":1,"O":3,"S":5,"L":3,"NL":2,"NO":2,"SO":4,"SL":4}, "face": "N"},
        "baixo": {"direcao": (0, 1), "peso": {"N":5,"O":3,"S":1,"L":3,"NL":4,"NO":4,"SO":2,"SL":2 }, "face": "S"},
        "esquerda": {"direcao": (-1, 0), "peso": {"N":3,"O":1,"S":3,"L":5,"NL":4,"NO":2,"SO":2,"SL":4}, "face": "O"},
        "direita": {"direcao": (1, 0), "peso": {"N":3,"O":5,"S":3,"L":1,"NL":2,"NO":4,"SO":4,"SL":2}, "face": "L"},
        
        "cima_esquerda": {"direcao": (-1, -1), "peso": {"N":2,"O":2,"S":4,"L":4,"NL":3,"NO":1,"SO":3,"SL":5}, "face": "NO"}, 
        "cima_direita": {"direcao": (1, -1), "peso": {"N":2,"O":4,"S":4,"L":2,"NL":1,"NO":3,"SO":5,"SL":3}, "face": "NL"},
        "baixo_esquerda": {"direcao": (-1, 1), "peso": {"N":4,"O":2,"S":2,"L":4,"NL":5,"NO":3,"SO":1,"SL":3}, "face": "SO"},
        "baixo_direita": {"direcao": (1, 1), "peso": {"N":4,"O":4,"S":2,"L":2,"NL":3,"NO":5,"SO":3,"SL":1}, "face": "SL"}
    }
```

### Explicação

Esta é uma das estruturas de dados mais importantes do código. O dicionário `movimentos` define todas as ações que o robô pode tomar a partir de uma determinada posição.

  - **Chave Principal** (ex: `"cima"`): O nome do movimento.
  - `"direcao"`: Uma tupla `(dx, dy)` que representa a mudança nas coordenadas. Por exemplo, `(0, -1)` significa mover uma unidade para cima no eixo Y.
  - `"peso"`: Este é um dicionário aninhado que define o **custo base** para realizar o movimento. O custo depende da orientação atual do robô (`face_robo`). Isso simula o custo de "virar" o robô. Por exemplo, se o robô está virado para o Norte (`"N"`) e o movimento é `"cima"`, o custo é baixo (`1`). No entanto, se ele estiver virado para o Sul (`"S"`), o custo para se mover para "cima" é alto (`5`), pois exige uma rotação completa.
  - `"face"`: A nova orientação do robô após completar o movimento. (N: Norte, S: Sul, L: Leste, O: Oeste, e combinações como NO: Noroeste).

### 2.2 - Criação de Zonas de Risco

```python
    #criando zonas de risco
    zona_de_risco = {}
    for x_pos, y_pos in obstaculos:
        zona_de_risco[(x_pos, y_pos - 1)] = 10  
        zona_de_risco[(x_pos, y_pos + 1)] = 10  
        zona_de_risco[(x_pos - 1, y_pos)] = 10  
        zona_de_risco[(x_pos + 1, y_pos)] = 10
        zona_de_risco[(x_pos - 1, y_pos - 1)] = 5
        zona_de_risco[(x_pos + 1, y_pos - 1)] = 5 
        zona_de_risco[(x_pos - 1, y_pos + 1)] = 5  
        zona_de_risco[(x_pos + 1, y_pos + 1)] = 5  
```

### Explicação

Este bloco de código cria uma zona de perigo ou ao redor de cada obstáculo. O objetivo é fazer com que o robô prefira caminhos que não passem muito perto das paredes ou obstáculos.

  - `zona_de_risco`: É um dicionário onde a chave é uma coordenada `(x, y)` e o valor é um custo de penalidade adicional.
  - `for x_pos, y_pos in obstaculos`: O loop itera sobre cada obstáculo.
  - Para cada obstáculo, ele adiciona uma penalidade às células vizinhas:
      - **Penalidade de `10`**: Para células adjacentes (em cima, embaixo, esquerda, direita).
      - **Penalidade de `5`**: Para células diagonais.

-----

## Seção 3: Inicialização das Variáveis de Busca

```python
    #declarando variaveis
    face_robo = "L"
    x_obj, y_obj = pos_objetivo
    pos_atual = pos_inicial
    x_atual, y_atual = pos_atual
    valor_do = abs(x_obj-x_atual)+abs(y_obj-y_atual)
    p_valor_da = 0
    valor_dt = p_valor_da + valor_do
    lista_pos_andadas = [pos_atual]
    lista_aberta = []
    lista_pos_add=set()
    qtd=0
```

### Explicação

Aqui, as variáveis fundamentais para o algoritmo A\* são inicializadas.

  - `face_robo`: A orientação inicial do robô (neste caso, "L" - Leste).
  - `x_obj, y_obj`: Desempacota as coordenadas do objetivo para facilitar o acesso.
  - `pos_atual`: O nó (posição) que o algoritmo está avaliando no momento. Começa com `pos_inicial`.
  - **`valor_do`**: "Distância ao Objetivo". Esta é a **heurística** (o *h(n)* na fórmula do A\*). Ela estima o custo do nó atual até o objetivo. A fórmula `abs(x_obj-x_atual)+abs(y_obj-y_atual)` é conhecida como **Distância de Manhattan**, uma heurística comum e eficiente para grids.
  - **`p_valor_da`**: "Valor da Distância Andada pelo Pai". Este é o custo real do caminho desde o início até o nó atual (o *g(n)* na fórmula do A\*). Começa em 0, pois ainda não nos movemos.
  - **`valor_dt`**: "Valor da Distância Total". Este é o valor principal do A\*, o *f(n)*. É a soma do custo real e da estimativa: $f(n) = g(n) + h(n)$. É usado para decidir qual nó explorar a seguir.
  - `lista_pos_andadas`: Armazena a sequência de posições do caminho que está sendo considerado o melhor até o momento.
  - **`lista_aberta`**: A "Lista Aberta" (Open List) do A\*. Ela armazena todos os nós que foram descobertos, mas ainda não avaliados. É implementada como uma **fila de prioridade** (usando a biblioteca `heapq`), que sempre nos dará o nó com o menor `valor_dt`.
  - `lista_pos_add`: Um `set` que funciona como a "Lista Fechada" (Closed List). Ele armazena as posições que já foram adicionadas à `lista_aberta` para evitar processá-las novamente. Usar um `set` torna a verificação de existência (`in`) extremamente rápida.
  - `qtd`: Um contador para rastrear quantas iterações (análises de posição) o loop principal executa.

-----

## Seção 4: O Loop Principal de Busca

```python
    #verificando se o robo chegou no objetivo
    while valor_do > 0:
```

### Explicação

Este é o início do loop principal do algoritmo. Ele continuará a ser executado enquanto a `pos_atual` não for a `pos_objetivo`. A condição `valor_do > 0` é uma forma inteligente de verificar isso, já que a Distância de Manhattan só é 0 quando as posições são idênticas.

### 4.1 - Iteração e Análise de Movimentos

```python
        # (código de impressão para depuração)

        #declarar as possibilidades de movimento
        for nome, info in movimentos.items():
            dx, dy = info["direcao"]
            if tem_bola:
                peso = info["peso"][face_robo] * 10  
            else:
                peso = info["peso"][face_robo]
            nova_face_robo = info["face"]
            novo_x, novo_y = x_atual + dx, y_atual + dy
            pos_nova=(novo_x,novo_y)
```

### Explicação

Dentro do loop `while`, para a `pos_atual`, o código agora explora todos os vizinhos.

  - `for nome, info in movimentos.items()`: Itera sobre todos os 8 movimentos possíveis.
  - `dx, dy = info["direcao"]`: Obtém a mudança de coordenadas para o movimento.
  - `if tem_bola:`: Verifica se o robô está carregando a bola. Se `True`, o custo base do movimento (`info["peso"][face_robo]`) é **multiplicado por 10**, penalizando fortemente qualquer movimento.
  - `pos_nova=(novo_x,novo_y)`: Calcula a coordenada da nova posição (o nó vizinho).

### 4.2 - Validação da Nova Posição

```python
            #verifica se está fora dos limites
            if 0 > novo_x or novo_x >= largura_grid or 0 > novo_y or novo_y >= altura_grid:
                continue

            #verifica se tal tupla já passou pela lista aberta
            if pos_nova in lista_pos_add:
                continue

            #verifica se tal tupla é um obstaculo
            if pos_nova in obstaculos:
                continue
```

### Explicação

Antes de calcular os custos, o código faz três verificações cruciais. Se qualquer uma for verdadeira, ele usa `continue` para pular para o próximo movimento.

1.  **Fora dos Limites**: Garante que o robô não saia do grid.
2.  **Já na Lista Aberta/Fechada**: Verifica se a `pos_nova` já está no `set` `lista_pos_add`. Isso evita reavaliar nós e entrar em loops infinitos.
3.  **É um Obstáculo**: Garante que a nova posição não é uma parede.

### 4.3 - Cálculo de Custos e Atualização da Lista Aberta

```python
            #acresentar peso à zona de risco
            if pos_nova in zona_de_risco:
                peso += zona_de_risco[pos_nova]
            
            # (código de impressão para depuração)

            #calculando valor de cada movimento
            valor_do = abs(x_obj-novo_x) + abs(y_obj-novo_y)
            valor_da = peso + p_valor_da
            valor_dt = valor_da + valor_do

            #armazenamento da lista aberta
            listas_pos_finais = lista_pos_andadas + [pos_nova]
            inf_pos_nova=(valor_dt, valor_da, valor_do, pos_nova, nova_face_robo, listas_pos_finais)
            
            import heapq # (Nota: A importação deve estar no topo do arquivo)
            heapq.heappush(lista_aberta, inf_pos_nova) 
            lista_pos_add.add(pos_nova)
```

### Explicação

Se uma `pos_nova` for válida, seus custos A\* são calculados.

  - `if pos_nova in zona_de_risco`: Adiciona a penalidade da zona de risco ao custo do movimento (`peso`).
  - `valor_do = abs(x_obj-novo_x) + abs(y_obj-novo_y)`: Calcula a heurística *h(n)* para a `pos_nova`.
  - `valor_da = peso + p_valor_da`: Calcula o custo *g(n)* para a `pos_nova`. É a soma do custo para chegar ao nó anterior (`p_valor_da`) com o custo do movimento atual (`peso`).
  - `valor_dt = valor_da + valor_do`: Calcula o valor total *f(n)*.
  - `listas_pos_finais = ...`: Cria uma cópia do caminho até o nó atual e adiciona a `pos_nova`.
  - `inf_pos_nova = (...)`: Agrupa todas as informações relevantes sobre este nó vizinho em uma tupla. **A ordem é crucial**: `valor_dt` está em primeiro lugar porque a fila de prioridade (`heapq`) usará o primeiro elemento para ordenar.
  - `heapq.heappush(lista_aberta, inf_pos_nova)`: Adiciona a tupla à `lista_aberta`. O `heapq` garante que o item com o menor `valor_dt` ficará "no topo".
  - `lista_pos_add.add(pos_nova)`: Adiciona a `pos_nova` ao `set` para que não seja reavaliada.

### 4.4 - Selecionando o Próximo Nó a Ser Avaliado

```python
        #verifica se ainda há posições para serem analisadas
        if lista_aberta:
            valor_dt, p_valor_da, valor_do, pos_atual, face_robo, lista_pos_andadas = heapq.heappop(lista_aberta)
        else: 
            print("Não foi possivel encontrar um caminho")
            return []
```

### Explicação

Após avaliar todos os vizinhos da `pos_atual`, esta seção escolhe o próximo nó para se tornar a `pos_atual`.

  - `if lista_aberta:`: Verifica se ainda há nós a serem explorados.
  - `heapq.heappop(lista_aberta)`: Esta é a essência do A\*. Ele **remove e retorna o item com o menor `valor_dt`** da lista aberta. Este item representa a promessa de caminho mais curto até o momento.
  - Os valores da tupla retornada são desempacotados e atualizam as variáveis do loop (`p_valor_da`, `valor_do`, `pos_atual`, etc.), preparando para a próxima iteração.
  - `else:`: Se a `lista_aberta` ficar vazia, significa que todos os caminhos possíveis foram explorados e o objetivo não foi alcançado. Um caminho é impossível.

-----

## Seção 5: Resultado

```python
    print(f"\n--------------------------Resultado final-------------------------------")
    print(f"Todas posição andadas: {lista_pos_andadas}")
    print(f"Posição atual: {pos_atual}")
    print(f"Valor andado: {p_valor_da}")
    print(f"Quantidade de analises: {qtd}")

    return lista_pos_andadas
```

### Explicação

Quando o loop `while` termina (porque `valor_do` se tornou 0, ou seja, `pos_atual == pos_objetivo`), este código é executado.

  - Ele imprime um resumo da solução encontrada:
      - `lista_pos_andadas`: A sequência completa de coordenadas do caminho de menor custo.
      - `pos_atual`: A posição final (que deve ser igual a `pos_objetivo`).
      - `p_valor_da`: O custo total (`g(n)`) do caminho encontrado.
      - `qtd`: O número de nós que foram expandidos, uma medida da eficiência da busca.
  - `return lista_pos_andadas`: A função retorna o caminho encontrado como uma lista de tuplas.

## Seção 6: Metodologia de Teste e o Simulador Comparativo

Para validar e comparar a eficácia de cada evolução do algoritmo, foi adotada uma metodologia de teste específica, que justifica a manutenção de arquivos separados para cada fase do projeto.

### Manutenção de Arquivos por Fase (básica, 1, 2, 3)

O projeto foi intencionalmente dividido em múltiplos arquivos, correspondendo a diferentes "fases" de desenvolvimento (ex: `fase_basica`, `fase_1`, `fase_2`, etc.). Cada fase representa uma versão do algoritmo com uma nova camada de complexidade ou uma modificação na lógica de cálculo de custos:

* A **fase básica** pode conter uma implementação simples do A*.
* A **fase 1** pode introduzir os custos de rotação (`peso` baseado na `face_robo`).
* A **fase 2** pode adicionar as `zonas_de_risco` ao redor de obstáculos.
* A **fase 3** pode incluir a penalidade por carregar um objeto (`tem_bola`).

Manter os arquivos separados foi uma decisão deliberada de design para permitir que cada versão do algoritmo pudesse ser executada de forma independente e, mais importante, **simultaneamente** para uma análise comparativa direta, em vez de ter que comentar ou descomentar blocos de código em um único arquivo.

### O Simulador Secundário

Para realizar essa análise comparativa, foi desenvolvido um **simulador secundário**. Este é um programa separado, provavelmente com uma interface gráfica (usando uma biblioteca como Pygame, Tkinter ou similar), cujo principal objetivo é executar todas as fases do algoritmo ao mesmo tempo, em um cenário idêntico, e exibir os resultados de forma visual e unificada.

#### Funcionamento do Simulador

1.  **Ambiente Unificado**: O simulador define um único grid, com a mesma posição inicial, objetivo e conjunto de obstáculos para todos os algorithos que serão testados.
2.  **Visualização Gráfica**: O simulador apresenta quatro grids na tela e, após receber o caminho retornado por cada função, renderiza esses trajetos sobre cada respectivo grid, a fim de faciliar a vizualização de cada código.
3.  **Análise de Métricas**: Além da visualização do trajeto, o simulador coleta e exibe em tempo real as métricas chave de cada fase, como o custo final do caminho (`p_valor_da`), a quantidade de nós analisados (`qtd`) e, potencialmente, o tempo de execução.

Essa abordagem oferece uma comparação imediata e intuitiva, tornando fácil observar visualmente como a adição de zonas de risco ou a penalidade por carregar a bola afeta a rota escolhida pelo robô, sua eficiência e o custo total do percurso.