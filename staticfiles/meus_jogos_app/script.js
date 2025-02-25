document.addEventListener("DOMContentLoaded", function() {
    const prevButton = document.querySelector('.prev');
    const nextButton = document.querySelector('.next');
    const carouselImages = document.querySelector('.carousel-images');
    const carouselItems = document.querySelectorAll('.carousel-item');
    let currentIndex = 0;

    // Função para atualizar o carrossel
    function updateCarousel() {
        const totalItems = carouselItems.length;
        if (currentIndex >= totalItems) {
            currentIndex = 0;
        } else if (currentIndex < 0) {
            currentIndex = totalItems - 1;
        }

        // Atualiza a posição do carrossel para a imagem atual
        carouselImages.style.transform = `translateX(-${currentIndex * 100}%)`;
    }

    // Evento de clique no botão "próximo"
    nextButton.addEventListener('click', function() {
        currentIndex++;
        updateCarousel();
    });

    // Evento de clique no botão "anterior"
    prevButton.addEventListener('click', function() {
        currentIndex--;
        updateCarousel();
    });

    // Atualiza o carrossel ao carregar a página
    updateCarousel();
});
