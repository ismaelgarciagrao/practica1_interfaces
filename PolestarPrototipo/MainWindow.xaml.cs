using System.Windows;
using System.Windows.Automation;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Animation;

namespace PolestarPrototipo
{
    /// <summary>
    /// Ventana única de la aplicación. Contiene tres paneles (ZonaInicio, ZonaGaleria y
    /// ZonaLogin) colocados uno encima del otro; solo uno está visible en cada momento.
    /// </summary>
    public partial class MainWindow : Window
    {
        // ---- Datos de la cuenta de demostración (prototipo: no hay base de datos) ----
        private const string CorreoDemo = "cliente@polestar.es";
        private const string ContrasenaDemo = "Polestar2026";
        private const string NombreDemo = "Usuario";
        private const int MaxIntentos = 3;

        private int intentosFallidos = 0;
        private bool sesionIniciada = false;

        public MainWindow()
        {
            InitializeComponent();
            // Pantalla inicial. Sin animación de entrada: el banner ya tiene la suya.
            MostrarPantalla(ZonaInicio, BtnInicio, "Inicio", false);
        }

        // =====================================================================
        // NAVEGACIÓN
        // =====================================================================

        /// <summary>
        /// Muestra una pantalla, oculta las demás y marca con la línea naranja
        /// el botón del menú correspondiente.
        /// </summary>
        private void MostrarPantalla(FrameworkElement pantalla, Button botonMenu, string titulo, bool animar = true)
        {
            // 1. Ocultar todas las pantallas y mostrar solo la pedida
            ZonaInicio.Visibility = Visibility.Collapsed;
            ZonaGaleria.Visibility = Visibility.Collapsed;
            ZonaLogin.Visibility = Visibility.Collapsed;
            pantalla.Visibility = Visibility.Visible;

            // 2. Quitar la línea de todos los botones y ponerla en el activo
            BtnInicio.BorderBrush = Brushes.Transparent;
            BtnGaleria.BorderBrush = Brushes.Transparent;
            BtnAcceder.BorderBrush = Brushes.Transparent;
            botonMenu.BorderBrush = (Brush)FindResource("ColorNaranja");

            // 3. Título de la ventana (indica dónde está el usuario) y volver arriba
            Title = "Polestar · " + titulo;
            ZonaContenido.ScrollToTop();

            // 4. Animación de entrada (se respeta la opción de Windows de desactivar animaciones)
            if (animar && SystemParameters.ClientAreaAnimation)
            {
                Storyboard entrada = (Storyboard)FindResource("AnimEntrada");
                entrada.Begin(pantalla);
            }
        }

        private void BtnLogo_Click(object sender, RoutedEventArgs e)
        {
            MostrarPantalla(ZonaInicio, BtnInicio, "Inicio");
        }

        private void BtnInicio_Click(object sender, RoutedEventArgs e)
        {
            MostrarPantalla(ZonaInicio, BtnInicio, "Inicio");
        }

        private void BtnGaleria_Click(object sender, RoutedEventArgs e)
        {
            MostrarPantalla(ZonaGaleria, BtnGaleria, "Galería");
        }

        private void BtnVerModelos_Click(object sender, RoutedEventArgs e)
        {
            MostrarPantalla(ZonaGaleria, BtnGaleria, "Galería");
        }

        private void BtnAcceder_Click(object sender, RoutedEventArgs e)
        {
            if (sesionIniciada)
            {
                CerrarSesion();
                return;
            }

            MostrarPantalla(ZonaLogin, BtnAcceder, "Acceso");
            if (TxtCorreo.IsEnabled)
            {
                LimpiarError();      // se empieza sin errores de una visita anterior
                TxtCorreo.Focus();   // el cursor queda listo para escribir
            }
        }

        // =====================================================================
        // INICIO DE SESIÓN
        // =====================================================================

