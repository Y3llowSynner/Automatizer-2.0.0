import traceback
import youtube_uploader

print("1. Módulo importado com sucesso.")

video_teste = r"E:\videosyt\TESTETESTE\Corte_1_Pico_Audio.mp4"

try:
    print("2. Iniciando envio de teste...")
    sucesso, resposta = youtube_uploader.upload_video_to_youtube(
        file_path=video_teste,
        title="Teste Direto Script #shorts",
        description="Teste de envio",
        tags="shorts",
        privacy_status="private"
    )
    print(f"3. Resultado -> Sucesso: {sucesso} | Resposta: {resposta}")
except Exception as e:
    print("\n[EXCEÇÃO CAPTURADA NO SCRIPT]")
    traceback.print_exc()