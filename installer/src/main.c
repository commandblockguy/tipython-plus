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

enum error {
	SUCCESS,
	ALREADY_INSTALLED,
	MISSING_VAR,
	PORT_SETUP_FAILED,
	NO_SPACE,
};

uint8_t install();
bool port_setup();

uint8_t try_install() {
	for(uint8_t i = 0; i < MAX_APPVARS; i++) {
		char filename[] = "PyInstA";
		filename[6] = 'A' + i;
		ti_var_t f = ti_Open(filename, "r");
		if(!f) {
			dbg_printf(dbgerr, "Appvar %s not found.\n", filename);
			return MISSING_VAR;
		}
		locations[i].data = ti_GetDataPtr(f);
		size_t size = ti_GetSize(f);
		locations[i].size = size;
		app_size += size;
		num_appvars++;
		ti_Close(f);
		if(size != APPVAR_SIZE) break;
	}
	code_offset = *(uint24_t*)(locations[0].data + MAIN_SECTION_OFFSET) + 0x100;
	if(port_setup()) {
		dbg_printf(dbgerr, "Failed to set up ports.\n");
		return PORT_SETUP_FAILED;
	}
	uint8_t err = install();
	dbg_printf("Installed to %p\n", install_loc);
	dbg_printf("Execution start: %p\n", install_loc + 0x100 + *(uint24_t*)(install_loc + 0x11B));
	return err;
}

void delete_vars() {
	for(uint8_t i = 0; i < num_appvars; i++) {
		char filename[] = "PyInstA";
		filename[6] = 'A' + i;
		ti_Delete(filename);
	}
	ti_DeleteVar("PYINST", TI_PPRGM_TYPE);
}

int main() {
	os_SetCursorPos(0, 0);
	os_ClrLCDFull();
	os_PutStrFull("Installing Python+");
	os_NewLine();
	os_PutStrFull("Please wait...");

	uint8_t error = try_install();
	os_SetCursorPos(0, 0);
	os_ClrLCDFull();
	switch(error) {
		case SUCCESS:
			os_PutStrFull("Successfully installed.");
			delete_vars();
			break;
		case ALREADY_INSTALLED:
			os_PutStrFull("Already installed.");
			os_NewLine();
			os_PutStrFull("Delete Python+ from the");
			os_NewLine();
			os_PutStrFull("mem menu to reinstall.");
			delete_vars();
			break;
		case MISSING_VAR:
			os_PutStrFull("Install failed.");
			os_NewLine();
			os_PutStrFull("Missing an appvar.");
			break;
		case PORT_SETUP_FAILED:
			os_PutStrFull("Install failed.");
			os_NewLine();
			os_PutStrFull("Unsupported OS version.");
			break;
		case NO_SPACE:
			os_PutStrFull("Install failed.");
			os_NewLine();
			os_PutStrFull("Out of archive space.");
			os_NewLine();
			os_PutStrFull("Try running the");
			os_NewLine();
			os_PutStrFull("GarbageCollect command.");
			break;
	}
	while(os_GetCSC());
	while(!os_GetCSC());
	return error;
}
