import os
import shutil
import sys
import datetime # Adicionado para uso futuro, se necessário
import time # Adicionado para pausas/animações se necessário

# Mapeamento de categorias e extensões
FILE_CATEGORIES = {
    # --- Fotos ---
    '.jpg': 'Fotos', '.jpeg': 'Fotos', '.png': 'Fotos', '.gif': 'Fotos',
    '.bmp': 'Fotos', '.webp': 'Fotos', '.tiff': 'Fotos', '.tif': 'Fotos',
    '.heic': 'Fotos', # Comum em iOS
    
    # --- Vídeos ---
    '.mp4': 'Videos', '.mkv': 'Videos', '.avi': 'Videos', '.mov': 'Videos',
    '.wmv': 'Videos', '.flv': 'Videos', '.webm': 'Videos', '.3gp': 'Videos',
    
    # --- Documentos ---
    '.pdf': 'Documentos', '.doc': 'Documentos', '.docx': 'Documentos',
    '.xls': 'Documentos', '.xlsx': 'Documentos', '.ppt': 'Documentos',
    '.pptx': 'Documentos', '.txt': 'Documentos', '.rtf': 'Documentos',
    '.odt': 'Documentos', '.ods': 'Documentos', '.odp': 'Documentos',
    '.csv': 'Documentos', '.md': 'Documentos', # Markdown
    
    # --- Áudio ---
    '.mp3': 'Audio', '.wav': 'Audio', '.flac': 'Audio', '.aac': 'Audio',
    '.ogg': 'Audio', '.wma': 'Audio', '.m4a': 'Audio',
    
    # --- Arquivos Comuns Diversos (Compactados, Executáveis, Imagens de Disco) ---
    '.zip': 'Arquivos_Comuns', '.rar': 'Arquivos_Comuns', '.7z': 'Arquivos_Comuns',
    '.exe': 'Arquivos_Comuns', '.apk': 'Arquivos_Comuns', '.iso': 'Arquivos_Comuns',
    '.tar': 'Arquivos_Comuns', '.gz': 'Arquivos_Comuns', '.tgz': 'Arquivos_Comuns',
    '.bz2': 'Arquivos_Comuns', '.xz': 'Arquivos_Comuns', '.msi': 'Arquivos_Comuns',
    '.dmg': 'Arquivos_Comuns', # Para macOS, pode aparecer em downloads
    
    # Adicione mais conforme necessário. O que não estiver aqui vai para 'Diversos'.
}

# Extensões de arquivos temporários a serem consideradas na limpeza
TEMP_EXTENSIONS = ['.tmp', '.bak', '.~tmp', '.~bak', '.temp', '.~lock']

def convert_bytes(num):
    """Converte um número de bytes para uma string legível (KB, MB, GB)."""
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return f"{num:.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} PB"


def get_downloads_path():
    """Retorna o caminho absoluto para a pasta Downloads no ambiente Termux."""
    return os.path.expanduser('~/storage/downloads')

def get_file_destination_paths(file_name, base_output_folder):
    """
    Determina a categoria e os caminhos de destino para um arquivo.
    Retorna (categoria_folder_path, final_extension_folder_path, category_name).
    """
    extension = os.path.splitext(file_name)[1].lower() # Pega a extensão e converte para minúsculas
    
    category_name = FILE_CATEGORIES.get(extension, 'Diversos') # Pega a categoria ou 'Diversos'
    
    # Caminho da pasta da categoria (Ex: 'Downloads/Arquivos/Fotos')
    category_folder_path = os.path.join(base_output_folder, category_name)
    
    # Nome da subpasta por extensão (Ex: 'Fotos.JPG', 'Diversos.OBB')
    # Usamos o nome da categoria + a extensão original (com ponto)
    extension_folder_name = f"{category_name}{extension.upper()}" # Ex: Fotos.JPG
    final_extension_folder_path = os.path.join(category_folder_path, extension_folder_name)
    
    return category_folder_path, final_extension_folder_path, category_name

