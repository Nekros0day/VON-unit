import numpy as np

# Initialize data arrays for the chips
c1Data = np.zeros(32768, dtype=np.uint8)
c2Data = np.zeros(32768, dtype=np.uint8)

# Micro-instruction lists per chip
c1MicroIns1 = ["TD", "CR", "JMP", "MI", "FI", "RI", "AD1I", "AD2I", "AI", "BI", "CI", "DI", "II", "XinI", "YinI"]
c1MicroIns2 = ["EIO", "IRQDIS", "S4", "N/A", "HLT", "PU", "PD", "CE", "XinINC", "XinDEC", "YinINC", "YinDEC", "S5", "N/A", "N/A"]

c2MicroIns1 = ["RO", "ADO", "AO", "BO", "CO-", "DO", "EO", "XinO", "YinO", "STRO", "SERIALO", "RD", "SR", "INTV", "CO"]
c2MicroIns2 = ["S0", "S1", "S2", "S3"]

# Instructions per row, row one = LDA and so on
Instructions = [
    ["DC", "CO|MI", "RO|II|CE", "ADO|MI", "RO|AI", "0", "0"],
    ["DC", "CO|MI", "RO|II|CE", "ADO|MI", "RO|BI", "0", "0"],
    ["DC", "CO|MI", "RO|II|CE", "ADO|MI", "RO|CI", "0", "0"],
    ["DC", "CO|MI", "RO|II|CE", "ADO|MI", "RO|DI", "0", "0"],
    ["DC", "CO|MI", "RO|II|CE", "ADO|MI", "RO|XinI", "0", "0"],
    ["DC", "CO|MI", "RO|II|CE", "ADO|MI", "RO|YinI", "0", "0"],
    ["DC", "CO|MI", "RO|II|CE", "CO|MI", "RO|AD1I|CE", "CO|MI", "RO|AD2I|CE"],
    ["DC", "CO|MI", "RO|II|CE", "ADO|MI", "RO|BI", "S3|S0|FI", "S3|S0|AI|EO"],
    ["DC", "CO|MI", "RO|II|CE", "ADO|MI", "RO|BI", "S2|S1|S5|FI", "S2|S1|S5|AI|EO"],
    ["DC", "CO|MI", "RO|II|CE", "ADO|MI", "RO|BI", "S2|S1|S4|FI", "S2|S1|S4|AI|EO"],
    ["DC", "CO|MI", "RO|II|CE", "EIO|AO|TD", "AO|TD", "0", "0"],
    ["DC", "CO|MI", "RO|II|CE", "AI|SERIALO", "0", "0", "0"],
    ["DC", "CO|MI", "RO|II|CE", "ADO|MI", "AO|RI", "0", "0"],
    ["DC", "CO|MI", "RO|II|CE", "ADO|JMP", "0", "0", "0"],
    ["ZF", "CO|MI", "RO|II|CE", "ADO|JMP", "0", "0", "0"],
    ["XinZF", "CO|MI", "RO|II|CE", "ADO|JMP", "0", "0", "0"],
    ["YinZF", "CO|MI", "RO|II|CE", "ADO|JMP", "0", "0", "0"],
    ["DC", "CO|MI", "RO|II|CE", "PU", "ADO|JMP", "0", "0"],
    ["DC", "CO|MI", "RO|II|CE", "PD", "0", "0", "0"],
    ["DC", "CO|MI", "RO|II|CE", "XinINC", "0", "0", "0"],
    ["DC", "CO|MI", "RO|II|CE", "YinINC", "0", "0", "0"],
    ["DC", "CO|MI", "RO|II|CE", "XinDEC", "0", "0", "0"],
    ["DC", "CO|MI", "RO|II|CE", "YinDEC", "0", "0", "0"],
    ["DC", "CO|MI", "RO|II|CE", "IRQDIS", "0", "0", "0"],
    ["DC", "CO|MI", "RO|II|CE", "HLT", "0", "0", "0"],
    ["DC", "CO|MI", "RO|II|CE", "CO|MI", "EIO|RO|CR", "RO|CR|CE", "0"],
    ["DC", "CO|MI", "RO|II|CE", "S2|S1|S4|FI", "0", "0", "0"],
    ["DC", "CO|MI", "RO|II|CE", "CO|MI", "RO|AI|CE", "0", "0"],
    ["DC", "CO|MI", "RO|II|CE", "0", "0", "0", "0"],
    ["DC", "CO|MI", "RO|II|CE", "0", "0", "0", "0"],
    ["DC", "CO|MI", "RO|II|CE", "0", "0", "0", "0"],
    ["DC", "CO|MI", "RO|II|CE", "0", "0", "0", "0"]
]

# JMP conditions instructions
conditions = ["CF", "ZF", "AmBF", "APBF", "XinZF", "YinZF", "INT", "DC"]

# Generate the instructions for Chip 1
print("Generating the instructions for Chip 1")
print("Setting Fetch cycle")

