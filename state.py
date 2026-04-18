from util import Stack, Memory, Storage

class State:
    def __init__(self, sender, program, value, gas, calldata = []):
        self.program_counter = 0
        self.stack = Stack()
        self.memory = Memory()
        self.storage = Storage()

        self.sender = sender
        self.program = program
        self.gas = gas
        self.value = value
        self.calldata = calldata

        self.stop_flag = False
        self.revert_flag = False

        self.returndata = []
        self.logs = []