def organize_files_in_downloads():
    """
    Organiza arquivos e subpastas dentro da pasta Downloads do celular
    com base na nova estrutura de categorias.
    """
    
    source_folder = get_downloads_path()
    output_folder = source_folder # A pasta de saída é a própria pasta de Downloads

    if not os.path.exists(source_folder):
        print(f"Erro: A pasta de Downloads não foi encontrada em '{source_folder}'.")
        print("Certifique-se de ter executado 'termux-setup-storage' e concedido as permissões necessárias.")
        input("Pressione Enter para continuar.")
        return 

    print(f"\n--- Analisando arquivos em '{source_folder}' ---")

    # Lista todos os arquivos (não pastas e não ocultos)
    all_files_in_source = [f for f in os.listdir(source_folder) 
                           if os.path.isfile(os.path.join(source_folder, f)) and not f.startswith('.')]

    # Lista todas as pastas (não ocultas)
    all_folders_in_source = [d for d in os.listdir(source_folder) 
                             if os.path.isdir(os.path.join(source_folder, d)) and not d.startswith('.')]
    
    # Filtra as pastas que são as pastas de destino do próprio organizador para não movermos elas
    folders_to_ignore = ['Arquivos', 'Pastas_Organizadas']
    folders_to_move = [d for d in all_folders_in_source if d not in folders_to_ignore]

    if not all_files_in_source and not folders_to_move:
        print("Nenhum arquivo ou pasta para organizar encontrado na pasta Downloads.")
        input("Pressione Enter para continuar.")
        return

    print("\nArquivos detectados para organização:")
    for file_name in all_files_in_source:
        _, final_path, category = get_file_destination_paths(file_name, os.path.join(output_folder, "Arquivos"))
        print(f"- {file_name} -> Categoria: {category} -> {os.path.basename(os.path.dirname(final_path))}/{os.path.basename(final_path)}/")
    
    if folders_to_move:
        print("\nPasta(s) detectada(s) para organização:")
        for folder_name in folders_to_move:
            print(f"- {folder_name}/ -> Pastas_Organizadas/")

    confirmacao = input("\nDigite 'confirmar' para iniciar a organização: ").strip().lower()

    if confirmacao != 'confirmar':
        print("Organização cancelada. Nada foi modificado.")
        input("Pressione Enter para continuar.")
        return

    print("\nIniciando organização...")

    total_items = len(all_files_in_source) + len(folders_to_move)
    processed_items = 0
    moved_files_count = {} # Para estatísticas de arquivos
    moved_folders_count = 0 # Para estatísticas de pastas

    # --- Configurações das Pastas Base ---
    main_archive_folder = os.path.join(output_folder, "Arquivos")
    os.makedirs(main_archive_folder, exist_ok=True)

    organized_folders_base_path = os.path.join(output_folder, "Pastas_Organizadas")
    os.makedirs(organized_folders_base_path, exist_ok=True)

    # --- Movendo Pastas Originais ---
    for folder_name in folders_to_move:
        source_path_folder = os.path.join(source_folder, folder_name)
        destination_path_folder = os.path.join(organized_folders_base_path, folder_name)
        
        try:
            shutil.move(source_path_folder, destination_path_folder)
            print(f"Movido pasta: '{folder_name}' para '{os.path.basename(organized_folders_base_path)}/'")
            processed_items += 1
            moved_folders_count += 1 # Incrementa contador de pastas movidas
        except Exception as e:
            print(f"Erro ao mover pasta '{folder_name}': {e}")
            processed_items += 1 
        
        # Atualiza progresso no terminal
        if total_items > 0:
            progress_percent = (processed_items / total_items) * 100
            sys.stdout.write(f"\rProgresso: {progress_percent:.1f}% ({processed_items}/{total_items} itens)")
            sys.stdout.flush()

    # --- Movendo Arquivos ---
    for file_name in all_files_in_source:
        source_path_file = os.path.join(source_folder, file_name)
        
        if file_name.startswith('.'): # Garante que arquivos ocultos não sejam processados
            processed_items += 1
            continue

        category_base_path, final_extension_folder_path, category_name = get_file_destination_paths(file_name, main_archive_folder)
        
        os.makedirs(category_base_path, exist_ok=True)
        os.makedirs(final_extension_folder_path, exist_ok=True)

        destination_path_file = os.path.join(final_extension_folder_path, file_name)

        if os.path.exists(destination_path_file):
            base_name = os.path.splitext(file_name)[0]
            extension = os.path.splitext(file_name)[1]
            suffix = 1
            new_file_name = f"{base_name}_{suffix}{extension}"
            while os.path.exists(os.path.join(final_extension_folder_path, new_file_name)):
                suffix += 1
                new_file_name = f"{base_name}_{suffix}{extension}"
            destination_path_file = os.path.join(final_extension_folder_path, new_file_name)
            print(f"\nConflito: '{file_name}' renomeado para '{new_file_name}'") 

        try:
            shutil.move(source_path_file, destination_path_file)
            print(f"\nMovido arquivo: '{file_name}' para '{os.path.basename(category_base_path)}/{os.path.basename(final_extension_folder_path)}/'")
            processed_items += 1
            # Atualiza estatísticas de arquivos
            moved_files_count[category_name] = moved_files_count.get(category_name, 0) + 1
        except Exception as e:
            print(f"\nErro ao mover arquivo '{file_name}': {e}")
            processed_items += 1
        
        if total_items > 0:
            progress_percent = (processed_items / total_items) * 100
            sys.stdout.write(f"\rProgresso: {progress_percent:.1f}% ({processed_items}/{total_items} itens)")
            sys.stdout.flush()

    print("\n\nOrganização concluída com sucesso!")
    print(f"Total de {processed_items} itens processados na pasta Downloads.")

    # --- Estatísticas da Organização ---
    print("\n--- Resumo da Organização ---")
    if moved_folders_count > 0:
        print(f"Pastas movidas para 'Pastas_Organizadas/': {moved_folders_count}")
    
    if moved_files_count:
        print("Arquivos movidos por categoria:")
        for category, count in sorted(moved_files_count.items()):
            print(f"- {category}: {count} arquivos")
    else:
        print("Nenhum arquivo foi movido.")
    print("-----------------------------")

    input("Pressione Enter para continuar.")


