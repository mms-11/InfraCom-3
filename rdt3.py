import socket 
import random


class RDT:
    # Construtor da classe. Inicializa o socket UDP, define o tipo (cliente ou servidor),
    # o endereço e a porta de comunicação, e inicializa os números de sequência para controle.
    def __init__(self, type : str, addrPort : int = 5000, addrName : str = 'localhost'):
        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addrPort = addrPort
        self.addrName = addrName
        self.type = type
        self.num_seq_c = 0
        self.num_seq_s = 0
        
        #vincula o socket do server a porta especificada.
        self.udp.bind(("", addrPort))
    
    def __del__(self):
        self.udp.close()

    # Cria um pacote de dados encapsulando os dados e o número de sequência em uma string codificada.
    def make_pkt(self, data, num_seq):
        return str({
            "data": data,
            "num_seq": num_seq
        }).encode()
    
    # Reseta os números de sequência
    def reset_num_seq(self):
        self.num_seq_c = 0
        self.num_seq_s = 0
    
    def close(self):
        self.__del__()

    # Envia dados utilizando o protocolo UDP para o endereço e porta especificados.
    def udt_send(self, data, addr = None):
        if (addr == None):
            addr = (self.addrName, self.addrPort) #(HOST, PORTA CLIENT)

        print('sending data to addr:', addr)

        if not isinstance(data, bytes):
            data = data.encode()

        # if random.random() < 0.2:
        #     print('Packet lost!')
        #     return

        self.udp.sendto(data, addr)
    
    # Recebe dados utilizando o protocolo UDP. Se for cliente, apenas recebe,
    # se for servidor, atualiza o endereço e porta do remetente para responder.
    def udt_rcv(self):
        bytes_read, addr = self.udp.recvfrom(4096)
        self.addrName = addr[0]
        self.addrPort = addr[1]
        addr = (self.addrName, self.addrPort)
        

        return (eval(bytes_read.decode()), addr)
    
    # Envia dados de forma confiável, aguardando ACK do receptor. Se não receber ACK,
    # reenvia os dados após um timeout.
    def rdt_send(self, data, addr = None):
        rcvpkt = None
        self.udp.settimeout(3)
        while True:
            print('making packet with data and num_seq:', self.num_seq_c)
            sndpkt = self.make_pkt(data, self.num_seq_c)
            print('sending packet:')
            self.udt_send(sndpkt, addr)
            try:
                print('waiting for ack')
                rcvpkt, add = self.rdt_rcv('wait_ack')
                if rcvpkt['num_seq'] == self.num_seq_c and rcvpkt['data'] == b'ACK':
                    break
            except socket.timeout:
                print('timeout, resending packet')
                continue
        self.udp.settimeout(None)
        self.num_seq_c = 1 - self.num_seq_c

    # Recebe dados de forma confiável. Se esperando por ACK, aguarda até receber o ACK correto.
    # Se recebendo dados regulares, envia ACK após a recepção correta.
    def rdt_rcv(self, state : str = 'null'):
        
        if(state == 'wait_ack'):
            print('waiting for ack with num_seq:', self.num_seq_c)
            rcvpkt = None
            while(not rcvpkt or rcvpkt['num_seq'] != self.num_seq_c or rcvpkt['data'] != b'ACK'):
                rcvpkt, addr = self.udt_rcv()
                print('received packet:', rcvpkt)
            
        else:
            print('waiting for regular packet')
            rcvpkt = None
            while(not rcvpkt or rcvpkt['num_seq'] != self.num_seq_s):
                rcvpkt, addr = self.udt_rcv()
                sndack = self.make_pkt(b'ACK',self.num_seq_s)
                self.udt_send(sndack, addr)
            
            sndack = self.make_pkt(b'ACK',rcvpkt['num_seq'])
            rcvpkt = rcvpkt['data']
            self.udt_send(sndack)
            self.num_seq_s = 1 - self.num_seq_s
        
        return rcvpkt, addr