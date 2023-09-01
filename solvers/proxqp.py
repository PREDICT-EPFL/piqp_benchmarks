import numpy as np
from proxsuite import proxqp
from . import statuses as s
from .results import Results
from utils.general import is_qp_solution_optimal


class PROXQPSolver(object):

    STATUS_MAP = {proxqp.QPSolverOutput.PROXQP_SOLVED: s.OPTIMAL,
                  proxqp.QPSolverOutput.PROXQP_MAX_ITER_REACHED: s.MAX_ITER_REACHED,
                  proxqp.QPSolverOutput.PROXQP_PRIMAL_INFEASIBLE: s.PRIMAL_INFEASIBLE,
                  proxqp.QPSolverOutput.PROXQP_DUAL_INFEASIBLE: s.DUAL_INFEASIBLE}

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

        result = proxqp.sparse.solve(
            problem['P'], problem['q'],
            A, b,
            C, cl, cu,
            **settings,
        )
        
        status = self.STATUS_MAP.get(result.info.status, s.SOLVER_ERROR)

        y = np.zeros(problem['m'])
        y[eq_rows] = result.y
        y[ineq_rows] = result.z

        if status in s.SOLUTION_PRESENT:
            if not is_qp_solution_optimal(problem,
                                          result.x,
                                          y,
                                          high_accuracy=high_accuracy):
                status = s.SOLVER_ERROR

        # Verify solver time
        if time_limit is not None:
            if result.info.run_time * 1e-6 > time_limit:
                status = s.TIME_LIMIT

        return_results = Results(status,
                                 result.info.objValue,
                                 result.x,
                                 y,
                                 result.info.run_time  * 1e-6,
                                 result.info.iter)

        return_results.setup_time = result.info.setup_time * 1e-6
        return_results.solve_time = result.info.solve_time * 1e-6

        return return_results
