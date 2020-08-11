import sys


class Stack:
    def __init__(self, size=1024):

        self.size = size
        self.__stk = []

    def put(self, value: int, index=0):
        """
        In stack all values are uint256.
        To store negative value I use
        toTwosComplement() function
        """

        value = toTwosComplement(value, self.size)
        self.__stk.insert(index, value)

    def popTop(self, sign=False):
        """
        since stack contains only unsign values,
        to get sign value set sign-flag true
        """

        if not self.__stk.__len__():
            raise IndexError

        if sign:
            return fromTwosComplement(self.__stk.pop(0), self.size)
        else:
            return self.__stk.pop(0)

    #
    # The same functions, but without add/remove and with indexes
    #

    def setElement(self, index, value):
        value = toTwosComplement(value, self.size)
        self.__stk[index] = value

    def getElement(self, index, sign=False):
        return None if index >= self.__stk.__len__() \
            else fromTwosComplement(self.__stk[index], self.size) \
            if sign else self.__stk[index]

    #

    def pprint(self):
        messageToPrint = 'Stack: '

        for value in self.__stk:
            if str(value).__len__() > 20:
                messageToPrint += f"| {hex(value)[:10]}..{hex(value)[-10:]} "
            else:
                messageToPrint += f"| {hex(value)} "
        if self.__stk.__len__() == 0:
            messageToPrint += "| EMPTY STACK "
        messageToPrint += "|"

        print(messageToPrint)

    def __len__(self):
        return self.__stk.__len__()


opcodes = {
    0x00: ['STOP', 0, 0, 0],
    0x01: ['ADD', 2, 1, 3],
    0x02: ['MUL', 2, 1, 5],
    0x03: ['SUB', 2, 1, 3],
    0x04: ['DIV', 2, 1, 5],
    0x05: ['SDIV', 2, 1, 5],
    0x06: ['MOD', 2, 1, 5],
    0x07: ['SMOD', 2, 1, 5],
    0x08: ['ADDMOD', 3, 1, 8],
    0x09: ['MULMOD', 3, 1, 8],
    0x0a: ['EXP', 2, 1, 10],
    0x0b: ['SIGNEXTEND', 2, 1, 5],
    0x10: ['LT', 2, 1, 3],
    0x11: ['GT', 2, 1, 3],
    0x12: ['SLT', 2, 1, 3],
    0x13: ['SGT', 2, 1, 3],
    0x14: ['EQ', 2, 1, 3],
    0x15: ['ISZERO', 1, 1, 3],
    0x16: ['AND', 2, 1, 3],
    0x17: ['OR', 2, 1, 3],
    0x18: ['XOR', 2, 1, 3],
    0x19: ['NOT', 1, 1, 3],
    0x1a: ['BYTE', 2, 1, 3],
    0x1b: ['SHL', 2, 1, 3],
    0x1c: ['SHR', 2, 1, 3],
    0x1d: ['SAR', 2, 1, 3],
    0x35: ['CALLDATALOAD', 1, 1, 3],
    0x36: ['CALLDATASIZE', 0, 1, 2],
    0x37: ['CALLDATACOPY', 3, 0, 3],
    0x3d: ['RETURNDATASIZE', 0, 1, 2],
    0x3e: ['RETURNDATACOPY', 3, 0, 3],
    0x50: ['POP', 1, 0, 2],
    0x51: ['MLOAD', 1, 1, 3],
    0x52: ['MSTORE', 2, 0, 3],
    0x53: ['MSTORE8', 2, 0, 3],
    0x54: ['SLOAD', 1, 1, 50],
    0x55: ['SSTORE', 2, 0, 0],
    0x56: ['JUMP', 1, 0, 8],
    0x57: ['JUMPI', 2, 0, 10],
    0x58: ['PC', 0, 1, 2],
    0x59: ['MSIZE', 0, 1, 2],
    0x5b: ['JUMPDEST', 0, 0, 1],
    0xf3: ['RETURN', 2, 0, 0],
    0xf5: ['CALLBLACKBOX', 7, 1, 40],
    0xfa: ['STATICCALL', 6, 1, 40],
    0xfd: ['REVERT', 2, 0, 0],
    0xff: ['SUICIDE', 1, 0, 0]
}

