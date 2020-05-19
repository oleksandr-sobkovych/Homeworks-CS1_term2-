"use strict";

const MAZE_FREE_VALUE = 0;
const MAZE_WALL_VALUE = 1;
const MAZE_START_VALUE = 2;
const MAZE_FINISH_VALUE = 3;
const ALERT_SHOW_TIMEOUT_MS = 5000;


let init_index = () => {
    let selectConstructType = document.getElementById('construct_type');
    selectConstructType.addEventListener('change', choseConstructType);
    selectConstructType.dispatchEvent(new Event('change'));

    let selectUserMazeSize = document.getElementById('mazeSize');
    selectUserMazeSize.addEventListener('change', renderUserMaze);
    selectUserMazeSize.dispatchEvent(new Event('change'));

    let rndThreshold = document.getElementById('randomThreshold');
    rndThreshold.addEventListener('change', thresholdChange);
    rndThreshold.dispatchEvent(new Event('change'));

    let submitButtonAPI = document.getElementById('mazeCreateFromAPI');
    submitButtonAPI.addEventListener('click', submitFromAPI);

    let submitButtonEditor = document.getElementById('mazeCreateFromEditor');
    submitButtonEditor.addEventListener('click', submitFromEditor);
    setActiveNavTab();
};


let init_stats = () => {
    // get URL parameters and apply to current filter state
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    for (let entry of urlParams.entries()) {
        let item = document.getElementById(entry[0]);
        if (item) {
            switch (item.tagName) {
                case 'SELECT':
                    item.value = entry[1];
                    break;
                case 'INPUT':
                    item.checked = true;
                    break;
                default:
                    break;
            }
        }
    }
    setActiveNavTab();
}


function setActiveNavTab() {
    const navRefs = document.querySelector('nav').querySelectorAll('li');
    navRefs.forEach(ref => {
        if (ref.childElementCount > 0) {
            if (ref.children[0].href === location.href) {
                ref.classList.add('active');
            } else {
                ref.classList.remove('active');
            }
        }
    });
}


function showAlertMessage(message_class, message_text) {
    let messageObj = document.getElementById('alertMessage');
    let alertObj = document.createElement('div');
    messageObj.appendChild(alertObj);

    alertObj.setAttribute('role', 'alert');
    alertObj.className = 'alert alert-dismissible fade show alert-' + message_class;
    alertObj.innerHTML = `${message_text}
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>`;
    setTimeout(() => {
        if (alertObj && alertObj.parentElement) {
            alertObj.parentElement.removeChild(alertObj);
        }
    }, ALERT_SHOW_TIMEOUT_MS);

    window.scrollTo({left:0, top:0, behavior:'smooth'});
}


function choseConstructType() {
    for (let [k,v] of Object.entries(this.options)) {
        let card = document.getElementById(v.value);
        if (card) {
            card.classList.add('d-none');
        }
    }
    document.getElementById(this.value).classList.remove('d-none');
}


function renderUserMaze() {
    let mazeFieldTable = document.getElementById('userMazeField');
    if ( !mazeFieldTable ) {
        return;
    }
    mazeFieldTable.innerHTML = '';
    let numRows = this.value.split('x')[0];
    let numCols = this.value.split('x')[1];
    let tbody = document.createElement('tbody');
    let fragment = document.createDocumentFragment();

    for (let i = 0; i < numRows; i++) {
      let tr = document.createElement('tr');
      for (let j = 0; j < numCols; j++) {
        let td = document.createElement('td');
        td.setAttribute('value', MAZE_FREE_VALUE);
        td.onclick = () => {
            toggleMazeCell(td);
        };
        tr.appendChild(td);
      }
      fragment.appendChild(tr);
    }
    tbody.appendChild(fragment);

    mazeFieldTable.appendChild(tbody);
}


function thresholdChange() {
    let label = document.getElementById('randomThresholdLabel');
    label.innerHTML = `Chance of placing a wall: ${this.value}%`;
}


function toggleMazeCell(cellObj) {
    if (document.getElementById('toggle-wall').checked) {
        mazeFieldToggleState(cellObj, MAZE_WALL_VALUE, 'wall');
    } else if (document.getElementById('toggle-start').checked) {
        mazeFieldToggleState(cellObj, MAZE_START_VALUE, 'start', true);
    } else if (document.getElementById('toggle-finish').checked) {
        mazeFieldToggleState(cellObj, MAZE_FINISH_VALUE, 'finish', true);
    } else {
        console.error('First you need to chose toggle object type (eg: wall, start or finish)' );
    }
}


function mazeFieldToggleState(cellObj, toggleValue, className, isExclusive = false) {
    let currTypeValue = parseInt(cellObj.getAttribute('value'));

    if (currTypeValue === toggleValue) {
        cellObj.setAttribute('value', MAZE_FREE_VALUE);
        cellObj.classList.remove(className);
    } else if (currTypeValue === MAZE_FREE_VALUE) {
        if (isExclusive) {
            mazeFieldClearValue(toggleValue, className);
        }
        cellObj.setAttribute('value', toggleValue);
        cellObj.classList.add(className);
    }
}


