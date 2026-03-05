#sukhman did this 
# pull a range of bits out of the instruction (hi and lo are both inclusive)
def get_bits(instr, hi, lo):
    return (instr >> lo) & ((1 << (hi - lo + 1)) - 1)
#sukhman did this 
# sign extend a value that's currently num_bits wide
def sign_ext(val, num_bits):
    sign_bit = 1 << (num_bits - 1)
    if val & sign_bit:
        val -= (1 << num_bits)
    return val

#sukhman did this 
# handles add, sub, and, or, xor, sll, srl, sra, slt, sltu
def decode_r(instr):
    rd = get_bits(instr, 11, 7)
    funct3 = get_bits(instr, 14, 12)
    rs1 = get_bits(instr, 19, 15)
    rs2 = get_bits(instr, 24, 20)
    funct7 = get_bits(instr, 31, 25)

    ops = {
        (0x00, 0): "add",  (0x20, 0): "sub",
        (0x00, 7): "and",  (0x00, 6): "or",
        (0x00, 4): "xor",  (0x00, 1): "sll",
        (0x00, 5): "srl",  (0x20, 5): "sra",
        (0x00, 2): "slt",  (0x00, 3): "sltu",
    }
    op = ops.get((funct7, funct3), "unknown")

    print("Instruction Type: R")
    print(f"Operation: {op}")
    print(f"Rs1: x{rs1}")
    print(f"Rs2: x{rs2}")
    print(f"Rd: x{rd}")
    print(f"Funct3: {funct3}")
    print(f"Funct7: {funct7}")

#cody did this part
# handles addi, andi, ori, xori, slti, sltiu, slli, srli, srai, lb, lh, lw, jalr
def decode_i(instr):
    opcode = get_bits(instr, 6, 0)
    rd = get_bits(instr, 11, 7)
    funct3 = get_bits(instr, 14, 12)
    rs1 = get_bits(instr, 19, 15)
    funct7 = get_bits(instr, 31, 25)
    imm_raw = get_bits(instr, 31, 20)   # 12-bit unsigned, used for hex display
    imm = sign_ext(imm_raw, 12)     # sign extended for decimal display

    if opcode == 0x13:   # arithmetic / shift immediates
        ops = {
            0: "addi", 7: "andi", 6: "ori", 4: "xori",
            2: "slti",  3: "sltiu",
            1: "slli",
        }
        if funct3 == 5:
            op = "srli" if funct7 == 0x00 else "srai"
        else:
            op = ops.get(funct3, "unknown")
    elif opcode == 0x03:   # loads
        op = {0: "lb", 1: "lh", 2: "lw"}.get(funct3, "unknown")
    elif opcode == 0x67:   # jalr
        op = "jalr"
    else:
        op = "unknown"

    print("Instruction Type: I")
    print(f"Operation: {op}")
    print(f"Rs1: x{rs1}")
    print(f"Rd: x{rd}")
    print(f"Immediate: {imm} (or 0x{imm_raw:X})")

#sukhman did this part
# handles sb, sh, sw
def decode_s(instr):
    funct3= get_bits(instr, 14, 12)
    rs1= get_bits(instr, 19, 15)
    rs2= get_bits(instr, 24, 20)
    imm_lo= get_bits(instr, 11, 7)   # imm[4:0]
    imm_hi= get_bits(instr, 31, 25)  # imm[11:5]
    imm_raw= (imm_hi << 5) | imm_lo
    imm= sign_ext(imm_raw, 12)

    op = {0: "sb", 1: "sh", 2: "sw"}.get(funct3, "unknown")

    print("Instruction Type: S")
    print(f"Operation: {op}")
    print(f"Rs1: x{rs1}")
    print(f"Rs2: x{rs2}")
    print(f"Immediate: {imm} (or 0x{imm_raw:X})")

#cody did this part
# handles beq, bne, blt, bge
def decode_sb(instr):
    funct3= get_bits(instr, 14, 12)
    rs1= get_bits(instr, 19, 15)
    rs2= get_bits(instr, 24, 20)

    # reassemble the immediate from its scattered pieces
    imm12 = get_bits(instr, 31, 31)  # sign bit
    imm11 = get_bits(instr, 7, 7)
    imm10_5= get_bits(instr, 30, 25)
    imm4_1= get_bits(instr, 11, 8)

    imm_raw = (imm12 << 12) | (imm11 << 11) | (imm10_5 << 5) | (imm4_1 << 1)
    imm = sign_ext(imm_raw, 13)

    op = {0: "beq", 1: "bne", 4: "blt", 5: "bge"}.get(funct3, "unknown")

    print("Instruction Type: SB")
    print(f"Operation: {op}")
    print(f"Rs1: x{rs1}")
    print(f"Rs2: x{rs2}")
    print(f"Immediate: {imm} (or 0x{imm_raw:X})")

#cody did this part
# only handles jal
def decode_uj(instr):
    rd = get_bits(instr, 11, 7)

    # piece together the UJ immediate from bits scattered around the word
    imm20 = get_bits(instr, 31, 31)  # sign bit
    imm19_12 = get_bits(instr, 19, 12)
    imm11 = get_bits(instr, 20, 20)
    imm10_1 = get_bits(instr, 30, 21)

    imm_raw = (imm20 << 20) | (imm19_12 << 12) | (imm11 << 11) | (imm10_1 << 1)
    imm = sign_ext(imm_raw, 21)

    print("Instruction Type: UJ")
    print("Operation: jal")
    print(f"Rd: x{rd}")
    print(f"Immediate: {imm} (or 0x{imm_raw:X})")

# sukhman did this part
# opcode table
DECODERS = {
    0x33: decode_r,
    0x13: decode_i,
    0x03: decode_i,
    0x67: decode_i,
    0x23: decode_s,
    0x63: decode_sb,
    0x6F: decode_uj,
}
#sukhman did this part
def main():
    while True:
        print("Enter an instruction:")
        try:
            bits = input().strip()
        except EOFError:
            break

        # convert the binary string into an integer we can work with
        instr= int(bits, 2)
        opcode= get_bits(instr, 6, 0)

        decoder = DECODERS.get(opcode)
        if decoder:
            decoder(instr)
        else:
            print(f"Unrecognized opcode: 0x{opcode:X}")

        print()

if __name__ == "__main__":
    main()