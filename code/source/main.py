import sys
sys.dont_write_bytecode = True

from functions.aliases import *
from functions.appearance import *
from functions.map import *
from functions.tk_extension import tk_window_setup, tk_sleep
from functions.rl import *

def decide(text):
	"""
	description:
		Routine that allows the player to choose an option (described
		in the text).
	syntax:
		bool = decide(text)
	"""
	while True:
		flag = slow_input(text + " (yes/no) ")
		if notebook: print()
		if flag in aliases_yes_no:
			break
		else:
			print("Incorrect value. Please select yes or no:")
	if aliases_yes_no[flag] == "yes":
		return True
	return False
	
def generate_map(seed = -1, k = -1):
	"""
	description:
		Generate the game map.
	syntax:
		m, seed = generate_map()
	"""
	if seed == -1: seed = random.randint(0, 1000)
	random.seed(seed)
	slow_print("Game settings")
	tab()
	if k == -1:
		k = slow_input("- Select map size (from 2 to 5): ")
		if notebook: print()
		while True:
			if k in aliases_size_parameters:
				k = int(aliases_size_parameters[k])
				break
			else:
				tab(6)
				k = slow_input("Incorrect value. Please insert a number from 2 to 5: ")
	else: slow_print("- Select map size (from 2 to 5): " + str(k))
	m = map(generate = k)
	return m, seed

def compute_modifier(best_life, best_stamina, difficulty):
	"""
	description:
		Compute the modified parameters (stamina and life) 
		based on the difficulty setted.
	syntax:
		life, stamina = compute_modifier(best_life, best_stamina, difficulty)
	"""
	if difficulty == "easy":
		return [round(3 * best_life), round(3 * best_stamina)]
	elif difficulty == "hard":
		return [round(1.5 * best_life), round(1.5 * best_stamina)]

def generate_parameters(m):
	"""
	description:
		Generate the session parameters.
	syntax:
		gamemode, difficulty, best_life, best_stamina, best_path, life, stamina = generate_parameters(m)
	"""
	tab()
	gamemode = slow_input("- Select a gamemode (balanced/survivor/explorer): ")
	if notebook: print()
	while True:
		if gamemode in aliases_gamemodes:
			break
		else:
			tab(6)
			gamemode = slow_input("Incorrect value. Please select balanced, survivor or explorer: ")
			if notebook: print()
	gamemode = aliases_gamemodes[gamemode]
	parameters = m.get_parameters(gamemode)
	tab()
	difficulty = slow_input("- Select a difficulty (easy/hard): ")
	if notebook: print()
	while True:
		if difficulty in aliases_difficulties:
			break
		else:
			tab(6)
			difficulty = slow_input("Incorrect value. Please select one among easy, hard: ")
			if notebook: print()
	difficulty = aliases_difficulties[difficulty]
	tab(6)
	if difficulty == "easy":
		slow_print("The maximum available score is set to 500.")
	elif difficulty == "hard":
		slow_print("The maximum available score is set to 1000.")
	print("\n" + "                    -------------------------------------                    " + "\n")
	return [gamemode, difficulty] + parameters + compute_modifier(parameters[0], parameters[1], difficulty)

def intro_game(gamemode):
	"""
	description:
		Introduction for the game (based on the gamemode).
	syntax:
		window = intro_game(gamemode)
	"""
	slow_print("You wake up in a gloomy cave.")
	slow_print("You can't remember how you ended up here. You just feel that it is not safe.")
	if gamemode == "balanced":
		slow_print("You are scared but also curious in some sense.")
		slow_print("You are in an hostile territory and you're not sure that your energy will" + "\n" + "last until the end.")
		time.sleep(0.5)
		print("\n" + " ------                                                               ------ ")
		print("| Find a way out from this cave, battle some monsters but try not to waste  |" + "\n" + \
	    	"| your remaining energies.                                                  |")
		print(" ------                                                               ------ " + "\n")
		time.sleep(0.5)
	elif gamemode == "survivor":
		slow_print("You are badly injured and tired.")
		slow_print("You just want to come back home and rest, trying not to get into trouble.")
		time.sleep(0.5)
		print("\n" + " ------                                                               ------ ")
		print("| Escape from this cave as fast as possible, trying to battle as few        |" + "\n" + \
			"| monsters as you can.                                                      |")
		print(" ------                                                               ------ " + "\n")
		time.sleep(0.5)
	elif gamemode == "explorer":
		slow_print("You are extremely curious and ready to fight.")
		slow_print("You want to explore the cave and battle, but you have to pay attention" + "\n" + "because you can't rest here.")
		time.sleep(0.5)
		print("\n" + " ------                                                               ------ ")
		print("| Explore this cave and gain experience trying to battle as many monsters   |" + "\n" + \
			"| as you can.                                                               |")
		print(" ------                                                               ------ " + "\n")
		time.sleep(0.5)
	slow_print("Looking in your pockets you find a compass, a torch, a piece of paper and a" + "\n" + "pen.")
	slow_print("These items allow you to explore the cave sistematically, drawing a map of" + "\n" + "the visited areas.")
	slow_print("Unfortunately the torch is not very powerful hence you can only glimpse what" + "\n" + "surrounds you.")
	slow_print("You start by drawing your current position in the center of the paper." + "\n")
	if not(notebook):
		# setup window
		window = tk_window_setup()
		# click the cmd to select it
		from pywinauto.mouse import click
		click(button = "left", coords = (100, 100))
		return window
	else:
		return -1

