import numpy as np
import scipy.sparse as spa
from scipy.sparse import csc_matrix
from scs import solve
from . import statuses as s
from .results import Results
from utils.general import is_qp_solution_optimal


class SCSSolver(object):

    STATUS_MAP = {1: s.OPTIMAL,
                  2: s.OPTIMAL_INACCURATE,
                  -2: s.PRIMAL_OR_DUAL_INFEASIBLE}

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
        settings['time_limit_secs'] = settings['time_limit']
        time_limit = settings.pop('time_limit', None)
        high_accuracy = settings.pop('high_accuracy', None)

        l_inf = problem['l']
        u_inf = problem['u']
        l_inf[l_inf > +9e19] = +np.inf
        u_inf[u_inf > +9e19] = +np.inf
        l_inf[l_inf < -9e19] = -np.inf
        u_inf[u_inf < -9e19] = -np.inf

        bounds_are_equal = u_inf - l_inf < 1e-10

        eq_rows = np.asarray(bounds_are_equal).nonzero()
        A = problem['A'][eq_rows]
        b = u_inf[eq_rows]

        ineq_rows = np.asarray(np.logical_not(bounds_are_equal)).nonzero()
        C = problem['A'][ineq_rows]
        cl = l_inf[ineq_rows]
        cu = u_inf[ineq_rows]

        data = {'P': problem['P'], 'c': problem['q']}
        cone = {}

        zero_row = csc_matrix((1, problem['n']))
        data['A'] = spa.vstack((A, zero_row, -C), format="csc")
        data['b'] = np.hstack((b, 1.0, np.zeros(ineq_rows[0].shape[0])))
        cone['z'] = b.shape[0]
        cone['bsize'] = 1 + cl.shape[0]
        cone['bl'] = cl
        cone['bu'] = cu

        result = solve(data, cone, **settings)
        
        status = self.STATUS_MAP.get(result['info']['status_val'], s.SOLVER_ERROR)

        y = np.zeros(problem['m'])
        y[eq_rows] = result['y'][:eq_rows[0].shape[0]]
        y[ineq_rows] = -result['y'][(eq_rows[0].shape[0] + 1):]

        if status in s.SOLUTION_PRESENT:
            if not is_qp_solution_optimal(problem,
                                          result['x'],
                                          y,
                                          high_accuracy=high_accuracy):
                status = s.SOLVER_ERROR

        run_time = result['info']['setup_time'] * 1e-3 + result['info']['solve_time'] * 1e-3

        # Verify solver time
        if time_limit is not None:
            if run_time > time_limit:
                status = s.TIME_LIMIT

        return_results = Results(status,
                                 result['info']['pobj'],
                                 result['x'],
                                 y,
                                 run_time,
                                 result['info']['iter'])

        return_results.setup_time = result['info']['setup_time'] * 1e-3
        return_results.solve_time = result['info']['solve_time'] * 1e-3

        return return_results
