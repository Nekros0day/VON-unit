; Example Program for the VON Unit
; Demonstrates basic operations, loops, subroutines, and I/O

; Initialize serial communication
ICR 151          ; Initialize serial communication
ICR 150
ICR 150

START:
    ; Print "Hello World"
    PRINTLN "Hello World"

    ; Load immediate value into A
    LDI 42          ; A = 42
    ; Store A into memory location NUM1
    LPR NUM1
    STA             ; Memory[PR] = A

    ; Load immediate value into A and store into NUM2
    LDI 17          ; A = 17
    LPR NUM2
    STA             ; Memory[PR] = A

    ; Perform addition: SUM = NUM1 + NUM2
    LPR NUM1
    LDA             ; A = NUM1
    LPR NUM2
    LDB             ; B = NUM2
    ADD             ; A = A + B
    LPR SUM
    STA             ; SUM = A

    ; Output the sum
    LPR SUM
    LDA             ; A = SUM
    LPR ASCII_OFFSET
    LDB             ; B = ASCII offset ('0')
    ADD             ; Convert to ASCII character
    OUT             ; Output character

    ; Print newline
    LDI 13          ; Carriage Return (CR)
    OUT
    LDI 10          ; Line Feed (LF)
    OUT

    ; Loop demonstration using COUNTER
    LDI 5           ; A = 5
    LPR COUNTER
    STA             ; COUNTER = 5

LOOP_START:
    ; Check if COUNTER == 0
    LPR COUNTER
    LDA             ; A = COUNTER
    LPR ZERO
    LDB             ; B = 0
    CMP             ; Compare A and B
    LPR LOOP_END
    JAZ             ; Jump if A == B

    ; Output 'X'
    LDI 'X'
    OUT

    ; Decrement COUNTER
    LPR COUNTER
    LDA             ; A = COUNTER
    LPR ONE
    LDB             ; B = 1
    SUB             ; A = A - B
    LPR COUNTER
    STA             ; COUNTER = A

    ; Jump back to LOOP_START
    LPR LOOP_START
    JMP

LOOP_END:
    ; Call subroutine to print a message
    LPR SUBROUTINE
    JMS

    ; Halt the program
    HLT

; Subroutine to print a message
SUBROUTINE:
    PRINTLN "Subroutine Called!"
    RFS

; Data definitions
NUM1:
    DB 0            ; Variable to store NUM1
NUM2:
    DB 0            ; Variable to store NUM2
SUM:
    DB 0            ; Variable to store SUM
COUNTER:
    DB 0            ; Loop counter
ZERO:
    DB 0            ; Constant 0
ONE:
    DB 1            ; Constant 1
ASCII_OFFSET:
    DB 48           ; ASCII offset for '0'
