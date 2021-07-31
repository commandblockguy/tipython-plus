include 'apppatch.inc'
include 'fasmg-ez80/ez80.inc'
include 'fasmg-ez80/ti84pceg.inc'

version = 0
test = 0

; Don't use ACK as a version number, so that it can be distinguished from the vanilla Python app's response
assert	version and $ff <> 6

if test = 0
	ti.coproc_read = $222C8
	ti.coproc_write = $222CC
end if

csi_args = $D186E2

namespace command_ids
	get_version	= 0
	load_lib	= 1
	?call		= 2
	mem_write	= 3
	mem_read	= 4
	mem_copy	= 5
	mem_set		= 6
	alloc		= 7
	free		= 8
	free_all	= 9
	test		= 10
end namespace

namespace command.status
	non_escape	= 0 ; not in the middle of an escape code
	await_command	= 1 ; waiting for which command to receive
	read_args	= 2 ; reading a fixed number of bytes for the given command type
	read_data	= 3 ; reading the data section of variable length
end namespace

patch_ram = ti.plotSScreen

virtual at patch_ram
	base64.read_active		rb	1
	base64.read_callback		rl	1
	base64.read_ptr			rl	1
	base64.read_end			rl	1
	base64.curr_pos			rb	1 ; index of next byte to receive into .buf
	base64.buf			rb	4
	malloc.base			rb	6
	s_sbrk.base			rl	1
	sp_bkp				rl	1
	func_ptr			rl	1


	patch_ram.size = $ - $$
	patch_ram.end = $
end virtual

; ref. app main section is at $341728

patch pythonPatch

replacement init, $1A999, $1A999, "Initialize the patch's RAM section"
	ld	hl,patch_ram
	ld	(hl),0
	ld	de,patch_ram+1
	ld	bc,patch_ram.size - 1
	ldir
	ld	hl,patch_ram.end
	ld	(s_sbrk.base),hl
end replacement

replacement base64_read_byte, 0, 0, "Handle an incoming base64 byte"
	ld	e,a
	ld	iy,base64.read_active
	lea	hl,iy+11 ; buf
	ld	a,(iy+10)
	ld	d,a
	add	a,l
	ld	l,a
	ld	(hl),e

	ld	a,d ; curr_pos
	inc	a
	ld	(iy+10),a
	cp	a,4
	ret	c

	; actaully convert from b64
	xor	a,a
	ld	(iy+10),a

	sbc	hl,hl
	lea	de,iy+14
	ld	b,4
.loop:
	ld	a,(de)
	sub	a,' '
	rla
	rla
repeat 6
	rla
	adc	hl,hl
end repeat
	dec	de
	djnz	.loop

	ld	(iy+11),hl ; buf

	ld	hl,(iy+7) ; end
	ld	bc,(iy+4) ; ptr
	or	a,a
	sbc	hl,bc

	ld	bc,3
	sbc	hl,bc
	jq	nc,.write
	add	hl,bc
	push	hl
	pop	bc
.write:
	lea	hl,iy+11 ; buf
	ld	de,(iy+4) ; read ptr
	ldir
	ld	(iy+4),de

	ld	hl,(iy+7) ; end
	or	a,a
	sbc	hl,de
	ret nz

	xor	a,a
	ld	(iy),a

	ld	hl,(iy+1) ; callback
	jp	(hl)

end replacement

replacement commands, 0, 0, "Command handlers"
	dl	commands.get_version
	dl	commands.load_lib
	dl	commands.call
	dl	commands.mem_write
	dl	commands.mem_read
	dl	commands.mem_copy
	dl	commands.mem_set
	dl	commands.alloc
	dl	commands.free
	dl	commands.free_all
	dl	commands.test


; no args; returns 24-bit version number
commands.get_version:
	ld	hl,version
	jp	send_hl

