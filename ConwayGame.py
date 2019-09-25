'''
File: ConwayGame.py

Programmer: Sergey Filimonov <safilimonv@gmail.com>

Revision history:
	4/22/2019 orginal version

Program to display Conway's Game of Life. Various famous 
'life forms' are included as intilization conditions such
as spaceship , blinker and the beehive. Game board is a 
toroid so it's impossible for life forms to go out of bounds.

To run: 
	python 'ConwayGame.py' 
		or
	python 'ConwayGame.py' --fps 30 --init_conditions 'init_glider'

Optional Parameters:
	--boardSize
		size of the game board (int)
	--fps
		frames per second of animation (int)
	--duration
		seconds animation will run (float)
	--init_conditions
		initilization conditions of the board. Various life forms
		are includes in the 'init_conditions_dic'. Defaults to a
		random value out of this. (str)

Error Checking: 
	I compared the output of various patterns in Conway's orginal
	sketches to what happened when I set these as initial conditions.
	Outputs were the same and the probability of this happening by chance
	is exceedingly small. 

To do:
	- add an optional paramter to save the file as .mov
	- would like to incorporate an alternative game theory version but 
	not sure if I'll have time to finish since this is very intensive.
		+ functionality associated with this is marked 'currently unused'
		in comments

'''
import copy
import numpy as np
import random

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import argparse

class past_agent_battles(object):
	# currently unused
	def __init__(self,x_1,y_1,x_2,y_2):
		#FIXME
		print 'work in progress'


class agent(object):
	'''
	Each specific tile on the gameboard. Represented by
	it's x-y coordinates.
	'''

	def __init__(self,x,y):
		'''
		Stores coordinates of agent (x, y) and status
		'''
		self.X = x
		self.Y = y
		
		#alive or dead
		self.status = 0

		#score from playing other agents
		self.score = 0
		
		#type of strategy agent playing
		self.strategy = random.randint(0,4)

		#last move played (0 - defect / 1 - cooperate)
		self.move_list = [random.randint(0,1)]

		# currently unused 
		# #list to store of all neighbors moves
		# self.left_neighbor_moves =   []
		# self.right_neighbor_moves =  []
		# self.bottom_neighbor_moves = []
		# self.top_neighbor_moves =    []


	def update_status(self, new_status):
		'''
		Updating status of agent:
		0 - dead
		1 - alive
		'''
		self.status = new_status

	def make_decision(self, neighbor):
		# currently unused
		always_defect = 	{0:0, 1:0}
		always_cooperate =  {0:1, 1:1}
		tit_tat = 			{0:0, 1:0}
		random_move = 		{0: random.randint(0,1),
							 1: random.randint(0,1)}

		move_dic = {
		0 : always_defect,
		1 : always_cooperate,
		2 : random_move,
		3 : tit_tat
		}

		neighbor_last_move = neighbor.move_list[-1]
		
		return move_dic[agent.strategy][neighbor_last_move]


def agent_battle(agent, neighbor):
	'''
	currently unused
	'''

	neighbor_last_move = neighbor.move_list[-1]

	return agent.make_decision(neighbor_last_move)



class gameBoard(object):
	def __init__(self,size,init_list):
		self.size = size	#size of gameBoard
		self.dic = {}		#holding status of current gameboard
		self.next_dic = {}  #holding the status of the next gameboard

		#intializing intitial game board
		for x in range(0,size):
			for y in range(0,size):
				self.dic[str([x,y])] = agent(x, y)
				self.next_dic[str([x,y])] = agent(x, y)

		#force updating agents that user specified (intial conditions of the board)
		self.force_update_many_agents(init_list)

	def get_agent_status(self,x,y):
		'''
		function to return specific agent status (0 or 1) 
		from the game board

		Params:
		x, y coordinates of agent (int)

		Returns:
		Status (0 or 1)
		'''

		#setting up toroid so we can't go out of bounds with agent search
		if x < 0:
			x += self.size
		if y < 0:
			y += self.size 

		if y >= self.size:
			y -= self.size 
		if x >= self.size:
			x -= self.size 

		agentKey = str([x,y])
		return self.dic[agentKey].status
 

	def force_update_agent(self,x,y,new_status):
		'''
		Function to force status update to new status.
		Used to initialize the intial gameboard
		'''

		agentKey = str([x,y])
		self.dic[agentKey].update_status(new_status)

	def force_update_many_agents(self,cord_list):
		'''
		Function given a list of coordinates will set 
		all those agents to 'alive' status
		
		Params:
		cord_list -> [ [1,2],[2,2] ] (nested list)
		'''

		for cord in cord_list:
			x = cord[0]
			y = cord[1]

			self.force_update_agent(x,y,1)

	def update_agent(self,x,y):
		'''
		Function to update the status of individual agent based on how many 
		other neighbors are alive
		0 - 1 neighbors -   agent dies
		2 - 3 neighbors -   agent survives
		4+ neighbors    - 	agent dies

		Params:
		myAgent -> agent object to investigate

		'''

		agentKey = str([x,y])
		myAgent = self.dic[agentKey]

		# number of live agents, subract 1 if agent's alive (since it's status gets counted)
		numberAlive = 0
		
		if self.get_agent_status(x, y) == 1:
			numberAlive = -1

		#looping through all neighbors
		for i in range(myAgent.X - 1, myAgent.X + 2):
			for j in range(myAgent.Y - 1, myAgent.Y + 2):
				#checking status of neighbor
				neighborStatus = self.get_agent_status(i, j)

				#checking if neighbor is alive
				if neighborStatus != 0:
					numberAlive += 1

		# -- updating status, possible convert this into a function -- 

		# Any live cell with two or three live neighbours lives on to the next generation
		if (myAgent.status == 1) & ((numberAlive == 2) |  (numberAlive == 3) ):
			self.next_dic[str([x,y])].update_status(1)

		# Any dead cell with exactly three live neighbours becomes a live cell
		if (numberAlive == 3) & (myAgent.status == 0):
			self.next_dic[str([x,y])].update_status(1)

		# Any live cell with more than three live neighbours dies, as if by overpopulation
		if (numberAlive > 3) & (myAgent.status == 1):
			self.next_dic[str([x,y])].update_status(0)	

		# Any live cell with fewer than two live neighbours dies, as if by underpopulation.
		if (numberAlive < 2) & (myAgent.status == 1):
			self.next_dic[str([x,y])].update_status(0)	


	def update_entire_board(self):
		'''
		Function to update every agent on the game board.
		'''
		for x in range(0,self.size):
			for y in range(0,self.size):
				self.update_agent(x,y)

		
		self.dic = copy.deepcopy(self.next_dic)

	def get_status_list(self):
		'''
		Function to take the gameboard and convert the status of every agent 
		into a nested list that we can animate with MatplotLib
		'''
		self.status_list = []

		for x in range(0,self.size):
			y_list = []
			for y in range(0,self.size):
				agentStatus = self.get_agent_status(x,y)
				y_list.append(agentStatus)
			self.status_list.append(y_list)

		return self.status_list

	def num_alive(self):	
		'''
		#currently unused

		Function to tell you how many agents are alive on
		the board
		'''

		numAlive = 0
		for x in range(0,self.size):
			for y in range(0,self.size):
				agentStatus = self.get_agent_status(x,y)
				if agentStatus != 0:
					numAlive += 1
		return numAlive

	def print_board(self):
		'''
		Function to print the board to the console. Useful in error checking
		'''
		print '\n'
		for x in range(0,self.size):
			for y in range(0,self.size):
				agentStatus = self.get_agent_status(x,y)
				#agent alive
				if agentStatus != 0:
					print x,y,
				#agent dead
				else:
					print ' . ',
				if (y + 1) % (self.size) == 0:
					print " "


