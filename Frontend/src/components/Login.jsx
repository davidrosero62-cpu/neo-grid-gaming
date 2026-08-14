import React, { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from 'react-router-dom';
import Alertas from "./Alertas";
import { loginUsuario } from "../../services/api";

/**
 * @description Componente que renderiza el formulario de inicio de sesion de la aplicacion
 * @returns {JSX.Element} Estructura de la vista login.
 */

function Login() {
    const [formData, setFormdata] = useState({ email: '', password:''});
    const navigate = useNavigate();
    const location = useLocation();
    const [alertas, setAlertas] = useState([]);

    useEffect(() => {
        if (location.state && location.state.mensajeExito) {
            setAlertas([{ texto: location.state.mensajeExito }]);
            window.history.replaceState({}, document.title);
        }
    }, [location]);

    const handleChange = (e) => {
        const {name, value} = e.target;
        setFormdata({...formData, [name]: value});
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const data = await loginUsuario({
                correo: formData.email,
                password: formData.password
            });
            sessionStorage.setItem("rol", data.rol);

            if (data.rol === "admin") {
                navigate("/admin", {state: { mensajeExito: "¡Bienvenido al panel de administración!"} });
            } else {
                navigate("/", {state: {mensajeExito: "¡Bienvenido a Neo Grid!" }})
            }
        } catch (error) {
            setAlertas([{texto: "Correo o contraseña incorrectos "}]);
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