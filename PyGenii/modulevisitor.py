

"""Define a ModuleVisitor for collecting statistics"""


import ast
import logging


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
        logging.debug("Begin Module")
        new_context = ModuleVisitor.Context()
        self.context_stack.append(new_context)
        
        self.stats[None] = []
        self.class_complexity[None] = 0
        
        ast.NodeVisitor.generic_visit(self, node)
        
        logging.debug("End Module")
        
    def visit_ClassDef(self, node):
        """Deal with class information"""
        logging.debug("Begin Class %s", node.name)
        new_context = ModuleVisitor.Context()
        new_context.class_name = node.name
        self.context_stack.append(new_context)
        
        self.stats[new_context.class_name] = []
        self.class_complexity[new_context.class_name] = 0
        
        ast.NodeVisitor.generic_visit(self, node)
        
        self.context_stack.pop()  
        logging.debug("End Class %s", node.name)
    
    @staticmethod   
    def is_frontier_node(node): 
        """Determine if code after node is unreachable"""
        if isinstance(node, ast.Return):
            return True
        elif isinstance(node, ast.If):
            fields = dict(ast.iter_fields(node))
            body = fields['body']
            orelse = fields['orelse']
            if (ModuleVisitor.is_frontier_node(body) and 
                    ModuleVisitor.is_frontier_node(orelse)):
                return True
            else: 
                return False
        elif isinstance(node, ast.For):
            fields = dict(ast.iter_fields(node))
            body = fields['body']
            if ModuleVisitor.is_frontier_node(body):
                return True
            else:
                return False
        elif isinstance(node, ast.While):
            fields = dict(ast.iter_fields(node))
            body = fields['body']
            if ModuleVisitor.is_frontier_node(body):
                return True
            else:
                return False
        elif isinstance(node, list):
            num_frontiers = [ModuleVisitor.is_frontier_node(c) 
                for c in node].count(True)
            if num_frontiers > 0:
                return True
            else:
                return False
        else:
            return False
        
    def visit_FunctionDef(self, node):
        """Collect function statistics"""
        logging.debug("Begin Function %s", node.name)
        logging.debug("FUNC dump: %s", ast.dump(node))
        new_context = ModuleVisitor.Context()
        prev_context = self.context_stack[-1]
        new_context.function_name = node.name
        new_context.class_name = prev_context.class_name
        new_context.decision_points = 0
        new_context.exit_points = 0
        new_context.depth = 0
        self.context_stack.append(new_context)
        
        statements = dict(ast.iter_fields(node))['body']
        logging.debug("statements %s", statements)
        frontiers = [self.is_frontier_node(n) for n in statements]
        logging.debug("frontiers %s", frontiers)
        
        try:
            first_frontier = frontiers.index(True)
            reachable = statements[:first_frontier + 1]
        except ValueError:
            reachable = statements        
        logging.debug("reachable %s", reachable)
                    
        for statement in statements:
            ast.NodeVisitor.visit(self, statement)
                
        if not frontiers[-1]:
            new_context.exit_points = new_context.exit_points + 1        
        complexity = new_context.decision_points - new_context.exit_points + 2
        self.stats[new_context.class_name].append((new_context.function_name,
            complexity))
        self.class_complexity[new_context.class_name] = (
            self.class_complexity[new_context.class_name] + complexity)
        self.module_complexity = self.module_complexity + complexity
        self.context_stack.pop()
        logging.debug("End Function %s", node.name)
           
    def visit_decision_point(self, node):
        """Visit decision point node"""
        current_context = self.context_stack[-1]
        current_context.increment_decision_points()
        current_context.increment_depth()
        logging.debug("DP dump: %s", ast.dump(node))
        
        ast.NodeVisitor.generic_visit(self, node)
        
        current_context.decrement_depth()
    
    visit_If = visit_And = visit_Or = visit_decision_point
    visit_For = visit_While = visit_decision_point
        
    def visit_Return(self, _):
        """Visit Return node"""           
        current_context = self.context_stack[-1]
        logging.debug("Return depth=%d", current_context.depth)       
        current_context.increment_exit_points()
    
    def visit_ExceptHandler(self, node):
        """Visit a Exception Handler node"""
        current_context = self.context_stack[-1]
        if self.use_exceptions:
            current_context.increment_decision_points()
            
        ast.NodeVisitor.generic_visit(self, node)
