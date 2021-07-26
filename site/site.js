async function handleFile(file) {
	window.location.href = URL.createObjectURL(await getPatchedInstaller(file));
}

function handleDrop(event) {
	event.preventDefault();

	const dataTransfer = event.dataTransfer;
	if (dataTransfer.items) {
		handleFile(dataTransfer.items[0].getAsFile());
	} else if (dataTransfer.files) { // why tf are there two apis for this
		handleFile(dataTransfer.files[0]);
	}
}

function handleChange(event) {
	handleFile(event.target.files[0]);
}

const drop = document.getElementById("drop");
drop.addEventListener("dragover", (event) => event.preventDefault()); // necessary
drop.addEventListener("drop", handleDrop);

document.getElementById("input").addEventListener("change", handleChange);