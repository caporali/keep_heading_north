"""
description:
	Global dictionaries which map some keywords to others.
"""
aliases_directions = {
	"north": "north", (0, 1): "north", "n": "north", "": "north",
	"north-east": "north-east", (1, 1): "north-east", "ne": "north-east",
	"east": "east", (1, 0): "east", "e": "east",
	"south-east": "south-east", (1, -1): "south-east", "se": "south-east",
	"south": "south", (0, -1): "south", "s": "south",
	"south-west": "south-west", (-1, -1): "south-west", "sw": "south-west",
	"west": "west", (-1, 0): "west", "w": "west",
	"north-west": "north-west", (-1, 1): "north-west", "nw": "north-west"
}
aliases_yes_no = {
	"yes": "yes", "y": "yes", "": "yes",
	"no": "no", "n": "no"
}
aliases_size_parameters = {
	"2": "2", "": "2",
	"3": "3",
	"4": "4",
	"5": "5"
}
aliases_gamemodes = {
	"balanced": "balanced", "b": "balanced", "1": "balanced", "": "balanced", 
	"survivor": "survivor", "s": "survivor", "2": "survivor",
	"explorer": "explorer", "e": "explorer", "3": "explorer"
}
aliases_difficulties = {
	"easy": "easy", "e": "easy", "": "easy",
	"hard": "hard", "h": "hard"
}