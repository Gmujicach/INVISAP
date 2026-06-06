document.addEventListener('DOMContentLoaded', () => {
  const toggleBtn = document.querySelector('.btn-password-toggle');
  const passwordInput = document.getElementById('pass_user');
  const eyeSpan = document.querySelector('.password-eye');
  const pupil = document.querySelector('.eye-pupil');

  // Funcionalidad de Mostrar/Ocultar
  toggleBtn.addEventListener('click', () => {
    const isHidden = passwordInput.type === 'password';
    passwordInput.type = isHidden ? 'text' : 'password';

    // Cambiar visual del ojo: si mostramos texto, abrimos el ojo.
    if (isHidden) {
      eyeSpan.classList.replace('is-closed', 'is-open');
    } else {
      eyeSpan.classList.replace('is-open', 'is-closed');
    }
  });

  // Ojo que sigue al cursor
  document.addEventListener('mousemove', (e) => {
    // Solo seguir el cursor si el ojo está abierto
    if (!pupil || eyeSpan.classList.contains('is-closed')) return;

    const rect = pupil.getBoundingClientRect();
    const eyeCenterX = rect.left + rect.width / 2;
    const eyeCenterY = rect.top + rect.height / 2;
    const dx = e.clientX - eyeCenterX;
    const dy = e.clientY - eyeCenterY;
    const angle = Math.atan2(dy, dx);
    const distance = Math.min(1.8, Math.sqrt(dx * dx + dy * dy) / 50);
    const moveX = Math.cos(angle) * distance;
    const moveY = Math.sin(angle) * distance;
    pupil.style.transform = `translate(${moveX}px, ${moveY}px)`;
  });
});