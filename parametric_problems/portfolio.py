"""
Solve Portoflio problem for one year simulation
"""
from problems.portfolio import PortfolioExample


class PortfolioSimulation(object):
    def __init__(self, dimension, lambda_array):
        self.dimension = dimension
        self.lambda_array