; 8 byte lib name + 1 byte version, function count; returns lib pointer or NULL
commands.load_lib:
	; Get relocation table size
	xor	a,a
	lea	hl,ix
	ld	bc,8
	cpir
	; hl = arg_buf + name len
	ld	bc,6 ; lib magic, null, version, 3 bytes code
	add	hl,bc
	ex	de,hl
	ld	hl,(ix+9)
	add	hl,hl
	add	hl,hl
	add	hl,de
	lea	bc,ix
	or	a,a
	sbc	hl,bc
	; hl = relocation table length
	push	hl
	call	malloc
	pop	de

	; check if null
	add	hl,de
	or	a,a
	sbc	hl,de
	jp	z,send_hl

	push	hl

	ld	a,$C0 ; library magic
	ld	(hl),a
	inc	hl

	ex	de,hl
	ld	c,8
	lea	hl,ix
.name_loop:
	ld	a,(hl)
	or	a,a
	jr	z,.end
	ldi
	ld	a,c
	or	a,a
	jr	nz,.name_loop
.end:
	xor	a,a
	ex	de,hl
	ld	(hl),a
	inc	hl
	ld	a,(ix+8) ; version
	ld	(hl),a
	inc	hl

	ld	de,0
	ld	bc,(ix+9) ; function count
.func_loop:
	ld	(hl),$C3
	inc	hl
	ld	(hl),de
	inc	hl
	inc	hl
	inc	hl
	inc	de
	inc	de
	inc	de
	dec	bc
	ld	a,b
	or	a,c
	jr	nz,.func_loop

	ld	de,$C9AFD1
	ld	(hl),de
	pop	hl

	push	hl
	call	load_lib
	pop	hl

	or	a,a
	jp	z,send_hl

	; error in libloading
	push	hl
	call	free
	pop	hl

	or	a,a
	sbc	hl,hl
	jp	send_hl

; hl = lib ptr
load_lib:
	push	hl
	ld	hl,.appvar
	call	ti.Mov9ToOP1
.findlibload:
	call	ti.ChkFindSym
	jr	c,.notfound
	call	ti.ChkInRam
	jr	nz,.inarc
	call	ti.PushOP1
	call	ti.Arc_Unarc
	call	ti.PopOP1
	jr	.findlibload
.inarc:
	ex	de,hl
	ld	de,9
	add	hl,de
	ld	e,(hl)
	add	hl,de
	inc	hl
	inc	hl
	inc	hl
	pop	de
	ld	bc,.notfound
	push	bc
	ld	bc,$aa55aa ; no error screen
	jp	(hl)
.notfound:
	pop	de
	ld	a,1
	ret
.appvar:
	db	21,"LibLoad",0

; address, stack length; stack contents; returns lhuea
commands.call:
.stack_size = 2048
	ld	iy,base64.read_active
	xor	a,a
	ld	(iy+10),a ; curr_pos
	ld	hl,.on_data
	ld	(iy+1),hl
	ld	hl,ti.stackBot + .stack_size
	ld	(iy+7),hl ; end
	ld	de,(ix+3) ; size
	sbc	hl,de
	ld	(iy+4),hl ; start
	ld	(sp_bkp),hl
	ld	hl,(ix)
	ld	(func_ptr),hl
	ld	a,d
	or	a,e
	jr	z,.on_data
	ld	a,1
	ld	(iy),a ; read active
	ret
.on_data:
	or	a,a
	sbc	hl,hl
	add	hl,sp
	ld	de,(sp_bkp)
	ld	(sp_bkp),hl
	ex	de,hl
	ld	sp,hl
	ld	hl,(func_ptr)
	ld	iy,ti.flags
	call	.jp_hl
	push	af,de
	call	send_hl
	pop	hl,af
	ld	h,a
	call	send_hl
	ld	hl,(sp_bkp)
	ld	sp,hl
	ret
.jp_hl:
	jp	(hl)

; address, size; data;
commands.mem_write:
	ld	iy,base64.read_active
	ld	de,(ix)
	ld	hl,(ix+3)
	add	hl,de
	or	a,a
	sbc	hl,de
	jp	z,send_ack

	ex	de,hl
	ld	(iy+4),hl ; read_ptr
	add	hl,de
	ld	(iy+7),hl ; read_end
	xor	a,a
	ld	(iy+10),a ; curr_pos
	inc	a
	ld	(iy),a ; read active
	ld	hl,send_ack
	ld	(iy+1),hl ; callback
	ret

