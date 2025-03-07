from fenics import *
from ufl import nabla_div
import numpy as np
from mshr import *
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Cross section classes
class Rectangle:
    def __init__(self,b,h):
        self.b = b
        self.h = h
    def BeamMesh(self,L,n):
        domain = Box(Point(0, 0, 0), Point(L, self.b, self.h))
        return generate_mesh(domain,n)
class Boxed:
    def __init__(self,b,h,t):
        self.b = b
        self.h = h
        self.t = t
    def BeamMesh(self,L,n):
        outer = Box(Point(0, 0, 0), Point(L, self.b, self.h))
        inner = Box(Point(0, self.t, self.t), Point(L, self.b-self.t, self.h-self.t))
        domain = outer - inner
        return generate_mesh(domain,n)
class Circle:
    def __init__(self,R):
        self.R = R
    def BeamMesh(self,L,n):
        domain = Cylinder(Point(0,self.R,self.R),Point(L,self.R,self.R),self.R,self.R)
        return generate_mesh(domain,n)
class Tube:
    def __init__(self,R,r):
        self.R = R
        self.r = r
    def BeamMesh(self,L,n):
        outer = Cylinder(Point(0,self.R,self.R),Point(L,self.R,self.R),self.R,self.R)
        inner = Cylinder(Point(0,self.R,self.R),Point(L,self.R,self.R),self.r,self.r)
        domain = outer - inner
        return generate_mesh(domain,n)
class Trapezoid:
    def __init__(self,B,b,h):
        self.B = B
        self.b = b
        self.h = h
    def BeamMesh(self,L,n):
        CS = Polygon([Point(0,0), Point(self.B,0), Point(0.5*(self.B+self.b),self.h), Point(0.5*(self.B-self.b),self.h)])
        domain = Extrude2D(CS,L)
        mesh_trap = generate_mesh(domain,n)
        MeshTransformation.rotate(mesh_trap, 90.0, 0, Point(0,0,0))
        MeshTransformation.rotate(mesh_trap, 90.0, 2, Point(0,0,0))
        return mesh_trap
class Ishape:
    def __init__(self,b,h,tf,tw):
        self.b = b
        self.h = h
        self.tf = tf
        self.tw = tw
    def BeamMesh(self,L,n):
        outer = Box(Point(0,0,0), Point(L,self.b,self.h))
        inner_1 = Box(Point(0,0.5*(self.b-self.tw),self.tf), Point(L,0,self.h-self.tf))
        inner_2 = Box(Point(0,0.5*(self.b+self.tw),self.tf), Point(L,self.b,self.h-self.tf))
        domain = outer - inner_1 - inner_2
        return generate_mesh(domain,n)
class Lshape:
    def __init__(self,b,h,t):
        self.b = b
        self.h = h
        self.t = t
    def BeamMesh(self,L,n):
        outer = Box(Point(0,0,0), Point(L,self.b,self.h))
        inner = Box(Point(0,self.t,self.t), Point(L,self.b,self.h))
        domain = outer - inner
        return generate_mesh(domain,n)

class load:
    def __init__(self,type,body_force=None,location=None,magnitude=None,direction=None):
        self.type = type
        if self.type == 'uniform':
            self.body_force = body_force
        elif self.type == 'point':
            self.location = location
            self.magnitude = magnitude
            self.direction = direction

# Function to scale direction of point loads
def scale(direction):
    x,y,z = direction[0],direction[1],direction[2]
    magnitude = (x**2 + y**2 + z**2)**0.5
    return tuple([(1e-4/magnitude)*i for i in list(direction)])

# Dirac delta function to approximate point loads
class Delta(UserExpression):
    def __init__(self, eps, x0, **kwargs):
        self.eps = eps
        self.x0 = x0
        UserExpression.__init__(self, **kwargs) 
    def eval(self, values, x):
        eps = self.eps
        values[0] = eps[0]/pi/(np.linalg.norm(x-self.x0)**2 + eps[0]**2)
        values[1] = eps[1]/pi/(np.linalg.norm(x-self.x0)**2 + eps[1]**2)
        values[2] = eps[2]/pi/(np.linalg.norm(x-self.x0)**2 + eps[2]**2)
    def value_shape(self): return (3, )

