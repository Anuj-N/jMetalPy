#!/usr/bin/python
# -*- coding: utf-8 -*-
from math import sqrt, pow, sin, pi, cos

from jmetal.core.problem import FloatProblem
from jmetal.core.solution import FloatSolution

import math
import copy
import random

class Individual:
    """A data structure to store objective values together with the solution.

    Some methods of the problem classes expect objects with the two
    attributes `phenome` and `objective_values`. The exact type of these
    objects is irrelevant, but this class would be the obvious fit. The
    term 'phenome' stems from biology and means the whole set of phenotypic
    entities, in other words the form of appearance, of an animate being.
    So, it matches quite well as description of what is evaluated by the
    objective function.

    """
    def __init__(self, phenome=None, objective_values=None):
        """Constructor.

        Parameters
        ----------
        phenome : object, optional
            An arbitrary object which somehow can be evaluated by an
            objective function.
        objective_values : float or list, optional
            A single float or a list of objective values.

        """
        self.phenome = phenome
        self.objective_values = objective_values


class BoundConstraintError(ValueError):
    """Used to report violations of bound constraints.

    Inherits from :class:`ValueError`.

    """
    def __init__(self, value, min_bound, max_bound, variable_name=None):
        bounds = "[" + str(min_bound) + ", " + str(max_bound) + "]"
        if variable_name is None:
            message = "Value " + str(value) + " out of bounds " + bounds
        else:
            message = "Variable " + variable_name + " (=" + str(value) + ") out of bounds " + bounds
        ValueError.__init__(self, message)


def correct_to_01(a, epsilon=1.0e-10):
	"""Sets values in [-epsilon, 0] to 0 and in [1, 1 + epsilon] to 1.

	Assumption is that these deviations result from rounding errors.

	"""

	assert epsilon >= 0.0
	min_value = 0.0
	max_value = 1.0
	min_epsilon = min_value - epsilon
	max_epsilon = max_value + epsilon
	if a <= min_value and a >= min_epsilon:
		return min_value
	elif a >= max_value and a <= max_epsilon:
		return max_value
	else:
		return a


def vector_in_01(x):
	"""Returns True if all elements are in [0, 1]."""

	for element in x:
		if element < 0.0 or element > 1.0:
			return False
	return True


def shape_args_ok(x, m):
	"""Helper function."""

	return vector_in_01(x) and m >= 1 and m <= len(x)


def calculate_f(
	d,
	x,
	h,
	s,
	):
	"""Helper function."""

	assert d > 0.0
	assert vector_in_01(x)
	assert vector_in_01(h)
	assert len(x) == len(h)
	assert len(h) == len(s)
	result = []
	for i in range(0, len(h)):
		assert s[i] > 0.0
		result.append(d * x[-1] + s[i] * h[i])
	return result


def b_poly(y, alpha):
	"""Transformation function."""

	assert y >= 0.0
	assert y <= 1.0
	assert alpha > 0.0
	assert alpha != 1.0
	return correct_to_01(math.pow(y, alpha))


def b_flat(
	y,
	a,
	b,
	c,
	):
	"""Transformation function."""

	assert y >= 0.0
	assert y <= 1.0
	assert a >= 0.0
	assert a <= 1.0
	assert b >= 0.0
	assert b <= 1.0
	assert c >= 0.0
	assert c <= 1.0
	assert b < c
	assert b != 0.0 or a == 0.0
	assert b != 0.0 or c != 1.0
	assert c != 1.0 or a == 1.0
	assert c != 1.0 or b != 0.0
	tmp1 = min(0.0, math.floor(y - b)) * a * (b - y) / b
	tmp2 = min(0.0, math.floor(c - y)) * (1.0 - a) * (y - c) / (1.0 - c)
	return correct_to_01(a + tmp1 - tmp2)


def b_param(
	y,
	u,
	a,
	b,
	c,
	):
	"""Transformation function."""

	assert y >= 0.0
	assert y <= 1.0
	assert u >= 0.0
	assert u <= 1.0
	assert a > 0.0
	assert a < 1.0
	assert b > 0.0
	assert b < c
	v = a - (1.0 - 2.0 * u) * abs(math.floor(0.5 - u) + a)
	return correct_to_01(math.pow(y, b + (c - b) * v))


