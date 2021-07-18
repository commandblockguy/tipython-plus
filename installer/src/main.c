#include <debug.h>
#include <fileioc.h>
#include <stddef.h>
#include <stdint.h>

// pretty sure you'll run out of flash past this point, lol
#define MAX_APPVARS 24
#define APPVAR_SIZE 60000

#define MAIN_SECTION_OFFSET 0x112

extern struct {
	void *data;
	size_t size;
} locations[MAX_APPVARS];

extern uint8_t num_appvars;
extern size_t app_size;
extern uint24_t code_offset;
extern void *install_loc;

void install();
bool port_setup();

// todo: let the user know what's happening

int main() {
	ti_CloseAll();
	for(uint8_t i = 0; i < MAX_APPVARS; i++) {
		char filename[] = "PyInstA";
		filename[6] = 'A' + i;
		ti_var_t f = ti_Open(filename, "r");
		if(!f) {
			dbg_printf(dbgerr, "Appvar %s not found.\n", filename);
			return 1;
		}
		locations[i].data = ti_GetDataPtr(f);
		size_t size = ti_GetSize(f);
		locations[i].size = size;
		app_size += size;
		num_appvars++;
		ti_Close(f);
		ti_Delete(filename);
		if(size != APPVAR_SIZE) break;
	}
	code_offset = *(uint24_t*)(locations[0].data + MAIN_SECTION_OFFSET) + 0x100;
	if(port_setup()) {
		dbg_printf(dbgerr, "Failed to set up ports.\n");
		return 1;
	}
	install();
	dbg_printf("Installed to %p\n", install_loc);
	dbg_printf("Execution start: %p\n", install_loc + 0x100 + *(uint24_t*)(install_loc + 0x11B));
	ti_DeleteVar("PYINST", TI_PPRGM_TYPE);
	return 0;
}
