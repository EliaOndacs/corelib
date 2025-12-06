    .text                       # place code in the executable section
    .globl forwardscale         # make this function visible to C and other languages
    .globl backwardscale        # same here

###############################################################################
# void forwardscale(const char* in, char* out)
#
# Arguments (SysV x86_64 ABI):
#   rdi = pointer to input string
#   rsi = pointer to output buffer
#
# This loop:
#   output[i] = input[i] + (i + 1)
###############################################################################
forwardscale:
    pushq   %rbx                # save rbx since it's a callee-saved register

    xor     %rdx, %rdx          # rdx = index = 0

# --- loop start -------------------------------------------------------------
.Lf_loop:
    movzbq  (%rdi,%rdx), %rax   # load input[i] as zero-extended byte into rax
    test    %al, %al            # check if input[i] == 0 (end of string)
    je      .Lf_done            # if zero, we're done

    mov     %dl, %bl            # copy index (rdx low byte) into bl
    inc     %bl                 # bl = index + 1

    add     %bl, %al            # al = input[i] + (index+1)
    movb    %al, (%rsi,%rdx)    # store result into output[i]

    inc     %rdx                # index++
    jmp     .Lf_loop            # repeat loop

# --- end of string ----------------------------------------------------------
.Lf_done:
    movb    $0, (%rsi,%rdx)     # write null terminator
    popq    %rbx                # restore saved register
    ret                         # return to caller

###############################################################################
# void backwardscale(const char* in, char* out)
#
# Exactly the same as above except it subtracts instead of adds.
###############################################################################
backwardscale:
    pushq   %rbx                # save rbx (callee-saved)

    xor     %rdx, %rdx          # index = 0

# --- loop start -------------------------------------------------------------
.Lb_loop:
    movzbq  (%rdi,%rdx), %rax   # load input[i]
    test    %al, %al            # is it '\0'?
    je      .Lb_done            # yes -> exit loop

    mov     %dl, %bl            # bl = index
    inc     %bl                 # bl = index + 1

    sub     %bl, %al            # al = input[i] - (index+1)
    movb    %al, (%rsi,%rdx)    # write result

    inc     %rdx                # index++
    jmp     .Lb_loop            # loop again

# --- end of string ----------------------------------------------------------
.Lb_done:
    movb    $0, (%rsi,%rdx)     # null-terminate
    popq    %rbx                # restore register
    ret                         # return to caller

