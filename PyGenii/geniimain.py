"""PyGenii: Python3 cyclomatic complexity analyzer"""


import argparse
import ast
import glob
import logging
import os
import sys

from PyGenii import modulevisitor, stats

            
def parse_args(argv):
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Evaluate cyclomatic complexity of Python modules")
    parser.add_argument('-a', '--all', dest='allItems', action='store_true', 
        default=False, help='print all metrics')
    parser.add_argument('-c', '--complexity', dest='complexity', 
        action='store_true', default=False, 
        help='print complexity details for each file/module')
    parser.add_argument('-m', '--modulestats', dest='module_stats', 
        action='store_true', default=False,
        help='print, for each module, a descriptive report of complexities')
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
        args.module_stats = True

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

    
def parse_module(source_file, module_name, stats, args):
    """Parse given module and return stats"""
    print("PARSE")
    parse_tree = ast.parse(source_file.read(), module_name)
    
    short_name = os.path.basename(module_name).replace(".py", "")
    
    if short_name.startswith("__"):
        return
    
    mod_visitor = modulevisitor.ModuleVisitor(args.exceptions)
    mod_visitor.visit(parse_tree)
        
    stats.complexity_table.append(('X', short_name, 
        mod_visitor.module_complexity))
  
    count, total_complexity = stats.summary['X']
    stats.summary['X'] = (count + 1, total_complexity + 
        mod_visitor.module_complexity)
        
    module_complexities = []
    
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
                
            module_complexities.append(complexity)
    
    if module_complexities:
        complexity_sum = sum(module_complexities)
        complexity_count = len(module_complexities)
        stats.module_table.append((short_name, complexity_count, complexity_sum,
            min(module_complexities), max(module_complexities),
            int(complexity_sum / complexity_count)))
    else:
        stats.module_table.append((short_name, 0, '-', '-', '-', '-'))
       
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
    global_stats = stats.Stats()
        
    for module_name in module_list:
        logging.info("Parsing module %s", module_name)
        source_file = open(module_name)
        
        parse_module(source_file, module_name, global_stats, args)
        
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
    
    # Module stats
    global_stats.print_module_stats(args, output_file)
    
    # Close file, if necessary
    if args.out_file:
        output_file.close()
    
    logging.info("Finished")
   
if __name__ == "__main__":
    sys.exit(main())
    