

"""Define a ModuleVisitor for collecting statistics"""


import ast


class ModuleVisitor(ast.NodeVisitor):
    """Visit nodes in parse tree"""

    
    class Status:
        """Abstract current status description"""
        def __init__(self):
            self.class_name = None
            self.function_name = None
            self.decision_points = 0
            self.exit_points = 0
            
        def increment_decision_points(self, count=1):
            """Shorthand for incrementing decision points"""
            self.decision_points = self.decision_points + count
            
        def increment_exit_points(self):
            """Shorthand for incrementing exit points"""
            self.exit_points = self.exit_points + 1

            
    def __init__(self, use_exceptions):
        ast.NodeVisitor.__init__(self)
        self.use_exceptions = use_exceptions
        self.current_status = ModuleVisitor.Status()
        self.stats = {}
        self.module_complexity = 0
        self.class_complexity = {}
    
    def visit_Module(self, node):
        """Deal with module/file"""
        self.current_status.class_name = None
        self.stats[self.current_status.class_name] = []
        self.class_complexity[self.current_status.class_name] = 0
        ast.NodeVisitor.generic_visit(self, node)
        
    def visit_ClassDef(self, node):
        """Deal with class information"""
        old_class_name = self.current_status.class_name
        self.current_status.class_name = node.name
        self.stats[self.current_status.class_name] = []
        self.class_complexity[self.current_status.class_name] = 0
        
        ast.NodeVisitor.generic_visit(self, node)
        
        self.current_status.class_name = old_class_name
        
    def visit_FunctionDef(self, node):
        """Collect function statistics"""
        self.current_status.function_name = node.name
        self.current_status.decision_points = 0
        self.current_status.exit_points = 0
        
        self.depth = 0
        
        ast.NodeVisitor.generic_visit(self, node)      
        
        self.current_status.exit_points = self.current_status.exit_points + 1
        complexity = (self.current_status.decision_points - 
            self.current_status.exit_points + 2)
        self.stats[self.current_status.class_name].append(
            (self.current_status.function_name, complexity))
        self.class_complexity[self.current_status.class_name] = (
            self.class_complexity[self.current_status.class_name] + complexity)
        self.module_complexity = self.module_complexity + complexity
        self.current_status.function_name = None
           
    def visit_decision_point(self, node):
        """Visit decision point node"""
        self.current_status.increment_decision_points()
        
        self.depth = self.depth + 1
        
        ast.NodeVisitor.generic_visit(self, node)
        
        self.depth = self.depth - 1
    
    visit_If = visit_And = visit_Or = visit_decision_point
    visit_For = visit_While = visit_decision_point
        
    def visit_Return(self, node):
        """Visit Return node"""
        
        if self.depth != 0:
            self.current_status.increment_exit_points()
        ast.NodeVisitor.generic_visit(self, node)
    
    def visit_ExceptHandler(self, node):
        """Visit a Exception Handler node"""
        if self.use_exceptions:
            self.current_status.increment_decision_points()
        ast.NodeVisitor.generic_visit(self, node)