def s_linear(y, a):
	"""Transformation function."""

	assert y >= 0.0
	assert y <= 1.0
	assert a > 0.0
	assert a < 1.0
	return correct_to_01(abs(y - a) / abs(math.floor(a - y) + a))


def s_decept(
	y,
	a,
	b,
	c,
	):
	"""Transformation function."""

	assert y >= 0.0
	assert y <= 1.0
	assert a > 0.0
	assert a < 1.0
	assert b > 0.0
	assert b < 1.0
	assert c > 0.0
	assert c < 1.0
	assert a - b > 0.0
	assert a + b < 1.0
	tmp1 = math.floor(y - a + b) * (1.0 - c + (a - b) / b) / (a - b)
	tmp2 = math.floor(a + b - y) * (1.0 - c + (1.0 - a - b) / b) / (1.0
			- a - b)
	return correct_to_01(1.0 + (abs(y - a) - b) * (tmp1 + tmp2 + 1.0
						 / b))


def s_multi(
	y,
	a,
	b,
	c,
	):
	"""Transformation function."""

	assert y >= 0.0
	assert y <= 1.0
	assert a >= 1
	assert b >= 0.0
	assert (4.0 * a + 2.0) * math.pi >= 4.0 * b
	assert c > 0.0
	assert c < 1.0
	tmp1 = abs(y - c) / (2.0 * (math.floor(c - y) + c))
	tmp2 = (4.0 * a + 2.0) * math.pi * (0.5 - tmp1)
	result = (1.0 + math.cos(tmp2) + 4.0 * b * math.pow(tmp1, 2.0)) \
		/ (b + 2.0)
	return correct_to_01(result)


def r_sum(y, w):
	"""Transformation function."""

	assert len(y) != 0
	assert len(w) == len(y)
	assert vector_in_01(y)
	numerator = 0.0
	denominator = sum(w)
	for i in range(len(y)):
		assert w[i] > 0.0
		numerator += w[i] * y[i]
	return correct_to_01(numerator / denominator)


def r_nonsep(y, a):
	"""Transformation function."""

	assert len(y) != 0
	assert vector_in_01(y)
	assert a >= 1
	assert a <= len(y)
	assert len(y) % a == 0
	numerator = 0.0
	for j in range(len(y)):
		numerator += y[j]
		for k in range(0, a - 1):
			numerator += abs(y[j] - y[(j + k + 1) % len(y)])
	tmp = math.ceil(a / 2.0)
	denominator = len(y) * tmp * (1.0 + 2.0 * a - 2.0 * tmp) / a
	return correct_to_01(numerator / denominator)


def linear(x, m):
	"""Shape function."""

	assert shape_args_ok(x, m)
	result = 1.0
	for i in range(1, len(x) - m + 1):
		result *= x[i - 1]
	if m != 1:
		result *= 1 - x[len(x) - m]
	return correct_to_01(result)


def convex(x, m):
	"""Shape function."""

	assert shape_args_ok(x, m)
	result = 1.0
	for i in range(1, len(x) - m + 1):
		result *= 1.0 - math.cos(x[i - 1] * math.pi / 2.0)
	if m != 1:
		result *= 1.0 - math.sin(x[len(x) - m] * math.pi / 2.0)
	return correct_to_01(result)


def concave(x, m):
	"""Shape function."""

	assert shape_args_ok(x, m)
	result = 1.0
	for i in range(1, len(x) - m + 1):
		result *= math.sin(x[i - 1] * math.pi / 2.0)
	if m != 1:
		result *= math.cos(x[len(x) - m] * math.pi / 2.0)
	return correct_to_01(result)


def mixed(x, a, alpha):
	"""Shape function."""

	assert vector_in_01(x)
	assert len(x) != 0
	assert a >= 1
	assert alpha > 0.0
	tmp = 2.0 * a * math.pi
	result = math.pow(1.0 - x[0] - math.cos(tmp * x[0] + math.pi / 2.0)
					  / tmp, alpha)
	return correct_to_01(result)


