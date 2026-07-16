import React, {use, useState} from "react";
import { Link, useNavigate} from 'react-router-dom';

/**
 * @description Componente que renderiza el formulario de registro de la aplicacion 
 * @returns {JSX.Element} Estructura de la vista login.
 */

function Register() {
     const[formData, setFormData] = useState({
        nombre: '',
        email: '', 
        password: ''
    });

const navigate = useNavigate(); /*Inicializa la función de navegación para poder usarla más adelante (por ejemplo, para mandar al usuario al login). */
const [mensaje, setMensaje] = useState("");/*Crea una variable de estado llamada mensaje (que empieza vacía) para guardar el texto de respuesta que envíe la API. */

    const handleChange = (e) => {
        const { name, value} = e.target;
        setFormData({
            ...formData,
            [name]: value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
    
try {
    const response = await fetch("http://localhost:5000/api/register",{
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(formData)
    });

    const data = await response.json();
    if (response.ok) {
        setMensaje(data.mensaje);
        setTimeout(() => {
            navigate("/login")
        }, 300);
    } else {
        // Si el servidor respondio con error (400, 500, etc)
        // Mostramos el mensaje que viene desde el backend
        setMensaje(data.mensaje || "Error al registrar usuario");
    }

    } catch (error) {
    // Solo entra aqui si el internet se cae o el servidor no responde.
        setMensaje("Hubo un error de conexion con el servidor");
    }
    };
    return(
        <main>
            <div className="contenedor-login">
                <h1>Regístrate</h1>
                {mensaje && <p className="alerta-mensaje">{mensaje}</p>}
                <form className="formulario" onSubmit={handleSubmit}>
                    <div className="grupo-input">
                        <label>Nombre de Usuario</label>
                        <input
                            type="text"
                            name="nombre" /*OJO al conectar con el Backend*/
                            placeholder="Ej: MasterChief117"
                            value={formData.nombre}
                            onChange={handleChange}
                            required
                        />
                    </div>

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

                    <button type="submit" className="btn-submit">Crear Cuenta</button>
                </form>
                <p className="link-registro">
                    ¿Ya tienes cuenta? <Link to="/login">Inicia sesión aquí</Link>
                </p>
            </div>
        </main>
    );
}

export default Register;