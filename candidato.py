# NOME DO CANDIDATO: Vitor Moraes Lages
# CURSO DO CANDIDATO: Engenharia Mecanica
# AREAS DE INTERESSE: Estrutura / Visão computacional

# Você pode importar as bibliotecas que julgar necessárias.
import heapq

def encontrar_caminho(pos_inicial, pos_objetivo, obstaculos, largura_grid, altura_grid, tem_bola=False):
    """
    Esta é a função principal que você deve implementar para o desafio EDROM.
    Seu objetivo é criar um algoritmo de pathfinding (como o A*) que encontre o
    caminho ótimo para o robô, considerando os diferentes níveis de complexidade.

    Args:
        pos_inicial (tuple): A posição (x, y) inicial do robô.
        pos_objetivo (tuple): A posição (x, y) do objetivo (bola ou gol).
        obstaculos (list): Uma lista de tuplas (x, y) com as posições dos obstáculos.
        largura_grid (int): A largura do campo em células.
        altura_grid (int): A altura do campo em células.
        tem_bola (bool): Um booleano que indica o estado do robô.
                         True se o robô está com a bola, False caso contrário.
                         Este parâmetro é essencial para o Nível 2 do desafio.

    Returns:
        list: Uma lista de tuplas (x, y) representando o caminho do início ao fim.
              A lista deve começar com o próximo passo após a pos_inicial e terminar
              na pos_objetivo. Se nenhum caminho for encontrado, retorna uma lista vazia.
              Exemplo de retorno: [(1, 2), (1, 3), (2, 3)]

    ---------------------------------------------------------------------------------
    REQUISITOS DO DESAFIO (AVALIADOS EM NÍVEIS):
    ---------------------------------------------------------------------------------
    [NÍVEL BÁSICO: A* Comum com Diagonal]
    O Algoritmo deve chegar até a bola e depois ir até o gol (desviando dos adversários) 
    considerando custos diferentes pdra andar reto (vertical e horizontal) e para andar em diagonal

    [NÍVEL 1: Custo de Rotação]
    O custo de um passo não é apenas a distância. Movimentos que exigem que o robô
    mude de direção devem ser penalizados. Considere diferentes penalidades para:
    - Curvas suaves (ex: reto -> diagonal).
    - Curvas fechadas (ex: horizontal -> vertical).
    - Inversões de marcha (180 graus).

    [NÍVEL 2: Custo por Estado]
    O comportamento do robô deve mudar se ele estiver com a bola. Quando `tem_bola`
    for `True`, as penalidades (especialmente as de rotação do Nível 1) devem ser
    AINDA MAIORES. O robô precisa ser mais "cuidadoso" ao se mover com a bola.

    [NÍVEL 3: Zonas de Perigo]
    As células próximas aos `obstaculos` são consideradas perigosas. Elas não são
    proibidas, mas devem ter um custo adicional para desencorajar o robô de passar
    por elas, a menos que seja estritamente necessário ou muito vantajoso.

    DICA: Um bom algoritmo A* é flexível o suficiente para que os custos de movimento
    (g(n)) possam ser calculados dinamicamente, incorporando todas essas regras.
    """

    # -------------------------------------------------------- #
    #                                                          #
    #             >>>  IMPLEMENTAÇÃO DO CANDIDATO   <<<        #
    #                                                          #
    # -------------------------------------------------------- #

    # O código abaixo é um EXEMPLO SIMPLES de um robô que apenas anda para frente.
    # Ele NÃO desvia de obstáculos e NÃO busca o objetivo.
    # Sua tarefa é substituir esta lógica simples pelo seu algoritmo A* completo.

    print(f"pos_inicial: {pos_inicial}\n")
    print(f"pos_objetivo: {pos_objetivo}\n")
    print(f"obstaculos: {obstaculos}\n")
    print(f"largura_grid: {largura_grid}\n")
    print(f"altura_grid: {altura_grid}\n")
    print(f"tem_bola: {tem_bola}\n")

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

    #verificando se o robo chegou no objetivo
    while valor_do > 0:
        qtd += 1
        print(f"\n---------------------------------------------------------------------------------")
        print(f"Posição atual: {pos_atual}")
        print(f"A face do robo é: {face_robo}")
        print(f"Valor andado: {p_valor_da}")
        print(f"---------------------------------------------------------------------------------\n")
        x_atual, y_atual = pos_atual

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

            #verifica se está fora dos limites
            if 0 > novo_x or novo_x >= largura_grid or 0 > novo_y or novo_y >= altura_grid:
                print("\n---------------------------------------------------------------------------------")
                print(f"Essa posição está fora dos limites ({pos_nova})")
                continue

            #verifica se tal tupla já passou pela lista aberta
            if pos_nova in lista_pos_add:
                print(f"Essa posição já esta na lista aberta ({pos_nova})")
                continue

            #verifica se tal tupla é um obstaculo
            if pos_nova in obstaculos:
                print(f"Essa posição é um obstaculo ({pos_nova})")
                print("---------------------------------------------------------------------------------\n")
                continue

            #acresentar peso à zona de risco
            if pos_nova in zona_de_risco:
                peso += zona_de_risco[pos_nova]
                
            print(f"Movimento: {nome} / Direção: ({dx}, {dy}) / Peso: {peso}")
            print(f"Nova posição: {pos_nova}") 

            #calculando valor de cada movimento
            valor_do = abs(x_obj-novo_x) + abs(y_obj-novo_y)
            valor_da = peso + p_valor_da
            valor_dt = valor_da + valor_do
            print(f"Valor da Distancia Total: {valor_dt}")

            #armazenamento da lista aberta
            listas_pos_finais = lista_pos_andadas + [pos_nova]
            inf_pos_nova=(valor_dt, valor_da, valor_do, pos_nova, nova_face_robo, listas_pos_finais)
            print(f"Novo item: {inf_pos_nova}\n")
            heapq.heappush(lista_aberta, inf_pos_nova) 
            lista_pos_add.add(pos_nova)

        #verifica se ainda há posições para serem analisadas
        if lista_aberta:
            valor_dt, p_valor_da, valor_do, pos_atual, face_robo, lista_pos_andadas = heapq.heappop(lista_aberta)
        else: 
            print("Não foi possivel encontrar um caminho")
            return []
    
    print(f"\n--------------------------Resultado final-------------------------------")
    print(f"Todas posição andadas: {lista_pos_andadas}")
    print(f"Posição atual: {pos_atual}")
    print(f"Valor andado: {p_valor_da}")
    print(f"Quantidade de analises: {qtd}")

    return lista_pos_andadas