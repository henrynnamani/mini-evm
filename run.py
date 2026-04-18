from state import EVM

SIMPLE_ADD = [0x60, 0x42, 0x60, 0xFF, 0x01, 0x55]
GAS = 21_000

evm = EVM(sender=0x1234, program=SIMPLE_ADD, value=0, gas=GAS)

evm.run()

print(evm.stack)