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