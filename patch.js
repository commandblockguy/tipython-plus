function getSlice(array, offset, length) {
	return new Uint8Array(array.buffer, array.byteOffset + offset, length);
}

DataView.prototype.getUint24 = function(byteOffset, littleEndian) {
	if(littleEndian) {
		return this.getUint16(byteOffset, true) |
			(this.getUint8(byteOffset + 2, true) << 16);
	} else {
		return (this.getUint16(byteOffset, false) << 8) |
			this.getUint8(byteOffset + 2);
	}
}

DataView.prototype.setUint24 = function(byteOffset, value, littleEndian) {
	if(littleEndian) {
		this.setUint16(byteOffset, value & 0xFFFF, true);
		this.setUint8(byteOffset + 2, value >> 16);
	} else {
		this.setUint16(byteOffset, value >> 8, false);
		this.setUint8(byteOffset + 2, value & 0xFF);
	}
}

function getChecksum(data) {
	let sum = 0;
	for(byte of new Uint8Array(data)) {
		sum = (sum + byte) & 0xFFFF;
	}
	return sum;
}

function createVariable(name, type, data) {
	const enc = new TextEncoder();
	const result = new Uint8Array(19 + data.byteLength);
	const view = new DataView(result.buffer);
	view.setUint16(0, 0x0D, true);
	view.setUint16(2, data.length + 2, true);
	view.setUint8(4, type);
	result.set(enc.encode(name), 5);
	view.setUint8(14, 0x80); // archived
	view.setUint16(15, data.length + 2, true);
	view.setUint16(17, data.length, true);
	result.set(data, 19);
	return result;
}

function createTIFile(data) {
	const enc = new TextEncoder();
	const result = new Uint8Array(55 + data.byteLength + 2);
	const view = new DataView(result.buffer);
	result.set(enc.encode("**TI83F*\x1A\x0A\x00"));
	view.setUint16(53, data.byteLength, true);
	result.set(data, 55);
	const checksum = getChecksum(data);
	view.setUint16(result.byteLength - 2, checksum, true);
	return result;
}

function createGroup(variables) {
	const totalLength = variables.reduce((tot, v) => {
		return tot + v.data.byteLength + 19;
	}, 0);
	const combinedData = new Uint8Array(totalLength);
	let offset = 0;
	for(let variable of variables) {
		const data = createVariable(variable.name, variable.type, variable.data);
		combinedData.set(data, offset);
		offset += data.byteLength;
	}
	return createTIFile(combinedData);
}

class App {
	/**
	 * Loads an app from a 8ek file.
	 * 
	 * @param appFile A Blob containing the contents of an 8ek file.
	 */
	async load(appFile) {
		const fileHeaderLen = 0x4E;
		const headerLen = 256;
		const infoLen = 0x2A;

		const data = (await appFile.arrayBuffer()).slice(fileHeaderLen);
		this.header = new Uint8Array(data, 0, headerLen);
		this.info = new Uint8Array(data, headerLen, infoLen);
		this.infoView = new DataView(data, headerLen, infoLen);

		console.log("Main section:", this.mainSectionOffs);
		console.log("Data section:", this.dataSectionOffs);
		console.log("Exec offset:", this.execEntryPointOffs);
		console.log("Exec lib table:", this.execLibTableOffs);
		console.log("Copyright offset:", this.copyrightOffs);

		const relocationTableLen = this.mainSectionOffs - infoLen;
		const relocationTable = new Uint8Array(data, headerLen + infoLen, relocationTableLen);
		this.relocations = App.getRelocations(relocationTable);

		this.mainSection = new Uint8Array(data, headerLen + infoLen + relocationTableLen);
		
		return this;
	}

	/**
	 * Reads the relocation table.
	 * 
	 * @param table A Uint8Array containing the relocation table.
	 * @returns A sparse array mapping hole addresses to values.
	 */
	static getRelocations(table) {
		let result = {};
		const view = new DataView(table.buffer, table.byteOffset, table.byteLength);
		const numRelocations = table.byteLength / 6;
		console.log(`Got ${numRelocations} relocations.`);
		for(let i = 0; i < numRelocations; i++) {
			const holeAddr = view.getUint24(i * 6, true);
			const rawHoleValue = view.getUint24(i * 6 + 3, true);
			const relValue = rawHoleValue & 0x3FFFFF;
			const base = rawHoleValue >> 22;
			const strBase = {0: "appmain", 2: "appdata"}[base];
			result[holeAddr] = {
				base: strBase,
				value: relValue,
			};
		}
		return result;
	}

