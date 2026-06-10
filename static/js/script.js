const contadorCarrito = document.querySelector('#cart-count');
const formularioProducto = document.querySelectorAll('.tarjeta-producto form');
let cantidadProductos = 0;

formularioProducto.forEach(function(formulario) { 
    formulario.addEventListener('submit', function(evento) {
        evento.preventDefault();
        cantidadProductos = cantidadProductos + 1;
        contadorCarrito.textContent = cantidadProductos;
    })
})