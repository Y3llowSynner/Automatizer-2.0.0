document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('processForm');
    const progressBar = document.getElementById('progressBar');
    const statusText = document.getElementById('statusText');
    const cutsContainer = document.getElementById('cutsContainer');

    // 1. Restaura entradas gravadas anteriormente no localStorage
    const inputs = form.querySelectorAll('input');
    inputs.forEach(input => {
        const savedValue = localStorage.getItem(`auto_config_${input.id}`);
        if (savedValue !== null) {
            if (input.type === 'checkbox') {
                input.checked = savedValue === 'true';
            } else {
                input.value = savedValue;
            }
        }

        // Salva qualquer alteração digitada pelo usuário
        input.addEventListener('input', () => {
            const val = input.type === 'checkbox' ? input.checked : input.value;
            localStorage.setItem(`auto_config_${input.id}`, val);
        });
    });

    // 2. Envio via JSON
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Montagem do payload lendo diretamente os valores da tela
        const payload = {
            video_path: document.getElementById('video_path').value.trim(),
            output_folder: document.getElementById('output_folder').value.trim(),
            prompt: document.getElementById('prompt').value.trim(),
            title_template: document.getElementById('title_template').value.trim(),
            num_cuts: parseInt(document.getElementById('num_cuts').value) || 1,
            min_time: parseFloat(document.getElementById('min_time').value) || 30,
            max_time: parseFloat(document.getElementById('max_time').value) || 40,
            post_to_youtube: document.getElementById('post_to_youtube').checked
        };

        statusText.innerText = "Iniciando comunicação com o servidor...";
        progressBar.style.width = "5%";

        try {
            const response = await fetch('/processar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (!response.ok) {
                alert(`Erro (${response.status}): ${result.error || 'Falha ao processar'}`);
                statusText.innerText = `Erro: ${result.error}`;
                return;
            }

            // Inicia leitura contínua de progresso via Server-Sent Events (SSE)
            const eventSource = new EventSource('/progresso');
            eventSource.onmessage = (event) => {
                const data = JSON.parse(event.data);

                if (data.progress !== undefined) {
                    progressBar.style.width = `${data.progress}%`;
                    statusText.innerText = `${data.status} (${data.progress}%)`;
                }

                if (data.progress >= 100) {
                    eventSource.close();
                    if (data.cuts && data.cuts.length > 0) {
                        cutsContainer.innerHTML = '<h3>Cortes Gerados:</h3>' + 
                            data.cuts.map(c => `<p><b>${c.title}</b> - ${c.yt_status}</p>`).join('');
                    }
                }

                if (data.error) {
                    eventSource.close();
                    alert(`Erro durante o processamento: ${data.error}`);
                }
            };

        } catch (err) {
            console.error("Erro no envio:", err);
            alert("Erro de conexão ao enviar os dados ao servidor Flask.");
        }
    });
});