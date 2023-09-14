from solvers.clarabel import ClarabelSolver
from solvers.ecos import ECOSSolver
from solvers.gurobi import GUROBISolver
from solvers.mosek import MOSEKSolver
from solvers.osqp import OSQPSolver
from solvers.piqp import PIQPSolver
from solvers.proxqp import PROXQPSolver
from solvers.scs import SCSSolver

CLARABEL = 'CLARABEL'
CLARABEL_high = CLARABEL + "_high"
ECOS = 'ECOS'
ECOS_high = ECOS + "_high"
GUROBI = 'GUROBI'
GUROBI_high = GUROBI + "_high"
OSQP = 'OSQP'
OSQP_high = OSQP + '_high'
OSQP_polish = OSQP + '_polish'
OSQP_polish_high = OSQP_polish + '_high'
PIQP = 'PIQP'
PIQP_high = PIQP + '_high'
PROXQP = 'PROXQP'
PROXQP_high = PROXQP + '_high'
SCS = 'SCS'
SCS_high = SCS + '_high'
MOSEK = 'MOSEK'
MOSEK_high = MOSEK + "_high"

SOLVER_MAP = {CLARABEL: ClarabelSolver,
              CLARABEL_high: ClarabelSolver,
              OSQP: OSQPSolver,
              OSQP_high: OSQPSolver,
              OSQP_polish: OSQPSolver,
              OSQP_polish_high: OSQPSolver,
              PIQP: PIQPSolver,
              PIQP_high: PIQPSolver,
              PROXQP: PROXQPSolver,
              PROXQP_high: PROXQPSolver,
              SCS: SCSSolver,
              SCS_high: SCSSolver,
              GUROBI: GUROBISolver,
              GUROBI_high: GUROBISolver,
              MOSEK: MOSEKSolver,
              MOSEK_high: MOSEKSolver,
              ECOS: ECOSSolver,
              ECOS_high: ECOSSolver
             }

time_limit = 1000. # Seconds
eps_abs_low = 1e-03
eps_rel_low = 1e-04
eps_abs_high = 1e-08
eps_rel_high = 1e-09

