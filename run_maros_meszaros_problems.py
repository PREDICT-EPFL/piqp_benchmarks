from maros_meszaros_problems.maros_meszaros_problem import MarosMeszarosRunner
import solvers.solvers as s
from utils.benchmark import compute_stats_info
import argparse

def main():
    '''
    Run Maros-Meszaros problems for the PIQP paper

    This code tests the solvers:
        - PIQP
        - OSQP
        - SCS
        - PROXQP
        - GUROBI
        - MOSEK

    '''
    parser = argparse.ArgumentParser(description='Maros Meszaros Runner')
    parser.add_argument('--high_accuracy', help='Test with high accuracy', default=False,
                        action='store_true')
    parser.add_argument('--verbose', help='Verbose solvers', default=False,
                        action='store_true')
    parser.add_argument('--parallel', help='Parallel solution', default=False,
                        action='store_true')
    args = parser.parse_args()
    high_accuracy = args.high_accuracy
    verbose = args.verbose
    parallel = args.parallel

    print('high_accuracy', high_accuracy)
    print('verbose', verbose)
    print('parallel', parallel)

    # Add high accuracy solvers when accuracy
    if high_accuracy:
        solvers = [s.PIQP_high, s.OSQP_high, s.QPALM_high, s.SCS_high, s.PROXQP_high, s.GUROBI_high, s.MOSEK_high]
        # solvers = [s.PIQP_high, s.OSQP_high, s.SCS_high, s.PROXQP_high, s.GUROBI_high, s.MOSEK_high]
        OUTPUT_FOLDER = 'maros_meszaros_problems_high_accuracy'
        for key in s.settings:
            s.settings[key]['high_accuracy'] = True
    else:
        solvers = [s.PIQP, s.OSQP, s.QPALM, s.SCS, s.PROXQP, s.GUROBI, s.MOSEK]
        # solvers = [s.PIQP, s.OSQP, s.SCS, s.PROXQP, s.GUROBI, s.MOSEK]
        OUTPUT_FOLDER = 'maros_meszaros_problems'

    # Shut up solvers
    if verbose:
        for key in s.settings:
            s.settings[key]['verbose'] = True

    # Run all examples
    maros_meszaros_runner = MarosMeszarosRunner(solvers,
                                                s.settings,
                                                OUTPUT_FOLDER)

    # DEBUG only: Choose only 2 problems
    # maros_meszaros_runner.problems = ["STADAT1", "BOYD1"]

    maros_meszaros_runner.solve(parallel=parallel, cores=8)

    # Compute results statistics
    compute_stats_info(solvers, OUTPUT_FOLDER,
                    high_accuracy=high_accuracy)


if __name__ == '__main__':
    main()
