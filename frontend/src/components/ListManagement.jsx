// src/components/ListManagement.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ListManagement() {
    const [lists, setLists] = useState([]);
    const [newValue, setNewValue] = useState('');
    const [selectedList, setSelectedList] = useState(null);

    useEffect(() => {
        // Загрузка списка
        axios.get('/list/all').then(response => setLists(response.data));
    }, []);

    const handleAddValue = () => {
        axios.post(`/list/${selectedList}/add`, { value: newValue })
            .then(response => {
                // Обновление списка
            });
    };

    return (
        <div>
            <h2>Manage Lists</h2>
            <select onChange={e => setSelectedList(e.target.value)}>
                {lists.map(list => (
                    <option key={list.id} value={list.id}>{list.name}</option>
                ))}
            </select>
            <input
                type="text"
                value={newValue}
                onChange={e => setNewValue(e.target.value)}
                placeholder="New Value"
            />
            <button onClick={handleAddValue}>Add Value</button>
        </div>
    );
}

export default ListManagement;
