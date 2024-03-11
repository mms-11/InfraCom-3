from rdt3 import RDT
import socket


class Sala:
    def __init__(self, nome):
        self.agenda = [
            ["", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", "", ""],
        ]
        self.nome = nome


sala1 = Sala("E101")
sala2 = Sala("E102")
sala3 = Sala("E103")
sala4 = Sala("E104")
sala5 = Sala("E105")

host = socket.gethostbyname(socket.gethostname())


salasList = [sala1, sala2, sala3, sala4, sala5]


class Cliente:
    def __init__(self, clientPort, nome, flag):
        self.endCliente = clientPort
        self.nome = nome
        self.flag = flag


clients = []


def send_everyone(server, msg):
    for client in clients:
        server.rdt_send(msg, (host, client.endCliente))


# def connect(clienteOBJ,clientlist,host,port,sala,dia,hora):
#
#            tamanho = clientlist.length
#            clientlist[tamanho +1] = clienteOBJ #atualiza vetor
#
#            #ver se a sala está ocupada
#
#            if sala.agenda[dia][hora]:#sala ocupada
#                 print("essa sala já está ocudada nesse dia, nessa hora")
#            else:
#
#                print(clienteOBJ.nome, "reservou a sala")


def look_for_client(addr):
    for client in clients:
        if client.endCliente == addr[1]:
            nome = client.nome
            break
        else:
            nome = "Unknown"
    return nome


def reserve(server, nome, numero, dia, horario):
    client_nomes = [client.nome for client in clients]  # List of client names
    if nome in client_nomes:
        for sala in salasList:
            if sala.nome == numero and sala.agenda[int(dia)][int(horario)] == "":
                sala.agenda[int(dia)][int(horario)] = nome
                msg = "Reservada confirmada"
                msg_all = (
                    "Reservada confirmada para "
                    + nome
                    + " na sala "
                    + numero
                    + " no dia "
                    + dia
                    + " no horário "
                    + horario
                )
                send_everyone(server, msg_all)
                return msg
            else:
                msg = "Sala ocupada por " + sala.agenda[int(dia)][int(horario)]
                return msg
    else:
        msg = "Você não está conectado"
        return msg


def cancel(server, nome, numero, dia, horario):
    client_nomes = [client.nome for client in clients]  # List of client names
    if nome in client_nomes:
        for sala in salasList:
            if sala.nome == numero and sala.agenda[int(dia)][int(horario)] == nome:
                sala.agenda[dia][horario] = ""
                msg = "Reserva cancelada"
                msg_all = (
                    "Reserva cancelada para "
                    + nome
                    + " na sala "
                    + numero
                    + " no dia "
                    + dia
                    + " no horário "
                    + horario
                )
                send_everyone(server, msg_all)
                return msg
            else:
                msg = "Você não tem reserva nessa sala"
                return msg
        else:
            msg = "Sala " + numero + " não existe"
            return msg
    else:
        msg = "Você não está conectado"
    return msg


def check(numero, dia, horario):
    for sala in salasList:
        if sala.nome == numero:
            if sala.agenda[int(dia)][int(horario)] == "":
                msg = "Sala " + numero + " está disponível"
            else:
                msg = (
                    "Sala "
                    + numero
                    + " está ocupada por "
                    + sala.agenda[int(dia)][int(horario)]
                )
            return msg
    msg = "Sala " + numero + " não existe"
    return msg


def main():
    server = RDT("server", 13009, "")

    while True:
        print("Server receiving")
        server.reset_num_seq()
        rcvpkt, addr = server.rdt_rcv()  # iniciando modo de escuta
        msg = rcvpkt["data"].split(" ")
        if msg[0] == "connect":
            print("Server received connection request")
            # TODO: fazer função que enviar que recebe uma mensagem como parametro e envia ela para todos os usuarios conectados
            clients.append(Cliente(addr[1], msg[1], True))
            send_everyone(server, msg[1] + " está conectado")
            server.rdt_send("Connected", addr)
        elif msg[0] == "check":
            print("Server received check request")
            msg_back = check(msg[1], msg[2], msg[3])
            server.rdt_send(msg_back, addr)
        elif msg[0] == "reservar":
            print("Server received reserve request")
            nome = look_for_client(addr)
            msg_back = reserve(server, nome, msg[1], msg[2], msg[3])
            server.rdt_send(msg_back, addr)
        elif msg[0] == "cancelar":
            print("Server received cancel request")
            nome = look_for_client(addr)
            msg_back = cancel(server, nome, msg[1], msg[2], msg[3])
            server.rdt_send(msg_back, addr)
        elif msg[0] == "list":
            print("Server received list request")
            msg_back = "Usuários conectados: "
            for client in clients:
                msg_back += client.nome + ", "
            msg_back = msg_back.rstrip(", ")
            server.rdt_send(msg_back, addr)

        elif msg[0] == "bye":
            print("Server received bye request")
            nome = look_for_client(addr)
            for client in clients:
                if client.endCliente == addr[1]:
                    clients.remove(client)
                    break
            send_everyone(server, nome + " desconectou")
            server.rdt_send("Desconectado", addr)


if __name__ == "__main__":
    main()
