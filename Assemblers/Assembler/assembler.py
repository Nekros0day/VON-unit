import sys
import re

# Define the instruction set with their 5-bit opcodes
INSTRUCTION_SET = {
    'LDA': '00000',
    'LDB': '00001',
    'LDC': '00010',
    'LDD': '00011',
    'LDX': '00100',
    'LDY': '00101',
    'LPR': '00110',
    'ADD': '00111',
    'SUB': '01000',
    'XOR': '01001',
    'OUT': '01010',
    'ITA': '01011',
    'STA': '01100',
    'JMP': '01101',
    'JAZ': '01110',
    'JXZ': '01111',
    'JYZ': '10000',
    'JMS': '10001',
    'RFS': '10010',
    'XIC': '10011',
    'YIC': '10100',
    'XDC': '10101',
    'YDC': '10110',
    'DIQ': '10111',
    'HLT': '11000',
    'ICR': '11001',
    'CMP': '11010',
    'LDI': '11011',
    # '11100' to '11111' are unassigned
}

# Regular expressions for parsing
LABEL_REGEX = re.compile(r'^(\w+):')
INSTR_REGEX = re.compile(r'^\s*(\w+)(?:\s+([^;]+))?(?:;.*)?$')
CHAR_REGEX = re.compile(r"^'(.)'$")
STRING_REGEX = re.compile(r'^"(.+)"$')

def parse_operand(operand):
    if operand is None:
        return None
    operand = operand.strip()
    if CHAR_REGEX.match(operand):
        # Return ASCII value of character
        return ord(CHAR_REGEX.match(operand).group(1))
    elif STRING_REGEX.match(operand):
        # Return list of ASCII values for each character
        return [ord(c) for c in STRING_REGEX.match(operand).group(1)]
    elif operand.startswith('HIGH(') and operand.endswith(')'):
        label = operand[5:-1]
        return ('HIGH', label)
    elif operand.startswith('LOW(') and operand.endswith(')'):
        label = operand[4:-1]
        return ('LOW', label)
    elif operand.startswith('0x'):
        # Hexadecimal number
        return int(operand, 16)
    elif operand.isdigit():
        # Decimal number
        return int(operand)
    else:
        # Assume it's a label or variable name
        return operand