def disc(
	x,
	a,
	alpha,
	beta,
	):
	"""Shape function."""

	assert vector_in_01(x)
	assert len(x) != 0
	assert a >= 1
	assert alpha > 0.0
	assert beta > 0.0
	tmp1 = a * math.pow(x[0], beta) * math.pi
	result = 1.0 - math.pow(x[0], alpha) * math.pow(math.cos(tmp1), 2.0)
	return correct_to_01(result)


class Shape:

	"""Abstract base class for shape objects."""

	@staticmethod
	def create_a(m, is_degenerate):
		assert m >= 2
		if is_degenerate:
			a = [0] * (m - 1)
			a[0] = 1
			return a
		else:
			return [1] * (m - 1)

	@staticmethod
	def normalize_z(z, z_max):
		result = []
		for i in range(0, len(z)):
			assert z[i] >= 0.0
			assert z[i] <= z_max[i]
			assert z_max[i] > 0.0
			result.append(z[i] / z_max[i])
		return result

	@staticmethod
	def calculate_x(tp, a):
		assert vector_in_01(tp)
		assert len(tp) != 0
		assert len(a) == len(tp) - 1
		result = []
		for i in range(0, len(tp) - 1):
			assert a[i] == 0 or a[i] == 1
			tmp1 = max(tp[-1], a[i])
			result.append(tmp1 * (tp[i] - 0.5) + 0.5)
		result.append(tp[-1])
		return result

	@staticmethod
	def calculate_f(x, h):
		assert vector_in_01(x)
		assert vector_in_01(h)
		assert len(x) == len(h)
		s = []
		for m in range(1, len(h) + 1):
			s.append(m * 2.0)
		return calculate_f(1.0, x, h, s)

	def __call__(self, tp):
		raise NotImplementedError('Abstract class `Shape` is not callable.'
								  )


class WFG(FloatProblem):

	"""The base class for WFG problems."""

	def __init__(
		self,
		objective_function,
		number_of_objectives,
		number_of_variables,
		k,
		**kwargs
		):

		assert number_of_objectives > 1
		assert k >= 1 and k < number_of_variables
		assert k % (number_of_objectives - 1) == 0
		self.max_objectives = None
		self.min_objectives = None
		if number_of_objectives == 3:
			self.max_objectives = [10.0, 10.0, 10.0]
			self.min_objectives = [0.0, 0.0, 0.0]
		elif number_of_objectives == 5:
			self.max_objectives = [10.0, 10.0, 10.0, 10.0, 12.0]
			self.min_objectives = [0.0, 0.0, 0.0, 0.0, 0.0]
		self.min_bounds = [0.0] * number_of_variables
		self.max_bounds = [2.0 * i for i in range(1, number_of_variables + 1)]
		self.lower_bound = number_of_variables * [0.0]
		self.upper_bound = number_of_variables * [1.0]

		self.k = k
		self.number_of_variables = number_of_variables
		self.is_deterministic = True
		self.do_maximize = False
		if number_of_objectives <= 4:
			self.default_reference_set_size = 500
		else:
			self.default_reference_set_size = 1000

	@staticmethod
	def args_ok(z, k, m):
		return k >= 1 and k < len(z) and m >= 2 and k % (m - 1) == 0

	def normalize_z(self, z):
		result = []
		for i in range(0, len(z)):
			if z[i] < self.min_bounds[i] or z[i] > self.max_bounds[i]:
				raise BoundConstraintError(z[i], self.min_bounds[i],
						self.max_bounds[i], 'z_' + str(i))
			result.append(z[i] / self.max_bounds[i])
		return result

	@property
	def m(self):
		"""The number of objective functions."""

		return self.number_of_objectives

	def evaluate(self, solution) :
		solution.objectives = self.objective_function(solution.variables)
		return solution



