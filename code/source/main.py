import sys
sys.dont_write_bytecode = True
from functions.map import *
from functions.draw_map import *
import pywinauto

def set_modifier(best_life, best_stamina, difficulty):
	if difficulty in ["easy", ""]:
		return(3 * best_life, 3 * best_stamina)
	elif difficulty == "hard":
		return(round(1.5 * best_life), round(1.5 * best_stamina))

def print_map(life, stamina, m, seed, window, update = -1):
	fig = m.draw(seed = seed, caption = [life, stamina], update = update, figure_size = 15)
	canvas = tk_plot(fig, window)
	return canvas

def clear_map(canvas):
	canvas.get_tk_widget().pack_forget()

def direction_to_text(direction):
	if direction == [0, 1]: return("north")
	if direction == [1, 1]: return("north-east")
	if direction == [1, 0]: return("east")
	if direction == [1, -1]: return("south-east")
	if direction == [0, -1]: return("south")
	if direction == [-1, -1]: return("south-west")
	if direction == [-1, 0]: return("west")
	if direction == [-1, 1]: return("north-west")
	return("error_direction")

def try_again():
	while True:
		flag = input("do you want to try again? ")
		if flag in ["yes", "y", "no", "n", ""]:
			break
	if flag in ["yes", "y", ""]:
		print("________________")
		return True
	return False

def start_game(life, stamina, m, seed):
	# intro
	if gamemode in ["balanced", ""]:
		print("intro per balanced...")
	elif gamemode == "survivor":
		print("intro per survivor...")
	elif gamemode == "explorer":
		print("intro per explorer...")
	# get entities' dict
	entities = m.get_entities()
	# create alias directions
	alias_directions = {
		"n": "north", "north": "north",
		"ne": "north-east", "north-east": "north-east",
		"e": "east", "east": "east",
		"se": "south-east", "south-east": "south-east",
		"s": "south", "south": "south",
		"sw": "south-west", "south-west": "south-west", 
		"w": "west", "west": "west",
		"nw": "north-west", "north-west": "north-west"
	}
	print("intro map appears...")
	window = tk_windows_setup()
	# click the cmd to select it
	pywinauto.mouse.click(button = "left", coords = (100, 100))
	visited_nodes = [0]
	visited_edges = []
	flag = True
	while flag:
		# map
		current_position = 0
		current_life = life
		current_stamina = stamina
		canvas = print_map(current_life, current_stamina, m, seed, window, update = [visited_nodes, visited_edges, current_position])
		# main
		while True:
			# choose direction
			available_edges = m.starting_edges(current_position)
			print("available directions:")
			available_directions = {}
			for edge in available_edges:
				key = direction_to_text(m.diff_coordinates(edge[0], edge[1], edge[2]))
				available_directions[key] = [edge[1], edge[2]]
				print("- " + key)
			while True:
				chosen_direction = input()
				if chosen_direction in alias_directions and alias_directions[chosen_direction] in list(available_directions.keys()):
					chosen_direction = alias_directions[chosen_direction]
					break
				else:
					print("it is impossible to go there")
			# move
			past_position = current_position
			current_position = available_directions[chosen_direction][0]
			new_edge = [past_position, current_position, available_directions[chosen_direction][1]]
			if current_position not in visited_nodes:
				visited_nodes.append(current_position)
			if new_edge not in visited_edges:
				visited_edges.append(new_edge)
			current_stamina -= available_directions[chosen_direction][1]
			# out of stamina
			if current_stamina < 0:
				print("you ran out of stamina: you lose")
				flag = try_again()
				break
			if current_position in entities:
				current_life -= entities[current_position]
			# update map
			clear_map(canvas)
			canvas = print_map(current_life, current_stamina, m, seed, window, update = [visited_nodes, visited_edges, current_position])
			# out of life
			if current_life < 0:
				print("you ran out of life: you lose")
				flag = try_again()
				break
			# win
			if current_position == m.get_end():
				print("you win!")
				return


print("\n \
  _                  _             _ _                        _   _    \n \
 | |_ ___ ___ ___   | |_ ___ ___ _| |_|___ ___    ___ ___ ___| |_| |_  \n \
 | '_| -_| -_| . |  |   | -_| .'| . | |   | . |  |   | . |  _|  _|   | \n \
 |_,_|___|___|  _|  |_|_|___|__,|___|_|_|_|_  |  |_|_|___|_| |_| |_|_| \n \
             |_|                          |___|                        \n \
\n")

while True:
	# generate map
	seed = random.randint(0, 1000)
	random.seed(seed)
	k = 2
	m = map(generate = k)
	# generate parameters
	while True:
		gamemode = input("select gamemode: ")
		parameters = m.get_parameters(gamemode)
		if parameters != "error_gamemode":
			break
	best_life, best_stamina, best_path = parameters
	while True:
		difficulty = input("select difficulty: ")
		if difficulty in ["easy", "hard", ""]:
			break
	life, stamina = set_modifier(best_life, best_stamina, difficulty)
	# game
	start_game(life, stamina, m, seed)
	print("________________________________")
	