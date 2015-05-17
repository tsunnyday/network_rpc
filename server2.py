import socket, select, Queue

HOST = 'localhost'
PORT = 1337



class Game:
	def __init__(self, p1, p2):
		self.p1 = p1
		self.p2 = p2
		self.choices = ["",""]
		



cur_id = 1
games = {}		#game_id:game
players = {}	#socket:[game_id,p#]
	
choices = ['r','p','s']
p1wins = [['s','r'],['p','s'],['r','p']]
	
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1)
print "LISTENING ON PORT %d" %PORT

inputs = [server]
outputs = []

message_queues = {}

waiting_list = []
	

def create_game(p1, p2, cur_id):
	players[p1] = [cur_id, 0]
	players[p2] = [cur_id, 1]
	games[cur_id] = Game(p1, p2)

def msg(sock, string):
	message_queues[sock].put(string)





while inputs:
	readable, writeable, exceptional = select.select(inputs, outputs, inputs)
	
	for s in readable:
		if s is server:
			conn, addr = server.accept()
			print "RECIEVED A CONNECTION FROM %s" %str(addr)
			conn.setblocking(0)
			inputs.append(conn)
			outputs.append(conn)
			message_queues[conn] = Queue.Queue()
			message_queues[conn].put("WELCOME TO NETWORK RPC!\n")
			if len(waiting_list):
				partner = waiting_list.pop()
				message_queues[conn].put("FOUND PARTNER.\n")
				message_queues[conn].put("MEET %s\n" %str(partner.getpeername()))
				if partner not in outputs:
					outputs.append(partner)
				message_queues[partner].put("FOUND PARTNER.\n")
				message_queues[partner].put("MEET %s\n" %str(conn.getpeername()))
				create_game(partner, conn, cur_id)
				message_queues[partner].put("STARTED GAME %d as P1\n" %cur_id)
				message_queues[conn].put("STARTED GAME %d as P2\n" %cur_id)
				cur_id += 1
				msg(conn, "CHOOSE\n")
				msg(partner, "CHOOSE\n")
				
			else:
				waiting_list.append(conn)
				message_queues[conn].put("WAIT FOR ANOTHER PLAYER\n")
		else:
			data = s.recv(1)
			if data:
				print "GOT " + data
				if data in choices:
					games[players[s][0]].choices[players[s][1]] = data
					if all(games[players[s][0]].choices):
						
						if games[players[s][0]].p1 not in outputs:
							outputs.append(games[players[s][0]].p1)
						if games[players[s][0]].p2 not in outputs:
							outputs.append(games[players[s][0]].p2)
						if games[players[s][0]].choices[0] == games[players[s][0]].choices[1]:
							msg(games[players[s][0]].p1, "TIE\n")
							msg(games[players[s][0]].p2, "TIE\n")
						elif [games[players[s][0]].choices[0], games[players[s][0]].choices[1]] in p1wins:
							msg(games[players[s][0]].p1, "P1 WINS\n")
							msg(games[players[s][0]].p2, "P1 WINS\n")
						else:
							msg(games[players[s][0]].p1, "P2 WINS\n")
							msg(games[players[s][0]].p2, "P2 WINS\n")
						msg(games[players[s][0]].p1, "THANKS FOR PLAYING\n")
						msg(games[players[s][0]].p2, "THANKS FOR PLAYING\n")
						finished_game = games.pop(players[s][0])
						print "FINISHED GAME #%d" %players[s][0]
						players.pop(finished_game.p1)
						players.pop(finished_game.p2)
			else:
				print "CLIENT DISCONNECTED"
				print "GAME %d JEOPARDIZED" %players[s][0]
				if games[players[s][0]].p1 == s:
					print "PLAYER 1 DISCONNECTED"
					other = games[players[s][0]].p2
					msg(other, "PLAYER 1 DISCONNECTED; SORRY\n")
				else:
					print "PLAYER 2 DISCONNECTED"
					other = games[players[s][0]].p1
					msg(games[players[s][0]].p1, "PLAYER 2 DISCONNECTED; SORRY\n")
				print str(other)
				players.pop(s)
				
				
				if s in outputs:
					outputs.remove(s)
				inputs.remove(s)
				s.close()
				del message_queues[s]
				
				
		
		
	for s in writeable:
		if not message_queues[s].empty():
			next_msg = message_queues[s].get_nowait()
			sent = s.send(next_msg)
			print "Sent %d out of %d bytes of message" %(sent, len(next_msg))
		else:
			outputs.remove(s)
			if s not in waiting_list and s not in players:
				print "DISCONNECTED " + str(s.getpeername())
				inputs.remove(s)
				s.close()
				del message_queues[s]
				
				
		
	for s in exceptional:
		print "E"
		inputs.remove(s)
		if s in outputs:
			outputs.remove(s)
		if s in waiting_list:
			waiting_list.remove(s)
		s.close()
		del message_queues[s]

print "SHUTTING DOWN"