opcodesMetropolis = {0x3d, 0x3e, 0xfa, 0xfd}

for i in range(1, 33):
    opcodes[0x5f + i] = ['PUSH' + str(i), 0, 1, 3]

for i in range(1, 17):
    opcodes[0x7f + i] = ['DUP' + str(i), i, i + 1, 3]
    opcodes[0x8f + i] = ['SWAP' + str(i), i + 1, i + 1, 3]


def safe_ord(value):
    if isinstance(value, int):
        return value
    else:
        return ord(value)


def signInt(integer, limit):
    a = 2 ** limit
    return integer if integer < a else integer - a


def toTwosComplement(value, bits):
    # If value < 0 then inverse bits and add 1
    if value < 0:
        value = 2 ** bits + value

    # Apply the mask 0xFFFF...FF
    return value & (2 ** bits - 1)


def fromTwosComplement(value: int, bits: int):
    if value > 2 ** (bits - 1) - 1:
        return -(2 ** bits - value)
    return value


def fromByteToInt(value: bytes):
    return int(value.hex(), 16)


def extendMemory(memory: bytearray, toIndex: int):
    to_extend = toIndex - memory.__len__()
    memory.extend(b'\x00' * to_extend)
    return memory


def pprintMemory(memory: bytearray, printAll=True):
    memoryHex = memory.hex()
    if memoryHex.__len__() > 20 and not printAll:
        memoryHex = f"{memoryHex[:10]}...{memoryHex[-10:]}"
    print(f"Memory: 0x{memoryHex}")


def fromByteArrayToInt(barray: bytearray):
    return int(barray.hex(), 16)


def printError(message):
    print(f"Error: {message}")
    exit()


def generateInput(params):
    calldata = ''
    for i in params:
        calldata += hex(i)[2:].zfill(64)[-64:]
    message = bytearray(bytes.fromhex(calldata))
    print(f'msg.data: {message}')
    return message


