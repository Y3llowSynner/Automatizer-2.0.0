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