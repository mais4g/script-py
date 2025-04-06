import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import sys

# --- Configuração ---
# 1. Configure Variáveis de Ambiente (MAIS SEGURO!)
#    No Linux/macOS: export SPOTIPY_CLIENT_ID='seu_client_id'
#                    export SPOTIPY_CLIENT_SECRET='seu_client_secret'
#                    export SPOTIPY_REDIRECT_URI='http://localhost:8888/callback'
#    No Windows (Prompt): set SPOTIPY_CLIENT_ID=seu_client_id
#                         set SPOTIPY_CLIENT_SECRET=seu_client_secret
#                         set SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
#    No Windows (PowerShell): $env:SPOTIPY_CLIENT_ID = 'seu_client_id'
#                             $env:SPOTIPY_CLIENT_SECRET = 'seu_client_secret'
#                             $env:SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'
#
# OU (Menos seguro, não recomendado para compartilhar):
# os.environ['SPOTIPY_CLIENT_ID'] = 'SEU_CLIENT_ID_AQUI'
# os.environ['SPOTIPY_CLIENT_SECRET'] = 'SEU_CLIENT_SECRET_AQUI'
# os.environ['SPOTIPY_REDIRECT_URI'] = 'http://localhost:8888/callback' # Ou a URI que você configurou

# Permissões necessárias para criar e modificar playlists
SCOPE = "playlist-modify-public playlist-modify-private"

# Nome do arquivo de texto com as músicas
ARQUIVO_MUSICAS = 'musicas.txt' # Mude se seu arquivo tiver outro nome

# Nome e descrição da playlist a ser criada no Spotify
NOME_PLAYLIST = 'Minha Playlist via Script'
DESCRICAO_PLAYLIST = 'Playlist criada automaticamente com Python e Spotipy'
# --------------------

def get_spotify_client():
    """Autentica e retorna um cliente Spotipy."""
    try:
        auth_manager = SpotifyOAuth(scope=SCOPE)
        sp = spotipy.Spotify(auth_manager=auth_manager)
        # Testa a conexão pegando o usuário atual
        sp.current_user()
        print("Autenticação bem-sucedida!")
        return sp
    except Exception as e:
        print(f"Erro na autenticação: {e}")
        print("Verifique suas credenciais (Client ID, Client Secret, Redirect URI) e se as variáveis de ambiente estão configuradas.")
        sys.exit(1) # Encerra o script se a autenticação falhar

def ler_musicas_do_arquivo(nome_arquivo):
    """Lê os nomes das músicas do arquivo de texto."""
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            # Lê cada linha, remove espaços em branco extras e ignora linhas vazias
            musicas = [linha.strip() for linha in f if linha.strip()]
        if not musicas:
            print(f"Arquivo '{nome_arquivo}' está vazio ou não contém nomes de música válidos.")
            return []
        print(f"Lidas {len(musicas)} músicas do arquivo '{nome_arquivo}'.")
        return musicas
    except FileNotFoundError:
        print(f"Erro: Arquivo '{nome_arquivo}' não encontrado.")
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao ler o arquivo '{nome_arquivo}': {e}")
        sys.exit(1)

def buscar_musicas_spotify(sp, lista_nomes_musicas):
    """Busca as URIs das músicas no Spotify."""
    uris_encontradas = []
    musicas_nao_encontradas = []
    print("\nBuscando músicas no Spotify...")

    for nome_musica in lista_nomes_musicas:
        try:
            # Busca pela música, limitando a 1 resultado para pegar o mais relevante
            resultado = sp.search(q=nome_musica, type='track', limit=1)
            items = resultado['tracks']['items']
            if items:
                track_uri = items[0]['uri']
                track_name = items[0]['name']
                artist_name = items[0]['artists'][0]['name']
                uris_encontradas.append(track_uri)
                print(f"  [ENCONTRADA] '{nome_musica}' -> '{track_name}' por {artist_name}")
            else:
                musicas_nao_encontradas.append(nome_musica)
                print(f"  [NÃO ENCONTRADA] '{nome_musica}'")
        except Exception as e:
            print(f"  [ERRO] Ocorreu um erro ao buscar '{nome_musica}': {e}")
            musicas_nao_encontradas.append(nome_musica)

    return uris_encontradas, musicas_nao_encontradas

def criar_playlist_spotify(sp, nome_playlist, descricao):
    """Cria uma nova playlist no Spotify."""
    user_id = sp.current_user()['id']
    try:
        playlist = sp.user_playlist_create(user=user_id,
                                           name=nome_playlist,
                                           public=False, # Mude para True se quiser pública
                                           description=descricao)
        print(f"\nPlaylist '{nome_playlist}' criada com sucesso!")
        print(f"Link: {playlist['external_urls']['spotify']}")
        return playlist['id']
    except Exception as e:
        print(f"Erro ao criar a playlist: {e}")
        sys.exit(1)

def adicionar_musicas_playlist(sp, playlist_id, lista_uris):
    """Adiciona músicas a uma playlist existente (em lotes de 100)."""
    if not lista_uris:
        print("Nenhuma música encontrada para adicionar à playlist.")
        return

    print(f"Adicionando {len(lista_uris)} músicas à playlist...")
    try:
        # A API do Spotify permite adicionar no máximo 100 faixas por vez
        for i in range(0, len(lista_uris), 100):
            lote = lista_uris[i:i + 100]
            sp.playlist_add_items(playlist_id, lote)
            print(f"  Lote de {len(lote)} músicas adicionado.")
        print("Todas as músicas encontradas foram adicionadas!")
    except Exception as e:
        print(f"Erro ao adicionar músicas à playlist: {e}")

# --- Execução Principal ---
if __name__ == "__main__":
    # 1. Autenticar
    spotify_client = get_spotify_client()

    # 2. Ler músicas do arquivo
    nomes_musicas = ler_musicas_do_arquivo(ARQUIVO_MUSICAS)
    if not nomes_musicas:
        print("Nenhuma música para processar. Saindo.")
        sys.exit(0)

    # 3. Buscar URIs no Spotify
    uris_musicas, nao_encontradas = buscar_musicas_spotify(spotify_client, nomes_musicas)

    # 4. Criar a playlist
    id_nova_playlist = criar_playlist_spotify(spotify_client, NOME_PLAYLIST, DESCRICAO_PLAYLIST)

    # 5. Adicionar músicas encontradas à playlist
    adicionar_musicas_playlist(spotify_client, id_nova_playlist, uris_musicas)

    # 6. Relatório final
    print("\n--- Resumo ---")
    print(f"Playlist criada: '{NOME_PLAYLIST}'")
    print(f"Total de músicas no arquivo: {len(nomes_musicas)}")
    print(f"Músicas adicionadas à playlist: {len(uris_musicas)}")
    if nao_encontradas:
        print(f"Músicas não encontradas ou com erro ({len(nao_encontradas)}):")
        for musica in nao_encontradas:
            print(f"  - {musica}")
    print("\nProcesso concluído!")