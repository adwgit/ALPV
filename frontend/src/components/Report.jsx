// src/components/Reports.js
import React, { useState, useEffect } from 'react';

function Reports() {
    const [reports, setReports] = useState([]);
    const [userReports, setUserReports] = useState([]);
    const [username, setUsername] = useState('');
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

        // Загрузка общих отчетов
        fetch('/report/actions', {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            }
        })
        .then(response => response.json())
        .then(data => setReports(data.results));
    }, []);

    const handleUserReport = () => {
        fetch(`/report/actions/${username}`, {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            }
        })
        .then(response => response.json())
        .then(data => setUserReports(data.results));
    };

    if (!isAdmin) {
        return <div>Access Denied</div>;
    }

    return (
        <div>
            <h2>Общие отчеты</h2>
            <ul>
                {reports.map((report, index) => (
                    <li key={index}>{report.action}: {report.count}</li>
                ))}
            </ul>

            <h2>Отчеты по пользователю</h2>
            <input
                type="text"
                placeholder="Имя пользователя"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
            />
            <button onClick={handleUserReport}>Получить отчет</button>
            <ul>
                {userReports.map((report, index) => (
                    <li key={index}>{report.action}: {report.count}</li>
                ))}
            </ul>
        </div>
    );
}

export default Reports;
