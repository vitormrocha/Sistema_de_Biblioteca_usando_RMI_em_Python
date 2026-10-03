import socket
import threading
import json

HOST = "0.0.0.0"
PORTA = 5000


class Biblioteca:
    def __init__(self):  # Construtor
        self.livros = {
            '1': {'titulo': 'Dom Casmurro', 'disponivel': True, 'matricula': None, 'nome_cliente': None},
            '2': {'titulo': 'Memorias Postumas', 'disponivel': True, 'matricula': None, 'nome_cliente': None},
            '3': {'titulo': 'O Senhor dos Aneis', 'disponivel': True, 'matricula': None, 'nome_cliente': None},
            '4': {'titulo': 'A Coisa', 'disponivel': True, 'matricula': None, 'nome_cliente': None}
        }
        self.lock = threading.Lock()

    def listar_livros(self):
        with self.lock:
            return self.livros

    def consultar_livro(self, codigo):
        with self.lock:
            return self.livros.get(codigo, None)

    def emprestar_livro(self, codigo, matricula, nome_cliente):
        with self.lock:
            if codigo not in self.livros:
                return "Erro: Esse livro nao foi encontrado"
            livro = self.livros[codigo]
            if livro['disponivel']:
                livro['disponivel'] = False
                livro['matricula'] = matricula
                livro['nome_cliente'] = nome_cliente
                return f"Sucesso: '{livro['titulo']}' foi emprestado para o cliente {nome_cliente}."
            else:
                return f"Erro: '{livro['titulo']}' ja foi emprestado para o cliente {livro['nome_cliente']}."

    def devolver_livro(self, codigo):
        with self.lock:
            if codigo not in self.livros:
                return "Erro: Este livro nao foi encontrado"
            livro = self.livros[codigo]
            if not livro['disponivel']:
                nome = livro['nome_cliente']
                livro['disponivel'] = True
                livro['matricula'] = None
                livro['nome_cliente'] = None
                return f"Sucesso: O cliente {nome} devolveu o livro '{livro['titulo']}'."
            return f"Erro: '{livro['titulo']}' ja esta disponivel"

    def consultar_disponibilidade(self, codigo):
        with self.lock:
            if codigo in self.livros:
                return self.livros[codigo]['disponivel']
            return False



biblioteca = Biblioteca()



def atender_cliente(cliente, endereco):
    print(f"[+] Cliente conectado: {endereco}", flush=True)

    try:
        # Escuta o cliente
        while True:
            dados = cliente.recv(4096)

            if not dados:  # Se o cliente fechou, sai do loop
                break

            # Desserialização
            requisicao = json.loads(dados.decode("utf-8"))
            metodo = requisicao.get("metodo")
            params = requisicao.get("params", [])

            print(f"[->] {endereco} chamou: {metodo}{tuple(params)}", flush=True)

            # Se o cliente chamou um metodo que existe
            if hasattr(biblioteca, metodo):
                try:
                    resultado = getattr(biblioteca, metodo)(*params)
                    resposta = {"status": "ok", "resultado": resultado}
                except Exception as e:
                    resposta = {"status": "erro", "mensagem": str(e)}
            else:
                resposta = {"status": "erro", "mensagem": f"Metodo '{metodo}' nao existe."}

            cliente.send(json.dumps(resposta).encode("utf-8"))
            print(f"[<-] Resposta enviada para {endereco}", flush=True)

    except Exception as erro:
        print(f"[!] Erro com {endereco}: {erro}", flush=True)
    finally:
        cliente.close()
        print(f"[-] Cliente desconectado: {endereco}", flush=True)


servidor = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((HOST, PORTA))
servidor.listen()

print("=" * 50)
print("Servidor da Biblioteca\nDesenvolvido por Vitor Martins Rocha e Odelmo Ferreira Neto")
print("=" * 50)
print(f"Servidor aguardando conexoes na porta {PORTA}...", flush=True)

while True:
    cliente, endereco = servidor.accept()
    thread = threading.Thread(target=atender_cliente, args=(cliente, endereco))
    thread.daemon = True
    thread.start()