def clean_files():
    """
    Identifica e oferece para remover arquivos vazios e temporários
    dentro da pasta Downloads e suas subpastas organizadas.
    """
    downloads_path = get_downloads_path()
    
    files_to_clean = []
    total_size_to_clean = 0 # Em bytes

    print(f"\n--- Analisando arquivos para limpeza em '{downloads_path}' ---")

    # Percorre a pasta Downloads e suas subpastas recursivamente
    for root, _, files in os.walk(downloads_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            try:
                file_size = os.path.getsize(file_path)
                file_ext = os.path.splitext(file_name)[1].lower()

                if file_size == 0:
                    files_to_clean.append((file_path, "Vazio", file_size))
                elif file_ext in TEMP_EXTENSIONS:
                    files_to_clean.append((file_path, f"Temporário ({file_ext})", file_size))
                
            except Exception as e:
                print(f"Erro ao analisar '{file_path}': {e}")

    if not files_to_clean:
        print("Nenhum arquivo vazio ou temporário encontrado para limpeza.")
        input("Pressione Enter para continuar.")
        return

    print("\n--- Arquivos detectados para limpeza: ---")
    for i, (f_path, reason, f_size) in enumerate(files_to_clean):
        # Mostra o caminho relativo a downloads_path para melhor leitura
        relative_path = os.path.relpath(f_path, downloads_path)
        print(f"{i+1}. {relative_path} (Motivo: {reason}, Tamanho: {convert_bytes(f_size)})")
        total_size_to_clean += f_size # Acumula o tamanho aqui

    print(f"\nTotal de {len(files_to_clean)} arquivos a serem removidos, totalizando {convert_bytes(total_size_to_clean)}.")
    
    confirmacao = input("\nDigite 'limpar' para confirmar a exclusão: ").strip().lower()

    if confirmacao != 'limpar':
        print("Limpeza cancelada. Nada foi removido.")
        input("Pressione Enter para continuar.")
        return

    print("\nIniciando limpeza...")
    removed_count = 0
    removed_size_total = 0 # Em bytes

    for f_path, _, f_size in files_to_clean:
        try:
            os.remove(f_path)
            print(f"Removido: {os.path.relpath(f_path, downloads_path)}")
            removed_count += 1
            removed_size_total += f_size
        except Exception as e:
            print(f"Erro ao remover '{os.path.relpath(f_path, downloads_path)}': {e}")
    
    print(f"\nLimpeza concluída! {removed_count} arquivos foram removidos.")
    print(f"Espaço total liberado: {convert_bytes(removed_size_total)}.")
    input("Pressione Enter para continuar.")


def display_menu():
    """Exibe o menu principal do organizador."""
    print("\n" + "="*40)
    print("      ORGANIZADOR DE DOWNLOADS CLI")
    print("="*40)
    print("1. Organizar arquivos (por categoria)")
    print("2. Limpar arquivos (vazios/temporários)")
    print("3. Sair")
    print("="*40)

def main_menu():
    """Loop principal do menu do aplicativo."""
    while True:
        display_menu()
        choice = input("Digite sua escolha (1-3): ").strip()

        if choice == '1':
            organize_files_in_downloads()
        elif choice == '2':
            clean_files()
        elif choice == '3':
            print("Saindo do organizador. Até mais!")
            break
        else:
            print("Opção inválida. Por favor, escolha 1, 2 ou 3.")
            input("Pressione Enter para continuar.")

if __name__ == "__main__":
    main_menu()
