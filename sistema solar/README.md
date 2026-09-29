Trabalho prático da disciplina INF1761 – Computação Gráfica da PUC-Rio.

O projeto implementa uma animação 2D do sistema solar interior (Sol, Mercúrio, Terra e Lua) sobre um fundo estrelado, utilizando a API WebGPU em Python (wgpu e rendercanvas) com o framework de grafo de cena.

Hierarquia dos Nós:
Cena / Pipeline Geral
  Fundo: Quadrado dimensionado com a textura do espaço.  
  Sol: Disco centralizado com escala própria.
  Órbita de Mercúrio: Gira em torno do Sol
  Órbita da Terra: Gira em torno do Sol
    Eixo da Terra: Rotação diária da Terra no próprio eixo.   
    Órbita da Lua: Gira ao redor da Terra.aa
    
Arquivos principais:
  final.py: Arquivo principal com a montagem da cena, carregamento das texturas e loop de desenho.
  disk.py: Gera a malha geométrica circular com coordenadas de textura.   
  square.py: Gera a malha geométrica retangular para o fundo.   
  shader.wgsl: Código do shader na GPU para projeção e amostragem de texturas.   
  Imagens.jpg: Texturas do espaço, Sol, Mercúrio, Terra e Lua.

Necessário instalar bibliotecas:
  pip install wgpu rendercanvas glfw pillow numpy
