from flask import Flask, render_template_string, request, jsonify
import sqlite3

app = Flask(__name__)

def create_user_table():
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

create_user_table()

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Database</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
</head>
<body>
    <h1>User Database</h1>
    <form id="addUserForm">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username">
        <button type="submit">Add User</button>
    </form>
    <button id="fetchUsersBtn">Fetch Users</button>
    <div id="userList"></div>
    <script>
        $('#addUserForm').submit(function(event) {
            event.preventDefault();
            $.ajax({
                type: 'POST',
                url: '/add_user',
                contentType: 'application/json',
                data: JSON.stringify({'username': $('#username').val()}),
                success: function(response) {
                    alert(response.message);
                    $('#username').val('');
                },
                error: function(xhr, status, error) {
                    alert('Failed to add user');
                }
            });
        });
        $('#fetchUsersBtn').click(function() {
            $.get('/get_users', function(users) {
                $('#userList').empty();
                users.forEach(user => {
                    $('#userList').append(`<div>User ID: ${user.id}, Username: ${user.username}<button class="deleteBtn" data-id="${user.id}">Delete</button></div>`);
                });
            });
        });
        $(document).on('click', '.deleteBtn', function() {
            $.ajax({
                url: '/delete_user/' + $(this).data('id'),
                type: 'DELETE',
                success: function(response) {
                    alert(response.message);
                    $('#fetchUsersBtn').click();
                }
            });
        });
    </script>
</body>
</html>
""")

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.json.get('username')
    if not username:
        return jsonify({'message': 'Username is required'}), 400
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username) VALUES (?)', (username,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'User added successfully'}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'message': 'Username already exists'}), 400

@app.route('/get_users', methods=['GET'])
def get_users():
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = [{'id': row[0], 'username': row[1]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(users), 200

@app.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'message': 'User not found'}), 404
    conn.commit()
    conn.close()
    return jsonify({'message': 'User deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