        private void BtnEntrar_Click(object sender, RoutedEventArgs e)
        {
            if (BtnVerContrasena.IsChecked == true)
            {
                TxtContrasena.Password = TxtContrasenaVisible.Text;
            }

            LimpiarError();
            string correo = TxtCorreo.Text.Trim();
            string contrasena = TxtContrasena.Password;

            // 1. Campos vacíos
            if (correo == "")
            {
                MostrarError("Escribe tu correo electrónico.", TxtCorreo);
                return;
            }
            // 2. Formato del correo (@ y puntos)
            if (!CorreoBienEscrito(correo))
            {
                MostrarError("El correo no está bien escrito. Debe tener la forma nombre@dominio.es", TxtCorreo);
                return;
            }
            if (contrasena == "")
            {
                MostrarError("Escribe tu contraseña.", TxtContrasena);
                return;
            }

            // 3. Datos incorrectos: no se dice cuál de los dos falla (seguridad)
            if (correo.ToLower() != CorreoDemo || contrasena != ContrasenaDemo)
            {
                intentosFallidos++;
                TxtContrasena.Clear();

                if (intentosFallidos >= MaxIntentos)
                {
                    BloquearAcceso();
                    return;
                }

                int quedan = MaxIntentos - intentosFallidos;
                MostrarError("Correo o contraseña incorrectos. Te quedan " + quedan + " intento(s).",
                             TxtContrasena, TxtCorreo);
                return;
            }

            // 4. Acceso correcto
            intentosFallidos = 0;
            sesionIniciada = true;
            TxtCorreo.Clear();
            TxtContrasena.Clear();
            TxtUsuario.Text = "Hola, " + NombreDemo;
            TxtUsuario.Visibility = Visibility.Visible;
            BtnAcceder.Content = "Cerrar _sesión";
            BtnAcceder.ToolTip = "Cerrar la sesión (Alt+S)";

            MessageBox.Show("¡Bienvenido, " + NombreDemo + "!\n\nHas iniciado sesión correctamente.",
                            "Polestar", MessageBoxButton.OK, MessageBoxImage.Information);
            MostrarPantalla(ZonaInicio, BtnInicio, "Inicio");
        }

        /// <summary>
        /// Comprueba la @ y los puntos: una sola @, texto antes de ella y, después,
        /// un dominio con al menos un punto que no esté ni al principio ni al final
        /// y sin dos puntos seguidos. Ejemplo válido: nombre@dominio.es
        /// </summary>
        private bool CorreoBienEscrito(string correo)
        {
            if (correo.Contains(" ")) return false;

            int arroba = correo.IndexOf('@');
            if (arroba <= 0 || arroba != correo.LastIndexOf('@')) return false;

            string usuario = correo.Substring(0, arroba);
            string dominio = correo.Substring(arroba + 1);

            if (usuario.StartsWith(".") || usuario.EndsWith(".")) return false;
            if (!dominio.Contains(".")) return false;
            if (dominio.StartsWith(".") || dominio.EndsWith(".")) return false;
            if (correo.Contains("..")) return false;

            return true;
        }

        /// <summary>
        /// Muestra el único mensaje de error, marca los campos indicados en rojo con
        /// fondo rosado, lleva el foco al primero y lanza la animación de error.
        /// </summary>
        private void MostrarError(string mensaje, params Control[] campos)
        {
            TxtError.Text = "⚠  " + mensaje;
            ZonaError.Visibility = Visibility.Visible;

            foreach (Control campo in campos)
            {
                campo.BorderBrush = (Brush)FindResource("ColorError");
                campo.Background = (Brush)FindResource("ColorFondoError");
            }
            if (campos.Length > 0 && campos[0].IsEnabled)
            {
                campos[0].Focus();
            }

            if (SystemParameters.ClientAreaAnimation)
            {
                Storyboard error = (Storyboard)FindResource("AnimError");
                error.Begin(this);
            }
        }

