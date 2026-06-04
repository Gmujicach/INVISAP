document.addEventListener('DOMContentLoaded', function(){
  function validateForm(form){
    const nombre = form.querySelector('[name=nombre_empleado]').value.trim();
    const apellido = form.querySelector('[name=apellido_empleado]').value.trim();
    const email = form.querySelector('[name=email_empleado]').value.trim();
    const salario = form.querySelector('[name=salario_empleado]').value.trim();
    if(!nombre || !apellido || !email || !salario) {
      alert('Por favor complete todos los campos requeridos');
      return false;
    }
    const emailRe = /[^@]+@[^@]+\.[^@]+/;
    if(!emailRe.test(email)){
      alert('Correo inválido');
      return false;
    }
    if(!/^[0-9.,]+$/.test(salario)){
      alert('Salario inválido');
      return false;
    }
    return true;
  }

  const form = document.getElementById('formEmpleado');
  if(form){
    form.addEventListener('submit', function(e){
      if(!validateForm(form)) e.preventDefault();
    });
  }
  const formUpd = document.getElementById('formEmpleadoUpdate');
  if(formUpd){
    formUpd.addEventListener('submit', function(e){
      if(!validateForm(formUpd)) e.preventDefault();
    });
  }
});
