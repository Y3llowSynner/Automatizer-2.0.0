import os
import sys
import json
import re
import math
import time
import ollama
import numpy as np
import librosa
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, render_template, request, jsonify, Response
from faster_whisper import WhisperModel
from moviepy import VideoFileClip

os.add_dll_directory(os.getcwd())

app = Flask(__name__)

MODELO_WHISPER_NOME = "medium"
print(f"Carregando modelo Whisper ({MODELO_WHISPER_NOME}) na GPU...")
whisper_model = WhisperModel(MODELO_WHISPER_NOME, device="cuda", compute_type="float16")

progresso_atual = {
    "porcentagem": 0,
    "etapa": "Inativo",
    "detalhes": "Aguardando início..."
}

def atualizar_status(porcentagem, etapa, detalhes=""):
    global progresso_atual
    progresso_atual["porcentagem"] = porcentagem
    progresso_atual["etapa"] = etapa
    progresso_atual["detalhes"] = detalhes

@app.route('/progresso')
def progresso():
    def gerar_eventos():
        while True:
            yield f"data: {json.dumps(progresso_atual)}\n\n"
            time.sleep(0.5)
    return Response(gerar_eventos(), content_type='text/event-stream')


def desenhar_legenda_dinamica(frame, t, lista_palavras, start_corte):
    tempo_relativo = start_corte + t
    texto_atual = ""

    for p in lista_palavras:
        if p['start'] <= tempo_relativo <= p['end']:
            texto_atual = p['word'].upper()
            break

    if not texto_atual:
        return frame

    img_pil = Image.fromarray(frame)
    draw = ImageDraw.Draw(img_pil)
    w, h = img_pil.size

    tamanho_fonte = int(h * 0.05)
    try:
        font = ImageFont.truetype("arialbd.ttf", tamanho_fonte)
    except IOError:
        try:
            font = ImageFont.truetype("arial.ttf", tamanho_fonte)
        except IOError:
            font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), texto_atual, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = (w - text_w) // 2
    y = int(h * 0.78)

    padding_x = 24
    padding_y = 12
    bg_box = [x - padding_x, y - padding_y, x + text_w + padding_x, y + text_h + padding_y]

    overlay = Image.new('RGBA', img_pil.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle(bg_box, radius=10, fill=(0, 0, 0, 190))

    img_pil = Image.alpha_composite(img_pil.convert('RGBA'), overlay)
    draw = ImageDraw.Draw(img_pil)

    borda = 2
    for dx in range(-borda, borda + 1):
        for dy in range(-borda, borda + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), texto_atual, font=font, fill=(0, 0, 0, 220))

    draw.text((x, y), texto_atual, font=font, fill="#FFFFFF")

    return np.array(img_pil.convert('RGB'))


