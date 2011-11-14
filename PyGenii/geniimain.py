"""PyGenii: Python3 cyclomatic complexity analyzer"""


import argparse
import ast
import glob
import logging
import os
import sys

import PyGenii.modulevisitor


class Stats:
    """Encapsulate stats and reporting capabilities"""
    def __init__(self):
        self.complexity_table = []
        self.summary = {'X':(0, 0), 'C':(0, 0), 'M':(0, 0), 'F':(0, 0)}
        
    def filter_and_print_result(self, args, output_file):
        """Filter rows under threshold and print table"""
        is_critical = lambda row : row[2] > args.threshold and row[0] in "FM"
        filtered_table = ([row for row in self.complexity_table 
            if is_critical(row)])
        
        if len(self.complexity_table) == 0:
            output_file.write("\nNo python files to parse!\n")
        elif len(filtered_table) == 0:
            output_file.write("\nThis code looks all good!\n")
        else:
            output_file.write("\nCritical functions\n")
            pretty_print(filtered_table, output_file)
            
    def print_complexity_report(self, args, output_file):
        """Print complexity table in a clear way"""
        if args.complexity and len(self.complexity_table) > 0:
            output_file.write("\nComplexity Report\n")
            pretty_print(self.complexity_table, output_file)
            
    def print_summary(self, args, output_file):
        """Print summary if asked by the user"""
        if args.summary and len(self.complexity_table) > 0:
            output_file.write("\nTotal cumulative statistics\n")
            pretty_print_summary(self.summary, output_file)

            
def parse_args(argv):
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Evaluate cyclomatic complexity of Python modules")
    parser.add_argument('-a', '--all', dest='allItems', action='store_true', 
        default=False, help='print all metrics')
    parser.add_argument('-c', '--complexity', dest='complexity', 
        action='store_true', default=False, 
        help='print complexity details for each file/module')
    parser.add_argument('-o', '--outfile', dest='out_file',
        default=None, help='output to OUTFILE (default=stdout)')
    parser.add_argument('-r', '--recursive', dest='recurs',
        action='store_true', default=False,
        help='process files recursively in a folder')
    parser.add_argument('-s', '--summary', dest='summary',
        action='store_true', default=False,
        help='print cumulative summary for each file/module')
    parser.add_argument('-t', '--threshold', dest='threshold', type=int, 
        default=7, help='threshold of complexity to be ignored (default=7)')
    parser.add_argument('-v', '--verbosity', choices=[0, 1, 2], 
        dest='verbosity', default=0, type=int,
        help='controls how much info is printed on screen')
    parser.add_argument('-x', '--exceptions', dest='exceptions', 
        action='store_true', default=False, 
        help='use exception handling code when measuring complexity')
    parser.add_argument('files', type=str, nargs='+', 
        help="input files")
    
    args = parser.parse_args(argv)
    
    if (args.allItems):
        args.complexity = True
        args.summary = True

    return args

    
def add_module(item_name, args, module_list):
    """Recursively add items to module list"""
    if os.path.isfile(item_name) and item_name.endswith(".py"):
        module_list.add(item_name)
    elif os.path.isdir(item_name):
        if args.recurs:
            for root, _, files in os.walk(item_name):
                for file_name in files:
                    full_name = os.path.abspath(os.path.join(root, file_name))
                    add_module(full_name, args, module_list)
    else:
        # In pygenie, this is the place where we take care of packages
        pass

        
def get_module_list(args):
    """Get list of modules from wildcards and directories"""
    # Expand User, Vars and wildcards
    expanded_items = []
    for item_name in args.files:
        logging.debug("item_name %s", item_name)
        item_name = os.path.expandvars(os.path.expanduser(item_name))
        logging.debug("expanded item_name %s", item_name)
        glob_list = glob.glob(item_name)
        logging.debug("glob_list %s", glob_list)
        expanded_items = expanded_items + glob_list
                
    logging.debug("expanded_items %s", expanded_items)
    # Call recursive helper function
    module_list = set()
    for item_name in expanded_items:
        add_module(item_name, args, module_list)
    
    return module_list
        
        
def pretty_print(complexity_table, output_file=sys.stdout):
    """Print complexity table"""
    max_name_length = max([len(item_name) for (_, item_name, _) 
        in complexity_table])
        
    col_sizes = 6, max_name_length + 1, 12
    row_col_sizes = col_sizes[0], col_sizes[1] - 1, col_sizes[2] - 1
    col_total = sum(col_sizes)
    
    logging.debug("col_sizes %s", col_sizes)
    logging.debug("col_total %d", col_total)
    
    sep_str = col_total * '-' + '\n'    
    header_str = ("Type".center(col_sizes[0]) + "Name".center(col_sizes[1]) +
        "Complexity".center(col_sizes[2])) + '\n'
    output_file.write(sep_str)
    output_file.write(header_str)
    output_file.write(sep_str)
    row_format_str = "{0:^%d}{1:<%d}{2:>%d}" % row_col_sizes
    for type_id, item_name, complexity in complexity_table:
        row_str = row_format_str.format(type_id, item_name, complexity) + '\n'
        output_file.write(row_str)
    output_file.write(sep_str)
        
    output_file.flush()
        
        