class WFG1(WFG):
	"""The WFG1 problem."""

	class WFG1Shape(Shape):
		def __call__(self, tp):
			assert vector_in_01(tp)
			assert len(tp) >= 2
			a = self.create_a(len(tp), False)
			x = self.calculate_x(tp, a)
			h = []
			for m in range(1, len(tp)):
				h.append(convex(x, m))
			h.append(mixed(x, 5, 1.0))
			return self.calculate_f(x, h)

	def __init__(self, k, number_of_variables, number_of_objectives, **kwargs) :
		super(WFG1, self).__init__(self.objective_function, number_of_objectives, number_of_variables, k, **kwargs)

		self.number_of_variables = number_of_variables
		self.number_of_objectives = number_of_objectives
		self.number_of_constraints = 0
		self.obj_directions = [self.MINIMIZE, self.MINIMIZE]
		self.obj_labels = ['x', 'y']

		self.shape = self.WFG1Shape()

	@staticmethod
	def transition1(y, k):
		n = len(y)
		assert vector_in_01(y)
		assert k >= 1
		assert k < n
		t = y[0:k]
		for i in range(k, n):
			t.append(s_linear(y[i], 0.35))
		return t

	@staticmethod
	def transition2(y, k):
		n = len(y)
		assert vector_in_01(y)
		assert k >= 1
		assert k < n
		t = y[0:k]
		for i in range(k, n):
			t.append(b_flat(y[i], 0.8, 0.75, 0.85))
		return t

	@staticmethod
	def transition3(y):
		n = len(y)
		assert vector_in_01(y)
		t = []
		for i in range(0, n):
			t.append(b_poly(y[i], 0.02))
		return t

	@staticmethod
	def transition4(y, k, m):
		n = len(y)
		assert vector_in_01(y)
		assert k >= 1
		assert k < n
		assert m >= 2
		assert k % (m - 1) == 0
		w = []
		for i in range(1, n + 1):
			w.append(2.0 * i)
		t = []
		for i in range(1, m):
			head = int((i - 1) * k / (m - 1))
			tail = int(i * k / (m - 1))
			y_sub = y[head:tail]
			w_sub = w[head:tail]
			t.append(r_sum(y_sub, w_sub))
		y_sub = y[k:n]
		w_sub = w[k:n]
		t.append(r_sum(y_sub, w_sub))
		return t

	def objective_function(self, phenome):
		assert len(phenome) == self.number_of_variables
		assert self.args_ok(phenome, self.k, self.m)
		y = self.normalize_z(phenome)
		y = self.transition1(y, self.k)
		y = self.transition2(y, self.k)
		y = self.transition3(y)
		y = self.transition4(y, self.k, self.m)
		return self.shape(y)

	def objective_function(self, phenome):
		assert len(phenome) == self.number_of_variables
		assert self.args_ok(phenome, self.k, self.m)
		y = self.normalize_z(phenome)
		y = self.transition1(y, self.k)
		y = self.transition2(y, self.k)
		y = self.transition3(y)
		y = self.transition4(y, self.k, self.m)
		return self.shape(y)

	def get_name(self):
		return 'WFG1'



class WFG2(WFG):
	"""The WFG2 problem."""

	class WFG2Shape(Shape):
		def __call__(self, tp):
			assert vector_in_01(tp)
			assert len(tp) >= 2
			a = self.create_a(len(tp), False)
			x = self.calculate_x(tp, a)
			h = []
			for m in range(1, len(tp)):
				h.append(convex(x, m))
			h.append(disc(x, 5, 1.0, 1.0))
			return self.calculate_f(x, h)

	def __init__(self, k, number_of_variables, number_of_objectives, **kwargs) :
		super(WFG2, self).__init__(self.objective_function, number_of_objectives, number_of_variables, k, **kwargs)
		self.number_of_variables = number_of_variables
		self.number_of_objectives = number_of_objectives
		self.number_of_constraints = 0
		self.obj_directions = [self.MINIMIZE, self.MINIMIZE]
		self.obj_labels = ['x', 'y']

		assert (number_of_variables - k) % 2 == 0
		self.shape = self.WFG2Shape()
		self.transition1 = WFG1.transition1


	@staticmethod
	def transition2(y, k):
		n = len(y)
		l = n - k
		assert vector_in_01(y)
		assert k >= 1
		assert k < n
		assert l % 2 == 0
		t = []
		for i in range(k):
			t.append(y[i])
		for i in range(k + 1, int(k + l / 2 + 1)):
			head = k + 2 * (i - k) - 2
			tail = k + 2 * (i - k)
			y_sub = y[head:tail]
			t.append(r_nonsep(y_sub, 2))
		return t


	@staticmethod
	def transition3(y, k, m):
		n = len(y)
		assert vector_in_01(y)
		assert k >= 1
		assert k < n
		assert m >= 2
		assert k % (m - 1) == 0
		w = [1.0] * n
		t = []
		for i in range(1, m):
			head = int((i - 1) * k / (m - 1))
			tail = int(i * k / (m - 1))
			y_sub = y[head:tail]
			w_sub = w[head:tail]
			t.append(r_sum(y_sub, w_sub))
		y_sub = y[k:n]
		w_sub = w[k:n]
		t.append(r_sum(y_sub, w_sub))
		return t

	def objective_function(self, phenome):
		assert len(phenome) == self.number_of_variables
		assert self.args_ok(phenome, self.k, self.m)
		assert (len(phenome) - self.k) % 2 == 0
		y = self.normalize_z(phenome)
		y = self.transition1(y, self.k)
		y = self.transition2(y, self.k)
		y = self.transition3(y, self.k, self.m)
		return self.shape(y)

	def get_name(self):
		return 'WFG2'


