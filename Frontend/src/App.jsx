import React from "react";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from "./components/Home"; // <-- Tu nuevo componente modular
import Footer from "./components/Footer";
import Login from "./components/Login";
import Register from "./components/Register";
import Admin from "./components/Admin";

function App() {
    return (
        <Router>
            {/* 1. La barra de navegación siempre fija arriba */}
            <Navbar />
            
            {/* 2. El contenedor inteligente de rutas */}
            <Routes>
                {/* Ruta para la página principal (Home) */}
                <Route path="/" element={<Home />} />

                {/* Ruta para el panel de admin */}
                <Route path="/admin" element={<Admin />} />

                {/* Rutas para la autenticación */}
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
            </Routes>

            {/* 3. Componentes globales que se ven en todas las páginas (abajo) */}
            <Footer />
        </Router>
    );
}

export default App;