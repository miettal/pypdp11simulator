.globl	_main
.text
_main:
~~main:
jsr	r5,csv
mov	$L2,(sp)
jsr	pc,*$_printf
L1:jmp	cret
.globl
.data
L2:.byte 150,145,154,154,157,12,0
