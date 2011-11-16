
"""Test main behaviour of the complexity analyzer"""


import unittest
from PyGenii import geniimain

class TestMainParser(unittest.TestCase):
    """Test main behaviour of the parser"""
    
    
    class MockModule:
        """Simulate a module from disk"""
        def __init__(self):
            self.code = ""
        
        def read(self):
            return self.code
            
    class MockStats:
        """Simulate a stats object"""
        def __init__(self):
            self.complexity_table = []
            self.summary = {'X':(0, 0), 'C':(0, 0), 'M':(0, 0), 'F':(0, 0)}
            self.module_table = []
            
    class MockArgs:
        """Simulate an args object"""
        def __init__(self):
            self.exceptions = False
            
            
    def setUp(self):
        self.module = TestMainParser.MockModule()
        self.stats = TestMainParser.MockStats()
        self.args = TestMainParser.MockArgs()
        
    def test_simple(self):
        self.module.code = """
def f(a):
    print(a + 10)
        """       
        expected_complexity = [('X', 'test', 1), ('F', 'test.f', 1)]
        expected_summary = {'X':(1, 1), 'C':(0, 0), 'M':(0, 0), 'F':(1, 1)}
        expected_module = [('test', 1, 1, 1, 1, 1)]
        
        geniimain.parse_module(self.module, "test", self.stats, self.args)         
        
        self.assertEqual(set(expected_complexity), 
            set(self.stats.complexity_table))   
        self.assertEqual(expected_summary, self.stats.summary)   
        self.assertEqual(expected_module, self.stats.module_table)
        
    def test_class(self):
        self.module.code = """
class C:
    def __init__(self):
        self.a = 0
    def inc(self, n):
        self.a = self.a + n
    def get(self):
        return self.a
        """
        expected_complexity = [('X', 'test', 3), ('C', 'test.C', 3), 
            ('M', 'test.C.__init__', 1), ('M', 'test.C.inc', 1), 
            ('M', 'test.C.get', 1)]
        expected_summary = {'X':(1, 3), 'C':(1, 3), 'M':(3, 3), 'F':(0, 0)}
        expected_module = [('test', 3, 3, 1, 1, 1)]
        
        geniimain.parse_module(self.module, "test", self.stats, self.args)         
        
        self.assertEqual(set(expected_complexity), 
            set(self.stats.complexity_table))   
        self.assertEqual(expected_summary, self.stats.summary)   
        self.assertEqual(expected_module, self.stats.module_table)

    def test_class_and_function(self):
        self.module.code = """
def f(x):
    return 10
class C:
    def __init__(self):
        self.a = 0
    def inc(self, n):
        self.a = self.a + n
    def get(self):
        return self.a
        """
        expected_complexity = [('X', 'test', 4), ('F', 'test.f', 1), 
            ('C', 'test.C', 3), ('M', 'test.C.__init__', 1), 
            ('M', 'test.C.inc', 1), ('M', 'test.C.get', 1)]
        expected_summary = {'X':(1, 4), 'C':(1, 3), 'M':(3, 3), 'F':(1, 1)}
        expected_module = [('test', 4, 4, 1, 1, 1)]
        
        geniimain.parse_module(self.module, "test", self.stats, self.args)         
        
        self.assertEqual(set(expected_complexity), 
            set(self.stats.complexity_table))   
        self.assertEqual(expected_summary, self.stats.summary)   
        self.assertEqual(expected_module, self.stats.module_table)
        
    def test_conditional(self):
        self.module.code = """
def f(x):
    a = 5
    if a < 4:
        return a
    elif a > 5:
        return a + 5
    else:
        print("error")
"""
        expected_complexity = [('X', 'test', 1), ('F', 'test.f', 1)]
        expected_summary = {'X':(1, 1), 'C':(0, 0), 'M':(0, 0), 'F':(1, 1)}
        expected_module = [('test', 1, 1, 1, 1, 1)]
        
        geniimain.parse_module(self.module, "test", self.stats, self.args)         
        
        self.assertEqual(set(expected_complexity), 
            set(self.stats.complexity_table))   
        self.assertEqual(expected_summary, self.stats.summary)   
        self.assertEqual(expected_module, self.stats.module_table)
        
    def test_nested_class(self):
        self.module.code = """
class A:
    class B:
        def f(self):
            pass
    def g(self):
        pass
"""
        expected_complexity = [('X', 'test', 2), ('C', 'test.A', 1), 
            ('M', 'test.A.g', 1), ('C', 'test.B', 1), ('M', 'test.B.f', 1)]
        expected_summary = {'X':(1, 2), 'C':(2, 2), 'M':(2, 2), 'F':(0, 0)}
        expected_module = [('test', 2, 2, 1, 1, 1)]
        
        geniimain.parse_module(self.module, "test", self.stats, self.args)         
        
        self.assertEqual(set(expected_complexity), 
            set(self.stats.complexity_table))   
        self.assertEqual(expected_summary, self.stats.summary)   
        self.assertEqual(expected_module, self.stats.module_table)

    def test_nested_function(self):
        self.module.code = """
def f(x):
    def g(y):
        return y * 2
    if x == 0:
        return 0
    else:
        return g(x)
"""
        expected_complexity = [('X', 'test', 2), ('F', 'test.f', 1), 
            ('F', 'test.g', 1)]
        expected_summary = {'X':(1, 2), 'C':(0, 0), 'M':(0, 0), 'F':(2, 2)}
        expected_module = [('test', 2, 2, 1, 1, 1)]

        geniimain.parse_module(self.module, "test", self.stats, self.args)         
        
        self.assertEqual(set(expected_complexity), 
            set(self.stats.complexity_table))   
        self.assertEqual(expected_summary, self.stats.summary)   
        self.assertEqual(expected_module, self.stats.module_table)
        
if __name__ == "__main__":
    unittest.main()