# Solver settings
settings = {
    CLARABEL: {'time_limit': time_limit,
               'tol_feas': eps_abs_low,
               'tol_gap_abs': eps_abs_low,
               'tol_gap_rel': eps_rel_low,
               'tol_infeas_abs': 1e-15,  # Disable infeas check
               'tol_infeas_rel': 1e-15
    },
    CLARABEL_high: {'time_limit': time_limit,
                    'tol_feas': eps_abs_low,
                    'tol_gap_abs': eps_abs_low,
                    'tol_gap_rel': eps_rel_low,
                    'tol_infeas_abs': 1e-15,  # Disable infeas check
                    'tol_infeas_rel': 1e-15
    },
    OSQP: {'time_limit': time_limit,
           'eps_abs': eps_abs_low,
           'eps_rel': eps_rel_low,
           'polish': False,
           'max_iter': int(1e09),
           'eps_prim_inf': 1e-15,  # Disable infeas check
           'eps_dual_inf': 1e-15,
    },
    OSQP_high: {'time_limit': time_limit,
                'eps_abs': eps_abs_high,
                'eps_rel': eps_rel_high,
                'polish': False,
                'max_iter': int(1e09),
                'eps_prim_inf': 1e-15,  # Disable infeas check
                'eps_dual_inf': 1e-15
    },
    OSQP_polish: {'time_limit': time_limit,
                  'eps_abs': eps_abs_low,
                  'eps_rel': eps_rel_low,
                  'polish': True,
                  'max_iter': int(1e09),
                  'eps_prim_inf': 1e-15,  # Disable infeas check
                  'eps_dual_inf': 1e-15
    },
    OSQP_polish_high: {'time_limit': time_limit,
                       'eps_abs': eps_abs_high,
                       'eps_rel': eps_rel_high,
                       'polish': True,
                       'max_iter': int(1e09),
                       'eps_prim_inf': 1e-15,  # Disable infeas check
                       'eps_dual_inf': 1e-15
    },
    PIQP: {'eps_abs': eps_abs_low,
           'eps_rel': eps_rel_low,
           'eps_duality_gap_abs': eps_abs_low,
           'eps_duality_gap_rel': eps_rel_low,
           'compute_timings': True,
    },
    PIQP_high: {'eps_abs': eps_abs_high,
                'eps_rel': eps_rel_high,
                'eps_duality_gap_abs': eps_abs_high,
                'eps_duality_gap_rel': eps_rel_high,
                'compute_timings': True,
    },
    PROXQP: {'eps_abs': eps_abs_low,
             'eps_rel': eps_rel_low,
             'check_duality_gap': True,
             'eps_duality_gap_abs': eps_abs_low,
             'eps_duality_gap_rel': eps_rel_low,
             'compute_timings': True,
    },
    PROXQP_high: {'eps_abs': eps_abs_high,
                  'eps_rel': eps_rel_high,
                  'check_duality_gap': True,
                  'eps_duality_gap_abs': eps_abs_high,
                  'eps_duality_gap_rel': eps_rel_high,
                  'compute_timings': True,
    },
    SCS: {'eps_abs': eps_abs_low,
          'eps_rel': eps_rel_low,
          'max_iters': int(1e09),
          'eps_infeas': 1e-15,
    },
    SCS_high: {'eps_abs': eps_abs_high,
               'eps_rel': eps_rel_high,
               'max_iters': int(1e09),
               'eps_infeas': 1e-15,
    },
    GUROBI: {'Threads': 1,
             'TimeLimit': time_limit,
             'FeasibilityTol': eps_abs_low,
             'OptimalityTol': eps_abs_low,
             },
    GUROBI_high: {'Threads': 1,
                  'TimeLimit': time_limit,
                  'FeasibilityTol': eps_abs_high,
                  'OptimalityTol': eps_abs_high,
                  },
    MOSEK: {'MSK_IPAR_NUM_THREADS': 1,
            'MSK_DPAR_OPTIMIZER_MAX_TIME': time_limit,
            'MSK_DPAR_INTPNT_TOL_PFEAS': eps_abs_low,
            'MSK_DPAR_INTPNT_TOL_DFEAS': eps_abs_low,
            'MSK_DPAR_INTPNT_QO_TOL_PFEAS': eps_abs_low,
            'MSK_DPAR_INTPNT_QO_TOL_DFEAS': eps_abs_low,
            'MSK_DPAR_INTPNT_CO_TOL_PFEAS': eps_abs_low,
            'MSK_DPAR_INTPNT_CO_TOL_DFEAS': eps_abs_low,
           },
    MOSEK_high: {'MSK_IPAR_NUM_THREADS': 1,
                 'MSK_DPAR_OPTIMIZER_MAX_TIME': time_limit,
                 'MSK_DPAR_INTPNT_TOL_PFEAS': eps_abs_high,
                 'MSK_DPAR_INTPNT_TOL_DFEAS': eps_abs_high,
                 'MSK_DPAR_INTPNT_QO_TOL_PFEAS': eps_abs_high,
                 'MSK_DPAR_INTPNT_QO_TOL_DFEAS': eps_abs_high,
                 'MSK_DPAR_INTPNT_CO_TOL_PFEAS': eps_abs_high,
                 'MSK_DPAR_INTPNT_CO_TOL_DFEAS': eps_abs_high,
                },
    ECOS: {'abstol': eps_abs_low,
           'reltol': eps_rel_low},
    ECOS_high: {'abstol': eps_abs_high,
                'reltol': eps_rel_high}
}

for key in settings:
    settings[key]['verbose'] = False
    settings[key]['time_limit'] = time_limit
