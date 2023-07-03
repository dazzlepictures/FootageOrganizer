let sequences = [];

fetch('sequences.json')
    .then(response => response.json())
    .then(data => {
        sequences = data;
        renderGallery(data);
    })
    .catch(error => console.error(error));

document.getElementById('search').addEventListener('input', function (e) {
    const searchTerm = e.target.value.toLowerCase();
    const filteredSequences = sequences.filter(sequence => sequence.sequence_name.toLowerCase().includes(searchTerm));
    renderGallery(filteredSequences);
});

function renderGallery(data) {
    const gallery = document.getElementById('gallery');
    gallery.innerHTML = ''; // clear the gallery

    data.forEach(sequence => {
        const card = document.createElement('div');
        card.className = 'card';

        const img = document.createElement('img');
        // fetch the thumbnail and correct slashes

        let absPath = sequence.proxy_output_path.replace(/\\/g, '/');

        let basePath = "E:/Fidel/footage_classifier/";

        let relativePath = absPath.replace(basePath, '');
        img.src = relativePath

        img.alt = sequence.sequence_name;
        card.appendChild(img);

        // add a button to open the folder in windows explorer C:/ using  the shell module

        const openFolderButton = document.createElement('button');

        openFolderButton.textContent = 'Open file';



        openFolderButton.addEventListener('click', function () {
            fetch(`http://localhost:5000/openfolder?path=${sequence.sequence_entire_name}`)
                .then(response => response.text())
                .then(data => {
                    console.log(data); // Log the response from the server
                })
                .catch(error => {
                    console.error(error); // Log any errors that occurred
                });
        });



        card.appendChild(openFolderButton);


        const h2 = document.createElement('h2');
        h2.textContent = sequence.sequence_name;
        card.appendChild(h2);

        const frameRange = document.createElement('p');
        frameRange.textContent = `Frame range: ${sequence.frame_range[0]} - ${sequence.frame_range[1]}`;
        card.appendChild(frameRange);

        const imageSize = document.createElement('p');
        imageSize.textContent = `Image size: ${sequence.image_size[0]} x ${sequence.image_size[1]}`;
        card.appendChild(imageSize);

        const imageChannels = document.createElement('p');
        imageChannels.textContent = `Image channels: ${sequence.image_channels}`;
        card.appendChild(imageChannels);

        const colorSpace = document.createElement('p');
        colorSpace.textContent = `Color space: ${sequence.color_space}`;
        card.appendChild(colorSpace);

        const compression = document.createElement('p');
        compression.textContent = `Compression: ${sequence.compression}`;
        card.appendChild(compression);

        const pixelAspectRatio = document.createElement('p');
        pixelAspectRatio.textContent = `Pixel aspect ratio: ${sequence.pixel_aspect_ratio}`;
        card.appendChild(pixelAspectRatio);

        const frameRate = document.createElement('p');
        frameRate.textContent = `Frame rate: ${sequence.frame_rate}`;
        card.appendChild(frameRate);

        const imageFormat = document.createElement('p');
        imageFormat.textContent = `Image format: ${sequence.image_format}`;
        card.appendChild(imageFormat);

        const index = document.createElement('p');
        index.textContent = `Index: ${sequence.index}`;
        card.appendChild(index);

        gallery.appendChild(card);
    });
}
