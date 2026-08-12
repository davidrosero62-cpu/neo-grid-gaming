import React, { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from 'react-router-dom';
import Alertas from "./Alertas";

/**
 * @description Componente que renderiza el formulario de inicio de sesion de la aplicacion
 * @returns {JSX.Element} Estructura de la vista login.
 */

function Login () {
    const[formData, setFormData] = useState({email: '', password: '' });
    const navigate = useNavigate();
    const location = useLocation(); // Hook para leer el estado enviado desde Register

    // Estado para controlar las alertas locales del login
    const[alertas, setAlertas] = useState([]);

    // Efecto para verificar si venimos desde el registro con un mensaje de exito
    useEffect(() => {
        if (location.state && location.state.mensajeExito) {
            // Guardamos el mensaje en el formato que espera el componente Alertas ([{ texto "..."}])
            setAlertas([{ texto: location.state.mensajeExito }]);

            //Limpiamos el historial de navegacion para que si el usuario recarga la pagina,
            // el mensaje de registro exitoso desaparezca
            window.history.replaceState({}, document.title);
        }
    }, [location]);


    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({
            ...formData,
            [name]: value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const response = await fetch("http://localhost:5000/api/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: 'include', // <---- Muy Importante
                body: JSON.stringify ({
                    correo: formData.email,
                    password: formData.password
                })
            });

            const data = await response.json();
            if (response.ok) {
                // Guardamos el rol en la memoria del navegador
                localStorage.setItem("rol", data.rol);

                if (data.rol === "admin") {
                    navigate("/admin", {state: { mensajeExito: "¡Bienvenido al panel de administración!"}});
                } else {
                    navigate("/", {state: {mensajeExito: "¡Bienvenido a Neo Grid!"}});
                }
            } else {
                // Si el login falla, mostramos el error del Backend en la alerta
                setAlertas([{ texto: "Hubo un error al iniciar sesión"}])
            }
        } catch (error) {
            setAlertas([{ texto: "Hubo un error de conexión con el servidor"}]);
        }
    }

   return (
        <div className="contenedor-login-vista">
            {/* 4. Renderizamos dinámicamente tu componente de Alertas cyberpunk si existen mensajes */}
            {alertas.length > 0 && <Alertas mensajes={alertas} />}

            <main>
                <div className="contenedor-login">
                    <h1>Iniciar Sesión</h1>
                    <form className="formulario" onSubmit={handleSubmit}>
                        <div className="grupo-input">
                            <label>Correo Electronico</label>
                            <input
                                type="email"
                                name="email"
                                placeholder="tu@correo.com"
                                value={formData.email}
                                onChange={handleChange}
                                required
                            />
                        </div>

                        <div className="grupo-input">
                            <label>Contraseña</label>
                            <input
                                type="password"
                                name="password"
                                placeholder="••••••••"
                                value={formData.password}
                                onChange={handleChange}
                                required
                            />
                        </div>
                        <button type="submit" className="btn-submit">Ingresar</button>
                    </form>
                    <p className="link-registro">
                        ¿No tienes cuenta? <Link to="/register">Regístrate aquí</Link>
                    </p>
                </div>
            </main>
        </div>
    );
}

export default Login;