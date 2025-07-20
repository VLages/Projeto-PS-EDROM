import pygame
import sys
import random

# Importar as estratégias de caminho
import candidato_basico
import candidato_fase1
import candidato_fase2
import candidato_fase3

# Configurações
COR_FUNDO = (20, 80, 40)
COR_LINHA = (255, 255, 255)
COR_ROBO = (0, 0, 255)
COR_ROBO_COM_BOLA = (100, 140, 255)
COR_BOLA = (255, 165, 0)
COR_OBSTACULO = (255, 0, 0)
COR_CAMINHO = (0, 255, 255)
COR_GOL = (255, 255, 0)
COR_PAINEL = (40, 40, 40)
COR_BOTAO = (80, 80, 80)
COR_TEXTO_BOTAO = (255, 255, 255)
COR_DIVISOR = (100, 100, 100) # Nova cor para os divisores

# Dimensões da Grade e da Tela
LARGURA_GRID = 20
ALTURA_GRID = 15
TAMANHO_CELULA = 25 # Diminuído ainda mais
ALTURA_PAINEL_CENARIO = 50 # Altura do painel para cada cenário, ajustado

# Desenho (funções auxiliares)
def desenhar_grade(tela, offset_x, offset_y):
    for x in range(0, LARGURA_GRID * TAMANHO_CELULA + 1, TAMANHO_CELULA):
        pygame.draw.line(tela, COR_LINHA, (x + offset_x, offset_y), (x + offset_x, offset_y + ALTURA_GRID * TAMANHO_CELULA))
    for y in range(0, ALTURA_GRID * TAMANHO_CELULA + 1, TAMANHO_CELULA):
        pygame.draw.line(tela, COR_LINHA, (offset_x, y + offset_y), (offset_x + LARGURA_GRID * TAMANHO_CELULA, y + offset_y))

def desenhar_retangulo(tela, pos_grid, cor, offset_x, offset_y):
    x, y = pos_grid
    rect = pygame.Rect(x * TAMANHO_CELULA + offset_x, y * TAMANHO_CELULA + offset_y, TAMANHO_CELULA, TAMANHO_CELULA)
    pygame.draw.rect(tela, cor, rect)
    
def desenhar_circulo(tela, pos_grid, cor, offset_x, offset_y, raio_fator=0.4):
    x, y = pos_grid
    centro_x = int(x * TAMANHO_CELULA + TAMANHO_CELULA / 2 + offset_x)
    centro_y = int(y * TAMANHO_CELULA + TAMANHO_CELULA / 2 + offset_y)
    raio = int(TAMANHO_CELULA * raio_fator)
    pygame.draw.circle(tela, cor, (centro_x, centro_y), raio)

def desenhar_caminho(tela, caminho, offset_x, offset_y):
    for passo in caminho:
        desenhar_circulo(tela, passo, COR_CAMINHO, offset_x, offset_y, raio_fator=0.2)
        
def desenhar_botao(tela, fonte, rect, texto, cor_fundo, cor_texto):
    pygame.draw.rect(tela, cor_fundo, rect, border_radius=8)
    superficie_texto = fonte.render(texto, True, cor_texto)
    rect_texto = superficie_texto.get_rect(center=rect.center)
    tela.blit(superficie_texto, rect_texto)

