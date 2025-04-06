import requests
import os
from urllib.parse import urlparse

def baixar_arquivo(url, pasta_destino="."):
    """
    Baixa um arquivo de uma URL e salva em uma pasta local.

    Args:
        url (str): A URL completa do arquivo a ser baixado.
        pasta_destino (str): O caminho da pasta onde o arquivo será salvo.
                             Se omitido, salva no diretório atual do script.
    """
    print(f"Iniciando download de: {url}")

    try:
        # Faz a requisição GET para a URL.
        # stream=True é importante para não carregar arquivos grandes inteiros na memória.
        # timeout define um limite de tempo para a conexão e leitura.
        response = requests.get(url, stream=True, timeout=(10, 30)) # Timeout de 10s para conectar, 30s para ler

        # Verifica se a requisição foi bem-sucedida (status code 200 OK, etc.)
        # Se não for (ex: 404 Not Found, 403 Forbidden), levanta uma exceção HTTPError.
        response.raise_for_status()

        # --- Determinar o nome do arquivo ---
        # 1. Tenta pegar o nome do arquivo da URL
        parsed_url = urlparse(url)
        nome_arquivo = os.path.basename(parsed_url.path)

        # 2. Se a URL não tem um nome de arquivo claro (ex: termina com '/'),
        #    tenta usar o header 'Content-Disposition' se disponível,
        #    ou gera um nome padrão ou informa erro.
        if not nome_arquivo:
            if 'content-disposition' in response.headers:
                # Tenta extrair o nome do header (pode ser complexo)
                cd = response.headers['content-disposition']
                fname_parts = [part for part in cd.split(';') if part.strip().startswith('filename=')]
                if fname_parts:
                    nome_arquivo = fname_parts[0].split('=')[1].strip('"\' ')
            if not nome_arquivo: # Se ainda não conseguiu
                 print("Aviso: Não foi possível determinar um nome de arquivo pela URL ou cabeçalhos.")
                 # Você pode definir um nome padrão ou pedir ao usuário
                 nome_arquivo = "arquivo_baixado_sem_nome" # Nome padrão
                 print(f"Usando nome padrão: {nome_arquivo}")
                 # Alternativa: return ou raise Exception("Nome do arquivo não encontrado")

        # --- Preparar o caminho completo para salvar ---
        # Garante que a pasta de destino exista, criando-a se necessário.
        os.makedirs(pasta_destino, exist_ok=True)

        # Junta o caminho da pasta e o nome do arquivo.
        caminho_completo = os.path.join(pasta_destino, nome_arquivo)

        print(f"Nome do arquivo detectado/definido: {nome_arquivo}")
        print(f"Salvando em: {caminho_completo}")

        # --- Salvar o conteúdo do arquivo ---
        # Abre o arquivo local no modo de escrita binária ('wb').
        with open(caminho_completo, 'wb') as f:
            # Itera sobre o conteúdo da resposta em pedaços (chunks).
            # Isso evita carregar arquivos muito grandes na memória de uma vez.
            chunk_size = 8192 # 8 KB por pedaço (um valor comum)
            total_baixado = 0
            print("Progresso: ", end="")
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:  # Filtra chunks vazios que podem ocorrer
                    f.write(chunk)
                    total_baixado += len(chunk)
                    # Imprime um ponto para indicar progresso (simples)
                    print(".", end="", flush=True)

        print(f"\nDownload concluído! Arquivo '{nome_arquivo}' salvo com sucesso em '{pasta_destino}'.")
        print(f"Tamanho total: {total_baixado / 1024:.2f} KB") # Mostra o tamanho em KB

    # --- Tratamento de Erros ---
    except requests.exceptions.MissingSchema:
        print(f"Erro: URL inválida '{url}'. Falta 'http://' ou 'https://'?")
    except requests.exceptions.ConnectionError:
        print(f"Erro: Falha na conexão com '{url}'. Verifique sua rede ou se a URL está correta/ativa.")
    except requests.exceptions.Timeout:
         print(f"Erro: Tempo limite excedido ao tentar conectar ou baixar de '{url}'.")
    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP: {http_err} - O servidor retornou um erro (ex: 404 Não Encontrado, 403 Acesso Negado).")
    except requests.exceptions.RequestException as e:
        # Erro genérico da biblioteca requests
        print(f"Erro durante a requisição: {e}")
    except OSError as e:
        # Erro relacionado ao sistema de arquivos (criar pasta, escrever arquivo)
        print(f"Erro de Sistema ao salvar o arquivo: {e} (Verifique permissões ou espaço em disco)")
    except Exception as e:
        # Captura qualquer outro erro inesperado
        print(f"Ocorreu um erro inesperado: {e}")

# --- Parte Principal do Script (onde ele começa a rodar) ---
if __name__ == "__main__":
    url_do_arquivo = input("Digite ou cole o link completo (URL) do arquivo: ")
    pasta_para_salvar = input("Digite o caminho da pasta onde deseja salvar (ou deixe em branco para salvar aqui): ")

    # Se o usuário não digitou uma pasta, usa o diretório atual (onde o script está rodando)
    if not pasta_para_salvar:
        pasta_para_salvar = "." # "." representa o diretório atual

    # Chama a função para fazer o download
    baixar_arquivo(url_do_arquivo, pasta_para_salvar)

    # (Opcional) Mantém a janela aberta no Windows se executar com duplo clique
    # input("\nPressione Enter para sair...")