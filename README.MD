 Automatizer AI 2.0

O Automatizer AI 2.0 é uma ferramenta desktop/web para automação inteligente de edição, renderização e publicação de vídeos. O sistema analisa arquivos longos de áudio e vídeo para extrair automaticamente os momentos mais marcantes, gerando cortes otimizados (Shorts/Reels/TikTok ou formato tradicional 16:9) com legendas dinâmicas acopladas e publicação automatizada no YouTube.

A ferramenta combina três métodos complementares de detecção e novos recursos de distribuição:

Transcrição e Análise Semântica (IA): Filtra trechos virais com base no contexto falado utilizando Ollama (Llama 3) e Faster-Whisper.

Detecção de Clímax (Análise de Áudio): Processa picos de volume e energia falada (como risadas, gritos ou reações) via Librosa.

Gatilhos por Palavra-Chave (Trigger Words): Localiza termos específicos informados na interface e realiza cortes automatizados em torno da fala.

Publicação e Agendamento Automático (YouTube Data API v3): Envia os cortes gerados diretamente para o seu canal do YouTube (Público, Privado, Não Listado ou Agendado com intervalo configurável de dias).

Persistência de Configurações Local: Salva automaticamente todos os caminhos, descrições, chaves e preferências no navegador via localStorage.

 Pré-requisitos e Dependências do Sistema
Para garantir que a transcrição pelo Whisper, a renderização e o envio automatizado funcionem corretamente, configure o ambiente conforme os passos abaixo.

1. Drivers e CUDA (NVIDIA)
Driver NVIDIA: Certifique-se de estar com os drivers da sua placa de vídeo atualizados.

CUDA Toolkit: Recomendado instalar a versão CUDA 11.8 ou 12.x.

cuDNN e bibliotecas DLL: O faster-whisper exige as DLLs do cuDNN e zlib no sistema.

Baixe e extraia os arquivos do cuDNN compatíveis com sua versão do CUDA.

Caso ocorram erros de DLL no Windows (como cublas64_11.dll ou cudnn64_8.dll), garanta que os caminhos das DLLs estejam adicionados às Variáveis de Ambiente (PATH) do Windows ou copiados para a pasta raiz do projeto.

2. Configuração da API do YouTube NOVIDADE!! (Google Cloud Console)
Para habilitar a publicação automática no YouTube:

Acesse o Google Cloud Console e crie ou selecione o seu projeto.

No menu de APIs, clique em + Ativar APIs e Serviços e ative a YouTube Data API v3.

Vá em Tela de permissão OAuth, configure o projeto e adicione seu e-mail do YouTube na seção Test users (Usuários de teste).

Em Credenciais, crie um ID do cliente OAuth 2.0 do tipo Aplicativo de Computador (Desktop App).

Baixe o arquivo de credenciais, renomeie para client_secret.json e salve-o na pasta raiz do projeto.

 Instalação e Configuração do Ollama
O Ollama roda o modelo de linguagem local que analisa o contexto da transcrição e seleciona os trechos virais.

Baixe e instale o Ollama em ollama.com.

Abra o terminal (Prompt de Comando ou PowerShell) e baixe o modelo Llama 3:

Bash
ollama pull llama3
Certifique-se de que o aplicativo do Ollama esteja rodando em segundo plano durante a execução da ferramenta.

 Estrutura do Projeto
Mantenha a estrutura de pastas organizada da seguinte forma:

Plaintext
automatizer-ai/
├── app.py
├── youtube_uploader.py      # Módulo de autenticação e upload da API do YouTube
├── client_secret.json       # Credencial baixada do Google Cloud
├── static/
│   └── style.css
└── templates/
    └── index.html
 Instalação do Ambiente Python
Recomenda-se utilizar o Python 3.10 ou 3.11.

Criar e ativar um ambiente virtual:

Bash
python -m venv venv

# No Windows (PowerShell):
.\venv\Scripts\activate

# No Windows (CMD):
.\venv\Scripts\activate.bat
Instalar as dependências do projeto:

Bash
pip install flask faster-whisper moviepy librosa numpy pillow ollama google-api-python-client google-auth-oauthlib google-auth-httplib2
Instalar o PyTorch com suporte a CUDA:

Bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
(Substitua cu118 por cu121 caso esteja utilizando o CUDA 12.x).

 Como Executar
Certifique-se de que o serviço do Ollama esteja rodando.

No terminal, dentro da pasta do projeto com o ambiente virtual ativo, execute:

Bash
python app.py

Abra o seu navegador e acesse:

[http://127.0.0.1:5000](http://127.0.0.1:5000)

 Opções do Painel

Caminho do Vídeo Original (.mp4): Diretório completo do arquivo de entrada.

Pasta de Destino: Local onde os vídeos cortados e os arquivos de cache (transcricao.json) serão salvos.

Prompt Customizado: Orientação sobre o estilo dos cortes desejados para a IA (ex: risadas, piadas, reações).

Modelo de Título e Descrição: Definição da estrutura do título (ex: {titulo} #shorts) e texto fixo da descrição do vídeo.

Modo de Operação & Formato: Escolha entre formato vertical (9:16 - Shorts/Reels/TikTok) ou horizontal (16:9).

Quantidade e Duração dos Cortes: Defina o limite de vídeos a serem gerados e os tempos mínimo/máximo em segundos.

Opções Avançadas:
Detecção de Clímax (Picos de Áudio/Librosa): Captura trechos com base na energia sonora do vídeo.

Queimar Legendas Automáticas: Gera legendas dinâmicas estilo redes sociais alinhadas palavra por palavra.

Ativar Trigger Word: Processa o vídeo buscando palavras-chave personalizadas (ex: Clipper, segredo, urgente).

Ativar Trigger Word: Processa o vídeo buscando palavras-chave personalizadas (ex: Clipper, segredo, urgente).

Postar Automático no YouTube:

Visibilidade: Escolha entre Público, Privado, Não Listado ou Programado.

Agendamento Inteligente: Define a data/hora inicial e o espaçamento em dias entre cada corte gerado.

Salvamento Automático de Preferências: Todas as opções e caminhos preenchidos são salvos automaticamente no navegador (localStorage), sem necessidade de reescrever ao recarregar a página.
