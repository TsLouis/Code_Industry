from flask import Flask, render_template, request, jsonify
from models import Todo, db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def index():
    todos = Todo.query.all()
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add_todo():
    todo_text = request.form.get('todo_text')
    if todo_text:
        new_todo = Todo(text=todo_text, done=False)
        db.session.add(new_todo)
        db.session.commit()
    return jsonify({'message': 'Todo added successfully'})

@app.route('/update/<int:todo_id>', methods=['POST'])
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo:
        todo.done = not todo.done
        db.session.commit()
        return jsonify({'message': 'Todo updated successfully'})
    return jsonify({'message': 'Todo not found'})

@app.route('/delete/<int:todo_id>', methods=['POST'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo:
        db.session.delete(todo)
        db.session.commit()
        return jsonify({'message': 'Todo deleted successfully'})
    return jsonify({'message': 'Todo not found'})

if __name__ == '__main__':
    app.run(debug=True)