	/**
	 * Recreates the relocation table.
	 * 
	 * @param relocations A list of relocations.
	 * @returns An Uint8Array 
	 */
	static genRelocationTable(relocations) {
		const numRelocations = Object.keys(relocations).length;
		const result = new Uint8Array(numRelocations * 6);
		const view = new DataView(result.buffer);
		let i = 0;
		for(const holeAddr in relocations) {
			const relValue = relocations[holeAddr].value;
			const strBase = relocations[holeAddr].base;
			const base = {appmain: 0, appdata: 2}[strBase];
			const rawValue = (base << 22) | relValue;
			view.setUint24(i * 6, holeAddr, true);
			view.setUint24(i * 6 + 3, rawValue, true);
			i++;
		}
		return result;
	}

	constructor() {
		const addresses = {
			mainSectionOffs: 0x12,
			dataSectionOffs: 0x15,
			execEntryPointOffs: 0x1B,
			execLibTableOffs: 0x21,
			copyrightOffs: 0x24
		};

		for(let property in addresses) {
			const address = addresses[property];
			Object.defineProperty(this, property, {
				get: () => this.infoView.getUint24(address, true),
				set: (x) => this.infoView.setUint24(address, x, true)
			});
		}
	}

	/**
	 * Gets the new size of the main section
	 */
	getNewSize(patch) {
		let size = this.mainSection.byteLength;
		for(const replacement of patch) {
			size += replacement.replacement.byteLength - (replacement.end - replacement.start);
		}
		return size;
	}

	patch(patch) {
		// add dummy replacement
		const replacements = [...patch, {
			start: this.mainSection.byteLength,
			end: this.mainSection.byteLength,
			replacement: new Uint8Array(0),
			relocations: {},
		}];
		replacements.sort((a, b) => {
			return a.start - b.start;
		});

		const oldProps = {};

		const newSize = this.getNewSize(replacements);
		const newMainSection = new Uint8Array(newSize);
		const newRelocations = {};
		const newOffsets = {};

		// make a list of relocations whose targets have not yet been adjusted
		const unrelocatedRelocations = [];
		for(const [addr, relocation] of Object.entries(this.relocations)) {
			if(relocation.base != "appdata") {
				unrelocatedRelocations.push(relocation);
			}
		}
		for(const replacement of Object.values(replacements)) {
			for(const [addr, relocation] of Object.entries(replacement.relocations)) {
				if(relocation.base != "appdata") {
					unrelocatedRelocations.push(relocation);
				}
			}
		}

		// move from lowest address to highest, keeping track of total amount shifted by, copying into result array and adjusting relocation addresses by shift amount
		let currentInputAddr = 0;
		let currentOutputAddr = 0;
		for(const replacement of replacements) {
			console.log(currentInputAddr, currentOutputAddr, replacement);

			// insert the section before this replacement
			const preSize = replacement.start - currentInputAddr;
			if(preSize > 0) {
				const preSection = getSlice(this.mainSection, currentInputAddr, preSize);
				newMainSection.set(preSection, currentOutputAddr);

				// Relocate relocations with values in this range
				for(const key of Object.keys(unrelocatedRelocations)) {
					const relocation = unrelocatedRelocations[key];
					if(relocation.base === "appmain" &&
						relocation.value >= currentInputAddr &&
						relocation.value < replacement.start) {
						relocation.value += currentOutputAddr - currentInputAddr;
						delete unrelocatedRelocations[key];
					}
				}

				// Relocate relocations with holes in this range
				for(const addr of Object.keys(this.relocations)) {
					const numAddr = Number(addr);
					if(numAddr >= currentInputAddr && numAddr < replacement.start) {
						const newAddr = numAddr + currentOutputAddr - currentInputAddr;
						newRelocations[newAddr] = this.relocations[numAddr];
					}
				}

				// Relocate global offsets in this range
				// TODO: debug this
				for(const prop of [
					"dataSectionOffs",
					"execEntryPointOffs",
					"execLibTableOffs",
					"copyrightOffs"
				]) {
					const addr = this[prop] - this.mainSectionOffs;
					if(addr >= currentInputAddr && addr < replacement.start) {
						newOffsets[prop] = addr - currentInputAddr + currentOutputAddr;
					}
				};

				currentInputAddr += preSize;
				currentOutputAddr += preSize;
			}


			// insert this replacement
			newMainSection.set(replacement.replacement, currentOutputAddr);

			// handle relocations with values inside this replacement
			for(const key of Object.keys(unrelocatedRelocations)) {
				const relocation = unrelocatedRelocations[key];
				if(relocation.base === replacement.name) {
					relocation.value += currentOutputAddr;
					relocation.base = "appmain";
					delete unrelocatedRelocations[key];
				}
			}

			// handle relocations with holes inside this replacement
			for(const relAddr of Object.keys(replacement.relocations)) {
				const relocData = replacement.relocations[relAddr];
				newRelocations[Number(relAddr) + currentOutputAddr] = relocData;
			}
			currentInputAddr += replacement.end - replacement.start;
			currentOutputAddr += replacement.replacement.byteLength;
		}

		// treat the offsets in the info table like relocation entries?
		this.mainSection = newMainSection;
		this.relocations = newRelocations;

		this.mainSectionOffs = 0x2A + 6 * Object.keys(this.relocations).length;

		for(const prop of Object.keys(newOffsets)) {
			this[prop] = this.mainSectionOffs + newOffsets[prop];
		}

		console.log("Main section:", this.mainSectionOffs);
		console.log("Data section:", this.dataSectionOffs);
		console.log("Exec offset:", this.execEntryPointOffs);
		console.log("Exec lib table:", this.execLibTableOffs);
		console.log("Copyright offset:", this.copyrightOffs);
	}