def execute(code: bytearray, stack: Stack, memory: bytearray, storage: dict, msg: bytearray, toprint=False, break_on_pc=None):
    """
    :param code: e.g. b'\0x60\0x01\0x60\0x01\0x01'
    :param stack: Stack() instance
    :param memory: bytearray for memory
    :param storage: dict for storage
    :param msg: msg.data, call data values
    :param toprint: if true then it will print status after each instruction
    """
    pc = 0

    while pc < code.__len__():

        # input()


        # |60|03|60|04|01|
        #        /\
        #        ||
        #        pc = 0002

        opcode = code[pc]

        if opcode not in opcodes:
            raise KeyError(f"I can not find such opcode '{opcode}'. pc = {pc}")

        opcodename, in_args, out_args, fee = opcodes[opcode]

        if len(stack) < in_args:
            print(f"Error: stack has length {len(stack)} but {opcodename} (PC={pc}) has to have {in_args} input args.")
            return b""

        amountOfArgs = 0
        # -----------
        # 0x00 - 0x10
        # -----------

        if opcodename == "STOP":
            return b""
        elif opcodename == "ADD":
            a, b = stack.popTop(sign=True), stack.popTop(sign=True)
            stack.put(a + b)
        elif opcodename == "MUL":
            stack.put(stack.popTop(sign=True) * stack.popTop(sign=True))
        elif opcodename == "SUB":
            stack.put(stack.popTop(sign=True) - stack.popTop(sign=True))
        elif opcodename == "DIV":
            a, b = stack.popTop(), stack.popTop()
            stack.put(0 if b == 0 else a // b)
        elif opcodename == "SDIV":
            a, b = stack.popTop(sign=True), stack.popTop(sign=True)
            stack.put(0 if b == 0 else a // b)
        elif opcodename == "MOD":
            a, b = stack.popTop(), stack.popTop()
            stack.put(0 if b == 0 else a % b)
        elif opcodename == "SMOD":
            a, b = stack.popTop(sign=True), stack.popTop(sign=True)
            stack.put(0 if b == 0 else a % b)
        elif opcodename == "ADDMOD":
            a, b, N = stack.popTop(sign=True), \
                      stack.popTop(sign=True), \
                      stack.popTop(sign=True)
            stack.put(0 if N == 0 else (a + b) % N)
        elif opcodename == "MULMOD":
            a, b, N = stack.popTop(sign=True), \
                      stack.popTop(sign=True), \
                      stack.popTop(sign=True)
            stack.put(0 if N == 0 else (a * b) % N)
        elif opcodename == "EXP":
            stack.put(stack.popTop() ** stack.popTop())
        elif opcodename == "SIGNEXTEND":
            raise Exception("Opcode is not implemented yet")

        # -----------
        # 0x10 - 0x19
        # -----------

        elif opcodename == "LT":
            stack.put(1 if stack.popTop() < stack.popTop() else 0)
        elif opcodename == "GT":
            stack.put(1 if stack.popTop() > stack.popTop() else 0)
        elif opcodename == "SLT":
            a, b = stack.popTop(sign=True), stack.popTop(sign=True)
            stack.put(1 if a < b else 0)
        elif opcodename == "SGT":
            a, b = stack.popTop(sign=True), stack.popTop(sign=True)
            stack.put(1 if a > b else 0)
        elif opcodename == "EQ":
            stack.put(1 if stack.popTop() == stack.popTop() else 0)
        elif opcodename == "ISZERO":
            stack.put(1 if stack.popTop() == 0 else 0)
        elif opcodename == "AND":
            stack.put(stack.popTop() & stack.popTop())
        elif opcodename == "OR":
            stack.put(stack.popTop() | stack.popTop())
        elif opcodename == "XOR":
            stack.put(stack.popTop() ^ stack.popTop())
        elif opcodename == "NOT":
            stack.put(stack.popTop() ^ (2 ** stack.size - 1))

        # -----------
        # 0x1A - 0x1D
        # -----------

        elif opcodename == "BYTE":
            i, x = stack.popTop(), stack.popTop()
            # idk what is it
            stack.put((x >> (248 - i * 8)) & 0xFF)
        elif opcodename == "SHL":
            shift, value = stack.popTop(sign=True), stack.popTop(sign=True)
            stack.put(value << shift)
        elif opcodename == "SHR":
            shift, value = stack.popTop(sign=True), stack.popTop(sign=True)
            stack.put(value >> shift)
        elif opcodename == "SAR":
            shift, value = stack.popTop(), stack.popTop()
            stack.put(value >> shift)

        # --------
        #
        # --------

        elif opcodename == "CALLDATALOAD":
            offset = stack.popTop()

            if offset + 32 > len(msg):
                print(
                    f"Error: message data has length {len(msg)} "
                    f"but {opcodename} (PC={pc}) refers to [{offset}:{offset + 32}]")
                return b""
            value = msg[offset:offset + 32]
            stack.put(fromByteArrayToInt(value))
        elif opcodename == "CALLDATASIZE":
            stack.put(len(msg))
        elif opcodename == "CALLDATACOPY":
            destOffset, offset, length = stack.popTop(), stack.popTop(), stack.popTop()
            if destOffset + length > len(memory):
                print(
                    f"Error: memory has length {len(memory)} "
                    f"but {opcodename} (PC={pc}) refers to [{destOffset}:{destOffset + length}]")
                return b""
            if offset + length > len(msg):
                print(
                    f"Error: message data has length {len(msg)} "
                    f"but {opcodename} (PC={pc}) refers to [{offset}:{offset + length}]")
                return b""

            memory[destOffset:destOffset + length] = msg[offset:offset + length]

        # -----------
        # 0x50 - 0x58
        # -----------

        elif opcodename == "POP":
            stack.popTop()
        elif opcodename == "MLOAD":
            offset = stack.popTop()
            if offset + 32 > len(memory):
                stack.put(0)
            else:
                value = memory[offset:offset + 32]
                stack.put(fromByteToInt(value))
        elif opcodename == "MSTORE":
            offset = stack.popTop()
            value = stack.popTop()
            memory = extendMemory(memory, offset)
            memory[offset:offset + 32] = value.to_bytes(32, byteorder='big')
        elif opcodename == "MSTORE8":
            offset = stack.popTop()
            value = stack.popTop()
            memory = extendMemory(memory, offset)
            memory[offset:offset + 32] = (value & 0xFF).to_bytes(32, byteorder='big')
        elif opcodename == "SLOAD":
            key = stack.popTop(sign=True)
            if key in storage:
                value = storage[key]
            else:
                value = 0
            stack.put(value)
        elif opcodename == "SSTORE":
            key = stack.popTop(sign=True)
            value = stack.popTop(sign=True)
            storage[key] = value
        elif opcodename == "JUMP":
            destination = stack.popTop()
            if code[destination] not in opcodes:
                raise Exception(f"Destination {destination} not in opcodes")
            if code[destination] != 0x5b:
                print(f"Error: Destination has to be JUMPDEST [0x5B] but it is {code[destination]}. (PC={pc})")
                return b""
            pc = destination
        elif opcodename == "JUMPI":
            destination, condition = stack.popTop(), stack.popTop()
            if code[destination] not in opcodes:
                raise Exception(f"Destination {destination} not in opcodes")
            if code[destination] != 0x5b:
                print(f"Error: Destination has to be JUMPDEST [0x5B] but it is {code[destination]}. (PC={pc})")
                return b""
            pc = destination if condition else pc + 1
        elif opcodename == "JUMPDEST":
            pass
        elif opcodename == "PC":
            stack.put(pc)

        # -----------
        # 0x60 - 0x9F
        # -----------

        elif opcodename.startswith("PUSH"):
            amountOfArgs = int(opcodename.replace("PUSH", ""))
            value = fromByteToInt(code[pc + 1:pc + amountOfArgs + 1])
            stack.put(value)
            pc += amountOfArgs
        elif opcodename.startswith("DUP"):
            amountOfArgs = int(opcodename.replace("DUP", "")) - 1
            value = stack.getElement(amountOfArgs)
            stack.put(value)
        elif opcodename.startswith("SWAP"):
            amountOfArgs = int(opcodename.replace("SWAP", ""))
            value1, value2 = stack.getElement(0), stack.getElement(amountOfArgs)
            stack.setElement(0, value2)
            stack.setElement(amountOfArgs, value1)

        # -----------
        # 0xF3 - 0xF3
        # -----------

        elif opcodename == "RETURN":
            offset = stack.popTop()
            length = stack.popTop()
            return memory[offset:offset + length]

        else:
            raise Exception(f"We have not such opcode yet {opcodename}")

        if toprint:
            args = code[pc - amountOfArgs + 1:pc + 1].hex()
            args = [args[i:i + 2] for i in range(0, len(args), 2)]
            print(f"[ {opcodename}{' ' if len(args) != 0 else ''}{' '.join(args)} ] has executed.")

            print(f"PC: {hex(pc)}")

            stack.pprint()

            pprintMemory(memory)

            print(f"Storage: {storage}")
            print('-' * 10)

        # If opcode is JUMP or JUMPI instruction, then skip this step
        if not opcodename in ["JUMP", "JUMPI"]:
            pc += 1

        if break_on_pc != None:
            if pc == break_on_pc:
                return b''

    raise Exception(f"Program finished but no RETURN opcode was met")


def main():
    stack = Stack(1024)
    debug = False

    try:
        input_file = sys.argv[2]
        if len(sys.argv) == 4:
            if sys.argv[3] == "-debug":
                debug = True
    except Exception as e:
        print("Problem with arguments: ", e)
        return 1
    try:
        with open(input_file, mode='r') as f:
            bytecode = f.read().rstrip()
    except Exception as e:
        print(f"Problem with input file {input_file}: ", e)
        return 1
    code = bytes.fromhex(bytecode)
    args = [int(x) for x in sys.stdin.read().rstrip().splitlines()]
    test_on_input = generateInput(args)

    memory = bytearray()
    storage = {}
    # To debug your code, set break_on_pc parameter
    # in some specific value to break execution in some
    # specific place (when PC will be equal this value)
    # E.g. for the code 6000356020350160005260206000F3
    # and break_on_pc=0x5, the break will happen after
    # the second CALLDATALOAD execution
    ans = execute(code, stack, memory, storage, test_on_input, toprint=debug, break_on_pc=None)

    if len(ans) > 0:
        print(f'RETURNED: {int.from_bytes(bytes(ans), byteorder="big")}')
    else:
        print(f'RETURNED: none')


if __name__ == "__main__":
    main()