def choose_direction(m, current_position):
	"""
	description:
		Choice of the direction to follow among the available possibilities.
	syntax:
		choose_direction(m, current_position)
	"""
	# create and print available_directions
	slow_print("It seems that the cave extends in the following directions:")
	available_edges = m.starting_edges(current_position)
	available_directions = {}
	for edge in available_edges:
		key = aliases_directions[m.diff_coordinates(edge[0], edge[1])]
		available_directions[key] = [edge[1], edge[2]]
		tab()
		slow_print("- " + key)
	# take the direction as input and check
	#	- it is valid alias
	#	- it is actually an available direction
	chosen_direction = slow_input("Insert one of them: ")
	if notebook: print()
	while True:
		if chosen_direction in aliases_directions:
			if aliases_directions[chosen_direction] in available_directions:
				chosen_direction = aliases_directions[chosen_direction]
				break
			else:
				chosen_direction = slow_input("It is impossible to go there. Try again: ")
				if notebook: print()
		else:
			chosen_direction = slow_input("Incorrect direction. Try again: ")
			if notebook: print()
	print()
	return available_directions[chosen_direction]

def out_of_resources(resource, counter_games):
	"""
	description:
		The function is triggered when the player runs out of stamina or life and 
		allows to choose whether to keep playing or not (if possible).
	syntax:
		flag = out_of_resources(resource, counter_games)
	"""
	if resource == "life":
		slow_print("The monster has defeated you. You ran out of life points.")
	elif resource == "stamina":
		slow_print("You are exhausted. You ran out of stamina points.")
		slow_print("You are so weary that you cannot even draw the last path you traversed.")
	slow_print("You faint. ", newline = "")
	time.sleep(0.5)
	if counter_games == 4:
		slow_print("You are trapped in this cave for more than 2 days.")
		slow_print("You never drank water and you are starving. You ran out of attempts.")
		slow_print("Game over." + "\n")
		return False
	slow_print("You wake up some hours later in the starting area.")
	slow_print("Someone rescued you and brought you back. All your stuff is beside you." + "\n")
	flag = decide("Do you want to try again?")
	if flag:
		slow_print("The map you drew is still here, it could be useful." + "\n")
	else:
		slow_print("Game over." + "\n")
	return flag

def entity_encountered(m, current_position, past_position, power):
	"""
	description:
		The function is triggered when the player encounter an entity.
	syntax:
		battle = entity_encountered(m, current_position, past_position, power)
	"""
	# if you can go back to the previous position
	#	then you can choose if you want to battle the entity
	# else
	#	you are forced to battle the entity
	slow_print("You encountered a monster.")
	if power == 1:
		print_entity(1)
		slow_print("It does not seem very smart. It doesn't even notice you (1 life point).")
	if power == 2:
		print_entity(2)
		slow_print("It has seen you and is approaching you threateningly (2 life points).")
	if power == 3:
		print_entity(3)
		slow_print("It is huge and follows all your moves. Pay attention (3 life points).")
	if m.check_adjacent(current_position, past_position):
		battle = decide("Do you want to battle against it?")
	else:
		slow_print("You can't escape. You have to engage in a battle.")
		battle = True
	time.sleep(0.5)
	if not(battle):
		slow_print("You manage to escape by going back to the previous area." + "\n")
	return battle

