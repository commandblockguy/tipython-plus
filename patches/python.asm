include 'apppatch.inc'
include 'ez80.inc'

patch pythonPatch

replacement test, 0, 0, "Test replacement"
	nop
	dl	$
	dl	app.sections.main
	dl	app.sections.data
	dl	test
end replacement

end patch
