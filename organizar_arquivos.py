import os
import shutil
import math

def organizar_arquivos_em_pastas(source_dir, files_per_folder=15):
    """
    Organiza arquivos de um diretório de origem em subpastas,
    com um número máximo de arquivos por subpasta.

    Args:
        source_dir (str): O caminho para o diretório de origem.
        files_per_folder (int): O número máximo de arquivos por subpasta. Padrão é 15.
    """
    # 1. Validar o diretório de origem
    if not os.path.isdir(source_dir):
        print(f"Erro: O diretório de origem '{source_dir}' não existe ou não é um diretório válido.")
        return

    print(f"Analisando o diretório: {source_dir}")

    # 2. Listar apenas os arquivos no diretório de origem (ignora subpastas)
    try:
        all_items = os.listdir(source_dir)
        # Garante que estamos pegando apenas arquivos, e não diretórios
        files_to_move = [f for f in all_items if os.path.isfile(os.path.join(source_dir, f))]
    except OSError as e:
        print(f"Erro ao listar arquivos em '{source_dir}': {e}")
        return

    # 3. Verificar se há arquivos para mover
    num_files = len(files_to_move)
    if num_files == 0:
        print(f"Nenhum arquivo encontrado em '{source_dir}' para organizar.")
        return

    print(f"Encontrados {num_files} arquivos para organizar.")

    # 4. Calcular o número de subpastas necessárias
    # math.ceil arredonda para cima, garantindo espaço para todos os arquivos
    num_folders_needed = math.ceil(num_files / files_per_folder)
    print(f"Serão criadas aproximadamente {num_folders_needed} subpastas (com no máximo {files_per_folder} arquivos cada).")

    # 5. Iterar sobre os arquivos e movê-los
    file_count = 0
    folder_index = 1
    current_target_dir = ""

    for file_name in files_to_move:
        # Determina em qual subpasta o arquivo atual deve ir
        if file_count % files_per_folder == 0:
            # Cria o nome da nova subpasta
            target_subdir_name = f"subpasta_{folder_index}"
            current_target_dir = os.path.join(source_dir, target_subdir_name)

            # Cria a subpasta (se já existir, não faz nada e não dá erro)
            try:
                os.makedirs(current_target_dir, exist_ok=True)
                print(f"--- Criando/Verificando pasta: {target_subdir_name} ---")
            except OSError as e:
                print(f"Erro ao criar a pasta '{current_target_dir}': {e}. Pulando arquivos para esta pasta.")
                # Se não puder criar a pasta, avança para a próxima leva de arquivos teóricos
                file_count = files_per_folder
                folder_index += 1
                continue # Pula para o próximo arquivo

            folder_index += 1

        # Constrói o caminho completo de origem e destino
        source_file_path = os.path.join(source_dir, file_name)
        target_file_path = os.path.join(current_target_dir, file_name)

        # Move o arquivo
        try:
            print(f"Movendo '{file_name}' para '{os.path.basename(current_target_dir)}'...")
            shutil.move(source_file_path, target_file_path)
            file_count += 1
        except (OSError, shutil.Error) as e:
            print(f"Erro ao mover '{file_name}': {e}. O arquivo pode ter sido pulado.")
        except Exception as e: # Captura genérica para outros erros inesperados
             print(f"Um erro inesperado ocorreu ao processar '{file_name}': {e}. O arquivo pode ter sido pulado.")

    print("\nOrganização concluída!")

# --- Como usar o script ---
if __name__ == "__main__":
    # Pede ao usuário o caminho da pasta
    diretorio_alvo = input("Digite o caminho completo da pasta que contém os arquivos: ")

    # Define o número máximo de arquivos por pasta (você pode mudar isso)
    max_arquivos_por_pasta = 15

    # Chama a função para organizar os arquivos
    organizar_arquivos_em_pastas(diretorio_alvo, max_arquivos_por_pasta)

    # Mantém a janela do console aberta (opcional, útil se executar com duplo clique no Windows)
    # input("\nPressione Enter para sair...")