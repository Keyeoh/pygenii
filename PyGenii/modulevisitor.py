

"""Define a ModuleVisitor for collecting statistics"""


import ast
import copy


class ModuleVisitor(ast.NodeVisitor):
    """Visit nodes in parse tree"""

    
    class Context:
        """Abstract current status description"""
        def __init__(self):
            self.class_name = None
            self.function_name = None
            self.decision_points = 0
            self.exit_points = 0
            self.depth = 0
            
        def increment_decision_points(self, count=1):
            """Shorthand for incrementing decision points"""
            self.decision_points = self.decision_points + count
            
        def increment_exit_points(self):
            """Shorthand for incrementing exit points"""
            self.exit_points = self.exit_points + 1
            
        def increment_depth(self):
            """Shorthand for incrementing depth"""
            self.depth = self.depth + 1
            
        def decrement_depth(self):
            """Shorthand for decreasing depth"""
            self.depth = self.depth - 1

            
    def __init__(self, use_exceptions):
        ast.NodeVisitor.__init__(self)
        self.use_exceptions = use_exceptions
        self.stats = {}
        self.module_complexity = 0
        self.class_complexity = {}
        self.context_stack = []
    
    def visit_Module(self, node):
        """Deal with module/file"""
        new_context = ModuleVisitor.Context()
        self.context_stack.append(new_context)
        
        self.stats[None] = []
        self.class_complexity[None] = 0
        
        ast.NodeVisitor.generic_visit(self, node)
        
    def visit_ClassDef(self, node):
        """Deal with class information"""
        new_context = ModuleVisitor.Context()
        new_context.class_name = node.name
        self.context_stack.append(new_context)
        
        self.stats[new_context.class_name] = []
        self.class_complexity[new_context.class_name] = 0
        
        ast.NodeVisitor.generic_visit(self, node)
        
        self.context_stack.pop()      
        
    def visit_FunctionDef(self, node):
        """Collect function statistics"""
        new_context = ModuleVisitor.Context()
        prev_context = self.context_stack[-1]
        new_context.function_name = node.name
        new_context.class_name = prev_context.class_name
        new_context.decision_points = 0
        new_context.exit_points = 0
        new_context.depth = 0
        self.context_stack.append(new_context)
        
        ast.NodeVisitor.generic_visit(self, node) 
        
        new_context.exit_points = new_context.exit_points + 1
        complexity = new_context.decision_points - new_context.exit_points + 2
        self.stats[new_context.class_name].append((new_context.function_name, 
            complexity))
        self.class_complexity[new_context.class_name] = (
            self.class_complexity[new_context.class_name] + complexity)
        self.module_complexity = self.module_complexity + complexity        
        
        self.context_stack.pop()
           
    def visit_decision_point(self, node):
        """Visit decision point node"""
        current_context = self.context_stack[-1]
        current_context.increment_decision_points()
        current_context.increment_depth()
        
        ast.NodeVisitor.generic_visit(self, node)
        
        current_context.decrement_depth()
    
    visit_If = visit_And = visit_Or = visit_decision_point
    visit_For = visit_While = visit_decision_point
        
    def visit_Return(self, node):
        """Visit Return node"""        
        current_context = self.context_stack[-1]
        if current_context.depth != 0:
            current_context.increment_exit_points()
            
        ast.NodeVisitor.generic_visit(self, node)
    
    def visit_ExceptHandler(self, node):
        """Visit a Exception Handler node"""
        current_context = self.context_stack[-1]
        if self.use_exceptions:
            current_context.increment_decision_points()
            
        ast.NodeVisitor.generic_visit(self, node)
