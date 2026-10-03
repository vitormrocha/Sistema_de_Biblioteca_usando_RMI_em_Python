import socket
import json

HOST = "127.0.0.1"
PORTA = 5000


class BibliotecaProxy:
    def __init__(self, host=HOST, porta=PORTA):
        self.host = host
        self.porta = porta
        self.sock = None
        self.conectar()

    def conectar(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.porta))

    def _chamar_remoto(self, metodo, *params):
        try:
            requisicao = {"metodo": metodo, "params": list(params)}
            self.sock.send(json.dumps(requisicao).encode("utf-8"))

            dados = self.sock.recv(4096).decode("utf-8")
            resposta = json.loads(dados)

            if resposta["status"] == "ok":
                return resposta["resultado"]
            return f"ERRO: {resposta['mensagem']}"
        except Exception as e:
            return f"ERRO de comunicacao: {e}"

    def fechar(self):
        if self.sock:
            self.sock.close()

    # Interface remota
    def listar_livros(self): return self._chamar_remoto("listar_livros")
    def consultar_livro(self, codigo): return self._chamar_remoto("consultar_livro", codigo)
    def emprestar_livro(self, codigo, mat, nome): return self._chamar_remoto("emprestar_livro", codigo, mat, nome)
    def devolver_livro(self, codigo): return self._chamar_remoto("devolver_livro", codigo)
    def consultar_disponibilidade(self, codigo): return self._chamar_remoto("consultar_disponibilidade", codigo)


#para mostrar todos os livros
def mostrar_acervo(biblioteca):
    """Pega a lista do servidor e imprime formatada."""
    livros = biblioteca.listar_livros()

    if not livros:
        print("   (acervo vazio)")
        return

    for codigo, info in livros.items():
        if info['disponivel']:
            print(f"   [{codigo}] {info['titulo']}  —  Disponivel")
        else:
            print(f"   [{codigo}] {info['titulo']}  —  Emprestado para {info['nome_cliente']}")



def iniciar_cliente():
    try:
        biblioteca = BibliotecaProxy()
    except ConnectionRefusedError:
        print("ERRO: Servidor offline. Rode o servidor primeiro.")
        return

    print("=" * 50)
    print("BIBLIOTECA UNIVERSITARIA\nCriado por Vitor Martins Rocha e Odelmo Ferreira Neto")
    print("=" * 50)

    nome = input("Digite seu nome: ").strip()
    matricula = input("Digite sua matricula: ").strip()

    if not nome or not matricula:
        print("Nome e matricula sao obrigatorios.")
        biblioteca.fechar()
        return

    print(f"\nOla, {nome}! Bem-vindo(a). Abaixo esta o menu de opcoes\n")

    while True:
        print(f"\n--- MENU ({nome}) ---")
        print("1. Listar acervo completo")
        print("2. Consultar disponibilidade de um livro")
        print("3. Emprestar livro")
        print("4. Devolver livro")
        print("5. Ver detalhes de um livro")
        print("6. Sair")

        opcao = input("Opcao: ").strip()

        if opcao == "1":
            print("\nAcervo da Biblioteca:")
            mostrar_acervo(biblioteca)

        elif opcao == "2":
            codigo = input("\nCodigo do livro que voce quer consultar\n>> ").strip()
            if biblioteca.consultar_disponibilidade(codigo):
                print("Livro DISPONIVEL.")
            else:
                dados = biblioteca.consultar_livro(codigo)
                if dados:
                    print(f"Livro emprestado para: {dados.get('nome_cliente')}")
                else:
                    print("Livro nao encontrado.")

        elif opcao == "3":
            codigo = input("\nCodigo do livro que voce quer pegar emprestado: ").strip()
            print(biblioteca.emprestar_livro(codigo, matricula, nome))

        elif opcao == "4":
            codigo = input("\nCodigo do livro que voce quer devolver\n>> ").strip()
            print(biblioteca.devolver_livro(codigo))

        elif opcao == "5":
            codigo = input("\nCodigo do livro que voce quer buscar\n>> ").strip()
            dados = biblioteca.consultar_livro(codigo)
            if dados:
                print(f"\nCodigo: {codigo}")
                print(f"Titulo: {dados.get('titulo', 'N/A')}")
                print(f"Disponivel: {'Sim' if dados['disponivel'] else 'Nao'}")
                print(f"Cliente: {dados['nome_cliente'] or '-'}")
                print(f"Matricula: {dados['matricula'] or '-'}")
            else:
                print("Livro nao encontrado.")

        elif opcao == "6":
            print(f"Ate logo, {nome}!")
            biblioteca.fechar()
            break
        else:
            print("Opcao invalida.")


if __name__ == "__main__":
    iniciar_cliente()