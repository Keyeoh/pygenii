

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
    def pretty_print(table, display_format, output_file=sys.stdout):
        """Generic pretty printing for the different tables we need"""        
        # Get the column widths
        n_cols = len(table[0])
        col_max_width = [max([len(str(row[col])) for row in table]) 
            for col in range(n_cols)]        
        logging.debug("display_format: %s", display_format)
        
        col_sizes = [max(a,len(b)) + 2 for (a,b) in zip(col_max_width, display_format['header'])]
        logging.debug("col_sizes: %s", col_sizes)
        
        row_col_sizes = col_sizes
        col_total = sum(col_sizes)
        
        # Write header
        sep_str = col_total * '-' + '\n' 
        header_str = ''.join([ header_name.center(col_sizes[i]) 
            for i, header_name in enumerate(display_format['header'])]) + '\n'
        logging.debug("header_str: %s", header_str)
        
        output_file.write(sep_str)
        output_file.write(header_str)
        output_file.write(sep_str)
        
        # Write body        
        logging.debug("col_align: %s", display_format['col_align'])
        row_format_str = ''.join(["{" + str(i) + ":" + align + "%d}" 
            for i, align in enumerate(display_format['col_align'])]) % tuple(row_col_sizes)
        logging.debug("row_format_str: %s", row_format_str)
        
        for row in table:
            padded_row = [ ' ' * display_format['pad_left'][i] + str(row_elem) + ' ' * display_format['pad_right'][i] for i, row_elem in enumerate(row)]
            row_str = (row_format_str.format(*padded_row) + '\n')
            output_file.write(row_str)
        
        # Write footer
        output_file.write(sep_str)
    
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
            display_format = {}
            display_format['header'] = ["Type", "Name", "Complexity"]
            display_format['col_align'] = ['^', '<', '>'] 
            display_format['pad_left'] = [1, 1, 1]
            display_format['pad_right'] = [1, 1, 2]
            self.pretty_print(filtered_table, display_format, output_file)   
            
    def print_complexity_report(self, args, output_file):
        """Print complexity table in a clear way"""
        if args.complexity and len(self.complexity_table) > 0:
            output_file.write("\nComplexity Report\n")
            display_format = {}
            display_format['header'] = ["Type", "Name", "Complexity"]
            display_format['col_align'] = ['^', '<', '>'] 
            display_format['pad_left'] = [1, 1, 1]
            display_format['pad_right'] = [1, 1, 2]
            self.pretty_print(self.complexity_table, display_format, output_file)    
            
    def print_summary(self, args, output_file):
        """Print summary if asked by the user"""
        if args.summary and len(self.complexity_table) > 0:
            output_file.write("\nTotal cumulative statistics\n")
            self.pretty_print_summary(output_file)            
    
    def print_module_stats(self, args, output_file):
        """Print module statistics"""
        if args.module_stats and len(self.complexity_table) > 0:
            output_file.write("\nModule statistics\n")
            display_format = {}
            display_format['header'] = ["Name", "Count", "Sum", "Min", "Avg", "Max"]
            display_format['col_align'] = ['<', '>', '>', '>', '>', '>'] 
            display_format['pad_left'] = [1, 1, 1, 1, 1, 1]
            display_format['pad_right'] = [1, 1, 1, 1, 1, 1]
            self.pretty_print(self.module_table, display_format, output_file)              
        
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
