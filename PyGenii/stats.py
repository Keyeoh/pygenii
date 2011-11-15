

"""Statistics and reports class"""


import logging
import sys


class Stats:
    """Encapsulate stats and reporting capabilities"""
    def __init__(self):
        self.complexity_table = []
        self.summary = {'X':(0, 0), 'C':(0, 0), 'M':(0, 0), 'F':(0, 0)}
        self.module_table = []
    
    @staticmethod
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
        header_str = ("Type".center(col_sizes[0]) 
            + "Name".center(col_sizes[1]) + "Complexity".center(col_sizes[2])
            + '\n')
        output_file.write(sep_str)
        output_file.write(header_str)
        output_file.write(sep_str)
        row_format_str = "{0:^%d}{1:<%d}{2:>%d}" % row_col_sizes
        for type_id, item_name, complexity in complexity_table:
            row_str = (row_format_str.format(type_id, item_name, complexity) 
                + '\n')
            output_file.write(row_str)
        output_file.write(sep_str)
            
        output_file.flush()
    
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
            self.pretty_print(filtered_table, output_file)
            
    def print_complexity_report(self, args, output_file):
        """Print complexity table in a clear way"""
        if args.complexity and len(self.complexity_table) > 0:
            output_file.write("\nComplexity Report\n")
            self.pretty_print(self.complexity_table, output_file)
            
    def print_summary(self, args, output_file):
        """Print summary if asked by the user"""
        if args.summary and len(self.complexity_table) > 0:
            output_file.write("\nTotal cumulative statistics\n")
            self.pretty_print_summary(output_file)
    
    def print_module_stats(self, args, output_file):
        """Print module statistics"""
        if args.module_stats and len(self.complexity_table) > 0:
            output_file.write("\nModule statistics\n")
            self.pretty_print_module_stats(output_file)
                
    def pretty_print_module_stats(self, output_file=sys.stdout):
        """Print statistics summary"""
        max_name_length = max([len(item_name) for (item_name, _, _, _, _, _) 
            in self.module_table])
            
        col_sizes = max_name_length + 1, 7, 5, 5, 5, 5
        row_col_sizes = (col_sizes[0], col_sizes[1] - 3, col_sizes[2] + 1, 
            col_sizes[3], col_sizes[4], col_sizes[5])
        col_total = sum(col_sizes)
        
        sep_str = col_total * '-' + '\n'    
        header_str = ("Name".center(col_sizes[0]) 
            + "Count".center(col_sizes[1]) + "Sum".center(col_sizes[2]) 
            + "Min".center(col_sizes[2]) + "Avg".center(col_sizes[2]) 
            + "Max".center(col_sizes[2]) + '\n')
            
        output_file.write(sep_str)
        output_file.write(header_str)
        output_file.write(sep_str)
        
        row_format_str = (" {0:<%d}{1:>%d}{2:>%d}{3:>%d}{4:>%d}{5:>%d}" 
            % row_col_sizes)
        for name, count, total, min_value, max_value, avg in self.module_table:
            row_str = row_format_str.format(name, count, total, min_value, avg,
            max_value) + '\n'
            output_file.write(row_str)
            
        output_file.write(sep_str)
        
    def pretty_print_summary(self, output_file=sys.stdout):
        """Print statistics summary"""
        col_sizes = 6, 7, 12
        row_col_sizes = col_sizes[0], col_sizes[1] - 2, col_sizes[2] - 1
        col_total = sum(col_sizes)
        
        sep_str = col_total * '-' + '\n'    
        header_str = ("Type".center(col_sizes[0]) 
            + "Count".center(col_sizes[1]) + "Complexity".center(col_sizes[2]) 
            + '\n')
            
        output_file.write(sep_str)
        output_file.write(header_str)
        output_file.write(sep_str)
        
        row_format_str = "{0:^%d}{1:>%d}{2:>%d}" % row_col_sizes
        for type_id, (count, complexity) in self.summary.items():
            row_str = row_format_str.format(type_id, count, complexity) + '\n'
            output_file.write(row_str)
            
        output_file.write(sep_str)
