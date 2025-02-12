document.addEventListener('DOMContentLoaded', function() {
    const rows = document.querySelectorAll('.game-row');
    const modal = document.getElementById('gameModal');
    const closeModal = document.querySelector('.close');

    // Seleciona os elementos do modal
    const modalPlacar = document.getElementById('modal-placar');
    const modalAdversario = document.getElementById('modal-adversario');
    const modalEstadio = document.getElementById('modal-estadio');
    const modalData = document.getElementById('modal-data');
    const modalCampeonato = document.getElementById('modal-campeonato');
    const modalArbitro = document.getElementById('modal-arbitro');
    const modalPublico = document.getElementById('modal-publico');

    rows.forEach(row => {
        row.addEventListener('click', function() {
            modalPlacar.textContent = `${row.dataset.gols_flu} x ${row.dataset.gols_adv}`;
            modalAdversario.textContent = row.dataset.adversario;
            modalEstadio.textContent = `${row.dataset.estadio} (${row.dataset.local_estadio})`;
            modalData.textContent = row.dataset.data;
            modalCampeonato.textContent = row.dataset.campeonato;
            modalArbitro.textContent = row.dataset.arbitro;
            modalPublico.textContent = row.dataset.publico;

            // Aqui, vamos buscar os gols e o autor
            // Adicione a lógica para buscar os gols associados ao jogo (via uma consulta Django ou já fornecendo os dados no HTML)
            let autoresGols = row.dataset.gols_flu_autores.split(',');  // Exemplo: uma lista de autores separada por vírgulas (você pode passar essa informação com os dados)
            modalAutorGol.textContent = autoresGols.join(', ');  // Exibe os autores dos gols no modal

            modal.style.display = 'block';
        });
    });

    closeModal.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});