def start_game(m, life, stamina, gamemode, seed = -1, save = []):
	"""
	description:
		Start the game after the preliminary choices
		(map generation and parameter setup).
	syntax:
		bool = start_game(m, life, stamina, gamemode, seed)
	"""
	# intro to the game
	window = intro_game(gamemode)
	canvas = None
	counter_games = 0
	visited_nodes = [0]
	visited_edges = []
	flag = True
	while flag:
		counter_games += 1
		# initialization of the parameters for the current game
		current_position = 0
		current_life = life
		current_stamina = stamina
		active_entities = m.get_entities().copy()
		# starting the map
		canvas = m.print_map(window, [current_life, current_stamina, counter_games], 
			canvas = canvas, seed = seed, update = [visited_nodes, visited_edges, current_position], active_entities = active_entities,
			save = save)
		# each iteration corresponds to an action in the game
		while True:
			# move
			past_position = current_position
			current_position, weight = choose_direction(m, current_position)
			crossed_edge = [past_position, current_position, weight]
			# stamina update / out of stamina
			current_stamina -= weight
			if current_stamina < 0:
				flag = out_of_resources("stamina", counter_games)
				break
			# update list of visited nodes/edges
			if current_position not in visited_nodes:
				visited_nodes.append(current_position)
			if crossed_edge not in visited_edges:
				visited_edges.append(crossed_edge)
			# update map
			canvas = m.print_map(window, [current_life, current_stamina, counter_games], 
				canvas = canvas, seed = seed, update = [visited_nodes, visited_edges, current_position], active_entities = active_entities,
				save = save)
			# entity encountered
			if current_position in active_entities:
				battle = entity_encountered(m, current_position, past_position, active_entities[current_position])
				if battle:
					# life update / out of life
					current_life -= active_entities[current_position]
					if current_life < 0:
						flag = out_of_resources("life", counter_games)
						break
					else:
						win_battle(active_entities[current_position])
					del active_entities[current_position]
				else:
					# you go back to the previous position
					current_position, past_position = past_position, current_position
					crossed_edge = [past_position, current_position, weight]
					# stamina update / out of stamina
					current_stamina -= weight
					if current_stamina < 0:
						flag = out_of_resources("stamina", counter_games)
						break
					if crossed_edge not in visited_edges:
						visited_edges.append(crossed_edge)
				# update map
				canvas = m.print_map(window, [current_life, current_stamina, counter_games], 
					canvas = canvas, seed = seed, update = [visited_nodes, visited_edges, current_position], active_entities = active_entities,
					save = save)
			# win
			if current_position == m.get_end():
				flag = False
				win_game()
				break
	return window, canvas, current_life, current_stamina, counter_games

def compute_score(life, current_life, best_life, stamina, current_stamina, best_stamina, counter_games, gamemode, difficulty):
	"""
	description:
		Compute the score of the current session.
	syntax:
		score = compute_score(life, current_life, best_life, stamina, current_stamina, best_stamina, counter_games, gamemode, difficulty)
	"""
	# reward_life
	reward_life = min(round((current_life / (life - best_life)) * 100), 100) if best_life != 0 else 100
	# reward_experience
	# 	best_experience = best_life
	reward_experience = min(round(((life - current_life) / best_life) * 100), 100) if best_life != 0 else 100
	# bonus_life
	bonus_life = 0
	n_life = 3
	if abs((life - current_life) - best_life) <= n_life:
		bonus_life = round(2 ** ((n_life + 1) - abs((life - current_life) - best_life)) / 2 ** (n_life + 1) * 100)
	# reward_stamina
	reward_stamina = min(round((current_stamina / (stamina - best_stamina)) * 100), 100)
	# bonus_stamina
	bonus_stamina = 0
	n_stamina = 5
	if abs((stamina - current_stamina) - best_stamina) <= n_stamina:
		bonus_stamina = round(2 ** ((n_stamina + 1) - abs((stamina - current_stamina) - best_stamina)) / 2 ** (n_stamina + 1) * 100)	
	# bonus_games
	bonus_games = (5 - counter_games) * 25
	# score
	if gamemode == "balanced":
		score = round(reward_life / 2 + reward_experience / 2) + bonus_life + reward_stamina + bonus_stamina + bonus_games
	elif gamemode == "survivor":
		score = reward_life + bonus_life + reward_stamina + bonus_stamina + bonus_games
	elif gamemode == "explorer":
		score = reward_experience + bonus_life + reward_stamina + bonus_stamina + bonus_games
	if difficulty == "easy":
		return score
	else:
		return score * 2

def show_results(life, current_life, best_life, stamina, current_stamina, best_stamina, counter_games, gamemode, difficulty):
	"""
	description:
		Show the results of the session.
	syntax:
		show_results(life, current_life, best_life, stamina, current_stamina, best_stamina, counter_games, gamemode, difficulty)
	"""
	print("                    -------------------------------------                    " + "\n")
	slow_print("Score")
	tab()
	slow_print("- Consumed stamina: " + str(stamina - current_stamina) + "/" + str(stamina))
	tab(6)
	slow_print("Optimal stamina consumption: " + str(best_stamina))
	# gained experience = consumed life
	tab()
	slow_print("- Gained experience: " + str(life - current_life))
	tab(6)
	slow_print("Optimal gained experience: " + str(best_life))
	# if win
	if current_stamina >= 0 and current_life >= 0:
		# compute score
		score = compute_score(life, current_life, best_life, stamina, current_stamina, best_stamina, counter_games, gamemode, difficulty)
		optimal_score = compute_score(life, life - best_life, best_life, stamina, stamina - best_stamina, best_stamina, 1, gamemode, difficulty)
		tab()
		slow_print("- Score: " + str(score) + "/" + str(optimal_score))
	print("\n" + "                    -------------------------------------                    " + "\n")

