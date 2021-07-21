macro patch name*
	local patch
	db 'const ',`name,' = [',$a

	macro replacement name*, start_addr*, end_addr*, comment
		local replacement
		element replacement.base
		element app.sections.main
		element app.sections.data

		name = replacement.base

		iterate base, replacement, appmain, appdata
			virtual at 0
				replacement.relocations.base.area::
			end virtual
		end iterate

		if `comment <> ''
			db '	// ',comment,$a
		end if

		db '	{name: "', `name, '", start: '
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
			if value relativeto replacement.base
				virtual replacement.relocations.replacement.area
					emit 3,address-replacement.base
					emit 3,value-replacement.base
				end virtual
				@ez80.word @size, -1
			else if value relativeto app.sections.main
				virtual replacement.relocations.appmain.area
					emit 3,address-replacement.base
					emit 3,value-app.sections.main
				end virtual
				@ez80.word @size, -1
			else if value relativeto app.sections.data
				virtual replacement.relocations.appdata.area
					emit 3,address-replacement.base
					emit 3,value-app.sections.data
				end virtual
				@ez80.word @size, -1
			else
				@ez80.word @size, value
			end if
		end macro

		macro end.replacement
				replacement.data.size = $-$$
			end virtual

			iterate base, replacement, appmain, appdata
				virtual replacement.relocations.base.area
					replacement.relocations.base.count = ($-$$)/6
				end virtual
			end iterate

			repeat replacement.data.size
				load char : byte from replacement.data.area:replacement.base+%-1
				repeat 1, d:char
					db `d,', '
				end repeat
			end repeat

			db ']), relocations: {'

			replacement.relocations.replacement.string = `name
			replacement.relocations.appmain.string = 'appmain'
			replacement.relocations.appdata.string = 'appdata'

			iterate base, replacement, appmain, appdata
				repeat replacement.relocations.base.count
					load addr : 3 from replacement.relocations.base.area:6*(%-1)
					load value : 3 from replacement.relocations.base.area:6*(%-1)+3
					repeat 1, dec_addr:addr
						repeat 1, dec_value:value
							db `dec_addr,': {base: "', replacement.relocations.base.string, '", value: ', `dec_value, '}, '
						end repeat
					end repeat
				end repeat
			end iterate

			db '}},',$a
			purge end.replacement
		end macro

		virtual at replacement.base
			replacement.data.area::
	end macro

	macro end.patch
		db '];',$a
		purge end.patch
	end macro
end macro