        /// <summary>Oculta el mensaje y devuelve los campos al aspecto del estilo.</summary>
        private void LimpiarError()
        {
            ZonaError.Visibility = Visibility.Collapsed;
            TxtCorreo.ClearValue(Control.BorderBrushProperty);
            TxtCorreo.ClearValue(Control.BackgroundProperty);
            TxtContrasena.ClearValue(Control.BorderBrushProperty);
            TxtContrasena.ClearValue(Control.BackgroundProperty);
        }

        private void BloquearAcceso()
        {
            TxtCorreo.IsEnabled = false;
            TxtContrasena.IsEnabled = false;
            BtnEntrar.IsEnabled = false;
            MostrarError("Acceso bloqueado tras " + MaxIntentos + " intentos fallidos. " +
                         "Por seguridad, contacta con tu concesionario para desbloquear tu cuenta.");
        }

        // Al escribir de nuevo, el error desaparece (el usuario está corrigiendo).
        // Si el acceso está bloqueado, los campos están desactivados y no se llega aquí.
        private void TxtCorreo_TextChanged(object sender, TextChangedEventArgs e)
        {
            LimpiarError();
        }

        private void TxtContrasena_PasswordChanged(object sender, RoutedEventArgs e)
        {
            LimpiarError();
        }

        private void TxtContrasenaVisible_TextChanged(object sender, TextChangedEventArgs e)
        {
            if (TxtContrasena.Password != TxtContrasenaVisible.Text)
            {
                TxtContrasena.Password = TxtContrasenaVisible.Text;
            }
            LimpiarError();
        }
 
        private void BtnVerContrasena_Click(object sender, RoutedEventArgs e)
        {
            PonerContrasenaVisible(BtnVerContrasena.IsChecked == true);
 
            // El cursor vuelve al campo que ahora se ve, para seguir escribiendo
            if (BtnVerContrasena.IsChecked == true)
            {
                TxtContrasenaVisible.Focus();
                TxtContrasenaVisible.CaretIndex = TxtContrasenaVisible.Text.Length;
            }
            else
            {
                TxtContrasena.Focus();
            }
        }
 
        /// <summary>
        /// Cambia qué campo se ve en el mismo sitio (PasswordBox o TextBox), el texto
        /// del botón, su nombre accesible y a qué campo lleva el atajo Alt+T.
        /// </summary>
        private void PonerContrasenaVisible(bool mostrar)
        {
            if (mostrar)
            {
                TxtContrasenaVisible.Text = TxtContrasena.Password;
                TxtContrasenaVisible.Visibility = Visibility.Visible;
                TxtContrasena.Visibility = Visibility.Collapsed;
                BtnVerContrasena.Content = "Ocultar";
                AutomationProperties.SetName(BtnVerContrasena, "Ocultar contraseña");
                EtiquetaContrasena.Target = TxtContrasenaVisible;
            }
            else
            {
                TxtContrasena.Visibility = Visibility.Visible;
                TxtContrasenaVisible.Visibility = Visibility.Collapsed;
                BtnVerContrasena.Content = "Mostrar";
                AutomationProperties.SetName(BtnVerContrasena, "Mostrar contraseña");
                EtiquetaContrasena.Target = TxtContrasena;
            }
        }
 
        /// <summary>El campo de contraseña que se está viendo (para marcar errores y dar el foco).</summary>
        private Control CampoContrasenaActivo()
        {
            if (TxtContrasenaVisible.Visibility == Visibility.Visible) return TxtContrasenaVisible;
            return TxtContrasena;
        }

        private void CerrarSesion()
        {
            MessageBoxResult respuesta = MessageBox.Show("¿Quieres cerrar la sesión?", "Polestar",
                                                         MessageBoxButton.YesNo, MessageBoxImage.Question);
            if (respuesta != MessageBoxResult.Yes) return;

            sesionIniciada = false;
            TxtUsuario.Visibility = Visibility.Collapsed;
            BtnAcceder.Content = "_Acceder";
            BtnAcceder.ToolTip = "Área de clientes (Alt+A)";
            MostrarPantalla(ZonaInicio, BtnInicio, "Inicio");
        }
    }
}
