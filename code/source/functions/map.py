import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np
import itertools
from scipy import sparse
from heapq import heappop, heappush
import copy

from functions.itertools_addendum import *
from functions.nx_addendum import *
from functions.tk_extension import tk_clear, tk_plot

class map():
	def __init__(self, generate = 0):
		"""
		description:
			Inizialization of an empty map (the map() class implements 
			a graph structure with dictionaries with several additional
			specifications).
		syntax:
			m = map()
		"""
		self._size_parameter = generate
		self._coordinates = {}
		self._vertices = {}
		self._end = None
		self._entities = {}
		self._stamina_life = {}
		if generate != 0:
			flag = False
			while not(flag):
				self._coordinates = {}
				self._vertices = {}
				self._entities = {}
				flag = self._generate(generate)
			self._add_entities()
			self._compute_stamina_life()

	def _insert_vertex(self, v, coord):
		""" 
		description:
			Insert a vertex v to the graph, it adds an entry corresponding 
			to v in the dictionary m._vertices and an entry with its 
			coordinates in the dictionary m._coordinates. 
			The coordinates are supposed to be a tuple with lenght 2.
		syntax:
			m._insert_vertex(v, coord)
		"""
		v = int(v)
		if v not in self._vertices:
			self._coordinates[v] = (int(coord[0]), int(coord[1]))
			self._vertices[v] = {}

	def _remove_vertex(self, v):
		""" 
		description:
			Remove a vertex v from the graph, it removes the entry 
			corresponding to v in both the dictionaries 
			(m._vertices and m._coordinates). 
			It also removes all the edges containing v.
		syntax:
			m._remove_vertex(v)	
		"""
		self._vertices.pop(v, None)
		self._coordinates.pop(v, None)
		for u in self._vertices:
			self._vertices[u].pop(v, None)

	def _insert_edge(self, edge, weight):
		""" 
		description:
			Add an edge (and its associated weight) to the graph.
			It assumes that edge is of type tuple.
		syntax:
			m._insert_edge(edge, weight)
		"""
		weight = round(float(weight))
		u, v = tuple(edge)
		u = int(u)
		v = int(v)
		(self._vertices[u])[v] = weight

	def _remove_edge(self, edge):
		""" 
		description:
			Remove an edge from the graph, it assumes that edge is of 
			type tuple.
		syntax:
			m._remove_edge(edge)
		"""
		u, v = tuple(edge)
		self._vertices[u].pop(v, None)

	def get_size_parameter(self):
		""" 
		description:
			Return the parameter size_parameter.
		syntax:
			size_parameter = m.get_size_parameter()
		"""
		return self._size_parameter
	
	def get_vertices(self):
		""" 
		description:
			Returns a list containing all the vertices of 
			the graph.
		syntax:
			vertices = m.get_vertices()
		"""
		return list(self._vertices.keys())
	
	def get_edges(self):
		""" 
		description:
			Returns a list of lists containing all the edges of the graph.
			Each tuple is a triple: [source, destination, weight].
		syntax:
			edges = m.get_edges()
		"""
		edges = []
		for u in self._vertices:
			for v in self._vertices[u].items():
				edges.append([u, v[0], v[1]])
		return edges
	
	def get_end(self):
		""" 
		description:
			Return the end vertex.
		syntax:
			end = m.get_end()
		"""
		return self._end
	
	def get_entities(self):
		""" 
		description:
			Return the dictionary containing entities and associated values.
		syntax:
			entities = m.get_entities()
		"""
		return self._entities
	
	def get_parameters(self, gamemode):
		""" 
		description:
			Return a list with life, stamina and their corresponding path
			associated to the gamemode.
		syntax:
			parameters = m.get_parameters(gamemode)
		"""
		lives = list(self._stamina_life.keys())
		lives.sort()
		if gamemode  == "balanced":
			life = lives[len(lives) // 2]
		elif gamemode == "survivor":
			life = lives[0]
		elif gamemode == "explorer":
			life = lives[-1]
		stamina = self._stamina_life[life][0]
		path = self._stamina_life[life][1]
		return [life, stamina, path]
	
	def get_stamina_life(self, path):
		""" 
		description:
			Retrieve the stamina and life consumption obtained traversing a path.
		syntax:
			stamina, life = m.get_stamina_life(path)
		"""
		entities = set()
		stamina = 0
		life = 0
		for i in range(len(path) - 1):
			if path[i] in self._entities:
				entities.add(path[i])
			stamina += (self._vertices[path[i]])[path[i + 1]]
		if path[-1] in self._entities:
			entities.add(path[-1])
		for entity in entities:
			life += self._entities[entity]
		return stamina, life
	
	def starting_edges(self, v):
		""" 
		description:
			Returns a list of lists containing all the edges starting from 
			a vertex u. 
			Each list is a triple: [source, destination, weight].
		syntax:
			starting_edges = m.starting_edges(v)
		"""
		starting_edges = []
		if v in self._vertices:
			for u in self._vertices[v].items():
				starting_edges.append([v, u[0], u[1]])
		return starting_edges
	
	def neighbours(self, v):
		""" 
		description:
			Returns a list containing the neighbours of a vertex v.
		syntax:
			neighbours = m.neighbours(v)
		"""
		neighbours = set()
		if v in self._vertices:
			neighbours = set(self._vertices[v].keys())
			for u in self._vertices:
				if v in self._vertices[u]:
					neighbours.add(u)
		return list(neighbours)
	
	def check_adjacent(self, u, v):
		""" 
		description:
			Check whether the vertices u and v are adjacent in the graph, 
			i.e. if exists an edge from u to v.
			Returns a boolean value.
		syntax:
			bool = m.check_adjacent(u, v)
		"""
		if u not in self._vertices:
			return False
		if v in self._vertices[u]:
			return True
		else:
			return False
		
	def diff_coordinates(self, start, end):
		""" 
		description:
			Compute the "direction" of the edge (as unitary vector in uniform norm).
		syntax:
			direction = m.diff_cooordinates(start, end, weight)
		"""
		coord_start = self._coordinates[start]
		coord_end = self._coordinates[end]
		return (np.sign(coord_end[0] - coord_start[0]), np.sign(coord_end[1] - coord_start[1]))

	def _find_vertex_from_coord(self, coord):
		""" 
		description:
			Find the label of a vertex inside the graph starting from its 
			coordinates (tuple).
			If the coordinates do not corresponds to any label it returns -1.
		syntax:
			v = m._find_vertex_from_coord(coord)
		"""
		try:
			return list(self._coordinates.keys())[list(self._coordinates.values()).index(coord)]
		except:
			return -1
		
	def _check_link(self, start, end, verbose = False):
		""" 
		description:
			Check whether there exists a path from start to end through a DFS visit.
			Verbose mode available.
		syntax:
			bool = m._check_link(start, end)
		"""
		if (start == end):
			return True
		n = len(self._vertices)
		explored = [False] * n
		explored[start] = True
		stack = [start]
		while stack:
			u = stack.pop()
			for v in self._vertices[u]:
				if explored[v] is False:
					if v == end:
						return True
					explored[v] = True
					stack.append(v)
		if verbose == True:
			print("error_check_link:", str(start) + "-" + str(end))
		return False
	
	def _generate(self, bound, verbose = False):
		""" 
		description:
			Generate a map (vertices with their coordinates and edges) randomly.
			It takes as argument a parameter bound which is correlated to the size of the map.
			Verbose mode available.
		syntax:
			bool = m._generate(bound)
		"""
		# maximum size of the map / size of the matrix representing the game field (location)
		# 	bound * 4 + 1 = (bound * 2) * 2 + 1
		# location: matrix of the game field
		#	0: not visited nodes (new)
		#	1: occupied nodes (vertex)
		#	2: visited nodes (edge)
		location = sparse.lil_matrix(np.zeros((bound * 4 + 1, bound * 4 + 1)))
		directions = ((0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1))
		max_step = 3
		# max_vertex: number of possible vertices that could be inserted in the map divided by 4
		max_vertex = (bound * 2 + 1) ** 2 // 4
		# insert the start (0)
		self._insert_vertex(0, (0, 0))
		location[2 * bound, 2 * bound] = 1
		# next_vertex: label of the next vertex to be inserted
		next_vertex = 1
		# visited: list of visited vertices
		visited = [0]
		for previous in visited:
			# previous: label of the current position
			prev_x, prev_y = self._coordinates[previous]
			n_neighbours = random.randint(1, 3)
			for _ in range(n_neighbours):
				flag = False
				while not(flag):
					# generate randomly direction and step
					direction = random.choice(directions)
					step = random.randint(1, max_step)
					# check of being inside the boundaries:
					#	if we are outside of the boundaries (vertically or horizontally) then continue
					if not(prev_x + direction[0] * step + bound in np.arange(bound * 2 + 1)) or \
						not(prev_y + direction[1] * step + bound in np.arange(bound * 2 + 1)):
						continue
					# try to find the arrival vertex (actually its label) inside the map (if it is not in the map it returns -1)
					vertex = self._find_vertex_from_coord((prev_x + direction[0] * step, prev_y + direction[1] * step))
					# backward edge:
					#	if the vertex is already in the map and the chosen edge has already been inserted
					#	then no additional control is required
					if vertex != -1 and self.check_adjacent(vertex, previous):
						break
					# overflow vertices:
					#	if we reached the maximum number of vertices in the map (max_vertex) and we are trying to add a new vertex
					#	then look for a new direction and step
					if next_vertex == max_vertex and vertex == -1:
						continue
					# check correctness edge:
					flag = True
					#	the flag is true if:
					#		the edge never passes on already taken nodes in the map (1 or 2 in location),
					#		the last half node is analyzed separately
					#		(check both integer and half nodes)
					for i in range(1, step):
						# 	- half nodes
						flag = flag and (location[(prev_x + direction[0] * i + bound) * 2 - direction[0], \
							(prev_y + direction[1] * i + bound) * 2 - direction[1]] == 0)
						# 	- integer nodes
						flag = flag and (location[(prev_x + direction[0] * i + bound) * 2, (prev_y + direction[1] * i + bound) * 2] == 0)
					# 	- last half node
					flag = flag and (location[(prev_x + direction[0] * step + bound) * 2 - direction[0], \
							(prev_y + direction[1] * step + bound) * 2 - direction[1]] == 0)
					#	same check for the last node taking in account that it is allowed to end in an already taken node (if it is a vertex)
					#	(note: location[vertex] = 0/1, it cannot be 2)
					flag = flag and (location[(prev_x + direction[0] * step + bound) * 2, (prev_y + direction[1] * step + bound) * 2] in [0, 1])
				# there is a probability of 0.5 to generate symmetric edges (back <= prob)
				back = random.random()
				prob = 0.5
				# if we are adding a new vertex 
				# 	then we insert both vertex and edge (also to the queue visited), in case we also add the backward edge
				# else
				# 	if the edge haven't already been inserted then we add it (in case also the backward edge)
				if vertex == -1:
					self._insert_vertex(next_vertex, (prev_x + direction[0] * step, prev_y + direction[1] * step))
					self._insert_edge((previous, next_vertex), step)
					visited.append(next_vertex)
					if back <= prob:
						self._insert_edge((next_vertex, previous), step)
					next_vertex += 1
				else:
					if not(self.check_adjacent(previous, vertex)):
						self._insert_edge((previous, vertex), step)
					if back <= prob and not(self.check_adjacent(vertex, previous)):
						self._insert_edge((vertex, previous), step)
				# update of the location matrix (following the rules at the beginning of the function)
				for i in range(1, step):
					#	- half nodes crossed by an edge
					location[(prev_x + direction[0] * i + bound) * 2 - direction[0], \
							(prev_y + direction[1] * i + bound) * 2 - direction[1]] = 2
					#	- nodes crossed by an edge
					location[(prev_x + direction[0] * i + bound) * 2, (prev_y + direction[1] * i + bound) * 2] = 2
				#	- last half node crossed by an edge
				location[(prev_x + direction[0] * step + bound) * 2 - direction[0], \
							(prev_y + direction[1] * step + bound) * 2 - direction[1]] = 2
				#	- last node occupied by a vertex
				location[(prev_x + direction[0] * step + bound) * 2, (prev_y + direction[1] * step + bound) * 2] = 1
		flag = True
		# check number of vertices is in [(bound * 2 + 1) ** 2 // 5, (bound * 2 + 1) ** 2 // 4]
		if next_vertex < (bound * 2 + 1) ** 2 // 5:
			if verbose == True:	
				print("error_generate:", next_vertex, "<", (bound * 2 + 1) ** 2 // 5)
			return False
		self._compute_end()
		# check that it is possible to arrive to the end from any position
		for u in self._vertices.keys():
			flag = flag and self._check_link(u, self._end, verbose)
		return flag

	def _compute_end(self, start = 0):
		""" 
		description:
			Compute the end of the map through a BFS visit.
			It chooses the last vertex of the last layer of the BFS tree.
		syntax:
			m._compute_end()
		"""
		n = len(self._vertices)
		explored = [False] * n
		explored[start] = True
		queue = [start]
		while queue:
			u = queue.pop(0)
			for v in self._vertices[u]:
				if explored[v] is False:
					explored[v] = True
					queue.append(v)
		self._end = u
	
	def _add_entities(self, num = -1):
		""" 
		description:
			Add a set of entities to the previously generated map. 
			Default number is: num = len(self._vertices) // 5 + 1.
		syntax:
			m._add_entities()
		"""
		if num == -1:
			num = len(self._vertices) // 5 + 1
		# create the list of candidates full_list (and a white_list)
		full_list = list(self._vertices.keys())
		full_list.remove(0)
		full_list.remove(self._end)
		white_list = full_list.copy()
		# max_power: maximum "power" of an entity
		max_power = 3
		for _ in range(num):
			if white_list:
				entity = random.choice(white_list)
				white_list.remove(entity)
				for neighbour in self.neighbours(entity):
					if neighbour in white_list: white_list.remove(neighbour)
			else:
				entity = random.choice(full_list)
			full_list.remove(entity)
			power = random.randint(1, max_power)
			self._entities[entity] = power

	def _dijkstra(self, start, end, blacklist = []):
		"""
		source:
			- https://stackoverflow.com/questions/71663362/performance-improvement-for-dijkstra-algorithm-using-heaps-in-python
			- https://gist.github.com/kachayev/5990802 
		description:
			Dijkstra algorithm implemented with heaps. It is also possible to add a 
			blacklist containing the vertices that we want to avoid 
			(note that neither start or end should be blacklisted).
		syntax:
			distance, path = m._dijkstra(start, end)
		"""
		n = len(self._vertices)
		distances = np.ones(n) * np.inf
		heap = [(0, start, ())]
		# seen = set() # normal dijkstra
		seen = set(blacklist) # blacklisted vertices are avoided
		while heap:
			dist, node, path = heappop(heap)
			if node not in seen:	
				seen.add(node)
				path = path + (node, )
				if node == end:
					return (dist, list(path))
				for neighbour, weight in self._vertices[node].items():
					if neighbour not in seen:
						new_dist = dist + weight
						if new_dist < distances[neighbour]:
							distances[neighbour] = new_dist
							heappush(heap, (new_dist, neighbour, path))
		# if it is impossible to find a path from start to end
		return (np.inf, [])
	
	def _compute_stamina_life(self):
		""" 
		description:
			Create a dictionary that stores, for each possible life cost,
			the best stamina cost and its associated path. 
		syntax:
			m._compute_stamina_life()
		"""
		# entities: list of labels of nodes where the entities are located
		# full_list: entities + start + end
		entities = list(self._entities.keys())
		full_list = entities + [0, self._end]
		# pairs: 
		# 	- dictionary containing the shortest path which avoids the nodes in the tuple blacklist 
		#		and its cost (tuple (cost, shortest_path)) for all couples in full_list;
		#	- the keys are triples of type tuple (node_1, node_2, blacklist);
		#	- we precompute pairs[(node_1, node_2, ())] for all couples (node_1, node_2);
		# pairs_alias:
		#	- dictionary which associates a triple (node_1, node_2, blacklist) with an already 
		#		precomputed touple (cost, shortest_path);
		# 	- the association is made following this assertion: 
		#		if we merge the blackist list and a generic subset of the entities which are not blacklisted nor in the path 
		# 		then we obtain a new blacklist which still leads to the same shortest path
		# (note: actually some couples are excluded from pairs because they are not useful:
		# 	- from any node to itself
		#	- from end to any node
		#	- from any node to start )
		pairs = {}
		pairs_alias = {}
		for node_1 in full_list:
			for node_2 in full_list:
				if (node_1 != node_2) and (node_1 != self._end) and (node_2 != 0):
					pairs[(node_1, node_2, ())] = self._dijkstra(node_1, node_2)
					for alias in powerset(set(entities) - set(pairs[(node_1, node_2, ())][1])):
						pairs_alias[(node_1, node_2, alias)] = (node_1, node_2, ())
		for k in range(len(entities) + 1):
			for permutation in itertools.permutations(entities, k):
				# permutation: ordered subset of the entities' set.
				#	we are looking for the shortest path that crosses these and only these entities, with order,
				#	starting from start and ending in end
				# flag: if the path we are considering is possible than True
				#	else False				
				flag = True
				# life/stamina: variable containing the life/stamina consumed while traversing the path
				life = 0
				stamina = 0
				# path: list containing the shortest path associated with the current permutation
				path = []
				full_permutation = [0] + list(permutation) + [self._end]
				# at each step we look for the shortest path between node_1 and node_2 such that does not cross
				#	the entities which are still "active" (stored in the blacklist variable)
				blacklist = entities.copy() + [self._end]
				for i in range(len(full_permutation) - 1):
					node_1 = full_permutation[i]
					node_2 = full_permutation[i + 1]
					blacklist.remove(node_2)
					# if we haven't got the shortest path for the triple (node_1, node_2, blacklist) we compute it and store it
					#	(we also update pairs_alias)
					if (node_1, node_2, tuple(blacklist)) not in pairs_alias:
						pairs[(node_1, node_2, tuple(blacklist))] = self._dijkstra(node_1, node_2, blacklist)
						current_cost, current_path = pairs[(node_1, node_2, tuple(blacklist))]
						for alias in powerset(set(entities) - set(pairs[(node_1, node_2, tuple(blacklist))][1]) - set(blacklist)):
							pairs_alias[(node_1, node_2, tuple(list(alias) + blacklist))] = (node_1, node_2, tuple(blacklist))
					# else we use the stored one
					else:
						current_cost, current_path = pairs[pairs_alias[(node_1, node_2, tuple(blacklist))]]
					if np.isfinite(current_cost): 
						if i != 0:
							life += self._entities[node_1]
							path += current_path[1:]
						else:
							path += current_path
						stamina += current_cost
					else:
						flag = False
						break
				if flag:
					# if the optimal path corresponding to the permutation costs less than the best path we found with the same life cost (life)
					#	we save in self._stamina_life[life] its stamina cost (stamina) and the path
					if (life not in self._stamina_life) or ((life in self._stamina_life) and (stamina < self._stamina_life[life][0])):
						self._stamina_life[life] = (stamina, path)

	def load(self, filename):
		""" 
		description:
			Load the map from a source file (filename), correctly formatted, i.e. 
			it must contain the following groups of lines separated by blank lines:
				1. a number corresponding to the size_parameter;
				2. one line per vertex containing id and coordinates (id coord_x coord_y);
				3. one line per edge composed as follows: (u v weight);
				4. a vertex id corresponding to the end of the map;
				5. one line per entity containing id and power.
		syntax:
			m.load(filename)
		"""
		with open(filename, "r") as file:
			lines = file.readlines()
		flag = 1
		for i in range(len(lines)):
			if lines[i] == "\n":
				flag += 1
				continue
			if flag == 1:
				size_parameter = lines[i].split()[0]
				self._size_parameter = int(size_parameter)
			elif flag == 2:
				vertex = lines[i].split()
				v, coord_x, coord_y = vertex[:3]
				self._insert_vertex(v, (coord_x, coord_y))
			elif flag == 3:
				edge = lines[i].split()
				u, v, weight = edge[:3]
				self._insert_edge((u, v), weight)
			elif flag == 4:
				end = lines[i].split()[0]
				self._end = int(end)
			elif flag == 5:
				entity = lines[i].split()
				v, power = entity[:2]		
				self._entities[int(v)] = int(power)
		self._compute_stamina_life()
		
	def save(self, filename):
		""" 
		description:
			Save the map in a file (filename).
		syntax:
			m.save(filename)
		"""
		lines = str(self._size_parameter) + "\n\n"
		for v in self._coordinates:
			lines += str(v) + " " + str(self._coordinates[v][0]) + " " + str(self._coordinates[v][1]) + "\n"
		lines += "\n"
		for u in self._vertices:
			for v in self._vertices[u]:
				lines += str(u) + " " + str(v) + " " + str(self._vertices[u][v]) + "\n"
		lines += "\n"
		lines += str(self._end) + "\n\n"
		for v in self._entities:
			lines += str(v) + " " + str(self._entities[v]) + "\n"
		with open(filename, "w") as file:
			file.write(lines)

	def draw(self,
	  		filename = "",
	  		seed = -1, caption = [], update = [], active_entities = {}, path = [],
			arc_rad = 0.25, font_size = 8, node_size = 1000, asp = 1, figure_size = 15):
		""" 
		description:
			Draw (and save) the map m with several optionals:
				- seed: seed of generation of the map;
				- caption = [life, stamina, games]: current variables for the game;
				- update = [visited_nodes, visited_edges, current_position]:
					current state of the map discovered by the player;
				- active_entities: dict of entities to display as active (red);
				- path: a path to show in the map, it is supposed to be a list 
					of the vertices to traverse.
			Several additional parameters can be setted:
				- arc_rad := angle of edges (in radiants);
				- font_size := font size of all the labels;
				- node_size := size of the nodes;
				- asp := aspect of the axis (1:1 by default);
				- figure_size := size of the figure.
			The output depends on the optional variable filename:
			if it is non-empty the map is saved as a png
			otherwise the output figure is returned.
		syntax:
			m.draw()
		"""
		# init of the figure
		fig = plt.figure(figsize = (figure_size, figure_size), layout = "tight")
		plt.gca().set_aspect("equal")
		# set the caption
		if seed != -1:
			fig.text(.01, .98, "seed: " + str(seed),
		 		fontdict = {"fontfamily": "monospace", "fontsize": 11})
		if caption:
			fig.text(.01, .01, "life: " + str(caption[0]) + "\n" + "stamina: " + str(caption[1]),
		   		fontdict = {"fontfamily": "monospace", "fontsize": 11})
			fig.text(.90, .98, "games: " + str(caption[2]),
				fontdict = {"fontfamily": "monospace", "fontsize": 11})
		# create graph
		m_draw = nx.DiGraph()
		for e in self.get_edges():
			m_draw.add_edge(e[0], e[1], weight = int(e[2]))
		# relabel the graph (and create relabeling map: nodes_labels)
		nodes_labels = {}
		for node in m_draw.nodes:
			if node in self._entities:
				nodes_labels[node] = str(node) + "/" + str(self._entities[node])
			else:
				nodes_labels[node] = str(node)
			if node == 0:
				nodes_labels[node] = "start"
			if node == self._end:
				nodes_labels[node] = "end"
		nx.relabel_nodes(m_draw, nodes_labels, copy = False)
		# assign weights
		weight_labels = nx.get_edge_attributes(m_draw, "weight")
		# assign coordinates
		coordinates = {nodes_labels[key]: (self._coordinates[key][0], self._coordinates[key][1] * asp) for key in self._coordinates.keys()}
		if not(update):
			# if we are drawing the full map (i.e. update = [])
			#	color the nodes (start/end, entities (in lightgreen the ones that are in the path) and standard)
			nodes_colors = []
			for node in m_draw.nodes:
				if node in ["start", "end"]:
					nodes_colors.append("forestgreen")
				elif "/" in node:
					if node not in path:
						nodes_colors.append("indianred")
					else:
						nodes_colors.append("lightgreen")
				else:
					nodes_colors.append("lightgray")
			#	create path
			for i in range(len(path)):
				path[i] = nodes_labels[path[i]]
			edges_path = list(zip(path, path[1:]))
			# 	if the path variable is empty
			#		then draw the complete map
			# 	else
			#		draw the complete map semi-transparent
			transparency = 1 if not(path) else 0.25
			nx.draw(m_draw, coordinates,
				with_labels = True, font_size = font_size, font_family = "monospace", node_size = node_size, node_color = nodes_colors,
				edgecolors = "black", alpha = transparency, connectionstyle = f"arc3, rad = {arc_rad}", edge_color = "black",
				min_target_margin = 20, min_source_margin = 0)
			draw_networkx_edge_labels_oriented(m_draw, coordinates,
				edge_labels = weight_labels, label_pos = 0.5, font_size = font_size * 0.8, font_family = "monospace", alpha = transparency,
				rad = arc_rad, verticalalignment = "center")
			# 	if the path variable is non-empty then draw the path
			if path:
				# 	initialize path graph
				path_draw = nx.DiGraph()
				for e in edges_path:
					path_draw.add_edge(e[0], e[1], weight = weight_labels[(e[0], e[1])])
				for node in path:
					path_draw.add_node(node)
				path_weight_labels = nx.get_edge_attributes(path_draw, "weight")
				#	color nodes and edges of path graph
				nodes_colors = []
				for node in path_draw.nodes:
					if node in ["start", "end"]:
						nodes_colors.append("forestgreen")
					elif "/" in node:
						nodes_colors.append("lightgreen")
					else:
						nodes_colors.append("lightgray")
				#	draw path graph
				nx.draw(path_draw, coordinates,
					with_labels = True, font_size = font_size, font_family = "monospace", node_size = node_size, node_color = nodes_colors,
					edgecolors = "black", connectionstyle = f"arc3, rad = {arc_rad}", edge_color = "black",
					min_target_margin = 20, min_source_margin = 0)
				draw_networkx_edge_labels_oriented(path_draw, coordinates,
					edge_labels = path_weight_labels, label_pos = 0.5, font_size = font_size * 0.8, font_family = "monospace", rad = arc_rad,
					verticalalignment = "center")				
		else:
			# if we are drawing the map during the game
			# 	initialize transparent draw (in order to fix the size)
			nx.draw(m_draw, coordinates, 
	   			with_labels = False, node_size = node_size, alpha = 0, connectionstyle = f"arc3, rad = {arc_rad}", 
				min_target_margin = 20, min_source_margin = 0)
			draw_networkx_edge_labels_oriented(m_draw, coordinates,
				edge_labels = weight_labels, label_pos = 0.5, font_size = font_size * 0.8, font_family = "monospace", alpha = 0,
				rad = arc_rad, verticalalignment = "center")
			# 	unpack update
			visited_nodes, visited_edges, current_position = copy.deepcopy(update)
			# 	find available_edges/directions and relabel available_edges
			available_edges = self.starting_edges(current_position)
			available_directions = []
			for i in range(len(available_edges)):
				if available_edges[i] not in visited_edges:
					direction = self.diff_coordinates(available_edges[i][0], available_edges[i][1])
					available_directions.append((\
							direction[0] + self._coordinates[available_edges[i][0]][0], \
							direction[1] + self._coordinates[available_edges[i][0]][1]))
				available_edges[i].pop()
				available_edges[i][0] = nodes_labels[available_edges[i][0]]
				available_edges[i][1] = nodes_labels[available_edges[i][1]]
			# 	relabel visited_edges/nodes, current_position
			for i in range(len(visited_nodes)):
				visited_nodes[i] = nodes_labels[visited_nodes[i]]	
			for i in range(len(visited_edges)):
				visited_edges[i][0] = nodes_labels[visited_edges[i][0]]
				visited_edges[i][1] = nodes_labels[visited_edges[i][1]]
			current_position = nodes_labels[current_position]
			# 	relabel active entities
			a_entities = list(active_entities.keys())
			for i in range(len(a_entities)):
				a_entities[i] = nodes_labels[a_entities[i]]
			# 	initialize current graph
			current_draw = nx.DiGraph()
			for e in visited_edges:
				current_draw.add_edge(e[0], e[1], weight = int(e[2]))
			for node in visited_nodes:
				current_draw.add_node(node)
			current_weight_labels = nx.get_edge_attributes(current_draw, "weight")
			# 	initialize directions graph
			if current_position != "end":
				directions_draw = nx.DiGraph()
				for i in range(len(available_directions)):
					directions_draw.add_edge(current_position, str(-(i + 1)), weight = 0)
					coordinates[str(-(i + 1))] = available_directions[i]
			#	color nodes and edges of current graph
			nodes_colors = []
			for node in current_draw.nodes:
				if node in ["start", "end"]:
					nodes_colors.append("forestgreen")
				elif "/" in node:
					if node in a_entities:
						nodes_colors.append("indianred")
					else:
						nodes_colors.append("lightgreen")
				else:
					nodes_colors.append("lightgray")
			edgecolors = ["dimgrey" if node == current_position else "black" for node in current_draw.nodes]
			edges_colors = []
			for edge in current_draw.edges:
				if list(edge) in available_edges:
					edges_colors.append("dimgrey")
				else:
					edges_colors.append("black")
			#	draw directions graph
			if (current_position != "end") and (current_position not in a_entities):
				nx.draw_networkx_edges(directions_draw, coordinates, connectionstyle = f"arc3, rad = {arc_rad}", edge_color = "dimgrey",
					min_target_margin = 20, min_source_margin = 0)
			#	draw current graph
			nx.draw(current_draw, coordinates,
				with_labels = True, font_size = font_size, font_family = "monospace", node_size = node_size, 
				node_color = nodes_colors, edgecolors = edgecolors, connectionstyle = f"arc3, rad = {arc_rad}", edge_color = edges_colors,
				min_target_margin = 20, min_source_margin = 0)
			draw_networkx_edge_labels_oriented(current_draw, coordinates, edge_labels = current_weight_labels, label_pos = 0.5, 
				font_size = font_size * 0.8, font_family = "monospace", rad = arc_rad, verticalalignment = "center")
		if not filename == "": 
			plt.savefig(filename, dpi = 300, bbox_inches = "tight")
		return fig

	def set_sizes(self):
		"""
		description:
			Set graphical parameters according to the size of the map.
		syntax:
			node_size, font_size = m.set_sizes()
		"""
		if self._size_parameter == 2: return (1200, 9)	 
		if self._size_parameter == 3: return (1000, 8)	 
		if self._size_parameter == 4: return (800, 7) 
		if self._size_parameter == 5: return (700, 7)

	def print_map(self, window, caption, canvas = None, seed = -1, update = [], active_entities = [], path = [], save = []):
		"""
		description:
			Print the map on a canvas inside the tkinter window and return it.
		syntax:
			canvas = m.print_map(window, caption, seed)
		"""
		if canvas is not None:
			tk_clear(canvas)
		node_size, font_size = self.set_sizes()
		if save:
			filename = "../maps/game/game_" + str(save[0]) + ".png"
			save[0] += 1
		else:
			filename = ""
		fig = self.draw(filename = filename,
			seed = seed, caption = caption, update = update, active_entities = active_entities, path = path,
			font_size = font_size, node_size = node_size, figure_size = 15)
		canvas = tk_plot(fig, window)
		plt.close(fig)
		return canvas