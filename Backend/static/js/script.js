// Variable global para controlar el tamaño base de la letra (en píxeles)
let tamanoActual = 16; 

// 1. Función para aumentar o disminuir la letra
function cambiarFuente(accion) {
    // Seleccionamos todo el cuerpo de la página (el body)
    let cuerpo = document.body;
    
    // Si accion es 1, suma 2px. Si es -1, resta 2px
    tamanoActual += (accion * 2);
    
    // Ponemos límites para que la letra no se vuelva gigante o invisible
    if (tamanoActual > 26) tamanoActual = 26;
    if (tamanoActual < 12) tamanoActual = 12;
    
    // Aplicamos el nuevo tamaño al CSS del body mediante el DOM
    cuerpo.style.fontSize = tamanoActual + "px";
}

// 2. Función para activar/desactivar el Alto Contraste
function toggleContraste() {
    let cuerpo = document.body;
    
    // .classList.toggle añade la clase si no existe, o la quita si ya existe
    cuerpo.classList.toggle("alto-contraste");
}