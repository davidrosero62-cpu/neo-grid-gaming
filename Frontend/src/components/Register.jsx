import React, {useState} from "react";
import { Link, useNavigate} from 'react-router-dom';
import { registrarUsuario  } from "../../services/api";

/**
 * @description Componente que renderiza el formulario de registro de la aplicacion 
 * @returns {JSX.Element} Estructura de la vista login.
 */

function Register(){
    const [formData, setFormdata] = useState({nombre: '', email: '', password:'' });
    const navigate = useNavigate();
    const [mensaje, setMensaje] = useState("");

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormdata({ ...formData, [name]: value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try{
            const data = await registrarUsuario(formData);
            navigate("/login", { state: {mensajeExito: data.mensaje } });
        } catch (error) {
            setMensaje(error.message || "Error al registrar usuario");
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
                            name="nombre" 
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