class WFG3(WFG):
	"""The WFG3 problem."""

	class WFG3Shape(Shape):
		def __call__(self, tp):
			assert vector_in_01(tp)
			assert len(tp) >= 2
			a = self.create_a(len(tp), True)
			x = self.calculate_x(tp, a)
			h = []
			for m in range(1, len(tp) + 1):
				h.append(linear(x, m))
			return self.calculate_f(x, h)

	def __init__(self, k, number_of_variables, number_of_objectives, **kwargs) :
		super(WFG3, self).__init__(self.objective_function, number_of_objectives, number_of_variables, k, **kwargs)
		self.number_of_variables = number_of_variables
		self.number_of_objectives = number_of_objectives
		self.number_of_constraints = 0
		self.obj_directions = [self.MINIMIZE, self.MINIMIZE]
		self.obj_labels = ['x', 'y']

		assert (number_of_variables - k) % 2 == 0
		self.shape = self.WFG3Shape()
		self.transition1 = WFG1.transition1
		self.transition2 = WFG2.transition2
		self.transition3 = WFG2.transition3


	def objective_function(self, phenome):
		assert len(phenome) == self.number_of_variables
		assert self.args_ok(phenome, self.k, self.m)
		assert (len(phenome) - self.k) % 2 == 0
		y = self.normalize_z(phenome)
		y = self.transition1(y, self.k)
		y = self.transition2(y, self.k)
		y = self.transition3(y, self.k, self.m)
		return self.shape(y)

	def get_name(self):
		return 'WFG3'


class WFG4(WFG):
	"""The WFG4 problem."""

	class WFG4Shape(Shape):
		def __call__(self, tp):
			assert vector_in_01(tp)
			assert len(tp) >= 2
			a = self.create_a(len(tp), False)
			x = self.calculate_x(tp, a)
			h = []
			for m in range(1, len(tp) + 1):
				h.append(concave(x, m))
			return self.calculate_f(x, h)

	def __init__(self, k, number_of_variables, number_of_objectives, **kwargs) :
		super(WFG4, self).__init__(self.objective_function, number_of_objectives, number_of_variables, k, **kwargs)
		self.number_of_variables = number_of_variables
		self.number_of_objectives = number_of_objectives
		self.number_of_constraints = 0
		self.obj_directions = [self.MINIMIZE, self.MINIMIZE]
		self.obj_labels = ['x', 'y']

		assert k % (number_of_objectives - 1) == 0
		self.shape = self.WFG4Shape()
		self.transition2 = WFG2.transition3


	@staticmethod
	def transition1(y):
		n = len(y)
		assert vector_in_01(y)
		t = []
		for i in range(0, n):
			t.append(s_multi(y[i], 30, 10, 0.35))
		return t


	def objective_function(self, phenome):
		assert len(phenome) == self.number_of_variables
		assert self.args_ok(phenome, self.k, self.m)
		y = self.normalize_z(phenome)
		y = self.transition1(y)
		y = self.transition2(y, self.k, self.m)
		return self.shape(y)

	def get_name(self):
		return 'WFG4'


