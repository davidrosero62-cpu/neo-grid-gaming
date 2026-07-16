import React, { useState } from "react";
import { Link, useNavigate } from 'react-router-dom';

/**
 * @description Componente que renderiza el formulario de inicio de sesion de la aplicacion
 * @returns {JSX.Element} Estructura de la vista login.
 */

function Login () {
    const[formData, setFormData] = useState({email: '', password: '' });
    const navigate = useNavigate();

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
                body: JSON.stringify ({
                    correo: formData.email,
                    password: formData.password
                })
            });

            const data = await response.json();
            if (response.ok) {
                // Guardamos el rol y el token en la memoria del navegador
                localStorage.setItem("token", data.token);
                localStorage.setItem("rol", data.rol);

                if (data.rol === "admin") {
                    navigate("/admin");
                } else {
                    navigate("/");
                }
            } else {
                alert(data.error || "Error al iniciar sesion")
            }
        } catch (error) {
            console.error("Error de conexion:", error);
            alert("No se puede conectar con el servidor")
        }
    }

    return (
        <div>
            <main>
                <div className="contenedor-login">
                    <h1> Iniciar Sesión</h1>
                    {/* Espacio para el formulario*/}
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
                        ¿No tienes cuenta? <Link to="/register">Regístarte aquí</Link>
                    </p>
                </div>
            </main>
        </div>
    );
}

export default Login;