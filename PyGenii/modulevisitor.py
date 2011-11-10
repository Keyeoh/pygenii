

"""Define a ModuleVisitor for collecting statistics"""


import ast


class ModuleVisitor(ast.NodeVisitor):
    """Visit nodes in parse tree"""
    def __init__(self):
        ast.NodeVisitor.__init__(self)
        self.current_class = None
        self.current_function = None
        self.current_decision_points = 0
        self.current_exit_points = 0
        self.stats = {}
        self.module_complexity = 0
        self.class_complexity = {}
    
    def visit_Module(self, node):
        """Deal with module/file"""
        self.current_class = None
        self.stats[self.current_class] = []
        self.class_complexity[self.current_class] = 0
        ast.NodeVisitor.generic_visit(self, node)
        
    def visit_ClassDef(self, node):
        """Deal with class information"""
        self.current_class = node.name
        self.stats[self.current_class] = []
        self.class_complexity[self.current_class] = 0
        ast.NodeVisitor.generic_visit(self, node)
        self.current_class = None
        
    def visit_FunctionDef(self, node):
        """Collect function statistics"""
        self.current_function = node.name
        self.current_decision_points = 0
        self.current_exit_points = 0
        ast.NodeVisitor.generic_visit(self, node)
        self.current_exit_points = max(1, self.current_exit_points)
        complexity = (self.current_decision_points - self.current_exit_points 
            + 2)
        self.stats[self.current_class].append((self.current_function, 
            complexity))
        self.class_complexity[self.current_class] = (
            self.class_complexity[self.current_class] + complexity)
        self.module_complexity = self.module_complexity + complexity
        self.current_function = None
           
    def visit_decision_point(self, node):
        """Visit decision point node"""
        self.current_decision_points = self.current_decision_points + 1
        ast.NodeVisitor.generic_visit(self, node)
    
    visit_If = visit_And = visit_Or = visit_decision_point
    visit_For = visit_While = visit_decision_point

        
    def visit_Return(self, node):
        """Visit Return node"""
        self.current_exit_points = self.current_exit_points + 1
        ast.NodeVisitor.generic_visit(self, node)