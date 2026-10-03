=========================================================
 SISTEMA DE BIBLIOTECA COM RMI
=========================================================

Trabalho avaliativo da disciplina de Sistemas Distribuidos -
implementacao de um sistema de biblioteca usando RMI (Remote
Method Invocation) sobre sockets TCP em Python.


---------------------------------------------------------
 AUTORES
---------------------------------------------------------

Vitor Martins Rocha - 12211BCC049
Odelmo Ferreira Neto - 12211BCC006

Disciplina: Sistemas Distribuidos (GBC074)
Instituicao: Universidade Federal de Uberlandia (UFU)
Professor(a): Fernanda Maria da Cunha Santos


---------------------------------------------------------
 SOBRE O PROJETO
---------------------------------------------------------

Sistema distribuido cliente-servidor onde multiplos clientes
podem se conectar simultaneamente a uma biblioteca central
para:

  - Listar o acervo completo
  - Consultar disponibilidade de um livro
  - Emprestar um livro
  - Devolver um livro
  - Ver detalhes de um livro

O sistema implementa os 4 componentes de RMI descritos na
arquitetura classica:

  +-------------+----------------------------------------+
  | Componente  | Onde esta no codigo                    |
  +-------------+----------------------------------------+
  | Proxy       | class BibliotecaProxy no cliente       |
  | Despachante | hasattr() + getattr() no servidor      |
  | Esqueleto   | json.loads() + (*params)               |
  | Servente    | Instancia da classe Biblioteca         |
  +-------------+----------------------------------------+


---------------------------------------------------------
 ARQUITETURA
---------------------------------------------------------

  +-------------------------+         +-------------------------+
  |        CLIENTE          |         |        SERVIDOR         |
  |                         |         |                         |
  |   +-----------------+   |         |   +-----------------+   |
  |   |   Aplicacao     |   |         |   |   Aplicacao     |   |
  |   |   (menu)        |   |         |   |   (servente)    |   |
  |   +--------+--------+   |         |   +--------+--------+   |
  |            |            |         |            |            |
  |            v            |         |            |            |
  |   +-----------------+   |  JSON   |   +-----------------+   |
  |   |  Biblioteca     |---+-------->|   |  Despachante    |   |
  |   |  Proxy          |   |  TCP    |   |  + Esqueleto    |   |
  |   +-----------------+   |<--------+---|                 |   |
  |                         |  JSON   |   +-----------------+   |
  +-------------------------+         +-------------------------+

Fluxo de uma chamada remota:

  1. Cliente chama biblioteca.emprestar_livro("1", "12211", "Vitor")
  2. O Proxy empacota em JSON:
     {"metodo": "emprestar_livro", "params": [...]}
  3. Envia via socket TCP para o servidor
  4. O Despachante le o campo "metodo" e busca o metodo correspondente
  5. O Esqueleto desserializa os parametros e chama o metodo no Servente
  6. O resultado volta pelo mesmo caminho como JSON


---------------------------------------------------------
 CONCORRENCIA EM SISTEMAS DISTRIBUIDOS
---------------------------------------------------------

O principal desafio tratado foi a concorrencia: varios clientes
podem tentar emprestar o MESMO livro ao mesmo tempo, causando
uma condicao de corrida (race condition).

Solucao: uso de threading.Lock (exclusao mutua) dentro dos
metodos da classe Biblioteca.

    def emprestar_livro(self, codigo, matricula, nome_cliente):
        with self.lock:              # Apenas UMA thread por vez
            # ... logica de emprestimo

O "with self.lock" garante que apenas UMA thread acesse o
estado do livro por vez, mesmo que o servidor esteja atendendo
varios clientes simultaneamente.


---------------------------------------------------------
 ESTRUTURA DO PROJETO
---------------------------------------------------------

Trab01-RMI/
  |-- servidor.py              # Servidor com a classe remota + threads + lock
  |-- cliente.py               # Cliente com o Proxy
  |-- teste_concorrencia.py    # (opcional) Testa o lock com 10 clientes
  |-- README.txt


---------------------------------------------------------
 COMO EXECUTAR
---------------------------------------------------------

Pre-requisitos:
  - Python 3.7 ou superior
  - Nenhuma biblioteca externa (usa so socket, threading e json)

1. Inicie o servidor:

     python servidor.py

   Saida esperada:

     ==================================================
     Servidor da Biblioteca
     Desenvolvido por Vitor Martins Rocha e Odelmo Ferreira Neto
     ==================================================
     Servidor aguardando conexoes na porta 5000...

2. Inicie um ou mais clientes (em terminais separados):

     python cliente.py

   O cliente vai pedir:
     - Seu nome
     - Sua matricula

   Depois exibe o menu de opcoes.


---------------------------------------------------------
 TESTANDO A CONCORRENCIA
---------------------------------------------------------

Para verificar que o Lock esta funcionando:

  1. Abra o servidor em um terminal
  2. Abra 3 ou mais clientes em terminais diferentes
  3. Em todos ao mesmo tempo, escolha a opcao 3 (Emprestar)
     e digite o MESMO codigo de livro (ex: 1)
  4. Resultado esperado:
       - Apenas 1 cliente recebe: "Sucesso: ..."
       - Os demais recebem: "Erro: ... ja foi emprestado para X"

Isso comprova que o Lock esta garantindo exclusao mutua.

Teste automatizado (opcional):

  Se voce criou o teste_concorrencia.py:

     python teste_concorrencia.py

  Dispara 10 clientes simultaneos tentando pegar o mesmo
  livro. A saida esperada e:

     Sucessos: 1
     Erros:    9
     Lock funcionou!


---------------------------------------------------------
 TECNOLOGIAS USADAS
---------------------------------------------------------

  +-------------+-------------------------------------------------+
  | Tecnologia  | Uso                                             |
  +-------------+-------------------------------------------------+
  | Python      | Linguagem principal                             |
  | socket      | Comunicacao TCP entre cliente e servidor        |
  | threading   | Multithreading no servidor + Lock               |
  | json        | Serializacao/desserializacao das mensagens      |
  +-------------+-------------------------------------------------+


---------------------------------------------------------
 CONCEITOS APLICADOS
---------------------------------------------------------

  - RMI (Remote Method Invocation) - chamada de metodos remotos
    como se fossem locais
  - Proxy Pattern - representante local do objeto remoto
  - Despachante + Esqueleto - componentes de middleware para RMI
  - Concorrencia - multiplas threads no servidor
  - Exclusao Mutua - threading.Lock para evitar race conditions
  - Serializacao - JSON para transporte de dados
  - Modelo Cliente-Servidor - arquitetura classica de sistemas
    distribuidos


---------------------------------------------------------
 REFERENCIAS
---------------------------------------------------------

  - Aula 4 - Processos e Threads (Profa. Fernanda Maria)
  - Aula 5 - Sockets (Profa. Fernanda Maria)
  - Aula 6 - RMI (Profa. Fernanda Maria)
  - RODRIGUES, E. M. et al. Artigo RMI Pratico. PUCRS.


---------------------------------------------------------
 OBSERVACOES
---------------------------------------------------------

  - O sistema NAO usa Pyro4 ou qualquer framework de RMI - toda
    a logica de serializacao e transporte foi implementada
    manualmente, replicando os componentes descritos no slide 11
    da Aula 6.

  - O acervo e dinamico: novos livros adicionados no servidor
    aparecem automaticamente no cliente.


=========================================================
 FIM
=========================================================
