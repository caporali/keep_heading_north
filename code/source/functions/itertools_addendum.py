import itertools

def powerset(iterable):
	""" 
	description:
		Returns an iterator over the powerset of an iterable (list, tuple, etc...). 
		E.g. powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
	syntax:
		powerset(iterable)
	"""
	s = list(iterable)
	return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))