document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('errorModal');
    const closeModalButton = document.getElementById('closeModal');

    modal.style.display = 'flex';

    closeModalButton.addEventListener('click', () => {
        modal.style.display = 'none';
    });
});