class WFG5(WFG):
	"""The WFG5 problem."""

	def __init__(self, k, number_of_variables, number_of_objectives, **kwargs) :
		super(WFG5, self).__init__(self.objective_function, number_of_objectives, number_of_variables, k, **kwargs)
		self.number_of_variables = number_of_variables
		self.number_of_objectives = number_of_objectives
		self.number_of_constraints = 0
		self.obj_directions = [self.MINIMIZE, self.MINIMIZE]
		self.obj_labels = ['x', 'y']

		self.shape = WFG4.WFG4Shape()
		self.transition2 = WFG2.transition3


	@staticmethod
	def transition1(y):
		n = len(y)
		assert vector_in_01(y)
		t = []
		for i in range(0, n):
			t.append(s_decept(y[i], 0.35, 0.001, 0.05))
		return t


	def objective_function(self, phenome):
		assert len(phenome) == self.number_of_variables
		assert self.args_ok(phenome, self.k, self.m)
		y = self.normalize_z(phenome)
		y = self.transition1(y)
		y = self.transition2(y, self.k, self.m)
		return self.shape(y)

	def get_name(self):
		return 'WFG5'


class WFG6(WFG):
	"""The WFG6 problem."""

	def __init__(self, k, number_of_variables, number_of_objectives, **kwargs) :
		super(WFG6, self).__init__(self.objective_function, number_of_objectives, number_of_variables, k, **kwargs)
		self.number_of_variables = number_of_variables
		self.number_of_objectives = number_of_objectives
		self.number_of_constraints = 0
		self.obj_directions = [self.MINIMIZE, self.MINIMIZE]
		self.obj_labels = ['x', 'y']

		self.shape = WFG4.WFG4Shape()
		self.transition1 = WFG1.transition1


	@staticmethod
	def transition2(y, k, m):
		n = len(y)
		assert vector_in_01(y)
		assert k >= 1
		assert k < n
		assert m >= 2
		assert k % (m - 1) == 0
		t = []
		for i in range(1, m):
			head = int((i - 1) * k / (m - 1))
			tail = int(i * k / (m - 1))
			y_sub = y[head:tail]
			t.append(r_nonsep(y_sub, int(k / (m - 1))))
		y_sub = y[k:n]
		t.append(r_nonsep(y_sub, n - k))
		return t


	def objective_function(self, phenome):
		assert len(phenome) == self.number_of_variables
		assert self.args_ok(phenome, self.k, self.m)
		y = self.normalize_z(phenome)
		y = self.transition1(y, self.k)
		y = self.transition2(y, self.k, self.m)
		return self.shape(y)

	def get_name(self):
		return 'WFG6'


class WFG7(WFG):
	"""The WFG7 problem."""

	def __init__(self, k, number_of_variables, number_of_objectives, **kwargs) :
		super(WFG7, self).__init__(self.objective_function, number_of_objectives, number_of_variables, k, **kwargs)
		self.number_of_variables = number_of_variables
		self.number_of_objectives = number_of_objectives
		self.number_of_constraints = 0
		self.obj_directions = [self.MINIMIZE, self.MINIMIZE]
		self.obj_labels = ['x', 'y']

		self.shape = WFG4.WFG4Shape()
		self.transition2 = WFG1.transition1
		self.transition3 = WFG2.transition3


	@staticmethod
	def transition1(y, k):
		n = len(y)
		assert vector_in_01(y)
		assert k >= 1
		assert k < n
		w = [1.0] * n
		t = []
		for i in range(k):
			y_sub = y[i+1:n]
			w_sub = w[i+1:n]
			u = r_sum(y_sub, w_sub)
			t.append(b_param(y[i], u, 0.98/49.98, 0.02, 50))
		for i in range(k, n):
			t.append(y[i])
		return t

	def objective_function(self, phenome):
		assert len(phenome) == self.number_of_variables
		assert self.args_ok(phenome, self.k, self.m)
		y = self.normalize_z(phenome)
		y = self.transition1(y, self.k)
		y = self.transition2(y, self.k)
		y = self.transition3(y, self.k, self.m)
		return self.shape(y)

	def get_name(self):
		return 'WFG7'