def detectar_picos_audio(video_path, qtd_cortes, tempo_min, tempo_max):
    clip = VideoFileClip(video_path)
    audio_path = "temp_audio.wav"
    clip.audio.write_audiofile(audio_path, logger=None)
    clip.close()

    y, sr = librosa.load(audio_path, sr=None)
    if os.path.exists(audio_path):
        os.remove(audio_path)

    tempo_medio = (tempo_min + tempo_max) / 2
    hop_length = 512
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)

    frames_por_segundo = sr / hop_length
    janela_frames = int(tempo_medio * frames_por_segundo)

    picos = []
    duracao_total = len(y) / sr

    for i in range(0, len(onset_env) - janela_frames, max(1, janela_frames // 2)):
        energia = np.sum(onset_env[i:i + janela_frames])
        tempo_inicio = max(0, (i / frames_por_segundo) - (tempo_medio / 3))
        tempo_fim = min(duracao_total, tempo_inicio + tempo_medio)
        picos.append({'inicio': round(tempo_inicio, 2), 'fim': round(tempo_fim, 2), 'energia': energia})

    picos.sort(key=lambda x: x['energia'], reverse=True)

    cortes = []
    for p in picos:
        if len(cortes) >= qtd_cortes:
            break
        if not any(abs(p['inicio'] - c['inicio']) < tempo_min for c in cortes):
            cortes.append({'inicio': p['inicio'], 'fim': p['fim'], 'titulo': 'Pico_Audio'})

    return cortes


def buscar_trigger_words(palavras_sincronizadas, trigger_words, qtd_cortes, tempo_min, tempo_max, duracao_total):
    palavras_alvo = [w.strip().lower() for w in trigger_words.split(',') if w.strip()]
    cortes = []
    tempo_medio = (tempo_min + tempo_max) / 2

    for p in palavras_sincronizadas:
        if len(cortes) >= qtd_cortes:
            break
        palavra_limpa = re.sub(r'[^\w]', '', p['word'].lower())
        if palavra_limpa in palavras_alvo:
            st = max(0, p['start'] - 5) # 5 segundos antes do gatilho
            et = min(duracao_total, st + tempo_medio)
            
            if not any(abs(st - c['inicio']) < tempo_min for c in cortes):
                cortes.append({'inicio': round(st, 2), 'fim': round(et, 2), 'titulo': f'Gatilho_{palavra_limpa}'})

    return cortes


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/processar', methods=['POST'])
def processar():
    try:
        dados = request.json
        video_path = dados.get('video_path', '').strip('"').strip("'")
        output_dir = dados.get('output_dir', '').strip('"').strip("'")
        prompt_customizado = dados.get('prompt_customizado', '')
        modo_operacao = dados.get('modo_operacao', 'multiplos')
        formato_video = dados.get('formato_video', '16:9')

        qtd_cortes = int(dados.get('qtd_cortes', 10))
        tempo_min = float(dados.get('tempo_min', 40))
        tempo_max = float(dados.get('tempo_max', 60))

        picos_audio_ativo = dados.get('picos_audio', False)
        queimar_legendas = dados.get('queimar_legendas', False)
        trigger_word_active = dados.get('trigger_word_active', False)
        trigger_words = dados.get('trigger_word', 'Clipper')

        if not os.path.exists(video_path):
            atualizar_status(0, "Erro", "Arquivo não encontrado")
            return jsonify({'sucesso': False, 'erro': 'Arquivo de vídeo não encontrado.'}), 400

        os.makedirs(output_dir, exist_ok=True)

        # 1. TRANSCRIÇÃO
        atualizar_status(25, "Transcrição de Áudio", "Executando Whisper na GPU...")
        json_transcricao_path = os.path.join(output_dir, "transcricao.json")
        
        texto_completo = ""
        palavras_sincronizadas = []

        if os.path.exists(json_transcricao_path) and os.path.getsize(json_transcricao_path) > 0:
            with open(json_transcricao_path, "r", encoding="utf-8") as f:
                dados_cache = json.load(f)
                texto_completo = dados_cache.get("texto_completo", "")
                palavras_sincronizadas = dados_cache.get("palavras_sincronizadas", [])
            duracao_total = VideoFileClip(video_path).duration
        else:
            segments_generator, info = whisper_model.transcribe(
                video_path, beam_size=5, language="pt", vad_filter=True, word_timestamps=True
            )
            duracao_total = info.duration

            for segment in list(segments_generator):
                texto_completo += f"[{round(segment.start, 2)}s -> {round(segment.end, 2)}s] {segment.text.strip()}\n"
                if segment.words:
                    for w in segment.words:
                        palavras_sincronizadas.append({
                            'word': w.word.strip(),
                            'start': w.start,
                            'end': w.end
                        })

            with open(json_transcricao_path, "w", encoding="utf-8") as f:
                json.dump({"texto_completo": texto_completo, "palavras_sincronizadas": palavras_sincronizadas}, f, ensure_ascii=False, indent=2)

        cortes_unicos = []

        # 2. DETECÇÃO
        if trigger_word_active and trigger_words:
            atualizar_status(40, "Processando Gatilhos", "Buscando Trigger Words na transcrição...")
            cortes_unicos.extend(buscar_trigger_words(palavras_sincronizadas, trigger_words, qtd_cortes, tempo_min, tempo_max, duracao_total))

        if picos_audio_ativo and len(cortes_unicos) < qtd_cortes:
            atualizar_status(50, "Análise de Clímax", "Analisando picos de áudio com Librosa...")
            cortes_unicos.extend(detectar_picos_audio(video_path, qtd_cortes - len(cortes_unicos), tempo_min, tempo_max))

        if len(cortes_unicos) < qtd_cortes:
            atualizar_status(60, "Análise do Conteúdo", "Identificando momentos virais com Ollama/Llama...")
            prompt = (
                f"Analise a transcrição abaixo e selecione até {qtd_cortes - len(cortes_unicos)} cortes virais.\n"
                f"Format JSON estrito: [{{\"inicio\": 12.5, \"fim\": 52.0, \"titulo\": \"Momento\"}}]\n"
                f"Duração: {tempo_min}s até {tempo_max}s. Foco: {prompt_customizado}\n\n"
                f"Transcrição:\n{texto_completo[:16000]}"
            )
            try:
                response = ollama.chat(
                    model="llama3",
                    messages=[
                        {"role": "system", "content": "Responda apenas com JSON puro."},
                        {"role": "user", "content": prompt}
                    ]
                )
                match = re.search(r'\[\s*\{.*\}\s*\]', response['message']['content'], re.DOTALL)
                if match:
                    for c in json.loads(match.group(0)):
                        cortes_unicos.append({'inicio': float(c['inicio']), 'fim': float(c['fim']), 'titulo': c.get('titulo', 'Destaque')})
            except Exception as e:
                print(f"Erro IA: {e}")

        # Fallback de segurança se precisar completar a quantidade solicitada
        if len(cortes_unicos) < qtd_cortes:
            intervalo = duracao_total / (qtd_cortes + 1)
            tempo_alvo = (tempo_min + tempo_max) / 2
            for i in range(qtd_cortes - len(cortes_unicos)):
                st = (i + 1) * intervalo
                et = min(duracao_total, st + tempo_alvo)
                cortes_unicos.append({'inicio': round(st, 2), 'fim': round(et, 2), 'titulo': f'Destaque_{i+1}'})

        # 3. RENDERIZAÇÃO
        clip_original = VideoFileClip(video_path)
        cortes_exportados = []
        total = min(len(cortes_unicos), qtd_cortes)

        for i, corte in enumerate(cortes_unicos[:total]):
            pct = 70 + int((i / total) * 28)
            atualizar_status(pct, "Renderizando Vídeo", f"Processando corte {i+1} de {total}...")

            start = max(0, float(corte['inicio']))
            end = min(clip_original.duration, float(corte['fim']))
            titulo_limpo = re.sub(r'[^\w\-_]', '_', str(corte['titulo']))
            nome_arquivo = f"Corte_{i+1}_{titulo_limpo}"

            subclip = clip_original.subclipped(start, end)
            w, h = subclip.size

            if formato_video == '9:16':
                new_width = int(h * (9 / 16))
                if new_width % 2 != 0:
                    new_width -= 1
                subclip_proc = subclip.cropped(x_center=w / 2, width=new_width)
            else:
                subclip_proc = subclip

            if queimar_legendas and palavras_sincronizadas:
                subclip_proc = subclip_proc.transform(
                    lambda get_frame, t: desenhar_legenda_dinamica(get_frame(t), t, palavras_sincronizadas, start)
                )

            out_path = os.path.join(output_dir, f"{nome_arquivo}.mp4")
            subclip_proc.write_videofile(out_path, codec="libx264", audio_codec="aac", fps=30)
            cortes_exportados.append({'titulo': nome_arquivo, 'path': out_path, 'duracao': round(end - start, 1)})

        clip_original.close()
        atualizar_status(100, "Concluído", "Vídeos gerados com sucesso!")

        return jsonify({
            'sucesso': True,
            'mensagem': f'{len(cortes_exportados)} vídeo(s) gerado(s) com sucesso!',
            'cortes': cortes_exportados
        })

    except Exception as e:
        atualizar_status(0, "Erro", str(e))
        return jsonify({'sucesso': False, 'erro': str(e)}), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)