	/**
	 * Checks if every relocation's hole contains FFFFFF.
	 */
	verifyRelocations() {
		for(const holeAddr of Object.keys(this.relocations)) {
			const numHoleAddr = Number(holeAddr);
			if(this.mainSection[numHoleAddr] != 0xFF ||
				this.mainSection[numHoleAddr + 1] != 0xFF ||
				this.mainSection[numHoleAddr + 2] != 0xFF) {
				console.log("Relocation does not match hole at", numHoleAddr);
				return false;
			}
		}
		return true;
	}

	data() {
		const relocationTable = App.genRelocationTable(this.relocations);
		const result = new Uint8Array(this.header.byteLength +
			this.info.byteLength +
			relocationTable.byteLength +
			this.mainSection.byteLength + 3);
		result.set(this.header, 0);
		result.set(this.info, this.header.byteLength);
		result.set(relocationTable, this.header.byteLength + this.info.byteLength);
		result.set(this.mainSection, result.byteLength - this.mainSection.byteLength - 3);
		new DataView(result.buffer).setUint24(result.byteLength - 3, result.byteLength - 3, true);
		return result;
	}

	async getInstallerZip() {
		const zip = new JSZip();

		const installer8xp = createGroup([{name: 'PYINST', type: 6, data: new Uint8Array(installer)}]);
		zip.file('PyInst.8xp', installer8xp);

		const appData = this.data();

		//zip.file('appdata.bin', appData);

		let currentSize = 0;
		let i = 0;
		while(currentSize < appData.byteLength) {
			const newSize = Math.min(appData.byteLength - currentSize, 60000);
			const data = new Uint8Array(appData.buffer, currentSize, newSize);
			const suffix = String.fromCharCode(65 + i);
			const appvar = createGroup([{
				name: 'PyInst' + suffix,
				type: 0x15, // appvar
				data: data
			}]);
			zip.file('PyInst' + suffix + '.8xv', appvar);
			currentSize += newSize;
			i++;
		}

		const zipdata = await zip.generateAsync({type: "uint8array"});

		return new File([zipdata], "PyInst.zip");
	}
}

/**
 * Applies a patch to an app and generates an installer for it.
 * 
 * @param file A Blob representing the contents of the app file.
 * @param patch The patch to apply.
 */
async function getPatchedInstaller(file, patch) {
	const app = await (new App()).load(file);
	// todo: remove
	window.app = app;
	console.log(app);
	app.patch(pythonPatch);
	console.log(app);
	console.log(app.verifyRelocations());
	return await app.getInstallerZip();
}