define ti? ti
namespace ti?
?FindAppStart			:= 0021100h
?DeleteApp			:= 002126Ch
end namespace

max_appvars = 24

	public	_install
	public	_locations
	public	_num_appvars
	public	_app_size
	public	_code_offset
	public	_install_loc
	extern	_port_unlock
	extern	_port_lock

_install:
	push	ix
;	call	open_debugger

	di
	ld	hl,app_name
	push	hl
	call	$21100
	pop	bc
	jq	nz,.continue
	ld	hl,$3b0000		; applications start here
.find:
	push	hl
	call	$22044			; locates start of next application header
	pop	de
	jr	nz,.find
	ex	de,hl
	dec	hl
	dec	hl
	dec	hl
	push	hl
	pop	hl
	ld	de,-3
_app_size = $-3
	or	a,a
	sbc	hl,de
	ex	de,hl
	ld	(_install_loc),de
	push	de
	ld	ix,_locations
	ld	a,0
_num_appvars = $-1
.loop:
	ld	hl,(ix)
	ld	bc,(ix+3)
	push	af
	call	_port_unlock
	call	$02e0
	call	_port_lock
	pop	af
	lea	ix,ix+6
	dec	a
	jr	nz,.loop
	pop	hl


	push	hl
	ld	de,0
_code_offset = $-3
	add	hl,de
	ex	de,hl			; de = relocation table end
	pop	hl
	ld	bc,table_offset
	add	hl,bc			; hl = relocation table start
.relocate:
	or	a,a
	sbc	hl,de
	add	hl,de
	jr	z,.endrelocate

	ld	ix,(hl)
	add	ix,de			; location to overwrite
	inc	hl
	inc	hl
	inc	hl			; hl points to value | base
	push	hl
	push	de
	ld	hl,(hl)

	ld	bc,$800000		; check if data- or code- relative
	or	a,a
	sbc	hl,bc
	add	hl,bc
	jr	c,.coderelative
	ld	de,data_loc - $800000
.coderelative:
	add	hl,de
	lea	de,ix
	ld	($d0062f),hl
	ld	hl,$d0062f
	ld	bc,3
	call	_port_unlock
	call	$02e0
	call	_port_lock
	pop	de
	pop	hl
	inc	hl
	inc	hl
	inc	hl
	jr	.relocate
.endrelocate:
	xor	a,a
.continue:
	pop	ix
	ret

app_name:
	db	'Python+',0

table_offset = $12a
data_loc = $d1787c

;app_size = $81e8d
;code_offset = $100 + $134b8
;table_offset = $12a
;data_loc = $d1787c

_locations:
	rl	2 * max_appvars

_install_loc:
	dl	0

; temp
;open_debugger:
;	push	hl
;	scf
;	sbc	hl,hl
;	ld	(hl),2
;	pop	hl
;	ret

; start: 32e170
; end: 3b0000
; size: 81e90