; address, size; returns b64 data
commands.mem_read:
	ld	de,(ix)
	ld	hl,(ix+3)
	add	hl,de
	push	hl
	pop	bc
	ex	de,hl
.loop:
	or	a,a
	sbc	hl,bc
	add	hl,bc
	ret	nc

	ld	de,(hl)
	push	hl,bc
	ex	de,hl
	call	send_hl
	pop	bc,hl
	inc	hl
	inc	hl
	inc	hl
	jr	.loop

; dest, src, size
commands.mem_copy:
	ld	hl,(ix+6)
	add	hl,de
	or	a,a
	sbc	hl,de
	jp	z,send_ack
	push	hl
	pop	bc
	ld	de,(ix)
	ld	hl,(ix+3)
	ldir
	jp	send_ack

; address, char, size
commands.mem_set:
	ld	hl,(ix+6)
	add	hl,de
	or	a,a
	sbc	hl,de
	push	hl
	pop	bc
	jq	z,send_ack
	ld	hl,(ix)
	ld	de,(ix)
	ld	a,(ix+3)
	ld	(hl),a
	inc	de
	dec	bc
	ldir
	jq	send_ack

; size; returns address or NULL
commands.alloc:
	ld	hl,(ix)
	push	hl
	call	malloc
	pop	de
	jq	send_hl

; address
commands.free:
	ld	hl,(ix)
	push	hl
	call	free
	pop	de
	jq	send_ack

; no args
commands.free_all:
	ld	ix,malloc.base
	or	a,a
	sbc	hl,hl
	ld	(ix),hl
	ld	(ix+3),hl
	ld	hl,patch_ram.end
	ld	(ix+6),hl
	jq	send_ack

commands.test:
	ld	hl,(ix)
	jq	send_hl

send_hl:
	ld	de,base64.buf+3
	ld	b,4
.loop:
	xor	a,a
repeat 6
	add	hl,hl
	rla
end repeat
	add	a,' '
	ld	(de),a
	dec	de
	djnz	.loop
	ld	bc,4
	push	bc
	ld	bc,base64.buf
	push	bc
	call	ti.coproc_write
	pop	bc,bc
	ret

send_ack:
	ld	bc,1
	push	bc
	ld	bc,.ack
	push	bc
	call	ti.coproc_write
	pop	bc,bc
	ret
.ack:
	db	6 ; ascii ACK
end replacement

replacement csi_p_handler, 0, 0, "CSI handler for 'p'"
	push	ix
	ld	ix,csi_args+3

	; todo: bounds check this or something
	ld	bc,0
	ld	c,(ix-3)
	ld	hl,commands
	add	hl,bc
	add	hl,bc
	add	hl,bc
	ld	iy,(hl)
	call	ti._indcall

	pop	ix
	ld	hl,(ix+$09)
	ld	(hl),1
	xor	a,a
	ld	sp,ix
	pop	ix
	ret
end replacement

replacement malloc, 0, 0, 'malloc function'
	include 'malloc.inc'
end replacement

if test = 1
replacement test_handler, 0, 0, 'Stats key test stuff'
	ld	a,($F50018)
	bit	7,a ; stat
	jp	z,ti._indcall

	scf
	sbc	hl,hl
	ld	(hl),2
	ret

ti.coproc_write:
ti.coproc_read:
	or	a,a
	sbc	hl,hl
	ret
end replacement

replacement test_call, $1AC4B, $1AC4F, 'Call thing for test handler'
	call	test_handler
end replacement
end if

replacement char_listener, $18805, $18805, "Calls B64 handler if active"
	ld	a,(base64.read_active)
	or	a,a
	jr	z,.b64_inactive
	ld	a,(ix-$01)
	push	ix
	call	base64_read_byte
	pop	ix
	jp	app.main + $1877E
.b64_inactive:
end replacement

replacement csi_switch_size, $19204, $19206, "CSI end character switch-case length"
	dw	8
end replacement

replacement csi_switch_p, $19222, $19222, "CSI end character switch-case entry for 'p'"
	db	'p' ; for "plus" or "private" idk
	dl	csi_p_handler
end replacement

end patch
