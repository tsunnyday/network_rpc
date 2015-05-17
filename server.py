import socket

HOST = 'localhost'
PORT = 1337

def send_a_msg(conn, msg):
	length = len(msg)
	sent = 0
	while sent < length:
		sent += conn.send(msg[sent:])

choices = ["r","p","s"]
		
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_sock.bind((HOST, PORT))
server_sock.listen(5)

print "LISTENING ON PORT %d" %PORT

while True:
	first_player, first_address = server_sock.accept()
	print "PLAYER 1 has connected from %s" %str(first_address)
	send_a_msg(first_player, "Please wait for another player to join.\n")
	second_player, second_address = server_sock.accept()
	print "PLAYER 2 has connected from %s" %str(second_address)
	send_a_msg(first_player, "Ready to play!\n")
	send_a_msg(second_player, "Ready to play!\n")
	first_choice, second_choice = "", ""
	while first_choice not in choices or second_choice not in choices:
		if first_choice not in choices:
			first_choice = first_player.recv(1)
			if first_choice in choices:
				print "FIRST PLAYER CHOOSES " + first_choice
		if second_choice not in choices:
			second_choice = second_player.recv(1)
			if second_choice in choices:
				print "SECOND PLAYER CHOOSES " + second_choice
	
	send_a_msg(first_player, "First player chooses " + first_choice + " second player chooses " + second_choice + "\n")
	send_a_msg(second_player, "First player chooses " + first_choice + " second player chooses " + second_choice + "\n")
	first_player.close()
	second_player.close()
	