def show_optimal_solution(m, window, canvas, seed, best_life, best_stamina, best_path, save = []):
	"""
	description:
		Show the optimal solution for the current session on the window.
	syntax:
		show_optimal_solution(m, window, canvas, seed, best_life, best_stamina, best_path)
	"""
	flag = decide("Do you want to visualize the optimal solution for the game?")
	if flag:
		canvas = m.print_map(window, [best_life, best_stamina, 1],
			canvas = canvas, seed = seed, path = best_path,
			save = save)
	return canvas
		
def rl_solution(m, window, canvas, seed, stamina, life, best_stamina, best_life, gamemode, difficulty, save = []):
	"""
	description:
		Show the solution created by a reinforcement learning (rl) algorithm.
	syntax:
		rl_solution(m, window, canvas, seed, stamina, life, best_stamina, best_life, gamemode, difficulty)
	"""
	if gamemode in ["survivor", "explorer"]:
		flag = decide("\n" + "Do you want to see a reinforcement learning algorithm play the last game?")
		if flag:
			slow_print("Computing the solution...")
			out = False
			n_iteration = 0
			while not(out) and n_iteration < 100:
				out = on_policy_first_visit_mc_control(m, gamemode)
				if out:
					consumed_stamina, consumed_life, path = out
					out = (consumed_stamina <= stamina) and (consumed_life <= life)
				n_iteration += 1
			if n_iteration >= 100:
				slow_print("Unfortunately it seems that the algorithm failed." + "\n" + \
	       			"Sometimes it happens with the learning algorithms." + "\n" + \
					"Maybe the map was too difficult.")
				return
			for index in range(len(path)):
				current_path = path[:(index + 1)]
				current_stamina, current_life = m.get_stamina_life(current_path)
				if not(notebook): 
					tk_sleep(1.5, window)
				else:
					time.sleep(1.5)
				canvas = m.print_map(window, [life - current_life, stamina - current_stamina, 1],
					canvas = canvas, seed = seed, path = current_path,
					save = save)
			slow_print("Score")
			tab()
			slow_print("- Consumed stamina: " + str(current_stamina) + "/" + str(stamina))
			tab()
			slow_print("- Gained experience: " + str(current_life))
			score = compute_score(life, life - current_life, best_life, stamina, stamina - current_stamina, best_stamina, 1, gamemode, difficulty)
			optimal_score = compute_score(life, life - best_life, best_life, stamina, stamina - best_stamina, best_stamina, 1, gamemode, difficulty)
			tab()
			slow_print("- Score: " + str(score) + "/" + str(optimal_score))

def play_again():
	"""
	description:
		The function is triggered when the game ends and the player has to
		decide whether to play again or not.
	syntax:
		restart = play_again()
	"""
	restart = decide("\n" + "Do you want to play again on another map?")
	print("\n" + "-----------------------------------------------------------------------------" + "\n")
	return restart

def main(seed = -1, bound = -1):
	# optional parameter
	#	if save == [0] then every canvas generated during the game is stored in the folder maps/game (debug mode)
	#	elif save = [] then nothing happens
	save = [] 
	print_title()
	while True:
		# generate map
		m, seed = generate_map(seed = seed, k = bound)
		# generate parameters
		gamemode, difficulty, best_life, best_stamina, best_path, life, stamina = generate_parameters(m)
		# start the game
		window, canvas, current_life, current_stamina, counter_games = start_game(m, life, stamina, gamemode, seed, save)
		# end of the game
		show_results(life, current_life, best_life, stamina, current_stamina, best_stamina, counter_games, gamemode, difficulty)
		# show optimal solution
		canvas = show_optimal_solution(m, window, canvas, seed, best_life, best_stamina, best_path, save)
		# let an rl algorithm play the same game
		rl_solution(m, window, canvas, seed, stamina, life, best_stamina, best_life, gamemode, difficulty, save)
		# play again
		restart = play_again()
		if restart:
			if not(notebook):
				window.destroy()
		else:
			break

# notebook environment
notebook = False

if __name__ == "__main__":
	main()