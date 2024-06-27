let textInput = document.querySelector('.textInput');
let submitButton = document.querySelector('.submit');
let output = document.querySelector('.output');
let tagContainer = document.querySelector('.tag-container');

let tags = []
let colorIndex = {};

const getColor = (colorNum, colors) => {
    if (colors < 1) {
        colors = 1;
    }

    return `hsl(${colorNum * (360 / colors) % 360}, 100%, 50% )`;
};

const getInput = () => {
    return textInput.value;
}

const writeOutput = (outHTML) => {
    output.innerHTML = outHTML;
}

const sendInput = async (input) => {
    let body = { tetxtInput: input };
    let response = await fetch("http://127.0.0.1:5000/getOutput",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(body)
        }
    );

    return await response.json();
};

const getTags = async () => {
    let response = await fetch("http://127.0.0.1:5000/getTags");
    tags = await response.json();

    let totalColors = tags.length;
    let tagIndex = 1;
    tags.forEach(tag => {
        colorIndex[tag] = getColor(tagIndex, totalColors);
        tagIndex++;
    });
};

const setTags = () => {
    for (val in colorIndex) {
        let tag = document.createElement('div');
        tag.classList.add('tag');
        tag.style.backgroundColor = colorIndex[val];
        tag.innerHTML = val;

        tagContainer.appendChild(tag);
    }
};

const getOutputHTML = (textList) => {
    let outHTML = document.createElement('div');
    textList.forEach((token) =>{
        let tag = document.createElement('result');
        tag.style.color = colorIndex[token[1]];
        tag.title = token[1];
        tag.innerText = token[0] + " ";

        outHTML.appendChild(tag);
    })

    return outHTML;
};

const updateOutput = (out) => {
    output.innerHTML = "";
    output.appendChild(out);
};

const getResult = async (inputText) => {
    response = await sendInput(inputText);
    html = getOutputHTML(response["output"]);
    updateOutput(html);
}

const fire = () => {
    getResult(getInput());
}

submitButton.addEventListener('click', fire);

textInput.addEventListener('keydown', (event) => {
    if (event.ctrlKey && event.key === 'Enter') {
        fire();
    }
});

window.onload = () => {
    getTags().then(() => { setTags() });
};