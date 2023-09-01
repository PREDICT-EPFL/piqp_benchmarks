import numpy as np
import scipy.sparse as spa
from scipy.sparse import csc_matrix
import clarabel
from . import statuses as s
from .results import Results
from utils.general import is_qp_solution_optimal


class ClarabelSolver(object):

    STATUS_MAP = {clarabel.SolverStatus.Solved: s.OPTIMAL,
                  clarabel.SolverStatus.MaxIterations: s.MAX_ITER_REACHED,
                  clarabel.SolverStatus.PrimalInfeasible: s.PRIMAL_INFEASIBLE,
                  clarabel.SolverStatus.DualInfeasible: s.DUAL_INFEASIBLE}

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
        c_settings = clarabel.DefaultSettings();
        for param, value in settings.items():
            if hasattr(c_settings, param):
                setattr(c_settings, param, value)

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

        ineq_rows_l =  np.asarray(np.logical_and(l_inf > -np.inf, np.logical_not(bounds_are_equal))).nonzero()
        ineq_rows_u =  np.asarray(np.logical_and(u_inf < np.inf, np.logical_not(bounds_are_equal))).nonzero()

        Gl = -problem['A'][ineq_rows_l]
        Gu = problem['A'][ineq_rows_u]
        hl = -l_inf[ineq_rows_l]
        hu = u_inf[ineq_rows_u]

        cA = spa.vstack((A, Gl, Gu), format="csc")
        cb = np.hstack((b, hl, hu))
        cones = []
        if len(eq_rows[0]) > 0:
            cones.append(clarabel.ZeroConeT(len(eq_rows[0])))
        if len(ineq_rows_l[0]) + len(ineq_rows_u[0]) > 0:
            cones.append(clarabel.NonnegativeConeT(len(ineq_rows_l[0]) + len(ineq_rows_u[0])))

        solver = clarabel.DefaultSolver(problem['P'], problem['q'], cA, cb, cones, c_settings);

        # Solve
        sol = solver.solve()
        status = self.STATUS_MAP.get(sol.status, s.SOLVER_ERROR)

        y = np.zeros(problem['m'])
        y[eq_rows] = np.array(sol.z)[:eq_rows[0].shape[0]]
        y[ineq_rows_l] -= np.array(sol.z)[eq_rows[0].shape[0]:(eq_rows[0].shape[0] + ineq_rows_l[0].shape[0])]
        y[ineq_rows_u] += np.array(sol.z)[(eq_rows[0].shape[0] + ineq_rows_l[0].shape[0]):(eq_rows[0].shape[0] + ineq_rows_l[0].shape[0] + ineq_rows_u[0].shape[0])]

        if status in s.SOLUTION_PRESENT:
            if not is_qp_solution_optimal(problem,
                                          np.array(sol.x),
                                          y,
                                          high_accuracy=high_accuracy):
                status = s.SOLVER_ERROR

        # Verify solver time
        if settings.get('time_limit') is not None:
            if sol.solve_time > settings.get('time_limit'):
                status = s.TIME_LIMIT

        return_results = Results(status,
                                 sol.obj_val,
                                 np.array(sol.x),
                                 y,
                                 sol.solve_time,
                                 sol.iterations)

        return return_results
