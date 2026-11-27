const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Traduce una Response de fetch a datos o lanza un error legible.
 * Centralizarlo aqui evita repetir `response.ok ? ...` en cada componente.
 */

async function manejarRespuesta(response) {
  const data = await response.json(). catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || data.mensaje || "Error en la petición");
  }
  return data;
}

export async function obtenerProductos() {
  const response = await fetch (`${API_URL}/`);
  return manejarRespuesta(response)
}

export async function loginUsuario({correo, password}) {
  const response = await fetch(`${API_URL}/api/login`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    credentials: "include", // Necesario para que el navegador guarde/envie la cookie httpOnly
    body: JSON.stringify({correo, password})
  });
  return manejarRespuesta(response);
  
}

export async function logoutUsuario() {
  const response = await fetch(`${API_URL}/api/logout`, {
    method: "POST",
    credentials: "include"
  });
  return manejarRespuesta (response);
}

export async function registrarUsuario({nombre, email, password }) {
  const response = await fetch(`${API_URL}/api/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json"},
    body: JSON.stringify({nombre, email, password })
  });
  return manejarRespuesta(response);
}

export async function obtenerCategorias() {
  const response = await fetch(`${API_URL}/api/categorias`,);
  return manejarRespuesta (response);
  
}

export async function obtenerProductosAdmin() {
  const response = await fetch (`${API_URL}/api/productos`, {
    credentials: "include" // Reemplaza el header 'Authorization: Bearer ...'
  });
  return manejarRespuesta(response);
  
}

export async function agregarProducto(formData) {
  const response = await fetch(`${API_URL}/api/productos`, {
    method: "POST",
    credentials: "include",
    body: formData // formData no necesita Content-Type manual
  });
  return manejarRespuesta(response);
}

export async function eliminarProducto(id) {
  const response = await fetch (`${API_URL}/api/productos/${id}`,{
    method: "DELETE",
    credentials: "include"
  });
  return manejarRespuesta(response);
}

export async function modificarProducto(id, datosProducto) {
  const response = await fetch (`${API_URL}/api/productos/${id}`,{
    method: "PUT",
    credentials: "include",
    body: datosProducto
  });
  return manejarRespuesta(response);
}


export async function obtener_usuario_actual() {
  const response = await fetch(`${API_URL}/api/me`, {
    method: "GET",
    credentials: "include"
  });
  return manejarRespuesta(response);
  
}

/**Rutas Carrito */

export async function agregarAlCarrito({id_producto, cantidad = 1}= {} ) {
  const response = await fetch (`${API_URL}/api/cart/add`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    credentials: "include",
    body: JSON.stringify({ id_producto, cantidad })
  });
  return manejarRespuesta(response);
}

export async function obtenerCarrito() {
  const response = await fetch (`${API_URL}/api/cart`,{
    credentials: "include"
  });
  return manejarRespuesta(response)
  
}

export async function actualizarCantidadCarrito({id_carrito, cantidad}= {}) {
  const response = await fetch (`${API_URL}/api/cart/update/${id_carrito}`,{
    method: "PUT",
    headers: {"Content-Type": "application/json"},
    credentials: "include",
    body: JSON.stringify({cantidad})
  });
  return manejarRespuesta(response)
}

export { API_URL};

export async function eliminarItemCarrito({id_carrito} = {}) {
  const response = await fetch(`${API_URL}/api/cart/remove/${id_carrito}`,{
    method: "DELETE",
    credentials: "include"
  });
  return manejarRespuesta(response)
}

export async function vaciarCarrito() {
  const response = await fetch (`${API_URL}/api/cart/clear`, {
    method: "DELETE",
    credentials: "include"
  });
  return manejarRespuesta(response)
}