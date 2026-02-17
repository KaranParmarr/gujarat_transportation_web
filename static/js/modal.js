const container = document.querySelector('.regi-container');
const registerBtn = document.querySelector('.register-btn');
const loginBtn = document.querySelector('.login-btn');

registerBtn.addEventListener('click', () => {
    container.classList.add('active');
})

loginBtn.addEventListener('click', () => {
    container.classList.remove('active');
})

// toggle
showRegister.onclick = () => container.classList.add("active");
showLogin.onclick = () => container.classList.remove("active");

// REGISTER
registerForm.addEventListener("submit", e => {
    e.preventDefault();
    fetch("/register", {
        method:"POST",
        body: new FormData(registerForm)
    })
    .then(r=>r.json())
    .then(d=>{
        if(d.status==="success"){
            window.parent.location.reload();
        } else {
            alert("Username already exists");
        }
    });
});

// LOGIN
loginForm.addEventListener("submit", e => {
    e.preventDefault();
    fetch("/login", {
        method:"POST",
        body: new FormData(loginForm)
    })
    .then(r=>r.json())
    .then(d=>{
        if(d.status==="success" || d.status==="admin"){
            window.parent.location.reload();
        } else {
            alert("Invalid login");
        }
    });
});

