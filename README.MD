#  Automatizer AI 2.0

O **Automatizer AI 2.0** é uma ferramenta desktop/web para automação inteligente de edição e renderização de vídeos. O sistema analisa arquivos longos de áudio e vídeo para extrair automaticamente os momentos mais marcantes, gerando cortes otimizados (Shorts/Reels/TikTok ou formato tradicional 16:9) com legendas dinâmicas acopladas.

A ferramenta combina três métodos complementares de detecção:
- **Transcrição e Análise Semântica (IA):** Filtra trechos virais com base no contexto falado utilizando Ollama (Llama 3) e Faster-Whisper.
- **Detecção de Clímax (Análise de Áudio):** Processa picos de volume e energia falada (como risadas, gritos ou reações) via Librosa.
- **Gatilhos por Palavra-Chave (Trigger Words):** Localiza termos específicos informados na interface e realiza cortes automatizados em torno da fala.

---

##  Pré-requisitos e Dependências do Sistema

Para garantir que a transcrição pelo Whisper e a renderização utilizem aceleração por hardware (GPU NVIDIA), é necessário configurar o ambiente CUDA antes de rodar a aplicação.

### 1. Drivers e CUDA (NVIDIA)
- **Driver NVIDIA:** Certifique-se de estar com os drivers da sua placa de vídeo atualizados.
- **CUDA Toolkit:** Recomendado instalar a versão **CUDA 11.8** ou **12.x**.
- **cuDNN e bibliotecas DLL:** O `faster-whisper` exige as DLLs do cuDNN e zlib no sistema.
  - Baixe e extraia os arquivos do cuDNN compatíveis com sua versão do CUDA.
  - Caso ocorram erros de DLL no Windows (como `cublas64_11.dll` ou `cudnn64_8.dll`), garanta que os caminhos das DLLs estejam adicionados às **Variáveis de Ambiente (`PATH`)** do Windows ou copiados para a pasta raiz do projeto.

---

##  Instalação e Configuração do Ollama

O Ollama roda o modelo de linguagem local que analisa o contexto da transcrição e seleciona os trechos virais.

1. Baixe e instale o **Ollama** em [ollama.com](https://ollama.com/).
2. Abra o terminal (Prompt de Comando ou PowerShell) e baixe o modelo Llama 3:
   ```bash
   ollama pull llama3
Certifique-se de que o aplicativo do Ollama esteja rodando em segundo plano durante a execução da ferramenta.

 Estrutura do Projeto
Mantenha a estrutura de pastas organizada da seguinte forma:

Plaintext
automatizer-ai/
├── app.py
├── static/
│   └── style.css
└── templates/
    └── index.html

 Instalação do Ambiente Python
Recomenda-se utilizar o Python 3.10 ou 3.11.

Criar e ativar um ambiente virtual (recomendado):

Bash
python -m venv venv

# No Windows (PowerShell):
.\venv\Scripts\activate

# No Windows (CMD):
.\venv\Scripts\activate.bat
Instalar as dependências do projeto:

Bash
pip install flask faster-whisper moviepy librosa numpy pillow ollama
Instalar o PyTorch com suporte a CUDA:
Para garantir a aceleração via GPU, instale a build com suporte ao CUDA:

Bash
pip install torch torchvision torchaudio --index-url [https://download.pytorch.org/whl/cu118](https://download.pytorch.org/whl/cu118)
(Substitua cu118 por cu121 caso esteja utilizando o CUDA 12.x).

 Como Executar
Inicie o serviço do Ollama.

No terminal, dentro da pasta do projeto com o ambiente virtual ativo, execute:

Bash
python app.py
Abra o seu navegador e acesse:

Plaintext
[http://127.0.0.1:5000](http://127.0.0.1:5000)
 Opções do Painel
Caminho do Vídeo Original (.mp4): Diretório completo do arquivo de entrada.

Pasta de Destino: Local onde os vídeos cortados e os arquivos de cache (transcricao.json) serão salvos.

Prompt do Que Você Procura: Orientação customizada para a IA sobre o estilo dos cortes desejados.

Modo de Operação & Formato: Escolha entre formato vertical (9:16) ou horizontal (16:9).

Quantidade de Cortes: Defina o limite de vídeos a serem gerados (sem restrição para mais de 20 cortes).

Opções Avançadas:

Detecção de Clímax (Picos de Áudio/Librosa): Captura trechos com base na energia do áudio.

Queimar Legendas Automáticas: Gera legendas dinâmicas P&B estilo redes sociais.

Ativar Trigger Word: Processa o vídeo buscando palavras-chave personalizadas (ex: Clipper, segredo, urgente).