function addTodo() {
    let todoInput = document.getElementById('todoInput').value;
    fetch('/add', {
        method: 'POST',
        body: JSON.stringify({todo_text: todoInput}),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(response => {
        if (response.ok) {
            location.reload();
        }
    });
}

function toggleTodo(todoId) {
    fetch(`/update/${todoId}`, {
        method: 'POST'
    }).then(response => {
        if (response.ok) {
            document.getElementById(`todo${todoId}`).classList.toggle('done');
        }
    });
}

function deleteTodo(todoId) {
    fetch(`/delete/${todoId}`, {
        method: 'POST'
    }).then(response => {
        if (response.ok) {
            document.getElementById(`todo${todoId}`).remove();
        }
    });
}