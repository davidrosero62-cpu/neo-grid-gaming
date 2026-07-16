import React, { useEffect, useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
/**
 * @component Navbar
 * @description Componente que renderiza la barra de navegacion de Neo Grid gaming
 */

function Navbar() {

    const navigate = useNavigate();
    const location = useLocation();// Detecta cambios de ruta para actualizar el estado de Navbar

    // ESTADOS
    const [fontSize, setFontSize] = useState(16);
    const [altoContraste, setAltoContraste] = useState(false);

    // Estados dinamicos para la sesion
    const [token, setToken] = useState(localStorage.getItem("token") || null);
    const [usuarioRol, setUsuarioRol] = useState(localStorage.getItem("rol") || null);

    // Efecto para la accesibilidad
    useEffect(() => {
        document.body.style.fontSize = `${fontSize}px`;
        document.body.classList.toggle('alto-contraste', altoContraste);

    }, [fontSize, altoContraste]);

    // Efecto para actualizar el token y el Rol cada vez que el usuario cambie de pagina
    useEffect(() => {
        setToken(localStorage.getItem("token"));
        setUsuarioRol(localStorage.getItem("rol"));
    }, [location]);

    // LOGICA DE CERRAR SESION

const handelLogout = () => {
    // 1. Borramos los datos de sesión del almacenamiento del navegador
    localStorage.removeItem("token");
    localStorage.removeItem("rol");

    // 2. Limpiamos el estado de React inmediatamente para actualizar el Navbar
    setToken(null);
    setUsuarioRol(null);
    
    // 3. Redirigimos al login
    navigate("/login");
}


    return 
