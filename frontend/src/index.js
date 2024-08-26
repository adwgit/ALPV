// src/index.js
// index.js является входной точкой для вашего React-приложения. Он монтирует компонент App в DOM.
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import './styles.css';

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);