class Cenário:
    def __init__(self, id_cenario, estrategia_modulo, nome_estrategia, estado_inicial_comum):
        self.id = id_cenario
        self.estrategia = estrategia_modulo
        self.nome_estrategia = nome_estrategia
        self.estado_inicial_comum = estado_inicial_comum # Recebe o estado inicial comum
        self.estado = self._resetar_para_estado_comum() # Inicia com o estado comum
        self.offset_x = 0 # Será definido na main
        self.offset_y = 0 # Será definido na main

    def _resetar_para_estado_comum(self):
        # Reseta para o estado inicial comum (mesmas posições)
        estado_copia = dict(self.estado_inicial_comum)
        estado_copia["simulacao_rodando"] = False
        estado_copia["caminho_atual"] = []
        estado_copia["tem_bola"] = False
        estado_copia["mensagem"] = f"Cenário {self.id} ({self.nome_estrategia}): Reiniciado!"
        return estado_copia

    def resetar_cenario(self):
        self.estado = self._resetar_para_estado_comum()

    def atualizar_estado_inicial_comum(self, novo_estado_comum):
        self.estado_inicial_comum = novo_estado_comum
        self.resetar_cenario()

    def atualizar(self):
        if self.estado["simulacao_rodando"]:
            if not self.estado["caminho_atual"]:
                objetivo_atual = self.estado["pos_bola"] if not self.estado["tem_bola"] else self.estado["pos_gol"]
                self.estado["caminho_atual"] = self.estrategia.encontrar_caminho(
                    pos_inicial=self.estado["pos_robo"], pos_objetivo=objetivo_atual, obstaculos=self.estado["obstaculos"],
                    largura_grid=LARGURA_GRID, altura_grid=ALTURA_GRID, tem_bola=self.estado["tem_bola"])
            if self.estado["caminho_atual"]:
                self.estado["pos_robo"] = self.estado["caminho_atual"].pop(0)
            if not self.estado["tem_bola"] and self.estado["pos_robo"] == self.estado["pos_bola"]:
                self.estado["tem_bola"] = True
                self.estado["caminho_atual"] = []
                self.estado["mensagem"] = f"Cenário {self.id} ({self.nome_estrategia}): Bola capturada! Rumo ao gol!"
            if self.estado["tem_bola"] and self.estado["pos_robo"] == self.estado["pos_gol"]:
                self.estado["mensagem"] = f"Cenário {self.id} ({self.nome_estrategia}): GOL! Cenário finalizado."
                # Pequena pausa visual antes de resetar para o estado inicial
                pygame.time.wait(500)
                self.resetar_cenario() # Volta para o estado inicial, não gera novo cenário

    def desenhar(self, tela, fonte_botao):
        offset_x = self.offset_x
        offset_y = self.offset_y
        
        # Desenha o fundo do cenário
        cenario_rect = pygame.Rect(offset_x, offset_y, LARGURA_GRID * TAMANHO_CELULA, ALTURA_GRID * TAMANHO_CELULA)
        pygame.draw.rect(tela, COR_FUNDO, cenario_rect)

        desenhar_grade(tela, offset_x, offset_y)
        
        if self.estado["caminho_atual"]:
            desenhar_caminho(tela, self.estado["caminho_atual"], offset_x, offset_y)

        desenhar_retangulo(tela, self.estado["pos_gol"], COR_GOL, offset_x, offset_y)
        for obs in self.estado["obstaculos"]:
            desenhar_retangulo(tela, obs, COR_OBSTACULO, offset_x, offset_y)

        if self.estado["tem_bola"]:
            desenhar_retangulo(tela, self.estado["pos_robo"], COR_ROBO_COM_BOLA, offset_x, offset_y)
            desenhar_circulo(tela, self.estado["pos_robo"], COR_BOLA, offset_x, offset_y, raio_fator=0.3)
        else:
            desenhar_retangulo(tela, self.estado["pos_robo"], COR_ROBO, offset_x, offset_y)
            desenhar_circulo(tela, self.estado["pos_bola"], COR_BOLA, offset_x, offset_y)
            
        # Painel de controle do cenário
        painel_rect = pygame.Rect(offset_x, offset_y + ALTURA_GRID * TAMANHO_CELULA, LARGURA_GRID * TAMANHO_CELULA, ALTURA_PAINEL_CENARIO)
        pygame.draw.rect(tela, COR_PAINEL, painel_rect)
        
        # Botões para este cenário
        self.botao_play_pause = pygame.Rect(offset_x + 5, painel_rect.top + 5, 60, 20)
        self.botao_reset = pygame.Rect(offset_x + 70, painel_rect.top + 5, 60, 20)
        self.botao_novo_cenario = pygame.Rect(offset_x + 135, painel_rect.top + 5, 90, 20)

        texto_play = "Pause" if self.estado["simulacao_rodando"] else "Play"
        desenhar_botao(tela, fonte_botao, self.botao_play_pause, texto_play, COR_BOTAO, COR_TEXTO_BOTAO)
        desenhar_botao(tela, fonte_botao, self.botao_reset, "Reiniciar", COR_BOTAO, COR_TEXTO_BOTAO)
        desenhar_botao(tela, fonte_botao, self.botao_novo_cenario, "Novo Cenário", COR_BOTAO, COR_TEXTO_BOTAO)
        
        # Mensagem do cenário
        superficie_msg = fonte_botao.render(self.estado["mensagem"], True, COR_TEXTO_BOTAO)
        tela.blit(superficie_msg, (offset_x + 5, painel_rect.top + 28))

        # Título da estratégia
        superficie_titulo = fonte_botao.render(f"Estratégia: {self.nome_estrategia}", True, COR_TEXTO_BOTAO)
        tela.blit(superficie_titulo, (offset_x + 5, painel_rect.top + 40))


