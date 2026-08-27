const sidebar = document.querySelector('#sidebar');
const menuButton = document.querySelector('#menuButton');

menuButton.addEventListener('click', () => {
  const isOpen = sidebar.classList.toggle('open');
  menuButton.setAttribute('aria-expanded', String(isOpen));
});

document.querySelectorAll('.nav-item').forEach((item) => {
  item.addEventListener('click', () => {
    document.querySelectorAll('.nav-item').forEach((link) => link.classList.remove('active'));
    item.classList.add('active');
    sidebar.classList.remove('open');
    menuButton.setAttribute('aria-expanded', 'false');
  });
});