def assemble_line(line, labels, current_address, pass_num):
    # Remove comments
    line = line.split(';', 1)[0].strip()

    # Check for label
    label_match = LABEL_REGEX.match(line)
    if label_match:
        label = label_match.group(1)
        if pass_num == 1:
            labels[label] = current_address
        line = line[label_match.end():].strip()

    if not line:
        return [], current_address  # Empty line

    instr_match = INSTR_REGEX.match(line)
    if not instr_match:
        raise ValueError(f"Invalid instruction format: {line}")

    mnemonic = instr_match.group(1).upper()
    operand = instr_match.group(2)

    machine_code = []
    increment = 0

    MNEMONICS_WITH_OPERAND_REQUIRED = {'LDI', 'LPR', 'ICR'}
    MNEMONICS_WITH_NO_OPERAND = {'OUT', 'ITA', 'RFS', 'XIC', 'YIC', 'XDC', 'YDC', 'DIQ', 'HLT', 'CMP'}
    MNEMONICS_WITH_OPTIONAL_OPERAND = {
        'LDA', 'LDB', 'LDC', 'LDD', 'LDX', 'LDY',
        'STA', 'ADD', 'SUB', 'XOR', 'JMS'
    }
    # Instructions that require LPR when an operand is provided
    MNEMONICS_LPR_BEFORE = {'JMP', 'JAZ', 'JXZ', 'JYZ'}

    if mnemonic == 'DB':
        if operand is None:
            raise ValueError("DB requires an operand")
        # Define byte(s)
        data = parse_operand(operand)
        if isinstance(data, list):
            machine_code.extend(data)
            increment += len(data)
        else:
            machine_code.append(data)
            increment += 1

    elif mnemonic == 'DW':
        if operand is None:
            raise ValueError("DW requires an operand")
        # Define word (16-bit)
        data = parse_operand(operand)
        # Store in little-endian order
        low_byte = data & 0xFF
        high_byte = (data >> 8) & 0xFF
        machine_code.extend([low_byte, high_byte])
        increment += 2

    elif mnemonic == 'PRINT' or mnemonic == 'PRINTLN':
        if operand is None:
            raise ValueError(f"{mnemonic} requires an operand")
        data = parse_operand(operand)
        if isinstance(data, list):
            for char_code in data:
                # LDI char_code
                machine_code.append(int(INSTRUCTION_SET['LDI'], 2))
                machine_code.append(char_code & 0xFF)
                increment += 2
                current_address += 2
                # OUT
                machine_code.append(int(INSTRUCTION_SET['OUT'], 2))
                increment += 1
                current_address += 1
            if mnemonic == 'PRINTLN':
                # Add CR and LF in correct order (CR first, then LF)
                machine_code.append(int(INSTRUCTION_SET['LDI'], 2))
                machine_code.append(10)
                machine_code.append(int(INSTRUCTION_SET['OUT'], 2))
                machine_code.append(int(INSTRUCTION_SET['LDI'], 2))
                machine_code.append(13)
                machine_code.append(int(INSTRUCTION_SET['OUT'], 2))
                increment += 6
                current_address += 6
        else:
            raise NotImplementedError(f"{mnemonic} for numbers or variables is not implemented")
        return machine_code, current_address

    else:
        # Existing instruction handling
        if mnemonic in INSTRUCTION_SET:
            opcode = INSTRUCTION_SET[mnemonic]
            if mnemonic in MNEMONICS_WITH_OPERAND_REQUIRED:
                if operand is None:
                    raise ValueError(f"Instruction {mnemonic} requires an operand")
                data = parse_operand(operand)
                machine_code.append(int(opcode, 2))
                increment += 1

                if mnemonic == 'LDI':
                    # Immediate value follows
                    if isinstance(data, tuple):
                        func, label = data
                        if pass_num == 2:
                            address = labels.get(label)
                            if address is None:
                                raise ValueError(f"Undefined label: {label}")
                            if func == 'HIGH':
                                machine_code.append((address >> 8) & 0xFF)
                            elif func == 'LOW':
                                machine_code.append(address & 0xFF)
                        else:
                            machine_code.append(0)
                    elif isinstance(data, str):
                        if pass_num == 2:
                            value = labels.get(data)
                            if value is None:
                                raise ValueError(f"Undefined label: {data}")
                            machine_code.append(value & 0xFF)
                        else:
                            machine_code.append(0)
                    else:
                        machine_code.append(data & 0xFF)
                    increment += 1

                elif mnemonic == 'LPR':
                    # Load 16-bit address into PR
                    machine_code.append(int(opcode, 2))
                    increment += 1
                    if isinstance(data, str):
                        if pass_num == 2:
                            address = labels.get(data)
                            if address is None:
                                raise ValueError(f"Undefined label: {data}")
                            # Store in little-endian order
                            low_byte = address & 0xFF
                            high_byte = (address >> 8) & 0xFF
                            machine_code.extend([low_byte, high_byte])
                        else:
                            machine_code.extend([0, 0])
                    else:
                        # Store in little-endian order
                        low_byte = data & 0xFF
                        high_byte = (data >> 8) & 0xFF
                        machine_code.extend([low_byte, high_byte])
                    increment += 2

                else:
                    # For other instructions with operands
                    if isinstance(data, int):
                        machine_code.append(data & 0xFF)
                    else:
                        raise ValueError(f"Invalid operand for instruction {mnemonic}")
                    increment += 1

            elif mnemonic in MNEMONICS_WITH_NO_OPERAND:
                if operand is not None:
                    raise ValueError(f"Instruction {mnemonic} does not take an operand")
                machine_code.append(int(opcode, 2))
                increment += 1

            elif mnemonic in MNEMONICS_WITH_OPTIONAL_OPERAND or mnemonic in MNEMONICS_LPR_BEFORE:
                if operand is not None:
                    # Operand provided, insert LPR instruction
                    data = parse_operand(operand)
                    lpr_opcode = int(INSTRUCTION_SET['LPR'], 2)
                    machine_code.append(lpr_opcode)
                    increment += 1

                    if isinstance(data, str):
                        if pass_num == 2:
                            address = labels.get(data)
                            if address is None:
                                raise ValueError(f"Undefined label: {data}")
                            # Store in little-endian order
                            low_byte = address & 0xFF
                            high_byte = (address >> 8) & 0xFF
                            machine_code.extend([low_byte, high_byte])
                        else:
                            machine_code.extend([0, 0])
                    else:
                        # Store in little-endian order
                        low_byte = data & 0xFF
                        high_byte = (data >> 8) & 0xFF
                        machine_code.extend([low_byte, high_byte])
                    increment += 2

                # Add the original instruction
                machine_code.append(int(opcode, 2))
                increment += 1

            else:
                raise ValueError(f"Unknown instruction {mnemonic}")
        else:
            raise ValueError(f"Unknown mnemonic: {mnemonic}")

    return machine_code, current_address + increment

def assemble(assembly_lines):
    labels = {}
    machine_code = []
    current_address = 0

    # First pass: collect labels
    for line in assembly_lines:
        try:
            _, current_address = assemble_line(line, labels, current_address, pass_num=1)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    # Second pass: generate machine code
    current_address = 0
    for line in assembly_lines:
        try:
            code, current_address = assemble_line(line, labels, current_address, pass_num=2)
            machine_code.extend(code)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    return machine_code

def main():
    if len(sys.argv) != 3:
        print("Usage: python assembler.py input.asm output.bin")
        sys.exit(1)

    input_filename = sys.argv[1]
    output_filename = sys.argv[2]

    try:
        with open(input_filename, 'r') as f:
            assembly_lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File {input_filename} not found.")
        sys.exit(1)

    machine_code = assemble(assembly_lines)

    with open(output_filename, 'wb') as f:
        f.write(bytearray(machine_code))

    print(f"Assembled {input_filename} to {output_filename} successfully.")

if __name__ == "__main__":
    main()