def main():
    pygame.init()
    
    estrategias = [
        (candidato_basico, "Básica"),
        (candidato_fase1, "Fase 1"),
        (candidato_fase2, "Fase 2"),
        (candidato_fase3, "Fase 3")
    ]

    # Função para gerar um estado inicial comum para todos os cenários
    def gerar_estado_inicial_comum():
        # Posições fixas
        pos_robo = (2, ALTURA_GRID // 2)
        pos_gol = (LARGURA_GRID - 1, ALTURA_GRID // 2)

        # Posição da Bola
        while True:
            pos_bola_x = random.randint(LARGURA_GRID // 2, LARGURA_GRID - 1)
            pos_bola_y = random.randint(0, ALTURA_GRID - 1)
            pos_bola = (pos_bola_x, pos_bola_y)
            if pos_bola != pos_gol and pos_bola != pos_robo:
                break

        # Posição dos Adversários (Obstaculos)
        MAX_OBSTACULOS = 25 # Aumentado para mais obstáculos
        obstaculos = []
        posicoes_ocupadas = {pos_robo, pos_gol, pos_bola}
        
        tentativas = 0
        while len(obstaculos) < MAX_OBSTACULOS:
            obs_x = random.randint(3, LARGURA_GRID - 1)
            obs_y = random.randint(0, ALTURA_GRID - 1)
            pos_obs = (obs_x, obs_y)

            dist_do_robo = abs(pos_obs[0] - pos_robo[0]) + abs(pos_obs[1] - pos_robo[1])
            dist_do_gol = abs(pos_obs[0] - pos_gol[0]) + abs(pos_obs[1] - pos_gol[1])

            if pos_obs in posicoes_ocupadas or dist_do_robo < 3 or dist_do_gol <= 1:
                tentativas += 1
                if tentativas > 1000:
                    print(f"AVISO: Não foi possível posicionar {MAX_OBSTACULOS} obstáculos. Continuando com {len(obstaculos)}.")
                    break
                continue
            
            obstaculos.append(pos_obs)
            posicoes_ocupadas.add(pos_obs)
            tentativas = 0

        return {
            "pos_robo": pos_robo, "pos_bola": pos_bola, "pos_gol": pos_gol, "obstaculos": obstaculos,
            "tem_bola": False, "caminho_atual": [], "simulacao_rodando": False,
            "mensagem": ""
        }

    estado_inicial_comum = gerar_estado_inicial_comum()

    cenarios = []
    for i, (estrategia_modulo, nome_estrategia) in enumerate(estrategias):
        cenarios.append(Cenário(i + 1, estrategia_modulo, nome_estrategia, estado_inicial_comum))

    # Ajustes para layout 2x2
    LARGURA_CENARIO = LARGURA_GRID * TAMANHO_CELULA
    ALTURA_CENARIO = ALTURA_GRID * TAMANHO_CELULA + ALTURA_PAINEL_CENARIO

    LARGURA_TELA = LARGURA_CENARIO * 2
    ALTURA_TELA = ALTURA_CENARIO * 2

    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("EDROM - Desafio A* - Múltiplos Cenários")
    clock = pygame.time.Clock()
    fonte_botao = pygame.font.Font(None, 18) # Fonte ainda menor para caber nos botões menores
    
    try:
        icone_imagem = pygame.image.load("icone_edrom.png")
        pygame.display.set_icon(icone_imagem)
    except pygame.error as e:
        print(f"Não foi possível carregar a imagem \'icone_edrom.png\': {e}")
    
    # Definir os offsets X e Y para cada cenário no layout 2x2
    # Cenário 1 (0,0), Cenário 2 (LARGURA_CENARIO, 0)
    # Cenário 3 (0, ALTURA_CENARIO), Cenário 4 (LARGURA_CENARIO, ALTURA_CENARIO)
    cenarios[0].offset_x = 0
    cenarios[0].offset_y = 0

    cenarios[1].offset_x = LARGURA_CENARIO
    cenarios[1].offset_y = 0

    cenarios[2].offset_x = 0
    cenarios[2].offset_y = ALTURA_CENARIO

    cenarios[3].offset_x = LARGURA_CENARIO
    cenarios[3].offset_y = ALTURA_CENARIO

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for cenario in cenarios:
                    if cenario.botao_play_pause.collidepoint(event.pos):
                        cenario.estado["simulacao_rodando"] = not cenario.estado["simulacao_rodando"]
                        cenario.estado["mensagem"] = f"Cenário {cenario.id} ({cenario.nome_estrategia}): Simulação em andamento..." if cenario.estado["simulacao_rodando"] else f"Cenário {cenario.id} ({cenario.nome_estrategia}): Simulação pausada."
                    elif cenario.botao_reset.collidepoint(event.pos):
                        cenario.resetar_cenario()
                    elif cenario.botao_novo_cenario.collidepoint(event.pos):
                        # Gerar um novo cenário comum para todos
                        novo_estado_comum = gerar_estado_inicial_comum()
                        for c in cenarios:
                            c.atualizar_estado_inicial_comum(novo_estado_comum)

        tela.fill(COR_FUNDO) # Limpa a tela antes de desenhar todos os cenários

        for cenario in cenarios:
            cenario.atualizar()
            cenario.desenhar(tela, fonte_botao)

        # Desenhar divisores
        pygame.draw.line(tela, COR_DIVISOR, (LARGURA_CENARIO, 0), (LARGURA_CENARIO, ALTURA_TELA), 3) # Divisor vertical
        pygame.draw.line(tela, COR_DIVISOR, (0, ALTURA_CENARIO), (LARGURA_TELA, ALTURA_CENARIO), 3) # Divisor horizontal

        pygame.display.flip()
        clock.tick(10) # Aumentei o tick para 10 para uma simulação mais fluida

if __name__ == '__main__':
    main()

