import React, {useState} from "react";
import Alertas from './components/Alertas';
import Navbar from './components/Navbar'
import Hero from './components/Hero';
import ProductGrid from "./components/ProductGrid";
import Footer from "./components/Footer";
import Login from "./components/Login";
import Register from "./components/Register";
import Admin from "./components/Admin";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
function App() {
    // Estado temporal para simular mensajes flash que enviaran el backend de Flask.
    const [mensajes, setMensajes] = useState([
    ]);

    return (
    <>
        <Router>
            {/* 1. La barra de navegación siempre fija arriba */}
            <Navbar />
            
            {/* 2. El contenedor inteligente de rutas */}
            <Routes>
                {/* Ruta para la página principal (Home) */}
                <Route path="/" element={
                    <>
                        <Hero />
                        <ProductGrid />
                    </>
                } />

                {/* Ruta para el panel de admin */}

                <Route path="/admin" element={<Admin />} />

                {/* Rutas para la autenticación */}
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
            </Routes>

            {/* 3. Componentes globales que se ven en todas las páginas (abajo) */}
            <Alertas mensajes={mensajes} />
            <Footer />
        </Router>
    </> );

}
export default App;