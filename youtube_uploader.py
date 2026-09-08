import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service(client_secrets_file='client_secret.json', token_file='token.pickle'):
    creds = None
    if os.path.exists(token_file):
        try:
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
        except Exception as e:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                if os.path.exists(token_file):
                    os.remove(token_file)
                raise Exception(f"Token expirado/inválido ao renovar: {str(e)}")
        else:
            target_file = client_secrets_file
            if not os.path.exists(target_file):
                if os.path.exists('client_secrets.json'):
                    target_file = 'client_secrets.json'
                else:
                    raise FileNotFoundError(
                        f"O arquivo '{client_secrets_file}' ou 'client_secrets.json' não foi encontrado na pasta raiz do projeto."
                    )
            
            flow = InstalledAppFlow.from_client_secrets_file(target_file, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    return build('youtube', 'v3', credentials=creds)


def upload_video_to_youtube(file_path, title, description="", tags="", category_id="22", privacy_status="public", publish_at=None):
    try:
        if not os.path.exists(file_path):
            return False, f"Arquivo de vídeo não encontrado no caminho: {file_path}"

        youtube = get_authenticated_service()

        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': [t.strip() for t in tags.split(',') if t.strip()] if isinstance(tags, str) else tags,
                'categoryId': category_id
            },
            'status': {
                'selfDeclaredMadeForKids': False
            }
        }

        if privacy_status == 'scheduled' and publish_at:
            body['status']['privacyStatus'] = 'private'
            body['status']['publishAt'] = publish_at
        else:
            body['status']['privacyStatus'] = privacy_status if privacy_status in ['public', 'private', 'unlisted'] else 'public'

        media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype='video/mp4')
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()

        video_id = response.get('id', 'Enviado')
        return True, video_id

    except Exception as e:
        msg = str(e).strip()
        if not msg:
            msg = f"Exceção do tipo '{type(e).__name__}' capturada sem mensagem explícita."
        return False, msg