def pretty_print_summary(summary, output_file=sys.stdout):
    """Print statistics summary"""
    col_sizes = 6, 7, 12
    row_col_sizes = col_sizes[0], col_sizes[1] - 2, col_sizes[2] - 1
    col_total = sum(col_sizes)
    
    sep_str = col_total * '-' + '\n'    
    header_str = ("Type".center(col_sizes[0]) + "Count".center(col_sizes[1]) +
        "Complexity".center(col_sizes[2])) + '\n'
        
    output_file.write(sep_str)
    output_file.write(header_str)
    output_file.write(sep_str)
    
    row_format_str = "{0:^%d}{1:>%d}{2:>%d}" % row_col_sizes
    for type_id, (count, complexity) in summary.items():
        row_str = row_format_str.format(type_id, count, complexity) + '\n'
        output_file.write(row_str)
        
    output_file.write(sep_str)

    
def parse_module(source_file, module_name, stats):
    """Parse given module and return stats"""
    parse_tree = ast.parse(source_file.read(), module_name)
    
    mod_visitor = PyGenii.modulevisitor.ModuleVisitor()
    mod_visitor.visit(parse_tree)

    short_name = os.path.basename(module_name).replace(".py", "")
    
    stats.complexity_table.append(('X', short_name, 
        mod_visitor.module_complexity))
  
    count, total_complexity = stats.summary['X']
    stats.summary['X'] = (count + 1, total_complexity + 
        mod_visitor.module_complexity)
        
    for class_name in mod_visitor.stats:
        if class_name:
            qualified_name = '.'.join([short_name, class_name])
            stats.complexity_table.append(('C', qualified_name, 
                mod_visitor.class_complexity[class_name]))
           
            count, total_complexity = stats.summary['C']
            stats.summary['C'] = (count + 1, total_complexity + 
                mod_visitor.class_complexity[class_name])
            type_id = 'M'
        else:
            type_id = 'F'
            
        for func_name, complexity in mod_visitor.stats[class_name]:
            if class_name:
                qualified_name = '.'.join([short_name, class_name, 
                    func_name])
            else:
                qualified_name = '.'.join([short_name, func_name])
            stats.complexity_table.append((type_id, qualified_name, complexity))
           
            count, total_complexity = stats.summary[type_id]
            stats.summary[type_id] = (count + 1, total_complexity + 
                complexity)
    
    
def filter_and_print_result(complexity_table, args, output_file):
    """Filter rows under threshold and print table"""
    is_critical = lambda row : row[2] > args.threshold and row[0] in "FM"
    filtered_table = [row for row in complexity_table if is_critical(row)]
    
    if len(complexity_table) == 0:
        output_file.write("\nNo python files to parse!\n")
    elif len(filtered_table) == 0:
        output_file.write("\nThis code looks all good!\n")
    else:
        output_file.write("\nCritical functions\n")
        pretty_print(filtered_table, output_file)
    
    
def main(argv=None):
    """Main function"""
    if argv is None:
        argv = sys.argv
   
    args = parse_args(argv)
    
    verbosity_list = [logging.WARNING, logging.INFO, logging.DEBUG]      
        
    logging.basicConfig(format ='%(levelname)s: %(message)s', 
        level = verbosity_list[args.verbosity])
    logging.info("Started")
    logging.debug("args %s", args)
    
    logging.info("Getting modules")
    module_list = get_module_list(args)
    logging.debug("module_list %s", module_list)

    # Module parsing
    global_stats = Stats()
        
    for module_name in module_list:
        logging.info("Parsing module %s", module_name)
        source_file = open(module_name)
        
        parse_module(source_file, module_name, global_stats)
        
        source_file.close()
   
    logging.info("Evaluating complexity table")
    for row in global_stats.complexity_table:
        logging.debug("%s", row)
        
    logging.info("Evaluating summary table")
    for key in global_stats.summary:
        logging.debug("%s %s", key, global_stats.summary[key])
            
    # Pipe to the right output stream
    if args.out_file:
        output_file = open(args.out_file, 'w')
    else:
        output_file = sys.stdout
         
    # Main result
    global_stats.filter_and_print_result(args, output_file)
    
    # Complexity report        
    global_stats.print_complexity_report(args, output_file)
    
    # Main summary
    global_stats.print_summary(args, output_file)        
    
    # Close file, if necessary
    if args.out_file:
        output_file.close()
    
    logging.info("Finished")
   
if __name__ == "__main__":
    sys.exit(main())
    