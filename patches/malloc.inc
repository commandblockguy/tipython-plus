	ld	hl, -6
	call	ti._frameset
	ld	hl, (ix + 6)
	ld	de, 6
	ld	bc, 0
	push	hl
	pop	iy
	add	iy, de
	ld	de, -6
	or	a, a
	sbc	hl, de
	jq	nc, .BB0_11
	lea	hl, iy + 0
	ld	iy, .base
	ld	(ix + -3), hl
.BB0_3:
	lea	de, iy + 0
	ld	iy, (iy)
	lea	hl, iy + 0
	add	hl, bc
	or	a, a
	sbc	hl, bc
	jq	z, .BB0_7
	ld	(ix + -6), de
	ld	bc, (iy + 3)
	push	bc
	pop	hl
	ld	de, (ix + -3)
	or	a, a
	sbc	hl, de
	ld	de, 12
	jq	c, .BB0_3
	ld	hl, (ix + 6)
	add	hl, de
	or	a, a
	sbc	hl, bc
	jq	nc, .BB0_9
	push	bc
	pop	hl
	ld	bc, (ix + -3)
	or	a, a
	sbc	hl, bc
	push	hl
	pop	de
	ld	(iy + 3), de
	add	iy, de
	ld	(iy + 3), bc
	jq	.BB0_10
.BB0_7:
	ld	hl, (ix + -3)
	push	hl
	call	s_sbrk
	push	hl
	pop	iy
	pop	hl
	lea	hl, iy + 0
	add	hl, bc
	or	a, a
	sbc	hl, bc
	ld	bc, 0
	jq	z, .BB0_11
	ld	hl, (ix + -3)
	ld	(iy + 3), hl
	jq	.BB0_10
.BB0_9:
	ld	de, (iy)
	ld	hl, (ix + -6)
	ld	(hl), de
.BB0_10:
	lea	bc, iy + 6
.BB0_11:
	push	bc
	pop	hl
	ld	sp, ix
	pop	ix
	ret

; (c) Copyright 2001-2008 Zilog, Inc.
;-------------------------------------------------------------------------
; Heap allocation routine s_sbrk
; Input:
;                 argument : 24 bit - number of bytes requested
;
; Output:
;       Result:   HL:	 24 bit address of memory allocated 
;		         HL = 0 if no memory available
;		        
; Registers Used:
;       
;-------------------------------------------------------------------------

s_sbrk:
	ld	hl,3
	add	hl,sp
	ld	hl,(hl)	;nbytes
	ld	de,(.base)
	add	hl,de
	jr	c,.fail
	
	; fail  if hl >= sp.
	; hl is now, or will be, the next un-allocated address = minimal value
	; for sp that will not corrupt allocated data or that writing to
	; allocated data may corrupt the stack.
	; Actually, if hl is anywhere close to sp we're probably in trouble :(
	
	push    hl
	sbc     hl,sp
	pop     hl
	jr	nc,.fail
.ok:
	ex	hl,de
	ld	(.base),de
	ret
.fail:
	or	a,a
	sbc	hl,hl
	ret

free:
	ld	hl, -9
	call	ti._frameset
	ld	hl, (ix + 6)
	add	hl, bc
	or	a, a
	sbc	hl, bc
	jq	z, .BB0_9
	push	hl
	pop	iy
	ld	bc, malloc.base
	lea	hl, iy + -6
	ld	(ix + -6), hl
	ld	de, (ix + -6)
.BB0_2:
	push	bc
	pop	iy
	ld	(ix + -3), iy
	ld	hl, (iy)
	push	hl
	pop	bc
	add	hl, bc
	or	a, a
	sbc	hl, bc
	jq	z, .BB0_4
	push	bc
	pop	hl
	or	a, a
	sbc	hl, de
	jq	c, .BB0_2
.BB0_4:
	ld	iy, (ix + 6)
	ld	de, (iy + -3)
	ld	hl, (ix + -6)
	ld	(ix + -9), de
	add	hl, de
	push	bc
	pop	de
	or	a, a
	sbc	hl, de
	jq	nz, .BB0_10
	push	bc
	pop	iy
	ld	hl, (iy + 3)
	ld	de, (ix + -9)
	add	hl, de
	ld	(ix + -9), hl
	ld	de, (ix + 6)
	push	de
	pop	iy
	ld	(iy + -3), hl
	ld	hl, (ix + -3)
	ld	hl, (hl)
	ld	bc, (hl)
	jq	.BB0_6
.BB0_10:
	ld	de, (ix + 6)
	push	de
	pop	iy
.BB0_6:
	ld	(iy + -6), bc
	ld	iy, (ix + -3)
	ld	bc, (iy + 3)
	add	iy, bc
	lea	hl, iy + 0
	ld	de, (ix + -6)
	or	a, a
	sbc	hl, de
	jq	nz, .BB0_8
	ld	hl, (ix + -9)
	add	hl, bc
	ld	iy, (ix + -3)
	ld	(iy + 3), hl
	lea	de, iy + 0
	ld	iy, (ix + 6)
	ld	hl, (iy + -6)
	push	de
	pop	iy
	ld	(iy), hl
	jq	.BB0_9
.BB0_8:
	ld	hl, (ix + -3)
	ld	(hl), de
.BB0_9:
	ld	sp, ix
	pop	ix
	ret
