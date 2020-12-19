import copy
from . import chaosGen as cg
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List

from jmetal.core.problem import Problem
from jmetal.core.solution import Solution

R = TypeVar('R')

"""
.. module:: generator
   :platform: Unix, Windows
   :synopsis: Population generators implementation.

.. moduleauthor:: Antonio Benítez-Hidalgo <antonio.b@uma.es>
"""


class Generator(Generic[R], ABC):

	@abstractmethod
	def new(self, problem: Problem) -> R:
		pass


class RandomGenerator(Generator):

	def new(self, problem: Problem):
		return problem.create_solution()
		
class ChaoticGenerator(Generator):

	def __init__ (self, Np):
		self.Np, self.counter = Np, 0
		self.cgen = None
		self.cp = None

	def new(self, problem: Problem):
		if self.cgen is None :
			self.cgen = cg.Lorenz((self.Np, problem.number_of_variables), gens=1)
		if self.counter % self.Np == 0 :
			self.cp = self.cgen.chaosPoints(1)
			self.counter = 0
				
		ret = problem.create_blank_solution()
		ret.variables = [l + (u-l)*z for l, u, z in zip(problem.lower_bound, problem.upper_bound, self.cp[self.counter])]
		self.counter += 1
		return ret
			

class InjectorGenerator(Generator):

	def __init__(self, solutions: List[Solution]):
		super(InjectorGenerator, self).__init__()
		self.population = []

		for solution in solutions:
			self.population.append(copy.deepcopy(solution))

	def new(self, problem: Problem):
		if len(self.population) > 0:
			# If we have more solutions to inject, return one from the list
			return self.population.pop()
		else:
			# Otherwise generate a new solution
			solution = problem.create_solution()

		return solution
