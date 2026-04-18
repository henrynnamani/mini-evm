from util import Stack, Memory, Storage
from opcode_constant import *
from evm_functions import *

class EVM:
    def __init__(self, sender, program, value, gas, calldata = []):
        self.pc = 0
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

    def peek(self): return self.program[self.pc]

    def gas_desc(self, amount):
        if self.gas < amount:
            raise Exception("Out of gas")
        self.gas -= amount

    def should_execute_nex_opcode(self):
        if self.pc > len(self.program) - 1: return False
        if self.stop_flag: return False
        if self.revert_flag: return False

        return True
    
    def run(self):
        while self.should_execute_nex_opcode():
            op = self.program[self.pc]

            if op == STOP_HEX: stop(self)

            elif op == ADD_HEX: add(self)
            elif op == MUL_HEX: mul(self)
            elif op == SUB_HEX:        sub(self)
            elif op == DIV_HEX:        div(self)
            elif op == SDIV_HEX:       sdiv(self)
            elif op == MOD_HEX:        mod(self)
            elif op == SMOD_HEX:       smod(self)
            elif op == ADDMOD_HEX:     addmod(self)
            elif op == MULMOD_HEX:     mulmod(self)
            elif op == EXP_HEX:        exp(self)
            elif op == SIGNEXTEND_HEX: signextend(self)

            elif op == LT_HEX:     lt(self)
            elif op == GT_HEX:     gt(self)
            elif op == SLT_HEX:    slt(self)
            elif op == SGT_HEX:    sgt(self)
            elif op == EQ_HEX:     eq(self)
            elif op == ISZERO_HEX: iszero(self)

            elif op == AND_HEX: and_op(self)
            elif op == OR_HEX:  or_op(self)
            elif op == XOR_HEX: xor_op(self)
            elif op == NOT_HEX: not_op(self)

            elif op == BYTE_HEX: byte(self)
            elif op == SHL_HEX:  shl(self)
            elif op == SHR_HEX:  shr(self)
            elif op == SAR_HEX:  sar(self)

            elif op == ADDRESS_HEX:        address(self)
            elif op == BALANCE_HEX:        balance(self)
            elif op == ORIGIN_HEX:         origin(self)
            elif op == CALLER_HEX:         caller(self)
            elif op == CALLVALUE_HEX:      callvalue(self)
            elif op == CALLDATALOAD_HEX:   calldataload(self)
            elif op == CALLDATASIZE_HEX:   calldatasize(self)
            elif op == CALLDATACOPY_HEX:   calldatacopy(self)
            elif op == CODESIZE_HEX:       codesize(self)
            elif op == CODECOPY_HEX:       codecopy(self)
            elif op == GASPRICE_HEX:       gasprice(self)
            elif op == EXTCODESIZE_HEX:    extcodesize(self)
            elif op == EXTCODECOPY_HEX:    extcodecopy(self)
            elif op == RETURNDATASIZE_HEX: returndatasize(self)
            elif op == RETURNDATACOPY_HEX: returndatacopy(self)
            elif op == EXTCODEHASH_HEX:    extcodehash(self)
            elif op == BLOCKHASH_HEX:      blockhash(self)
            elif op == COINBASE_HEX:       coinbase(self)
            elif op == TIMESTAMP_HEX:      timestamp(self)
            # elif op == NUMBER_HEX:         number(self)
            elif op == PREVRANDAO_HEX:     prevrandao(self)
            # elif op == GASLIMIT_HEX:       gaslimit(self)
            # elif op == CHAINID_HEX:        chainid(self)
            elif op == SELFBALANCE_HEX:    balance(self)
            # elif op == BASEFEE_HEX:        basefee(self)

            elif op == POP_HEX: pop_op(self)

            elif op == MLOAD_HEX:   mload(self)
            elif op == MSTORE_HEX:  mstore(self)
            elif op == MSTORE8_HEX: mstore8(self)
            
            # Storage Operations
            elif op == SLOAD_HEX:  sload(self)
            elif op == SSTORE_HEX: sstore(self)
            
            # Jump Operations
            elif op == JUMP_HEX:     jump(self)
            elif op == JUMPI_HEX:    jumpi(self)
            elif op == PC_HEX:       pc(self)
            elif op == JUMPDEST_HEX: jumpdest(self)
            
            # Transient Storage Operations
            elif op == TLOAD_HEX:  tload(self)
            elif op == TSTORE_HEX: tstore(self)
            
            # Push Operations (0x60-0x7F)
            elif op == PUSH1_HEX:  push_op(self, 1)
            elif op == PUSH2_HEX:  push_op(self, 2)
            elif op == PUSH3_HEX:  push_op(self, 3)
            elif op == PUSH4_HEX:  push_op(self, 4)
            elif op == PUSH5_HEX:  push_op(self, 5)
            elif op == PUSH6_HEX:  push_op(self, 6)
            elif op == PUSH7_HEX:  push_op(self, 7)
            elif op == PUSH8_HEX:  push_op(self, 8)
            elif op == PUSH9_HEX:  push_op(self, 9)
            elif op == PUSH10_HEX: push_op(self, 10)
            elif op == PUSH11_HEX: push_op(self, 11)
            elif op == PUSH12_HEX: push_op(self, 12)
            elif op == PUSH13_HEX: push_op(self, 13)
            elif op == PUSH14_HEX: push_op(self, 14)
            elif op == PUSH15_HEX: push_op(self, 15)
            elif op == PUSH16_HEX: push_op(self, 16)
            elif op == PUSH17_HEX: push_op(self, 17)
            elif op == PUSH18_HEX: push_op(self, 18)
            elif op == PUSH19_HEX: push_op(self, 19)
            elif op == PUSH20_HEX: push_op(self, 20)
            elif op == PUSH21_HEX: push_op(self, 21)
            elif op == PUSH22_HEX: push_op(self, 22)
            elif op == PUSH23_HEX: push_op(self, 23)
            elif op == PUSH24_HEX: push_op(self, 24)
            elif op == PUSH25_HEX: push_op(self, 25)
            elif op == PUSH26_HEX: push_op(self, 26)
            elif op == PUSH27_HEX: push_op(self, 27)
            elif op == PUSH28_HEX: push_op(self, 28)
            elif op == PUSH29_HEX: push_op(self, 29)
            elif op == PUSH30_HEX: push_op(self, 30)
            elif op == PUSH31_HEX: push_op(self, 31)
            elif op == PUSH32_HEX: push_op(self, 32)

            # Dup Operations (0x80-0x8F)
            elif op == DUP1_HEX:  dup_op(self, 1)
            elif op == DUP2_HEX:  dup_op(self, 2)
            elif op == DUP3_HEX:  dup_op(self, 3)
            elif op == DUP4_HEX:  dup_op(self, 4)
            elif op == DUP5_HEX:  dup_op(self, 5)
            elif op == DUP6_HEX:  dup_op(self, 6)
            elif op == DUP7_HEX:  dup_op(self, 7)
            elif op == DUP8_HEX:  dup_op(self, 8)
            elif op == DUP9_HEX:  dup_op(self, 9)
            elif op == DUP10_HEX: dup_op(self, 10)
            elif op == DUP11_HEX: dup_op(self, 11)
            elif op == DUP12_HEX: dup_op(self, 12)
            elif op == DUP13_HEX: dup_op(self, 13)
            elif op == DUP14_HEX: dup_op(self, 14)
            elif op == DUP15_HEX: dup_op(self, 15)
            elif op == DUP16_HEX: dup_op(self, 16)

            # Swap Operations (0x90-0x9F)
            elif op == SWAP1_HEX:  swap_op(self, 1)
            elif op == SWAP2_HEX:  swap_op(self, 2)
            elif op == SWAP3_HEX:  swap_op(self, 3)
            elif op == SWAP4_HEX:  swap_op(self, 4)
            elif op == SWAP5_HEX:  swap_op(self, 5)
            elif op == SWAP6_HEX:  swap_op(self, 6)
            elif op == SWAP7_HEX:  swap_op(self, 7)
            elif op == SWAP8_HEX:  swap_op(self, 8)
            elif op == SWAP9_HEX:  swap_op(self, 9)
            elif op == SWAP10_HEX: swap_op(self, 10)
            elif op == SWAP11_HEX: swap_op(self, 11)
            elif op == SWAP12_HEX: swap_op(self, 12)
            elif op == SWAP13_HEX: swap_op(self, 13)
            elif op == SWAP14_HEX: swap_op(self, 14)
            elif op == SWAP15_HEX: swap_op(self, 15)
            elif op == SWAP16_HEX: swap_op(self, 16)

            # Log Operations
            elif op == LOG0_HEX: log0(self)
            elif op == LOG1_HEX: log1(self)
            elif op == LOG2_HEX: log2(self)
            elif op == LOG3_HEX: log3(self)
            elif op == LOG4_HEX: log4(self)

            # Contract Operations
            elif op == REVERT_HEX:       revert(self)

            else:
                raise Exception(f"Unknown opcode: {hex(op)}")
            
    def reset(self):
        self.pc      = 0
        self.stack   = Stack()
        self.memory  = Memory()
        self.storage = Storage()