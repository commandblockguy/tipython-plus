include 'apppatch.inc'
include 'ez80.inc'
include 'ti84pceg.inc'

version = 0

; Don't use ACK as a version number, so that it can be distinguished from the vanilla Python app's response
assert	version <> 6

ti.coproc_read = $222C8
ti.coproc_write = $222CC

command_char = $10

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
	test		= 9
end namespace

namespace command.status
	non_escape	= 0 ; not in the middle of an escape code
	await_command	= 1 ; waiting for which command to receive
	read_args	= 2 ; reading a fixed number of bytes for the given command type
	read_data	= 3 ; reading the data section of variable length
end namespace

patch_ram = $D1887C

virtual at patch_ram
	command.status		rb	1
	command.current		rb	1
	command.ptr		rl	1
	command.end		rl	1
	arg_buf			rb	16 ; todo: check this


	; Don't run into the stack
	assert $ < $D1987E
	patch_ram.size = $ - $$
end virtual

; ref. app main section is at $341728

patch pythonPatch

replacement init, $1A999, $1A999, "Initialize the patch's RAM section"
	ld	hl,patch_ram
	ld	(hl),0
	ld	de,patch_ram+1
	ld	bc,patch_ram.size - 1
	ldir
end replacement

replacement dle_seq_handle_byte, 0, 0, "Handle a byte received during a DLE sequence"
	ld	bc,0
	ld	c,a
	ld	a,(command.status)
	cp	a,command.status.await_command
	jq	nz,.read
	; received byte is the new command
	ld	a,c
	ld	(command.current),a
	ld	hl,command_arg_lengths
	add	hl,bc
	ld	a,(hl)
	or	a,a
	jq	z,.args_recd
	ld	c,a ; bc = arg length
	ld	hl,arg_buf
	ld	(command.ptr),hl
	add	hl,bc
	ld	(command.end),hl
	ld	a,command.status.read_args
	ld	(command.status),a
	ret
.read:
	ld	hl,(command.ptr)
	ld	a,c
	ld	(hl),a
	inc	hl
	ld	(command.ptr),hl
	ld	de,(command.end)
	or	a,a
	sbc	hl,de
	ret	nz
	; end of buffer reached
	ld	a,(command.current)
	ld	c,a
	ld	hl,command_data_handlers
	ld	a,(command.status)
	cp	a,command.status.read_data
	jq	z,.jump_table
.args_recd:
	ld	hl,command_arg_handlers
.jump_table:
	add	hl,bc ; bc = current command
	add	hl,bc
	add	hl,bc
	ld	hl,(hl)
	jp	(hl)

; no args; returns a single byte representing the current version number
commands.get_version:
.on_args:
	ld	bc,1
	push	bc
	ld	bc,.version
	push	bc
	call	ti.coproc_write
	pop	bc,bc
	xor	a,a
	ld	(command.status),a
	ret
.on_data = 0
.args_len = 0
.version:
	db	version

; 8 byte lib name, 1 byte version, 3 byte function count; returns 3-byte lib pointer or NULL
commands.load_lib:
.on_args:
	xor	a,a
	ld	(command.status),a
	ret
.on_data = 0
.args_len = 12

; 3 byte address, 3 byte stack length, stack contents; returns alhue
commands.call:
.on_args:
	ld	a,command.status.read_args
	ld	(command.status),a
	ret
.on_data:
	xor	a,a
	ld	(command.status),a
	ret
.args_len = 6

; 3 byte address, 3 byte size, variable length data; returns ACK
commands.mem_write:
.on_args:
	ld	a,command.status.read_args
	ld	(command.status),a
	ret
.on_data:
	xor	a,a
	ld	(command.status),a
	ret
.args_len = 6

; 3 byte address, 3 byte size; returns variable length data
commands.mem_read:
.on_args:
	ld	hl,(arg_buf+3)
	push	hl
	ld	hl,(arg_buf)
	push	hl
	call	ti.coproc_write
	pop	bc,bc
	xor	a,a
	ld	(command.status),a
	ret
.on_data = 0
.args_len = 6

; 3 byte dest, 3 byte src, 3 byte size; returns ACK
commands.mem_copy:
.on_args:
	xor	a,a
	ld	(command.status),a
	ret
.on_data = 0
.args_len = 9

; 3 byte address, 1 byte data, 3 byte size; returns ACK
commands.mem_set:
.on_args:
	xor	a,a
	ld	(command.status),a
	ret
.on_data = 0
.args_len = 0

; 3 byte size; returns address or NULL
commands.alloc:
.on_args:
	xor	a,a
	ld	(command.status),a
	ret
.on_data = 0
.args_len = 0

; 3 byte address; returns ACK
commands.free:
.on_args:
	xor	a,a
	ld	(command.status),a
	ret
.on_data = 0
.args_len = 0

; length of the fixed-length args of each command
command_arg_lengths:
	db	commands.get_version.args_len
	db	commands.load_lib.args_len
	db	commands.call.args_len
	db	commands.mem_write.args_len
	db	commands.mem_read.args_len
	db	commands.mem_copy.args_len
	db	commands.mem_set.args_len
	db	commands.alloc.args_len
	db	commands.free.args_len

; function to be called after all fixed-length args are received
command_arg_handlers:
	dl	commands.get_version.on_args
	dl	commands.load_lib.on_args
	dl	commands.call.on_args
	dl	commands.mem_write.on_args
	dl	commands.mem_read.on_args
	dl	commands.mem_copy.on_args
	dl	commands.mem_set.on_args
	dl	commands.alloc.on_args
	dl	commands.free.on_args

; function to be called after variable-length data is received
command_data_handlers:
	dl	commands.get_version.on_data
	dl	commands.load_lib.on_data
	dl	commands.call.on_data
	dl	commands.mem_write.on_data
	dl	commands.mem_read.on_data
	dl	commands.mem_copy.on_data
	dl	commands.mem_set.on_data
	dl	commands.alloc.on_data
	dl	commands.free.on_data
end replacement

replacement char_listener, $18805, $18805, "Listens for DLE characters"

	ld	a,(command.status)
	or	a,a
	jr	z,.dle_inactive
	ld	a,(ix-$01)
	push	ix
	call	dle_seq_handle_byte
	pop	ix
	jp	app.main + $1877E

.dle_inactive:
	ld	a,(ix-$01)
	cp	a,command_char ; data link escape
	jr	nz,.not_dle
	ld	a,1
	ld	(command.status),a
	jp	app.main + $1877E
.not_dle:

end replacement

end patch
