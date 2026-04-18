import time
import random
import math

from evm_gas_constant import THREE_GAS, FIVE_GAS, EIGHT_GAS

# ── Constants ─────────────────────────────────────────────────────
JUMPDEST          = 0x5B
UINT_256_MAX      = 2**256 - 1
UINT_255_MAX      = 2**255 - 1
SIGN_BIT          = 1 << 255

# ── Helpers ───────────────────────────────────────────────────────
def pos_or_neg(number):
    return -1 if number < 0 else 1

def unsigned_to_signed(value):
    return value if value < 2**255 else value - 2**256

def size_in_bytes(number):
    if number == 0:
        return 1
    bits_needed = math.ceil(math.log2(abs(number) + 1))
    return math.ceil(bits_needed / 8)

def calc_log_gas(topic_count, size, memory_expansion_cost=0):
    return 375 + (375 * topic_count) + (8 * size) + memory_expansion_cost

def is_warm(evm, address):
    """Check if an address is warm and mark it warm if not."""
    warm = address in evm.accessed_addresses
    if not warm:
        evm.accessed_addresses.add(address)
    return warm

# ── Stop ─────────────────────────────────────────────────────────
def stop(evm):
    evm.stop_flag = True

# ── Arithmetic ────────────────────────────────────────────────────
def add(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    evm.stack.push((a + b) & UINT_256_MAX)  # clamp to 256-bit
    evm.pc += 1
    evm.gas_dec(THREE_GAS)

def mul(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    evm.stack.push((a * b) & UINT_256_MAX)
    evm.pc += 1
    evm.gas_dec(FIVE_GAS)

def sub(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    evm.stack.push((a - b) & UINT_256_MAX)
    evm.pc += 1
    evm.gas_dec(THREE_GAS)

def div(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    evm.stack.push(0 if b == 0 else a // b)
    evm.pc += 1
    evm.gas_dec(FIVE_GAS)

def sdiv(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    if b == 0:
        evm.stack.push(0)
    else:
        sign   = pos_or_neg(a * b)
        result = sign * (abs(a) // abs(b))
        evm.stack.push(result & UINT_256_MAX)
    evm.pc += 1
    evm.gas_dec(FIVE_GAS)

def mod(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    evm.stack.push(0 if b == 0 else a % b)
    evm.pc += 1
    evm.gas_dec(FIVE_GAS)

def smod(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    if b == 0:
        evm.stack.push(0)
    else:
        sign   = pos_or_neg(a)
        result = abs(a) % abs(b) * sign
        evm.stack.push(result & UINT_256_MAX)
    evm.pc += 1
    evm.gas_dec(FIVE_GAS)

def addmod(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    N    = evm.stack.pop()
    evm.stack.push(0 if N == 0 else (a + b) % N)
    evm.pc += 1
    evm.gas_dec(EIGHT_GAS)

def mulmod(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    N    = evm.stack.pop()
    evm.stack.push(0 if N == 0 else (a * b) % N)
    evm.pc += 1
    evm.gas_dec(EIGHT_GAS)

def exp(evm):
    a, exponent = evm.stack.pop(), evm.stack.pop()
    evm.stack.push((a ** exponent) & UINT_256_MAX)
    evm.pc += 1
    evm.gas_dec(10 + (50 * size_in_bytes(exponent)))

def signextend(evm):
    b, x = evm.stack.pop(), evm.stack.pop()
    if b <= 31:
        testbit  = b * 8 + 7
        sign_bit = 1 << testbit
        if x & sign_bit:
            result = x | (UINT_256_MAX - sign_bit + 1)
        else:
            result = x & (sign_bit - 1)
    else:
        result = x
    evm.stack.push(result)
    evm.pc += 1
    evm.gas_dec(FIVE_GAS)

# ── Comparison ────────────────────────────────────────────────────
def lt(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    evm.stack.push(1 if a < b else 0)
    evm.pc += 1
    evm.gas_dec(THREE_GAS)

def gt(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    evm.stack.push(1 if a > b else 0)
    evm.pc += 1
    evm.gas_dec(THREE_GAS)

def slt(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    evm.stack.push(1 if unsigned_to_signed(a) < unsigned_to_signed(b) else 0)
    evm.pc += 1
    evm.gas_dec(THREE_GAS)

def sgt(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    evm.stack.push(1 if unsigned_to_signed(a) > unsigned_to_signed(b) else 0)
    evm.pc += 1
    evm.gas_dec(THREE_GAS)

def eq(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    evm.stack.push(1 if a == b else 0)
    evm.pc += 1
    evm.gas_dec(THREE_GAS)

def iszero(evm):
    a = evm.stack.pop()
    evm.stack.push(1 if a == 0 else 0)
    evm.pc += 1
    evm.gas_dec(THREE_GAS)

# ── Bitwise ───────────────────────────────────────────────────────
def _and(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    evm.stack.push(a & b)
    evm.pc += 1
    evm.gas_dec(THREE_GAS)

def _or(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    evm.stack.push(a | b)
    evm.pc += 1
    evm.gas_dec(THREE_GAS)

def _xor(evm):
    a, b = evm.stack.pop(), evm.stack.pop()
    evm.stack.push(a ^ b)
    evm.pc += 1
    evm.gas_dec(THREE_GAS)

def _not(evm):
    a = evm.stack.pop()
    evm.stack.push(~a & UINT_256_MAX)  # mask to keep it 256-bit unsigned
    evm.pc += 1
    evm.gas_dec(THREE_GAS)

def byte(evm):
    i, x = evm.stack.pop(), evm.stack.pop()
    result = 0 if i >= 32 else (x // pow(256, 31 - i)) % 256
    evm.stack.push(result)
    evm.pc += 1
    evm.gas_dec(THREE_GAS)

def shl(evm):
    shift, value = evm.stack.pop(), evm.stack.pop()
    evm.stack.push((value << shift) & UINT_256_MAX)
    evm.pc += 1
    evm.gas_dec(THREE_GAS)

def shr(evm):
    shift, value = evm.stack.pop(), evm.stack.pop()
    evm.stack.push(value >> shift)
    evm.pc += 1
    evm.gas_dec(THREE_GAS)

def sar(evm):
    shift, value = evm.stack.pop(), evm.stack.pop()

    if shift >= 256:
        # if negative, fills with 1s (-1), if positive fills with 0s
        result = 0 if (value >> 255) == 0 else UINT_256_MAX
    else:
        if value & SIGN_BIT:
            signed_value = value - (1 << 256)  # convert to negative
        else:
            signed_value = value
        result = (signed_value >> shift) & UINT_256_MAX

    evm.stack.push(result)
    evm.pc += 1
    evm.gas_dec(THREE_GAS)

# ── Block / Env ───────────────────────────────────────────────────
def address(evm):
    evm.stack.push(evm.sender)
    evm.pc += 1
    evm.gas_dec(2)

def balance(evm):
    addr = evm.stack.pop()
    warm = is_warm(evm, addr)
    evm.stack.push(evm.state[addr].balance if addr in evm.state else 0)
    evm.pc += 1
    evm.gas_dec(100 if warm else 2600)

def origin(evm):
    evm.stack.push(evm.origin)
    evm.pc += 1
    evm.gas_dec(2)

def caller(evm):
    evm.stack.push(evm.caller)
    evm.pc += 1
    evm.gas_dec(2)

def callvalue(evm):
    evm.stack.push(evm.value)
    evm.pc += 1
    evm.gas_dec(2)

def calldataload(evm):
    i        = evm.stack.pop()
    # pad with zeros if calldata is shorter than needed
    raw      = evm.calldata[i:i + 32]
    padded   = raw + bytes(32 - len(raw))  # right-pad with 0x00 bytes
    evm.stack.push(int.from_bytes(padded, "big"))
    evm.pc += 1
    evm.gas_dec(THREE_GAS)

def calldatasize(evm):
    evm.stack.push(len(evm.calldata))
    evm.pc += 1
    evm.gas_dec(2)

def calldatacopy(evm):
    destOffset = evm.stack.pop()
    offset     = evm.stack.pop()
    size       = evm.stack.pop()

    calldata              = evm.calldata[offset:offset + size]
    memory_expansion_cost = evm.memory.store(destOffset, calldata)

    minimum_word_size = (size + 31) // 32
    dynamic_gas       = 3 * minimum_word_size + memory_expansion_cost

    evm.gas_dec(THREE_GAS + dynamic_gas)
    evm.pc += 1

def codesize(evm):
    evm.stack.push(len(evm.program))
    evm.pc += 1
    evm.gas_dec(2)

def codecopy(evm):
    destOffset = evm.stack.pop()
    offset     = evm.stack.pop()
    size       = evm.stack.pop()

    code                  = evm.program[offset:offset + size]
    memory_expansion_cost = evm.memory.store(destOffset, code)

    minimum_word_size = (size + 31) // 32
    dynamic_gas       = 3 * minimum_word_size + memory_expansion_cost

    evm.gas_dec(THREE_GAS + dynamic_gas)
    evm.pc += 1

def gasprice(evm):
    evm.stack.push(evm.gasprice)
    evm.pc += 1
    evm.gas_dec(2)

def extcodesize(evm):
    addr = evm.stack.pop()
    warm = is_warm(evm, addr)
    size = len(evm.state[addr].code) if addr in evm.state else 0
    evm.stack.push(size)
    evm.pc += 1
    evm.gas_dec(100 if warm else 2600)

def extcodecopy(evm):
    addr       = evm.stack.pop()
    destOffset = evm.stack.pop()
    offset     = evm.stack.pop()
    size       = evm.stack.pop()

    warm    = is_warm(evm, addr)
    extcode = evm.state[addr].code[offset:offset + size] if addr in evm.state else bytes(size)

    memory_expansion_cost = evm.memory.store(destOffset, extcode)

    minimum_word_size    = (size + 31) // 32
    dynamic_gas          = 3 * minimum_word_size + memory_expansion_cost
    address_access_cost  = 100 if warm else 2600

    evm.gas_dec(dynamic_gas + address_access_cost)
    evm.pc += 1

def returndatasize(evm):
    evm.stack.push(len(evm.returndata) if evm.returndata else 0)
    evm.pc += 1
    evm.gas_dec(2)

def returndatacopy(evm):
    destOffset = evm.stack.pop()
    offset     = evm.stack.pop()
    size       = evm.stack.pop()

    returndata            = evm.returndata[offset:offset + size]
    memory_expansion_cost = evm.memory.store(destOffset, returndata)

    minimum_word_size = (size + 31) // 32
    dynamic_gas       = 3 * minimum_word_size + memory_expansion_cost

    evm.gas_dec(THREE_GAS + dynamic_gas)
    evm.pc += 1

def extcodehash(evm):
    addr = evm.stack.pop()
    warm = is_warm(evm, addr)
    # push 0 if account doesn't exist, otherwise keccak256 of code
    evm.stack.push(evm.state[addr].code_hash if addr in evm.state else 0)
    evm.pc += 1
    evm.gas_dec(100 if warm else 2600)

def blockhash(evm):
    block_number = evm.stack.pop()
    if block_number > 256:
        raise Exception("Only last 256 blocks can be accessed")
    evm.stack.push(evm.block.get_hash(block_number))
    evm.pc += 1
    evm.gas_dec(20)

def coinbase(evm):
    evm.stack.push(evm.block.coinbase)
    evm.pc += 1
    evm.gas_dec(2)

def timestamp(evm):
    now = int(time.time())
    now -= now % 12  # round down to nearest 12s slot
    evm.stack.push(now)
    evm.pc += 1
    evm.gas_dec(2)

def prevrandao(evm):
    prev_mix_hash = random.randint(0, UINT_256_MAX)
    evm.stack.push(prev_mix_hash)
    evm.pc += 1
    evm.gas_dec(2)

# ── Stack / Memory / Storage ──────────────────────────────────────
def _pop(evm):
    evm.stack.pop()
    evm.pc += 1
    evm.gas_dec(2)

def mload(evm):
    offset        = evm.stack.pop()
    value         = evm.memory.load(offset)
    evm.stack.push(int.from_bytes(value, "big"))
    evm.pc += 1
    evm.gas_dec(THREE_GAS)

def mstore(evm):
    offset, value = evm.stack.pop(), evm.stack.pop()
    # store as 32-byte big-endian
    evm.memory.store(offset, value.to_bytes(32, "big"))
    evm.pc += 1
    evm.gas_dec(THREE_GAS)

def mstore8(evm):
    offset, value = evm.stack.pop(), evm.stack.pop()
    # store only the lowest byte
    evm.memory.store(offset, [value & 0xFF])
    evm.pc += 1
    evm.gas_dec(THREE_GAS)

def sload(evm):
    key          = evm.stack.pop()
    warm, value  = evm.storage.load(key)
    evm.stack.push(value)
    evm.gas_dec(100 if warm else 2100)  # warm=cheap, cold=expensive
    evm.pc += 1

def sstore(evm):
    key, value       = evm.stack.pop(), evm.stack.pop()
    warm, old_value  = evm.storage.store(key, value)

    if value == old_value:
        base_dynamic_gas = 100           # no change — cheapest
    elif old_value == 0:
        base_dynamic_gas = 20000         # writing to empty slot — most expensive
    else:
        base_dynamic_gas = 2900          # modifying existing value

    access_cost = 100 if warm else 2100
    evm.gas_dec(base_dynamic_gas + access_cost)
    evm.pc += 1

def tload(evm):
    key          = evm.stack.pop()
    value        = evm.transient_storage.get(key, 0)
    evm.stack.push(value)
    evm.gas_dec(100)
    evm.pc += 1

def tstore(evm):
    key, value = evm.stack.pop(), evm.stack.pop()
    evm.transient_storage[key] = value
    evm.gas_dec(100)
    evm.pc += 1

# ── Control Flow ─────────────────────────────────────────────────
def jump(evm):
    counter = evm.stack.pop()
    if evm.program[counter] != JUMPDEST:
        raise Exception(f"Invalid jump destination: {counter:#x}")
    evm.pc = counter
    evm.gas_dec(EIGHT_GAS)

def jumpi(evm):
    counter, condition = evm.stack.pop(), evm.stack.pop()
    if condition != 0:
        if evm.program[counter] != JUMPDEST:
            raise Exception(f"Invalid jump destination: {counter:#x}")
        evm.pc = counter
    else:
        evm.pc += 1
    evm.gas_dec(10)

def pc(evm):
    evm.stack.push(evm.pc)
    evm.pc += 1
    evm.gas_dec(2)

def jumpdest(evm):
    evm.pc += 1
    evm.gas_dec(1)

# ── Push / Dup / Swap ─────────────────────────────────────────────
def _push(evm, n):
    evm.pc += 1
    value = []
    for _ in range(n):
        value.append(evm.peek())
        evm.pc += 1
    evm.stack.push(int.from_bytes(bytes(value), "big"))
    evm.gas_dec(THREE_GAS)

def _dup(evm, n):
    value = evm.stack.get(n - 1)  # 1-indexed: DUP1 copies top item
    evm.stack.push(value)
    evm.pc += 1
    evm.gas_dec(THREE_GAS)

def _swap(evm, n):
    top   = evm.stack.get(0)
    other = evm.stack.get(n)
    evm.stack.set(0, other)
    evm.stack.set(n, top)
    evm.pc += 1
    evm.gas_dec(THREE_GAS)

# ── Logs ──────────────────────────────────────────────────────────
class Log:
    def __init__(self, data, *topics):
        self.data   = data
        self.topics = list(topics)

    def __str__(self):
        return f"Log(data={self.data}, topics={self.topics})"

def _log(evm, topic_count):
    offset = evm.stack.pop()
    size   = evm.stack.pop()
    topics = [evm.stack.pop() for _ in range(topic_count)]

    data                  = evm.memory.access(offset, size)
    memory_expansion_cost = evm.memory.store(offset, data)

    log = Log(data, *topics)
    evm.append_log(log)

    evm.pc += 1
    evm.gas_dec(calc_log_gas(topic_count, size, memory_expansion_cost))

def log0(evm): _log(evm, 0)
def log1(evm): _log(evm, 1)
def log2(evm): _log(evm, 2)
def log3(evm): _log(evm, 3)
def log4(evm): _log(evm, 4)

def revert(evm):
    offset, size    = evm.stack.pop(), evm.stack.pop()
    evm.returndata  = evm.memory.access(offset, size)
    evm.stop_flag   = True
    evm.revert_flag = True
    evm.pc += 1
    evm.gas_dec(0)

def _return(evm):
    offset, size   = evm.stack.pop(), evm.stack.pop()
    evm.returndata = evm.memory.access(offset, size)
    evm.stop_flag  = True
    evm.pc += 1
    evm.gas_dec(0)