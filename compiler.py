import sys


class CodeBlock:  # mk - code of prog start pos

    def __init__(self, is_function=False, pre_output='', func_name='', start_pos=0, func_params=()):
        self.output = pre_output
        self.is_function = is_function
        self.func_name = func_name
        self.start_pos = start_pos
        self.func_params = func_params
        self.while_stack = []

    def prog(self, *program_blocks):
        if self.is_function:
            self.output += '5b'
        for block in program_blocks:
            self.execute(block)
        if self.is_function:
            self.load_from_memory()
            self.output += '56'

    def oper_while(self, condition, body):
        hex_code = hex(len(self.output) // 2)[2:].rjust(4, '0')
        self.while_stack.append(len(self.while_stack) + 1)
        my_code = hex(self.while_stack[-1])[2:].rjust(2, '0')
        self.output += '5b'
        self.execute(condition)
        self.output += '1561{' + my_code + '}57'
        self.execute(body)
        self.output += '61' + hex_code + '56'
        current_pos = hex(len(self.output) // 2)[2:].rjust(4, '0')
        self.output += '5b'
        self.output = self.output.replace('{' + my_code + '}', current_pos)
        self.while_stack.pop()

    def oper_break(self):
        current_code = hex(self.while_stack[-1])[2:].rjust(2, '0')
        self.output += '61{' + current_code + '}56'

    def cond(self, condition, success, fail=None):
        if fail is None:
            self.execute(condition)
            self.output += '1561____57'
            change_index = len(self.output) - 6
            self.execute(success)
            self.output = self.output[:change_index] + hex(len(self.output) // 2)[2:].rjust(4, '0') + self.output[change_index + 4:]
            self.output += '5b'
        else:
            self.execute(condition)
            self.output += '1561____57'
            change_index1 = len(self.output) - 6
            self.execute(success)
            self.output += '61____56'
            change_index2 = len(self.output) - 6
            self.output = self.output[:change_index1] + hex(len(self.output) // 2)[2:].rjust(4, '0') + self.output[change_index1 + 4:]
            self.output += '5b'
            self.execute(fail)
            self.output = self.output[:change_index2] + hex(len(self.output) // 2)[2:].rjust(4, '0') + self.output[change_index2 + 4:]
            self.output += '5b'

    def setq(self, key, value, for_func=None, external=False):
        if not self.is_function and for_func is None:
            self.execute(value)
            self.decode_and_push_var(key)
            self.output += '55'
        else:
            if for_func is None:
                self.set_function_var(key, value, self.func_name, external)
            else:
                self.set_function_var(key, value, for_func, external)

    def read(self, arg):
        self.execute(arg)
        self.output += '60200235'

    def return_func(self, value):
        self.execute(value)
        if not self.is_function:
            self.output += '60005260206000f3'
        else:
            self.load_from_memory()
            self.output += '56'

    def plus(self, arg1, arg2):
        self.execute(arg1)
        self.execute(arg2)
        self.output += '01'

    def minus(self, arg1, arg2):
        self.execute(arg2)
        self.execute(arg1)
        self.output += '03'

    def times(self, arg1, arg2):
        self.execute(arg1)
        self.execute(arg2)
        self.output += '02'

    def divide(self, arg1, arg2):
        self.execute(arg2)
        self.execute(arg1)
        self.output += '04'

    def equal(self, arg1, arg2):
        self.execute(arg2)
        self.execute(arg1)
        self.output += '14'

    def nonequal(self, arg1, arg2):
        self.execute(arg2)
        self.execute(arg1)
        self.output += '1415'

    def less(self, arg1, arg2):
        self.execute(arg2)
        self.execute(arg1)
        self.output += '10'

    def lesseq(self, arg1, arg2):
        self.execute(arg2)
        self.execute(arg1)
        self.output += '10'
        main_prog.equal(arg1, arg2)
        self.output += '17'

    def greater(self, arg1, arg2):
        self.execute(arg2)
        self.execute(arg1)
        self.output += '11'

    def greatereq(self, arg1, arg2):
        self.execute(arg2)
        self.execute(arg1)
        self.output += '11'
        main_prog.equal(arg1, arg2)
        self.output += '17'

    def oper_and(self, arg1, arg2):
        self.execute(arg2)
        self.execute(arg1)
        self.output += '16'  # 02

    def oper_or(self, arg1, arg2):
        self.execute(arg2)
        self.execute(arg1)
        self.output += '17'  # 01

    def oper_not(self, arg):
        self.execute(arg)
        self.output += '15'

    # Utils functions

    def to_hex(self, data):
        return hex(data)[2:].rjust(2, '0')

    def execute(self, arg):
        if type(arg) == list:
            if type(arg[0]) == list:
                for item in arg:
                    self.execute(item)
            else:
                if arg[0] in sp_list:
                    eval('self.' + sp_list[arg[0]])(*arg[1:])
                else:
                    if arg[0] in functions:
                        need_params = functions[arg[0]]['params']
                    else:
                        need_params = self.func_params
                    # load vars to memory
                    for i in range(len(need_params)):
                        self.setq(need_params[i], self.execute(arg[1:][i]), for_func=arg[0], external=True)  # TODO !!!!
                    # change recursion depth +1
                    self.load_unsized_data(self.encode_var(arg[0]))
                    self.output += '54600101'
                    self.load_unsized_data(self.encode_var(arg[0]))
                    self.output += '55'
                    # load return code to memory
                    # self.save_to_memory(hex(len(self.output) // 2 + 21)[2:].rjust(4, '0'))
                    self.save_position_to_memory()
                    # make jump to function
                    if arg[0] in functions:
                        self.output += '61' + functions[arg[0]]['start_pos'] + '565b'
                    else:
                        self.output += '61' + hex(self.start_pos)[2:].rjust(4, '0') + '565b'
                    # change recursion depth -1
                    self.output += '6001'
                    self.load_unsized_data(self.encode_var(arg[0]))
                    self.output += '5403'
                    self.load_unsized_data(self.encode_var(arg[0]))
                    self.output += '55'

        elif type(arg) == str:
            if arg.isdigit():
                self.push_number(int(arg))
            else:
                self.load_var(arg)

    def decode_and_push_var(self, name, global_context=True):  # TODO change when add functions
        self.output += hex(95 + len(name))[2:] + self.encode_var(name)

    def push_number(self, data):
        hex_data = hex(data)[2:]
        length = len(hex_data)
        if length % 2 != 0:
            hex_data = '0' + hex_data
            length += 1
        self.output += hex(95 + length // 2)[2:] + hex_data

    @staticmethod
    def resolve_number(data):
        hex_data = hex(data)[2:].rjust(4, '0')
        return hex_data

    def load_unsized_data(self, data):  # data is decoded
        self.output += hex(95 + len(data) // 2)[2:] + data

    def set_function_var(self, varname, value, funcname, external=False):
        self.execute(value)
        self.output += '600101'
        varname = '1' + funcname + varname
        encoded = self.encode_var(varname) + '00'
        self.load_unsized_data(encoded)
        self.load_unsized_data(self.encode_var(funcname))
        self.output += '5401'
        if external:
            self.output += '600101'
        self.output += '55'

    def load_function_var(self, varname, funcname):
        varname_en = '1' + funcname + varname
        encoded = self.encode_var(varname_en) + '00'
        self.output += '6001'
        self.load_unsized_data(encoded)
        self.load_unsized_data(self.encode_var(funcname))
        self.output += '5401548061____575050'
        change_index1 = len(self.output) - 10
        self.load_unsized_data(self.encode_var(varname))
        self.output += '5461____56'
        change_index2 = len(self.output) - 6
        self.output = self.output[:change_index1] + hex(len(self.output) // 2)[2:].rjust(4, '0') + self.output[change_index1 + 4:]
        self.output += '5b03'
        self.output = self.output[:change_index2] + hex(len(self.output) // 2)[2:].rjust(4, '0') + self.output[change_index2 + 4:]
        self.output += '5b'

    def encode_var(self, name):  # TODO change when add functions
        res = ''
        for symbol in name:
            res += hex(ord(symbol))[2:]
        return res

    def load_var(self, varname):
        if not self.is_function:
            self.decode_and_push_var(varname)
            self.output += '54'
        else:
            self.load_function_var(varname, self.func_name)

    def save_to_memory(self, data):
        self.output += '61' + data + '6000516001018060005260200252'

    def save_position_to_memory(self):
        self.output += '586016016000516001018060005260200252'

    def load_from_memory(self):
        self.output += '600051806001900360005260200251'


def lexer(raw_code):
    raw_code = raw_code.replace(')', ' ) ').replace('(', ' ( ')
    operators = raw_code.split()
    return operators


def set_depth_level(code_tree, level):
    piece = code_tree
    for i in range(level):
        piece = piece[-1]
    return piece


def parser(tokens):
    code_tree = []
    current_level = code_tree
    level = 0
    for token in tokens:
        if token == '(':
            current_level.append([])
            current_level = current_level[-1]
            level += 1
            continue
        if token == ')':
            level -= 1
            current_level = set_depth_level(code_tree, level)
            continue
        current_level.append(token)
    return code_tree


def postprocess():
    output = main_prog.output
    output = output.format(mk=prog_start)
    main_prog.output = output


main_prog = CodeBlock()

sp_list = {
    'prog': "prog",
    'cond': "cond",
    "while": "oper_while",
    "break": "oper_break",
    'setq': "setq",
    'read': "read",
    'return': "return_func",
    'plus': "plus",
    'minus': "minus",
    'times': "times",
    'divide': "divide",
    'equal': "equal",
    'nonequal': "nonequal",
    'less': "less",
    'lesseq': "lesseq",
    'greater': "greater",
    'greatereq': "greatereq",
    'and': "oper_and",
    'or': "oper_or",
    'not': "oper_not"
}

prog_start = '0000'

functions = {}


def main():
    global prog_start
    try:
        input_file = sys.argv[2]
        output_file = sys.argv[4]
    except Exception as e:
        print("Problem with arguments: ", e)
        return 1
    try:
        with open(input_file, mode='r') as f:
            code = f.read().rstrip()
    except Exception as e:
        print(f"Problem with input file {input_file}: ", e)
        return 1
    code_tree = parser(lexer(code))
    global_output = '61{mk}56'
    for block in code_tree:
        if block[0] == 'prog':
            prog_start = CodeBlock.resolve_number(len(global_output) // 2)
            main_prog.start_pos = prog_start
            global_output += '5b'
            main_prog.output = global_output
            main_prog.prog(*block[1])
            break
        start_pos = len(global_output) // 2
        func = CodeBlock(is_function=True, pre_output=global_output, func_name=block[1], start_pos=start_pos, func_params=block[2])
        func.prog(block[3])
        global_output = func.output
        functions[block[1]] = {
            'params': block[2],
            'start_pos': hex(start_pos)[2:].rjust(4, '0'),
            'end_pos': hex(len(global_output) // 2)[2:].rjust(4, '0')
        }
    postprocess()
    try:
        with open(output_file, mode='w+') as f:
            f.write(main_prog.output)
            print(f"Result: {main_prog.output}")
            print("Successfully written to the output file")
    except Exception as e:
        print(f"Problem with output file {output_file}: ", e)
        return 1


if __name__ == "__main__":
    main()
