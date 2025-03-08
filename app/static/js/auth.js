// Archivo: app/static/js/auth.js

// Referencia a la autenticación de Firebase
const auth = firebase.auth();

// Configuración de FirebaseUI
const uiConfig = {
    // Modo de redirección: 'popup' o 'redirect'
    signInFlow: 'popup',
    
    // No redirigir a ninguna URL
    signInSuccessUrl: '#',
    
    // Proveedores de inicio de sesión a usar
    signInOptions: [
        // Configurar los proveedores de autenticación que deseas
        firebase.auth.GoogleAuthProvider.PROVIDER_ID,
        firebase.auth.EmailAuthProvider.PROVIDER_ID,
        // Puedes agregar más proveedores como:
        // firebase.auth.FacebookAuthProvider.PROVIDER_ID,
        // firebase.auth.TwitterAuthProvider.PROVIDER_ID,
        // firebase.auth.GithubAuthProvider.PROVIDER_ID,
    ],
    
    // Términos de servicio URL
    tosUrl: '#',
    
    // Política de privacidad URL
    privacyPolicyUrl: '#',
    
    // Función de callback para cuando el inicio de sesión es exitoso
    callbacks: {
        signInSuccessWithAuthResult: function(authResult, redirectUrl) {
            // No redireccionar - manejamos la UI nosotros mismos
            return false;
        }
    }
};

// Variables para los elementos de la UI
const authSection = document.getElementById('auth-section');
const userSignedIn = document.getElementById('user-signed-in');
const userName = document.getElementById('user-name');
const userEmail = document.getElementById('user-email');
const signOutButton = document.getElementById('sign-out-button');
const appContent = document.getElementById('app-content');

// Inicializar FirebaseUI
let ui = new firebaseui.auth.AuthUI(auth);

// Escuchar cambios en el estado de autenticación
auth.onAuthStateChanged(function(user) {
    if (user) {
        // Usuario ha iniciado sesión
        console.log("Usuario autenticado:", user.displayName || user.email);
        
        // Actualizar la UI para mostrar información del usuario
        showUserInfo(user);
        
        // Mostrar contenido de la aplicación
        appContent.classList.remove('hidden');
        
        // Ocultar el contenedor de FirebaseUI
        document.getElementById('firebaseui-auth-container').style.display = 'none';
        
        // Mostrar sección de usuario autenticado
        userSignedIn.classList.remove('hidden');
    } else {
        // Usuario no ha iniciado sesión
        console.log("Usuario no autenticado");
        
        // Ocultar contenido de la aplicación
        appContent.classList.add('hidden');
        
        // Ocultar sección de usuario autenticado
        userSignedIn.classList.add('hidden');
        
        // Mostrar el contenedor de FirebaseUI
        document.getElementById('firebaseui-auth-container').style.display = 'block';
        
        // Iniciar la UI de autenticación
        ui.start('#firebaseui-auth-container', uiConfig);
    }
});

// Mostrar información del usuario autenticado
function showUserInfo(user) {
    // Mostrar el nombre si existe, o el email como alternativa
    userName.textContent = user.displayName || user.email.split('@')[0];
    userEmail.textContent = user.email;
}

// Manejar cierre de sesión
if (signOutButton) {
    signOutButton.addEventListener('click', function() {
        console.log("Cerrando sesión...");
        auth.signOut()
            .then(function() {
                console.log("Sesión cerrada con éxito");
            })
            .catch(function(error) {
                console.error("Error al cerrar sesión:", error);
            });
    });
}