"use strict";

const MAZE_FREE_VALUE = 0;
const MAZE_WALL_VALUE = 1;
const MAZE_START_VALUE = 2;
const MAZE_FINISH_VALUE = 3;

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
};


let init_stats = () => {
    let filterButton = document.getElementById('buttonApplyMazeFilter');
    filterButton.addEventListener('click', applyMazeFilter);
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
    label.innerHTML = 'Chance of placing a wall: ' + this.value + '%';
}


function toggleMazeCell(cellObj) {
    let toggleWall = document.getElementById('toggle-wall').checked;
    let toggleStart = document.getElementById('toggle-start').checked;
    let toggleFinish = document.getElementById('toggle-finish').checked;

    if (toggleWall) {
        switch(parseInt(cellObj.getAttribute('value'))) {
            case MAZE_FREE_VALUE:
                cellObj.setAttribute('value', MAZE_WALL_VALUE);
                cellObj.classList.add('wall');
                break;
            case MAZE_WALL_VALUE:
                cellObj.setAttribute('value', MAZE_FREE_VALUE);
                cellObj.classList.remove('wall');
                break;
        }
    } else if (toggleStart) {
        switch(parseInt(cellObj.getAttribute('value'))) {
            case MAZE_FREE_VALUE:
                mazeFieldClearValue(MAZE_START_VALUE, 'start');
                cellObj.setAttribute('value', MAZE_START_VALUE);
                cellObj.classList.add('start');
                break;
            case MAZE_START_VALUE:
                cellObj.setAttribute('value', MAZE_FREE_VALUE);
                cellObj.classList.remove('start');
                break;
        }
    } else if (toggleFinish) {
        switch(parseInt(cellObj.getAttribute('value'))) {
            case MAZE_FREE_VALUE:
                mazeFieldClearValue(MAZE_FINISH_VALUE, 'finish');
                cellObj.setAttribute('value', MAZE_FINISH_VALUE);
                cellObj.classList.add('finish');
                break;
            case MAZE_FINISH_VALUE:
                cellObj.setAttribute('value', MAZE_FREE_VALUE);
                cellObj.classList.remove('finish');
                break;
        }
    } else {
        console.error('First you need to chose toggle object type (eg: wall, start or finish)' );
    }
}


function mazeFieldClearValue(value, class_name) {
    let mazeFieldTable = document.getElementById('userMazeField');
    if ( !mazeFieldTable ) {
        return;
    }
    for (let i = 0; i < mazeFieldTable.rows.length; i++) {
        for (let j = 0; j < mazeFieldTable.rows[i].cells.length; j++) {
            let cell = mazeFieldTable.rows[i].cells[j];
            if (parseInt(cell.getAttribute('value')) == value) {
                cell.setAttribute('value', MAZE_FREE_VALUE);
                cell.classList.remove(class_name);
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
            let rndValue = Math.random();
            if (rndValue * 100 < rndThreshold.value) {
                cell.setAttribute('value', MAZE_WALL_VALUE);
                cell.classList.add('wall');
            } else {
                cell.setAttribute('value', MAZE_FREE_VALUE);
                cell.className = '';
            }
        }
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
        mazeName.classList.add('is-invalid');
        mazeName.oninput = () => {
            mazeName.classList.remove('is-invalid');
        }
        isDataValid = false;
    }

    let solutionLenValue = 0;
    if (solutionLen && solutionLen.value.length) {
        let numsOnly = solutionLen.value.replace(/\D/g,'');
        if (numsOnly.length) {
            solutionLenValue = parseInt(numsOnly);
        }
    }
    if (solutionLenValue <= 0) {
        solutionLen.classList.add('is-invalid');
        solutionLen.oninput = () => {
            solutionLen.classList.remove('is-invalid');
        }
        isDataValid = false;
    }

    if (mazeId.value.length == 0) {
        mazeId.classList.add('is-invalid');
        mazeId.oninput = () => {
            mazeId.classList.remove('is-invalid');
        }
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
    postDataToServer('api/', api_data);
}


function submitFromEditor() {
    let mazeFieldTable = document.getElementById('userMazeField');
    if ( !mazeFieldTable ) {
        return;
    }
    let maze_name = document.getElementById('maze_name');
    if (maze_name.value.length == 0) {
        maze_name.classList.add('is-invalid');
        maze_name.oninput = () => {
            maze_name.classList.remove('is-invalid');
        }
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
    postDataToServer('editor/', editor_data);
}


function applyMazeFilter() {
    let filter_data = {
        'sort': document.getElementById('sort_option').value,
        'filters': [],
    }

    let inputs = document.querySelectorAll("input[type='checkbox']");
    for (let i = 0; i < inputs.length; i++) {
        if (inputs[i].checked) {
            filter_data.filters.push(inputs[i].id);
        }
    }
    postDataToServer('filter/', filter_data);
}


function postDataToServer(destination, txData) {
    console.log('POST data:', txData);
    fetch(`${window.origin}/` + destination, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(txData),
        cache: "no-cache",
        headers: new Headers({
          "content-type": "application/json"
        })
      })
        .then(function (response) {
          if (response.status !== 200) {
            showAlertMessage('danger', `Request failed: ${response.status} - ${response.statusText}`);
            // console.log(`Looks like there was a problem. Status code: ${response.status}`);
            return;
          }
          response.json().then(function (data) {
            showAlertMessage('success', 'Request succeed, response data: ' + JSON.stringify(data));
            // console.log(data);
          });
        })
        .catch(function (error) {
          console.log("Fetch error: " + error);
        });
}
