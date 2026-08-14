import React, { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { logoutUsuario  } from "../../services/api";

/**
 * @component Navbar
 * @description Componente que renderiza la barra de navegacion de Neo Grid gaming
 */

function Navbar() {
    const navigate = useNavigate();
    const location = useLocation();

    const [fontSize, setFontSize] = useState(16);
    const [altoContraste, setAltoContraste] = useState(false);
    const [usuarioRol, setUsuarioRol] = useState(sessionStorage.getItem("rol") || null);

    useEffect(() =>{
        document.body.style.fontSize = `${fontSize}px`;
        document.body.classList.toggle('alto-contraste', altoContraste);
    }, [fontSize, altoContraste]);

    useEffect(() => {
        setUsuarioRol(sessionStorage.getItem("rol"));
    }, [location]);

    const handleLogout = async () => {
        try {
            await logoutUsuario(); // Invalida la cookie del lado del servidor
        } catch (error) {
            console.error("Error al cerrar sesión", error);
        } finally {
            sessionStorage.removeItem("rol");
            setUsuarioRol(null);
            navigate("/login", {state: {mensajeExito: "Sesión cerrada correctamente"} });
        }
};



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

        <div className="nav-actions">
            <div className="cart">
                <Link to="/carrito" id="cart-icon">
                    <i className="fas fa-shopping-cart"></i>
                </Link>
                <span id="cart-count">0</span>
            </div>

            <div className="login-container">
                {usuarioRol ? (
                    <button onClick={handleLogout} className="btn-logout-nav" title="Cerrar Sesión">
                        <i className="fas fa-sign-out-alt"></i> Cerrar Sesión
                    </button>
                ) : (
                    <Link to="/login" className="login-navbar-link">
                        <i className="fas fa-user"></i> Iniciar Sesión
                    </Link>
                )}
            </div>

            {usuarioRol === 'admin' && (
                <Link to="/admin" className="btn-panel-nav" title="Panel de administración">
                    <i className="fas fa-user-shield"></i> Admin
                </Link>
            )}
        </div>


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