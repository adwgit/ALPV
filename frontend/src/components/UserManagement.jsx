// src/components/UserManagement.js
import React, { useState, useEffect } from 'react';

function UserManagement() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [role, setRole] = useState('');
    const [message, setMessage] = useState('');
    const [isAdmin, setIsAdmin] = useState(false);

    useEffect(() => {
        // Проверка роли пользователя
        fetch('/token/verify', {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            }
        })
        .then(response => response.json())
        .then(data => setIsAdmin(data.role === 'admin'));
    }, []);

    const handleCreateUser = () => {
        fetch('/create_user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            },
            body: JSON.stringify({ username, password, role })
        })
        .then(response => response.json())
        .then(data => setMessage(data.success ? 'User created successfully' : data.error));
    };

    if (!isAdmin) {
        return <div>Access Denied</div>;
    }

    return (
        <div>
            <h2>Управление пользователями</h2>
            <input
                type="text"
                placeholder="Имя пользователя"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
            />
            <input
                type="password"
                placeholder="Пароль"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />
            <input
                type="text"
                placeholder="Роль"
                value={role}
                onChange={(e) => setRole(e.target.value)}
            />
            <button onClick={handleCreateUser}>Создать пользователя</button>
            {message && <p>{message}</p>}
        </div>
    );
}

export default UserManagement;
