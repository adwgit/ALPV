// src/App.js
import React from 'react';
import ListManagement from './components/ListManagement';
import UserManagement from './components/UserManagement';
import Reports from './components/Reports';

function App() {
    return (
        <div>
            <h1>My Project Dashboard</h1>
            <ListManagement />
            <UserManagement />
            <Reports />
        </div>
    );
}

export default App;
