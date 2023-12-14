import qpalm
from . import statuses as s
from .results import Results
from utils.general import is_qp_solution_optimal


class QPALMSolver(object):

    STATUS_MAP = {'solved': s.OPTIMAL,
                  'maximum iterations reached': s.MAX_ITER_REACHED,
                  'primal infeasible': s.PRIMAL_INFEASIBLE,
                  'dual infeasible': s.DUAL_INFEASIBLE,
                  'time limit exceeded': s.TIME_LIMIT}

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

        # Setup QPALM
        data = qpalm.Data(problem['P'].shape[0], problem['A'].shape[0])
        data.Q = problem['P']
        data.q = problem['q']
        data.A = problem['A']
        data.bmin = problem['l']
        data.bmax = problem['u']

        qpalm_settings = qpalm.Settings()
        for param, value in settings.items():
            if hasattr(qpalm_settings, param):
                setattr(qpalm_settings, param, value)

        solver = qpalm.Solver(data, qpalm_settings)
        solver.solve()
        status = self.STATUS_MAP.get(solver.info.status, s.SOLVER_ERROR)

        if status in s.SOLUTION_PRESENT:
            if not is_qp_solution_optimal(problem,
                                          solver.solution.x,
                                          solver.solution.y,
                                          high_accuracy=high_accuracy):
                status = s.SOLVER_ERROR

        # Verify solver time
        if settings.get('time_limit') is not None:
            if solver.info.run_time > settings.get('time_limit'):
                status = s.TIME_LIMIT

        return_results = Results(status,
                                 solver.info.objective,
                                 solver.solution.x,
                                 solver.solution.y,
                                 solver.info.run_time,
                                 solver.info.iter)

        return_results.setup_time = solver.info.setup_time
        return_results.solve_time = solver.info.solve_time

        return return_results
