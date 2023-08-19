import numpy as np

from functions.itertools_addendum import *

def init_parameters(m, gamemode):
	""" 
	description:
		Initialize the main parameters for the function on_policy_first_visit_mc_control.
		It also creates start and end.
	syntax:
		parameters, start, end = init_parameters(m, gamemode)
	"""
	# initialize the following main parameters
	# 	available_actions, proposed_actions, rewards, count_returns, returns, state_value, action_value
	available_actions, proposed_actions, rewards, count_returns, returns, state_value, action_value = {}, {}, {}, {}, {}, {}, {}
	if gamemode == "shortest_path":
		entities = {}
		value = 1
	else:
		entities = m.get_entities()
		value = 0
		for power in entities.values():
			value += power
	if gamemode in ["shortest_path", "survivor"]:
		states = m.get_vertices()
		for state in states: # state = vertex
			available_actions[state], count_returns[state], returns[state], state_value[state] = [], 0, 0, 0
			maximum = -np.inf
			for _, action, weight in m.starting_edges(state): # action = arrival_vertex
				available_actions[state].append(action)
				rewards[(state, action)] = -weight
				if action in entities:
					rewards[(state, action)] += -20 * entities[action]
				if rewards[(state, action)] > maximum:
					maximum = rewards[(state, action)]
					proposed_actions[state] = action
				action_value[(state, action)] = -np.inf
		state_value[m.get_end()] = 100 * value
		end = [m.get_end()]
		start = 0
	elif gamemode == "explorer":
		states = []
		for active_entities in powerset(list(entities.keys())):
			for vertex in m.get_vertices():
				states.append((vertex, active_entities))
		for state in states:
			available_actions[state], count_returns[state], returns[state], state_value[state] = [], 0, 0, 0
			maximum = -np.inf
			for _, arrival_vertex, weight in m.starting_edges(state[0]):
				if arrival_vertex not in state[1]: # state[1] = active_entities for the state
					action = (arrival_vertex, state[1])
				else:
					new_active_entities = tuple([x for x in state[1] if x != arrival_vertex])
					action = (arrival_vertex, new_active_entities)
				available_actions[state].append(action)
				rewards[(state, action)] = -weight
				if arrival_vertex in state[1]:
					rewards[(state, action)] += +20 * entities[arrival_vertex]
				if rewards[(state, action)] > maximum:
					maximum = rewards[(state, action)]
					proposed_actions[state] = action
				action_value[(state, action)] = -np.inf
		end = []
		for active_entities in powerset(entities):
			state_value[(m.get_end(), active_entities)] = 100 * value
			end.append((m.get_end(), active_entities))
		start = (0, tuple(entities.keys()))
	return [available_actions, proposed_actions, rewards, count_returns, returns, state_value, action_value], start, end

def eps_greedy_policy(state, available_actions, proposed_action, eps):
	""" 
	description:
		Implementation of the epsilon-greedy policy.
	syntax:
		action = eps_greedy_policy(state, available_actions, proposed_action, eps)
	"""
	p = np.random.random()
	if p < (1 - eps) and proposed_action is not None:
		return proposed_action
	else:
		return available_actions[state][np.random.choice(len(available_actions[state]))]
 
def policy_prediction_and_improvement(available_actions, proposed_actions, rewards, count_returns, returns, state_value, action_value,
		start, end, eps):
	""" 
	description:
		Main loop of the function on_policy_first_visit_mc_control.
		It is divided in 3 phases:
		- generation of an episode (following the epsilon-greedy policy);
		- prediction phase;
		- improvement phase.
	syntax:
		policy_prediction_and_improvement(available_actions, proposed_actions, rewards, count_returns, returns, state_value, action_value,
			start, end, eps)
	"""
	# generate an episode
	#	initial state
	state = start
	episode = []
	episode_states = []
	#	max_iteration: maximum number of iteration, it is necessary to guarantee the termination of the function
	max_iteration = 0
	#	loop until reaching the end or reaching max_iteration
	while state not in end and max_iteration < 1000:
		action = eps_greedy_policy(state, available_actions, proposed_actions[state], eps)
		episode.append((state, action))
		episode_states.append(state)
		state = action
		max_iteration += 1
	# prediction phase
	#	update returns, action_value
	total_return = 0
	for index in range(len(episode)):
		state, action = episode[-(index + 1)]
		total_return = total_return + rewards[(state, action)]
		if state not in episode_states[:-(index + 1)]:
			count_returns[state] += 1
			returns[state] += total_return
			state_value[state] = returns[state] / count_returns[state]
		# improvement phase
		action_value[(state, action)] = state_value[action] + rewards[(state, action)]
	for state in episode_states:
		action_value_state = {}
		for action in available_actions[state]:
			action_value_state[action] = action_value[(state, action)]
		#	proposed_actions[state] = argmax_{action} action_value[(state, action)]
		proposed_actions[state] = max(action_value_state, key = action_value_state.get)

def on_policy_first_visit_mc_control(m, gamemode):
	""" 
	description:
		On-policy first-visit MC control algorithm with epsilon-greedy policy.
		If the algorithm does not find a path it returns False, otherwise
		it returns a triple stamina, life, path.
	syntax:
		out = on_policy_first_visit_mc_control(m, gamemode)
	"""
	# init phase
	parameters, start, end = init_parameters(m, gamemode)
	available_actions, proposed_actions, rewards, count_returns, returns, state_value, action_value = parameters
	# control phase
	eps = 0.75
	for _ in range(1000):
		policy_prediction_and_improvement(available_actions, proposed_actions, rewards, count_returns, returns, state_value, action_value,
			start, end, eps)
	# creation of the final path
	path = [0]
	state = start
	max_iteration = 0
	while state not in end and max_iteration < 100:
		state = proposed_actions[state]
		if type(state) is tuple: # = if gamemode == "explorer"
			path.append(state[0])
		else:
			path.append(state)
		max_iteration += 1
	if max_iteration < 100:
		stamina, life = m.get_stamina_life(path)
		return stamina, life, path
	else:
		return False