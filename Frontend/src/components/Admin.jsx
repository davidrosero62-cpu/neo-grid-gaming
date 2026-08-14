import React, {useEffect, useState} from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Alertas from "./Alertas";
import { obtenerCategorias, obtenerProductosAdmin, agregarProducto, eliminarProducto, API_URL } from "../../services/api";

/**
 * Componente de adminstracion (CRUD) para la gesion del invebtariio.
 * Permite agregar nuevos productos mediante un formulario multimedia
 * y visualizar, modificar o eliminar los productos xistentes nen una tabla.
 * *@component
 * *@typedef {Object} FormData
 * @property {string} nombre - Nombre comercial del producto.
 * @property {number|string} precio - Costo unitario del producto en COP.
 * @property {number|string} stock - Cantdad de unidades disponibles.
 * @property {string} descripcion - Detalles tecnicos y caaracteristicas.
 * @property {string} categoria - ID de la categoria seleccionada.
 * @property {file|null} imagen - Archivo binario de la imagen cargada.
 * *@typedef {object} Producto
 * @property {number} id_producto - Identificador unico en la base de datos.
 * @property {string} nombre - Nombre del producto.
 * @property {number} precio - Precio numerico
 * @property {number} stock - Unidades en el inventario
 * @property {string} categoria_id_categoria - Nombre o ID de la categoria asociada.
 * @property {string} imagen - Nombre del archivo de imagen almacenado.
 * *@returns {React.JSX.Element} Panel de administracion dividido en formulario y tabla de inventario.
 * 
 */

const Admin = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [alertas, setAlertas] = useState([]);

    useEffect(() => {
        if (location.state && location.state.mensajeExito) {
            setAlertas([{ texto: location.state.mensajeExito }]);
            window.history.replaceState({}, document.title);
        }
    }, [location]);

    const [formData, setFormData] = useState({
        nombre: '', precio: '', stock: '', descripcion: '', categoria: '', imagen: null
    });
    const [categorias, setCategorias] = useState([]);
    const [productos, setProductos] = useState([]);
    const [loading, setLoading] = useState(false);

    // Portero de UI: solo decide qué se RENDERIZA. La autorización real
    // la aplica el backend en cada endpoint, validando la cookie httpOnly.
    useEffect(() => {
        const rolUsuario = sessionStorage.getItem("rol");
        if (rolUsuario !== "admin") {
            alert("No tienes permisos para acceder a esta sección.");
            navigate("/login");
        }
    }, [navigate]);

    useEffect(() => {
        const cargarDatosIniciales = async () => {
            try {
                const [cats, prods] = await Promise.all([
                    obtenerCategorias(),
                    obtenerProductosAdmin()
                ]);
                setCategorias(cats);
                if (Array.isArray(prods)) {
                    setProductos(prods);
                } else {
                    console.warn("Se recibió un error en lugar de la lista de productos", prods);
                }
            } catch (error) {
                console.error('Error al cargar datos:', error);
            }
        };
        cargarDatosIniciales();
    }, []);

    const handleChange = (e) => {
        const { name, value, type, files } = e.target;
        setFormData({ ...formData, [name]: type === 'file' ? files[0] : value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        const data = new FormData();
        data.append('nombre', formData.nombre);
        data.append('precio', formData.precio);
        data.append('stock', formData.stock);
        data.append('descripcion', formData.descripcion);
        data.append('categoria_id', formData.categoria);
        if (formData.imagen) data.append('imagen', formData.imagen);

        try {
            await agregarProducto(data);
            alert('Producto guardado correctamente');
            setFormData({ nombre: '', precio: '', stock: '', descripcion: '', categoria: '', imagen: null });
            window.location.reload();
        } catch (error) {
            alert('Error al guardar el producto: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    const handleEliminar = async (id) => {
        if (window.confirm('¿Está seguro de eliminar este producto?')) {
            try {
                await eliminarProducto(id);
                setProductos(productos.filter(p => p.id_producto !== id));
                alert('Producto eliminado');
            } catch (error) {
                console.error('Error al eliminar:', error);
            }
        }
    };

    return (
        
         <div className="contenedor-login-vista">
            {/* 4. Renderizamos dinámicamente tu componente de Alertas cyberpunk si existen mensajes */}
            {alertas.length > 0 && <Alertas mensajes={alertas} />}

        <main className="contenedor-admin">
            <section className="seccion-admin">
                <h1>Panel de Administración</h1>
                <h2>Agregar Nuevos Productos</h2>

                <form onSubmit={handleSubmit} className="formulario">
                    <div className="grupo-input">
                        <label htmlFor="nombre">Nombre del Producto</label>
                        <input
                            id="nombre"
                            type="text"
                            name="nombre"
                            placeholder="EJ: Playstation 5"
                            value={formData.nombre}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="grupo-input">
                        <label htmlFor="precio">Precio (COP)</label>
                        <input
                            id="precio"
                            type="number"
                            name="precio"
                            placeholder="Ej: 2250000"
                            value={formData.precio}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="grupo-input">
                        <label htmlFor="stock">Stock</label>
                        <input
                            id="stock"
                            type="number"
                            name="stock"
                            placeholder="EJ: 10"
                            value={formData.stock}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="grupo-input">
                        <label htmlFor="descripcion">Descripción</label>
                        <textarea
                            id="descripcion"
                            name="descripcion"
                            placeholder="Características del producto"
                            value={formData.descripcion}
                            onChange={handleChange}
                            required
                        ></textarea>
                    </div>

                    <div className="grupo-input">
                        <label htmlFor="categoria">Categoría</label>
                        <select
                            id="categoria"
                            name="categoria"
                            value={formData.categoria}
                            onChange={handleChange}
                            required
                        >
                            <option value="">Seleccione una categoría</option>
                            {categorias.map((cat) => (
                                <option key={cat.id_categoria} value={cat.id_categoria}>
                                    {cat.nombre_categoria}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="grupo-input">
                        <label htmlFor="imagen">Imagen del producto</label>
                        <input
                            id="imagen"
                            type="file"
                            name="imagen"
                            accept="image/*"
                            onChange={handleChange}
                        />
                    </div>

                    <button type="submit" className="btn-submit" disabled={loading}>
                        {loading ? "Guardando..." : "Guardar Producto"}
                    </button>
                </form>
            </section>

            <section className="seccion-admin">
                <h2>Inventario Actual</h2>
                <div className="tabla-admin">
                    <table className="tabla-inventario">
                        <thead>
                            <tr>
                                <th>Imagen</th>
                                <th>Nombre</th>
                                <th>Precio</th>
                                <th>Stock</th>
                                <th>Categoría</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {productos.map((producto) => (
                                <tr key={producto.id_producto}>
                                    <td>
                                        <img
                                            src={`${API_URL}/static/img/productos/${producto.imagen}`}
                                            alt={producto.nombre}
                                            className="img-tabla"
                                            style={{ width: '50px', height: '50px', objectFit: 'cover' }}
                                            onError={(e) => e.target.src = '/img/placeholder.png'} // Imagen por defecto si falla
                                        />
                                    </td>
                                    <td>{producto.nombre}</td>
                                    <td>{producto.precio?.toLocaleString('es-CO')} COP</td>
                                    <td>{producto.stock}</td>
                                    <td>{producto.nombre_categoria}</td>
                                    <td>
                                        <div className="acciones-flex">
                                            <button className="btn-accion btn-editar">Modificar</button>
                                            <button
                                                onClick={() => handleEliminar(producto.id_producto)}
                                                className="btn-accion btn-eliminar"
                                            >
                                                Eliminar
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </section>
        </main>
    </div>
    );
};

export default Admin;