# FETCH cycle for Chip 1
for i, instruction in enumerate(Instructions):
    for j in range(1, 3):  # Columns 2 and 3 (index 1 and 2)
        micro_instrs = instruction[j].split('|')
        s = 0
        for micro_instr in micro_instrs:
            if micro_instr in c1MicroIns1:
                s += c1MicroIns1.index(micro_instr) + 1
            if micro_instr in c1MicroIns2:
                s += (c1MicroIns2.index(micro_instr) + 1) << 4
        for p in range(1, 129):
            FlagStateAddress = (p - 1) << 8
            TstateAddress = (j - 1) << 5
            Address = FlagStateAddress + TstateAddress + i
            c1Data[Address] = s

print("Setting Execute cycle")

# Execute cycle for Chip 1
for i, instruction in enumerate(Instructions):
    condition_code = instruction[0]
    Fcon = conditions.index(condition_code) if condition_code in conditions else None
    for j in range(2, len(instruction)):
        micro_instrs = instruction[j].split('|')
        s = 0
        for micro_instr in micro_instrs:
            if micro_instr in c1MicroIns1:
                s += c1MicroIns1.index(micro_instr) + 1
            if micro_instr in c1MicroIns2:
                s += (c1MicroIns2.index(micro_instr) + 1) << 4
        if condition_code == "DC":
            for p in range(1, 129):
                FlagStateAddress = (p - 1) << 8
                TstateAddress = (j - 1) << 5
                Address = FlagStateAddress + TstateAddress + i
                c1Data[Address] = s
        else:
            for p in range(1, 129):
                FlagStateAddress = (p - 1) << 8
                FlagStateAddress = FlagStateAddress | (1 << Fcon)
                TstateAddress = (j - 1) << 5
                Address = FlagStateAddress + TstateAddress + i
                c1Data[Address] = s

print("Setting Interrupt Request handler")

# Interrupt sequence for Chip 1
IRQS = ["PU", "INTV|JMP", "RD|EIO", "RD", "IRQDIS", "0"]

for i in range(len(IRQS)):
    micro_instrs = IRQS[i].split('|')
    s = 0
    for micro_instr in micro_instrs:
        if micro_instr in c1MicroIns1:
            s += c1MicroIns1.index(micro_instr) + 1
        if micro_instr in c1MicroIns2:
            s += (c1MicroIns2.index(micro_instr) + 1) << 4
    for r in range(32):
        for p in range(64):
            FlagStateAddress = p << 8
            TstateAddress = i << 5
            Address = FlagStateAddress + TstateAddress + r + 16384
            c1Data[Address] = s

print("Writing data for Chip 1")
with open('chip1.bin', 'wb') as chip1_file:
    chip1_file.write(c1Data.tobytes())

print("Chip 1 completed as chip1.bin")

# Generate the instructions for Chip 2
print("Generating the instructions for Chip 2")
print("Setting Fetch cycle")

# FETCH cycle for Chip 2
for i, instruction in enumerate(Instructions):
    for j in range(1, 3):  # Columns 2 and 3 (index 1 and 2)
        micro_instrs = instruction[j].split('|')
        s = 0
        for micro_instr in micro_instrs:
            if micro_instr in c2MicroIns1:
                s += c2MicroIns1.index(micro_instr) + 1
            if micro_instr in c2MicroIns2:
                F = c2MicroIns2.index(micro_instr)
                s += (1 << F) << 4
        for p in range(1, 129):
            FlagStateAddress = (p - 1) << 8
            TstateAddress = (j - 1) << 5
            Address = FlagStateAddress + TstateAddress + i
            c2Data[Address] = s

print("Setting Execute cycle")

# Execute cycle for Chip 2
for i, instruction in enumerate(Instructions):
    condition_code = instruction[0]
    Fcon = conditions.index(condition_code) if condition_code in conditions else None
    for j in range(2, len(instruction)):
        micro_instrs = instruction[j].split('|')
        s = 0
        for micro_instr in micro_instrs:
            if micro_instr in c2MicroIns1:
                s += c2MicroIns1.index(micro_instr) + 1
            if micro_instr in c2MicroIns2:
                F = c2MicroIns2.index(micro_instr)
                s += (1 << F) << 4
        if condition_code == "DC":
            for p in range(1, 129):
                FlagStateAddress = (p - 1) << 8
                TstateAddress = (j - 1) << 5
                Address = FlagStateAddress + TstateAddress + i
                c2Data[Address] = s
        else:
            for p in range(1, 129):
                FlagStateAddress = (p - 1) << 8
                FlagStateAddress = FlagStateAddress | (1 << Fcon)
                TstateAddress = (j - 1) << 5
                Address = FlagStateAddress + TstateAddress + i
                c2Data[Address] = s

print("Setting Interrupt Request handler")

# Interrupt sequence for Chip 2
for i in range(len(IRQS)):
    micro_instrs = IRQS[i].split('|')
    s = 0
    for micro_instr in micro_instrs:
        if micro_instr in c2MicroIns1:
            s += c2MicroIns1.index(micro_instr) + 1
        if micro_instr in c2MicroIns2:
            s += (c2MicroIns2.index(micro_instr) + 1) << 4
    for r in range(32):
        for p in range(64):
            FlagStateAddress = p << 8
            TstateAddress = i << 5
            Address = FlagStateAddress + TstateAddress + r + 16384
            c2Data[Address] = s

print("Writing data for Chip 2")
with open('chip2.bin', 'wb') as chip2_file:
    chip2_file.write(c2Data.tobytes())

print("Chip 2 completed as chip2.bin")
print("All Done")