# Main beam problem class
class beamProblem:
    
    def __init__(self,material,cross_section,length,num_elements,bc_input,load_input):
        self.material = material
        self.length = length
        self.bc_input=bc_input
        self.num_elements = num_elements
        self.mainMesh = cross_section.BeamMesh(self.length,num_elements)
        self.load_input=load_input
        
        # material properties
        if self.material=="steel":
            self.E=200e9
            nu=0.285
            self.rho=7700
        elif self.material=="aluminum":
            self.E=69e9
            nu=0.334
            self.rho=2700
        self.mu=self.E/(2*(1+nu))
        self.lambda_=self.E*nu/((1+nu)*(1-2*nu))
    
    def solution(self):
        
        # input variables
        rho = self.rho
        bc_input=self.bc_input
        
        # Other variables/constants
        mu = self.mu
        lambda_ = self.lambda_
        g = 9.81
        
        # Create mesh and define function space
        mesh = self.mainMesh
        V = VectorFunctionSpace(mesh, 'P', 1)
        
        # Define boundary conditions
        tol = 1E-14
        def clamped_left(x, on_boundary):
            return on_boundary and x[0] < tol
        def clamped_right(x, on_boundary):
            return on_boundary and near(x[0],self.length,tol)
        #defining rotating boundary functions
        def all_boundary(x, on_boundary):
            return on_boundary
        def yaxis(x, on_boundary):
            return on_boundary and near(x[1], 0, tol)
        def pinned_right(x, on_boundary):
            return on_boundary and near(x[2], 0, tol) and near(x[0],self.length,tol)
        def pinned_left(x, on_boundary):
            return on_boundary and near(x[2], 0, tol) and near(x[0],0,tol)
        
        if bc_input=="clamped free":
            bc=DirichletBC(V,Constant((0,0,0)),clamped_left)
        elif bc_input=="clamped clamped":
            bc1=DirichletBC(V,Constant((0,0,0)),clamped_left)
            bc2=DirichletBC(V,Constant((0,0,0)),clamped_right)
            bc=[bc1, bc2]
        elif bc_input=="clamped pinned":
            bc1=DirichletBC(V,Constant((0,0,0)),clamped_left)
            bc2=DirichletBC(V,Constant((0,0,0)),pinned_right)
            bc=[bc1, bc2]
        elif bc_input=="pinned pinned":
            bc1=DirichletBC(V,Constant((0,0,0)),pinned_left)
            bc2=DirichletBC(V,Constant((0,0,0)),pinned_right)
            bc=[bc1, bc2]
        
        # Define strain and stress
        def epsilon(u):
            return 0.5*(nabla_grad(u) + nabla_grad(u).T)
            #return sym(nabla_grad(u))
            
        def sigma(u):
            return lambda_*nabla_div(u)*Identity(d) + 2*mu*epsilon(u)

        # Define variational problem
        u = TrialFunction(V)
        d = u.geometric_dimension() # space dimension
        v = TestFunction(V)
        T = Constant((0,0,0))
        a = inner(sigma(u), epsilon(v))*dx
        
        # Apply uniform load if called for
        if bool(self.load_input) and self.load_input.type == 'uniform':
            u_l = self.load_input.body_force
            f = Constant((0+u_l[0], 0+u_l[1], -rho*g+u_l[2]))
        else:
            f = Constant((0,0,-rho*g))
        
        # Apply point load if called for
        if bool(self.load_input) and self.load_input.type == 'point':
            p_l = self.load_input
            delta = Delta(eps=scale(p_l.direction), x0=p_l.location, degree=5)
            L = dot(f, v)*dx + dot(T, v)*ds + inner(Constant(p_l.magnitude)*delta, v)*dx
        else:
            L = dot(f, v)*dx + dot(T, v)*ds
        

        # Compute solution
        u = Function(V)
        solve(a==L, u, bc)
        
        s = sigma(u) - (1./3)*tr(sigma(u))*Identity(d) # deviatoric stress
        von_Mises = sqrt(3./2*inner(s, s))
        V = FunctionSpace(mesh, 'P', 1)
        von_Mises = project(von_Mises, V)
        
        # Compute magnitude of displacement
        u_magnitude = sqrt(dot(u, u))
        u_magnitude = project(u_magnitude, V)
        
        # Important data outputs
        coordinates = V.tabulate_dof_coordinates().reshape((-1, mesh.geometry().dim()))
        # Displacement magnitudes
        um_plot = u_magnitude.vector()[:]
        # Displacement vectors
        uv_plot = np.reshape(u.vector()[:],(np.shape(coordinates)))
        # Stress magnitudes
        vm_plot = von_Mises.vector()[:]
        
        #Plotting:
        #xyz coordinates
        x_plot3d = coordinates[:,0]
        y_plot3d = coordinates[:,1]
        z_plot3d = coordinates[:,2]
        #Change in xyz coordinates
        u_vec_i = uv_plot[:,0]
        u_vec_j = uv_plot[:,1]
        u_vec_k = uv_plot[:,2]
        #Scale factor for displaying change in coordinates
        scaling = (z_plot3d.max() - z_plot3d.min()) / abs(um_plot).max()
        #Deformed xyz coordinates
        x_plot_def = x_plot3d + scaling * u_vec_i
        y_plot_def = y_plot3d + scaling * u_vec_j
        z_plot_def = z_plot3d + scaling * u_vec_k
        
        #Finding where deformation and stress are each at a maximum
        loc_u_max = []
        um_plot_max = []
        loc_vm_max = []
        vm_plot_max = []
        for i in range(um_plot.size):
            if um_plot[i] == um_plot.max():
                um_plot_max.append(um_plot.max())
                loc_u_max = list(coordinates[i])
            if vm_plot[i] == vm_plot.max():
                vm_plot_max.append(vm_plot.max())
                loc_vm_max = list(coordinates[i])
        #Convert to numpy arrays for plotting
        um_plot_max = np.array(um_plot_max)
        vm_plot_max = np.array(vm_plot_max)
        
        #Plot Results
        #%matplotlib auto #Uncomment to set backend if ipy file 
        fig = plt.figure(figsize=plt.figaspect(1.8))
        fig.tight_layout()
        cmap = plt.get_cmap('jet')
        
        #Plotting displacement
        ax_uv = fig.add_subplot(2,1,1, projection='3d')
        im_um = ax_uv.scatter(x_plot_def,y_plot_def,z_plot_def, c=um_plot.ravel(), cmap=cmap)
        fig.colorbar(im_um, ax=ax_uv, format = '%.0E')
        ax_uv.auto_scale_xyz([0,self.length],[-self.length/2,self.length/2],[-self.length/2,self.length/2])
        ax_uv.set_title('Displacement (m)\nVisual Deflection = {:.3E}:1'.format(scaling))
        ax_uv.set_xlabel('x (m)')
        ax_uv.set_ylabel('y (m)')
        ax_uv.set_zlabel('z (m)')
        label_uv = 'u = {:.3E}m at ({:.1f}, {:.1f}, {:.1f})m'.format(um_plot.max(),loc_u_max[0],loc_u_max[1],loc_u_max[2])
        ax_uv.text(-self.length/2,-self.length,-self.length/4,label_uv)
        
        #Plotting von Mises stress
        ax_vm = fig.add_subplot(2,1,2, projection='3d')
        im_vm = ax_vm.scatter(x_plot_def,y_plot_def,z_plot_def, c=vm_plot.ravel(), cmap=cmap)
        ax_vm.auto_scale_xyz([0,self.length],[-self.length/2,self.length/2],[-self.length/2,self.length/2])
        fig.colorbar(im_vm, ax=ax_vm, format='%.0E')
        ax_vm.set_title('von Mises Stress (Pa)\nVisual Deflection = {:.3E}:1'.format(scaling))
        ax_vm.set_xlabel('x (m)')
        ax_vm.set_ylabel('y (m)')
        ax_vm.set_zlabel('z (m)')
        label_vm = 'sigma = {:.3E}Pa at ({:.1f}, {:.1f}, {:.1f})m'.format(vm_plot.max(),loc_vm_max[0],loc_vm_max[1],loc_vm_max[2])
        ax_vm.text(-self.length/2,-self.length,-self.length/4,label_vm)
        label_sf = 'SF = {:.1f} at ({:.1f}, {:.1f}, {:.1f})m'.format(self.E/vm_plot.max(),loc_vm_max[0],loc_vm_max[1],loc_vm_max[2])
        ax_vm.text(-self.length/2,-self.length,-self.length/2,label_sf)
        
        plt.show()
        
        return {'Coordinates':coordinates,
                'Displacement Magnitudes':um_plot, 
                'Displacement Vectors':uv_plot, 
                'Stress Magnitudes': vm_plot}

# Example Problem
        
# Inputs
material = 'steel'
b = 0.1
h = 0.5
cross_section = Rectangle(b,h)
length = 2
num_elements = 16
boundary_conditions = 'clamped free'
load_in = load('point', location=(length,b/2,h/2), magnitude=1e9, direction=(0,0,-1))

# Problem object
beam = beamProblem(material, cross_section, length, num_elements, boundary_conditions, load_in)

# Solution
output = beam.solution()