class WFG8(WFG):
	"""The WFG8 problem."""

	def __init__(self, k, number_of_variables, number_of_objectives, **kwargs) :
		super(WFG8, self).__init__(self.objective_function, number_of_objectives, number_of_variables, k, **kwargs)
		self.number_of_variables = number_of_variables
		self.number_of_objectives = number_of_objectives
		self.number_of_constraints = 0
		self.obj_directions = [self.MINIMIZE, self.MINIMIZE]
		self.obj_labels = ['x', 'y']

		self.shape = WFG4.WFG4Shape()
		self.transition2 = WFG1.transition1
		self.transition3 = WFG2.transition3
		if number_of_objectives <= 4:
			self.default_reference_set_size = 500
		else:
			self.default_reference_set_size = 1000

	@staticmethod
	def transition1(y, k):
		n = len(y)
		assert vector_in_01(y)
		assert k >= 1
		assert k < n
		w = [1.0] * n
		t = y[0:k]
		for i in range(k, n):
			y_sub = y[0:i]
			w_sub = w[0:i]
			u = r_sum(y_sub, w_sub)
			t.append(b_param(y[i], u, 0.98 / 49.98, 0.02, 50))
		return t


	def objective_function(self, phenome):
		assert len(phenome) == self.number_of_variables
		assert self.args_ok(phenome, self.k, self.m)
		y = self.normalize_z(phenome)
		y = self.transition1(y, self.k)
		y = self.transition2(y, self.k)
		y = self.transition3(y, self.k, self.m)
		return self.shape(y)

	def get_name(self):
		return 'WFG8'



class WFG9(WFG):
	"""The WFG9 problem."""

	def __init__(self, k, number_of_variables, number_of_objectives, **kwargs) :
		super(WFG9, self).__init__(self.objective_function, number_of_objectives, number_of_variables, k, **kwargs)
		self.number_of_variables = number_of_variables
		self.number_of_objectives = number_of_objectives
		self.number_of_constraints = 0
		self.obj_directions = [self.MINIMIZE, self.MINIMIZE]
		self.obj_labels = ['x', 'y']

		self.shape = WFG4.WFG4Shape()
		self.transition3 = WFG6.transition2
		if number_of_objectives <= 4:
			self.default_reference_set_size = 500
		else:
			self.default_reference_set_size = 1000


	def optimal_solution(self, k, l, pos_params):
		"""Create one Pareto-optimal solution with given position parameters."""
		result = []
		result.extend(pos_params)
		result.extend([0.0] * l)
		# calculate the distance parameters
		result[k + l - 1] = 0.35
		for i in range(k + l - 2, k - 1, -1):
			result_sub = []
			for j in range(i + 1, k + l):
				result_sub.append(result[j])
			w = [1.0] * len(result_sub)
			tmp1 = r_sum(result_sub, w)
			result[i] = pow(0.35, pow(0.02 + 1.96 * tmp1, -1.0))
		# scale to the correct domains
		for i in range(k + l):
			result[i] *= 2.0 * (i + 1)
		ind = Individual()
		ind.phenome = result
		return ind


	@staticmethod
	def transition1(y):
		n = len(y)
		assert vector_in_01(y)
		w = [1.0] * n
		t = []
		for i in range(0, n - 1):
			y_sub = y[i+1:n]
			w_sub = w[i+1:n]
			u = r_sum(y_sub, w_sub)
			t.append(b_param(y[i], u, 0.98 / 49.98, 0.02, 50))
		t.append(y[-1])
		return t


	@staticmethod
	def transition2(y, k):
		n = len(y)
		assert vector_in_01(y)
		assert k >= 1
		assert k < n
		t = []
		for i in range(0, k):
			t.append(s_decept(y[i], 0.35, 0.001, 0.05))
		for i in range(k, n):
			t.append(s_multi(y[i], 30, 95, 0.35))
		return t


	def objective_function(self, phenome):
		assert len(phenome) == self.number_of_variables
		assert self.args_ok(phenome, self.k, self.m)
		y = self.normalize_z(phenome)
		y = self.transition1(y)
		y = self.transition2(y, self.k)
		y = self.transition3(y, self.k, self.m)
		return self.shape(y)

	def get_name(self):
		return 'WFG9'
