import React, { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";

/**
 * @component Navbar
 * @description Componente que renderiza la barra de navegacion de Neo Grid gaming
 */
function Navbar() {
    const navigate = useNavigate();
    const location = useLocation(); // Detecta cambios de ruta para actualizar el estado del Navbar

    // --- ESTADOS ---
    const [fontSize, setFontSize] = useState(16);
    const [altoContraste, setAltoContraste] = useState(false);
    
    // Estados dinámicos para la sesión
    const [usuarioRol, setUsuarioRol] = useState(localStorage.getItem("rol") || null);

    useEffect (() => {
        setUsuarioRol(localStorage.getItem("rol"));
    }, [location]);


    // Efecto para la accesibilidad
    useEffect(() => {
        document.body.style.fontSize = `${fontSize}px`;
        document.body.classList.toggle('alto-contraste', altoContraste);
    }, [fontSize, altoContraste]);

    // Efecto para actualizar  Rol cada vez que el usuario cambie de página
    useEffect(() => {
        setUsuarioRol(localStorage.getItem("rol"));
    }, [location]);

    // --- LÓGICA DE CERRAR SESIÓN ---
    const handleLogout = async () => {
        try {
            await fetch("http://localhost:5000/api/logout", {
                method: "POST",
                credentials: "include" // para que viaje la cookie que vamos a invalidar
            });
        } catch (error) {
            console.error("Error al cerrar la sesión", error);
        } finally {
            //Limpiamos el estado local independientemente del resultado de la petición
            localStorage.removeItem("rol");
            setUsuarioRol(null);
            navigate("/login", {state: { mensajeExito: "Sesión cerrada correctamente"} });
        }
    }

    return (
    <header>
        <nav className="navbar">
        <div className="logo">
            <Link to="/" className="logo-link">
                <img src="/img/logo.svg" alt="Neo Grid Gaming" className="img-logo" />
            </Link>
        </div>
      
        <ul className="nav-links">
            <li><a href="#consolas">Consolas</a></li>
            <li><a href="#pc">PC</a></li>
            <li><a href="#accesorios">Accesorios</a></li>
            <li><a href="#contacto">Contacto</a></li>
            <li><a href="#nosotros">Nosotros</a></li>
            <li><a href="#politicas">Políticas</a></li>
        </ul>

        <div className="cart">
            <a href="/carrito" id="cart-icon">
                <i className="fas fa-shopping-cart"></i>
                <span id="cart-count">0</span>
            </a>

            <div className="login">
                {usuarioRol ? (
                    
                    <button 
                        onClick={handleLogout} 
                        className="btn-logout-nav" 
                        title="Cerrar Sesión"
                        style={{ 
                            background: 'none', 
                            border: 'none', 
                            color: 'inherit', 
                            cursor: 'pointer', 
                            font: 'inherit',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '5px'
                        }}
                    >
                        <i className="fas fa-arrow-right-from-bracket"></i> Cerrar Sesión
                    </button>
                ) : (
                    /* BOTÓN DE INICIAR SESIÓN (Se muestra si NO hay un token activo) */
                    /* Cambiado de <a> a <Link> para evitar recargas completas en React */
                    <Link to="/login">
                        <i className="fas fa-user"></i> Iniciar Sesión
                    </Link>
                )}
            </div>
        </div>

        {/* PUNTO 2: EL BOTÓN DE ADMIN SOLO ES VISIBLE SI EL ROL ES 'admin' */}
        {usuarioRol === 'admin' && (
            <Link to="/admin" className="btn-panel-nav" title="Panel de Administración">
                <i className="fas fa-user-shield"></i> Admin
            </Link>
        )}

        {/* Menu de accesibilidad */}
        <div className="accesibilidad-menu">
            <button onClick={() => setFontSize(prev => Math.min(prev + 2, 26))} title="Aumentar letra">A+</button>
            <button onClick={() => setFontSize(prev => Math.max(prev - 2, 12))} title="Disminuir letra">A-</button>
            <button onClick={() => setAltoContraste(!altoContraste)} title="Alto contraste">🌓</button>
        </div>

        </nav>
    </header>
    );
}

export default Navbar;