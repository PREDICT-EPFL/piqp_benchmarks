import numpy as np
import scipy.sparse as spa
import scipy.io as spio
import cvxpy


class MarosMeszaros(object):
    '''
    Maros Meszaros
    '''
    def __init__(self, file_name, create_cvxpy_problem=False):
        '''
        Generate Maros problem in QP format and CVXPY format

        NB. By default, the CVXPY problem is not created
        '''
        # Load problem from file
        self.P, self.q, self.r, self.A, self.l, self.u, self.n, self.m = \
            self._load_maros_meszaros_problem(file_name)

        self.qp_problem = self._generate_qp_problem()

        if create_cvxpy_problem:
            self.cvxpy_problem = self._generate_cvxpy_problem()

    @staticmethod
    def _load_maros_meszaros_problem(f):
        # Load file
        m = spio.loadmat(f)

        # Convert matrices
        P = m['P'].astype(float).tocsc()
        q = m['q'].T.flatten().astype(float)
        r = m['r'].T.flatten().astype(float)[0]
        A = m['A'].astype(float).tocsc()
        l = m['l'].T.flatten().astype(float)
        u = m['u'].T.flatten().astype(float)
        n = m['n'].T.flatten().astype(int)[0]
        m = m['m'].T.flatten().astype(int)[0]

        return P, q, r, A, l, u, n, m

    @staticmethod
    def name():
        return 'Maros Meszaros'

    def _generate_qp_problem(self):
        '''
        Generate QP problem
        '''
        problem = {}
        problem['P'] = self.P
        problem['q'] = self.q
        problem['r'] = self.r
        problem['A'] = self.A
        problem['l'] = self.l
        problem['u'] = self.u
        problem['n'] = self.n
        problem['m'] = self.m

        l_inf = self.l
        u_inf = self.u
        l_inf[l_inf > +9e19] = +np.inf
        u_inf[u_inf > +9e19] = +np.inf
        l_inf[l_inf < -9e19] = -np.inf
        u_inf[u_inf < -9e19] = -np.inf

        # A == vstack([C, spa.eye(n)])
        self.xl = l_inf[-self.n:]
        self.xu = u_inf[-self.n:]
        C = self.A[:-self.n]
        cl = l_inf[:-self.n]
        cu = u_inf[:-self.n]

        self.A_eq, self.b, self.G, self.h, self.eq_rows, self.ineq_rows_l, self.ineq_rows_u = \
            self._convert_problem_from_double_sided(C, cl, cu)

        problem['A_eq'] = self.A_eq
        problem['b'] = self.b
        problem['G'] = self.G
        problem['h'] = self.h
        problem['xl'] = self.xl
        problem['xu'] = self.xu
        problem['eq_rows'] = self.eq_rows
        problem['ineq_rows_l'] = self.ineq_rows_l
        problem['ineq_rows_u'] = self.ineq_rows_u

        return problem

    def _convert_problem_from_double_sided(self, C, l, u):

        bounds_are_equal = u - l < 1e-10

        eq_rows = np.asarray(bounds_are_equal).nonzero()
        A = C[eq_rows]
        b = u[eq_rows]

        ineq_rows = np.asarray(np.logical_not(bounds_are_equal)).nonzero()
        G = spa.vstack([C[ineq_rows], -C[ineq_rows]], format="csc")
        h = np.hstack([u[ineq_rows], -l[ineq_rows]])
        h_finite = h < np.inf
        if not h_finite.all():
            G = G[h_finite]
            h = h[h_finite]

        eq_rows = eq_rows[0]
        ineq_rows = ineq_rows[0]
        ineq_rows_l = ineq_rows[u[ineq_rows] < np.inf] if ineq_rows.shape[0] > 0 else ineq_rows
        ineq_rows_u = ineq_rows[l[ineq_rows] > -np.inf] if ineq_rows.shape[0] > 0 else ineq_rows

        return A, b, G, h, eq_rows, ineq_rows_l, ineq_rows_u

    def _generate_cvxpy_problem(self):
        '''
        Generate QP problem
        '''
        x_var = cvxpy.Variable(self.n)
        objective = .5 * cvxpy.quad_form(x_var, self.P) + self.q * x_var + \
            self.r
        # constraints = [self.A * x_var <= self.u, self.A * x_var >= self.l]
        constraints = [self.A_eq * x_var == self.b,
                       self.G * x_var <= self.h,
                       x_var <= self.xu, x_var >= self.xl]
        problem = cvxpy.Problem(cvxpy.Minimize(objective), constraints)

        return problem

    def revert_cvxpy_solution(self):
        '''
        Get QP primal and duar variables from cvxpy solution
        '''

        variables = self.cvxpy_problem.variables()
        constraints = self.cvxpy_problem.constraints

        # primal solution
        x = variables[0].value

        # dual solution
        # y = constraints[0].dual_value - constraints[1].dual_value
        y = np.zeros(self.m)
        y[self.eq_rows] = constraints[0].dual_value
        y[self.ineq_rows_l] = constraints[1].dual_value[:self.ineq_rows_l.shape[0]]
        y[self.ineq_rows_u] -= constraints[1].dual_value[self.ineq_rows_l.shape[0]:]
        y[-self.n:] = constraints[2].dual_value - constraints[3].dual_value

        return x, y
