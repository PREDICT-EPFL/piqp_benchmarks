import numpy as np
import piqp
from . import statuses as s
from .results import Results
from utils.general import is_qp_solution_optimal


class PIQPSolver(object):

    STATUS_MAP = {piqp.PIQP_SOLVED: s.OPTIMAL,
                  piqp.PIQP_MAX_ITER_REACHED: s.MAX_ITER_REACHED,
                  piqp.PIQP_PRIMAL_INFEASIBLE: s.PRIMAL_INFEASIBLE,
                  piqp.PIQP_DUAL_INFEASIBLE: s.DUAL_INFEASIBLE}

    def __init__(self, settings={}):
        '''
        Initialize solver object by setting require settings
        '''
        self._settings = settings

    @property
    def settings(self):
        """Solver settings"""
        return self._settings

    def solve(self, example):
        '''
        Solve problem

        Args:
            problem: problem structure with QP matrices

        Returns:
            Results structure
        '''
        problem = example.qp_problem
        settings = self._settings.copy()
        high_accuracy = settings.pop('high_accuracy', None)

        # Setup PIQP
        m = piqp.SparseSolver()
        for param, value in settings.items():
            if hasattr(m.settings, param):
                setattr(m.settings, param, value)

        m.setup(problem['P'], problem['q'],
                problem['A_eq'], problem['b'],
                problem['G'], problem['h'],
                problem['xl'], problem['xu'])

        # Solve
        m.solve()
        status = self.STATUS_MAP.get(m.result.info.status, s.SOLVER_ERROR)

        y = np.zeros(problem['m'])
        y[problem['eq_rows']] = m.result.y
        y[problem['ineq_rows_l']] = m.result.z[:problem['ineq_rows_l'].shape[0]]
        y[problem['ineq_rows_u']] -= m.result.z[problem['ineq_rows_l'].shape[0]:]
        y[-problem['n']:] = m.result.z_ub - m.result.z_lb

        if status in s.SOLUTION_PRESENT:
            if not is_qp_solution_optimal(problem,
                                          m.result.x,
                                          y,
                                          high_accuracy=high_accuracy):
                status = s.SOLVER_ERROR

        # Verify solver time
        if settings.get('time_limit') is not None:
            if m.result.info.run_time > settings.get('time_limit'):
                status = s.TIME_LIMIT

        return_results = Results(status,
                                 m.result.info.primal_obj,
                                 m.result.x,
                                 y,
                                 m.result.info.run_time,
                                 m.result.info.iter)

        return_results.setup_time = m.result.info.setup_time
        return_results.solve_time = m.result.info.solve_time
        return_results.update_time = m.result.info.update_time

        return return_results