def random_list(boardSize, density):
	'''
	Function to create a random list for the setting the 
	gameboard intitial conditions
	'''
	init_list = []

	numAgents = int(density * boardSize ** 2)

	for _ in range(numAgents):

		x = np.random.randint(0,boardSize)
		y = np.random.randint(0,boardSize)

		init_list.append([x,y])

	return init_list



#famous patterns in cellular automata
init_beehive 			   = [ [4,5],[4,4],[5,6],[6,5],[6,4],[5,3] ]
init_blinker               = [ [5,6],[5,5],[5,4] ]
init_glider 			   = [ [7,8], [8,9] , [9,9], [9,8] , [9,7] ]
init_heavyweight_spaceship = [ [3,10], [2,9],[4,10],[5,10],[5,9],[5,8],[5,7],
							   [5,6] , [5,5] , [4,4] ]
init_penta_decathlon  	   = [ [5,12],[5,11],[5,10],[5,9], [5,8] , [5,7],
						 	   [5,6], [5,5] , [5,4], [5,13] ]
init_figure_eight 		   = [ [3,4], [3,5], [3,6],
							   [4,4], [4,5], [4,6],
							   [5,4], [5,5], [5,6],
							   [6,7], [6,8], [6,9],
							   [7,7], [7,8], [7,9],
							   [8,7], [8,8], [8,9] ]
init_tee                   = [ [5,5],[4,5],[6,5],[5,6] ]


init_conditions_dic = {'init_beehive':init_beehive,'init_blinker': init_blinker,
						'init_glider':init_glider, 'init_heavyweight_spaceship':
						init_heavyweight_spaceship, 'init_penta_decathlon': 
						init_penta_decathlon, 'init_figure_eight' :
						init_figure_eight, 'init_tee': init_tee}


#random patterns
init_triangle			   = [ [1,5], [0,5] , [1,4] ]
init_spinner_2  		   = [ [0,5], [0,4], [0,3] ]

ims = []

def main():

	parser = argparse.ArgumentParser(description="Conway's Game of Life") 
  
    # add arguments 
	parser.add_argument('--board_size', 
						dest='boardSize', 
						required=False, 
						default = 20,
						type = int) 

	parser.add_argument('--fps', 
    					dest='fps',
    					default = 8,
    					type = float,
    					required=False) 


	parser.add_argument('--duration', 
    					dest='duration',
    					default = 10,
    					type = float,
    					required=False) 

	parser.add_argument('--init_conditions', 
						action='store',
    					dest='init_conditions',
    					type = str,
    					required=False) 

	args = parser.parse_args() 
	
	# creating variables from arguments
	frame_interval = ( 1. / args.fps ) * 1000
	num_frames = int(args.duration *  ( args.fps ) )

	if args.init_conditions == None:
		init_conditions = random.choice(list(init_conditions_dic ) )
	else:
		init_conditions = args.init_conditions


	#generating random intialization
	init_list_random = random_list(args.boardSize,0.1)

	#intializing game board
	myBoard = gameBoard(args.boardSize,
						init_conditions_dic[init_conditions])
	
	fig = plt.figure()

	# looping through and rendering images
	for _ in range(num_frames):
		#updating board
		myBoard.update_entire_board()
		data = myBoard.get_status_list()
		
		#adding individual frame to frame list
		im = plt.imshow(data)
		ims.append([im])

	ani = animation.ArtistAnimation(fig, ims, 
									interval=frame_interval, 
									blit=True,
	                                repeat_delay=50)

	fig.suptitle(init_conditions)

	plt.show()

if __name__ == '__main__': 
    main() 
