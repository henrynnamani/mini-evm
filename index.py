MAXIMUM_STACK_SIZE = 1024;

class Stack:
    def __init__(self):
        self.items = [];

    def __str__(self):
        ws = []
        for index, item in enumerate(self.items[::-1]):
            if   index == 0                : ws.append(f"{item} <first")
            elif index == len(self.items)-1: ws.append(f"{item} <last") 
            else                       : ws.append(str(item))

        return "\n".join(ws)
        
    def push(self, value):
        if len(self.items) == MAXIMUM_STACK_SIZE - 1: raise Exception("Stack Overflow")
        self.items.append(value)


    def pop(self):
        if len(self.items) == 0: raise Exception("Stack Underflow")
        return self.items.pop()
    
    @property
    def stack(self):
        return self.items.copy()
    
class SimpleMemory:
    def __init__(self):
        self.memory = []

    def access(self, offset, size):
        return self.memory[offset:offset+size]
    def load(self, offset):
        return self.access(offset, 32)
    def store(self, offset, value):
        self.memory[offset:offset+len(value)] = value

class Memory(SimpleMemory):
    def store(self, offset, value):
        old_cost = self.calc_memory_expansion_gas()
        if len(self.memory) <= offset + len(value):
            expansion_size = 0
            if len(self.memory) == 0:
                expansion_size = 32
                self.memory = [0x00 for _ in range(32)]

            if len(self.memory) < offset + len(value):
                expansion_size += offset + len(value) - len(self.memory)
                self.memory.extend([0x00] * expansion_size)

        super().store(offset, value)
        new_cost = self.calc_memory_expansion_gas()
        return new_cost - old_cost
    
    def calc_memory_expansion_gas(self):
        memory_size_word = (len(self.memory) + 31) / 32
        memory_cost = (memory_size_word ** 2) / 512 + (3 * memory_size_word)
        return round(memory_cost)
    
class KeyValue:
    def __init__(self): 
        self.storage = {}

    def load(self, key): 
        return self.storage[key]
    def store(self, key, value): self.storage[key] = value

class Storage(KeyValue):
    def __init__(self):
        super().__init__()
        self.cache = []

    def load(self, key):
        warm = True if key in self.cache else False
        if not warm:
            self.cache.append(key)
        if key not in self.storage: return 0x00
        return warm, super().load(key)

storage = Storage()

storage.store(1, 420)

print(storage.load(1))
print(storage.load(506))
