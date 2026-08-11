const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

/**
 * Obtiene la lista de productos desde la API.
 * 
 * @async
 * @function obtenerProductos
 * @returns {Promise<Array>} Retorna un array con los productos o un array vacío en caso de error.
 */
export const obtenerProductos = async () => {
  try {
    const respuesta = await fetch(`${API_URL}/`);
    
    if (!respuesta.ok) {
      throw new Error("Error al obtener los productos del servidor");
    }
    
    const datos = await respuesta.json();
    return datos;
    
  } catch (error) {
    console.error("Hubo un problema con la petición:", error);
    return [];
  }
};

/**
 * 
 * @async
 * @function loginUsuario
 * @param {object} credenciales - Objeto con el correo/usuario y contraseña.
 * @returns {Promise<Object>} Retorna los datos de sesión (token/usuario) o lanza un error si falla.
 */
export const loginUsuario = async (credenciales) => {
    const respuesta = await fetch(`${API_URL}/api/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credenciales),
    });

    const datos = await respuesta.json();

    if (!respuesta.ok) {
        throw new Error(datos.error || "Hubo un error al inciar sesión");
    }
    return datos;
};
