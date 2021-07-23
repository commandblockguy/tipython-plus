macro patch patchname*
	local patch
	element app.main:0
	element app.data:1

	patch.bases.0.base = app.main
	patch.bases.1.base = app.data

	patch.bases.0.string = 'appmain'
	patch.bases.1.string = 'appdata'

	patch.next_base = 2

	db 'const ',`patchname,' = [',$a

	macro replacement repname*, start_addr*, end_addr*, comment
		local replacement
		element replacement.base: patch.next_base

		repeat 1, id: patch.next_base
			patch.bases.id.base = replacement.base
			patch.bases.id.string = `repname
		end repeat
		patch.next_base = patch.next_base + 1

		repeat patch.total_bases, base:0
			virtual at 0
				replacement.relocations.base.area::
			end virtual
		end repeat

		if `comment <> ''
			db '	// ',comment,$a
		end if

		db '	{name: "', `repname, '", start: '
		repeat 1, d:start_addr
			db `d
		end repeat
		db ', end: '
		repeat 1, d:end_addr
			db `d
		end repeat
		db ', replacement: new Uint8Array(['

		macro @ez80.word @size*, @value*
			local value, address
			value = @value
			address = $
			if value scale 1 <> 0
				repeat 1, id: value metadata 1
					virtual replacement.relocations.id.area
						emit 3,address-replacement.base
						emit 3,value-patch.bases.id.base
					end virtual
				end repeat
				@ez80.word @size, -1
			else
				@ez80.word @size, value
			end if
		end macro

		macro end.replacement
				replacement.data.size = $-$$
			end virtual

			repeat replacement.data.size
				load char : byte from replacement.data.area:replacement.base+%-1
				repeat 1, d:char
					db `d,', '
				end repeat
			end repeat

			db ']), relocations: {'

			repeat patch.total_bases, base:0
				virtual replacement.relocations.base.area
					replacement.relocations.base.count = ($-$$)/6
				end virtual
				repeat replacement.relocations.base.count
					load addr : 3 from replacement.relocations.base.area:6*(%-1)
					load value : 3 from replacement.relocations.base.area:6*(%-1)+3
					repeat 1, dec_addr:addr
						repeat 1, dec_value:value
							db `dec_addr,': {base: "', patch.bases.base.string, '", value: ', `dec_value, '}, '
						end repeat
					end repeat
				end repeat
			end repeat

			db '}},',$a
			purge @ez80.word
			purge end.replacement
		end macro

		virtual at replacement.base
			replacement.data.area::
			repname:
	end macro

	macro end.patch
		patch.total_bases = patch.next_base - 1
		db '];',$a
		purge replacement
		purge end.patch
	end macro
end macro