function mazeFieldClearValue(value, className) {
    let mazeFieldTable = document.getElementById('userMazeField');
    if ( !mazeFieldTable ) {
        return;
    }
    for (let i = 0; i < mazeFieldTable.rows.length; i++) {
        for (let j = 0; j < mazeFieldTable.rows[i].cells.length; j++) {
            let cell = mazeFieldTable.rows[i].cells[j];
            if (parseInt(cell.getAttribute('value')) === value) {
                cell.setAttribute('value', MAZE_FREE_VALUE);
                cell.classList.remove(className);
                return;
            }
        }
    }
}


function mazeRandomFill() {
    let mazeFieldTable = document.getElementById('userMazeField');
    let rndThreshold = document.getElementById('randomThreshold');
    if ( !mazeFieldTable || !rndThreshold ) {
        return;
    }
    for (let i = 0; i < mazeFieldTable.rows.length; i++) {
        for (let j = 0; j < mazeFieldTable.rows[i].cells.length; j++) {
            let cell = mazeFieldTable.rows[i].cells[j];
            if (Math.random() * 100 < rndThreshold.value) {
                cell.setAttribute('value', MAZE_WALL_VALUE);
                cell.classList.add('wall');
            } else {
                cell.setAttribute('value', MAZE_FREE_VALUE);
                cell.className = '';
            }
        }
    }
}


function markInvalidInputData(obj) {
    obj.classList.add('is-invalid');
    obj.oninput = () => {
        obj.classList.remove('is-invalid');
    }
}


function submitFromAPI() {
    let mazeFieldTable = document.getElementById('userMazeField');
    if ( !mazeFieldTable ) {
        return;
    }
    let mazeName = document.getElementById('maze_name');
    let solutionLen = document.getElementById('api_length');
    let mazeId = document.getElementById('api_maze_id');
    let isDataValid = true;

    if (mazeName.value.length == 0) {
        markInvalidInputData(mazeName);
        isDataValid = false;
    }

    let solutionLenValue;
    if (solutionLen && solutionLen.value.length) {
        let numsOnly = solutionLen.value.replace(/\D/g,'');
        if (numsOnly.length) {
            solutionLenValue = parseInt(numsOnly);
        }
    }
    else {
        solutionLenValue = 0;
    }
    if (solutionLenValue < 0) {
        markInvalidInputData(solutionLen);
        isDataValid = false;
    }

    if ( !isDataValid ) {
        showAlertMessage('danger', 'Please provide correct input for all necessary fields!');
        return;
    }

    let api_data = {
        name:         maze_name.value,
        dimensions:   document.getElementById('api_maze_size').value.split('x'),
        algo:         document.getElementById('api_algorithm').value,
        solution_len: solutionLenValue,
        maze_id:      mazeId
    };

    let btnObj = this;
    let savedBtnText = disableButton(btnObj, 'Wait...');

    postDataToServer('api/', api_data)
        .then(() => {
            enableButton(btnObj, savedBtnText);
        });
}


function submitFromEditor() {
    let mazeFieldTable = document.getElementById('userMazeField');
    if ( !mazeFieldTable ) {
        return;
    }
    let maze_name = document.getElementById('maze_name');
    if (maze_name.value.length === 0) {
        markInvalidInputData(maze_name);
        showAlertMessage('danger', 'Please provide correct input for all necessary fields!');
        return;
    }
    let editor_data = {
        name: maze_name.value,
        size: document.getElementById('mazeSize').value.split('x'),
        array: []
    };

    for (let i = 0; i < mazeFieldTable.rows.length; i++) {
        let tr_data = [];
        for (let j = 0; j < mazeFieldTable.rows[i].cells.length; j++) {
            tr_data.push(parseInt(mazeFieldTable.rows[i].cells[j].getAttribute('value')));
        }
        editor_data.array.push(tr_data);
    }

    let btnObj = this;
    let savedBtnText = disableButton(btnObj, 'Wait...');

    postDataToServer('editor/', editor_data)
        .then(() => {
            enableButton(btnObj, savedBtnText);
        });
}


function disableButton(obj, text) {
    let savedText = '';
    if (obj) {
        savedText = obj.innerHTML;
        obj.disabled = true;
        obj.innerHTML = `<span class="spinner-border spinner-border-sm"></span> ${text}`;
    }
    return savedText;
}


function enableButton(obj, text) {
    if (obj) {
        obj.disabled = false;
        obj.innerHTML = text;
    }
}


async function postDataToServer(destination, data) {
    let request_params = {
        method:      "POST",
        credentials: "include",
        body:        JSON.stringify(data),
        cache:       "no-cache",
        headers:     new Headers({"content-type":"application/json"})
    };

    let response = await fetch(`${window.origin}/${destination}`, request_params);

    if (response.status === 200) {
        showAlertMessage('success', `Request succeed, status code: ${response.status}.`);
    } else {
        showAlertMessage('danger', `Request failed, status code: ${response.status} (${response.statusText})!`);
    }
}
