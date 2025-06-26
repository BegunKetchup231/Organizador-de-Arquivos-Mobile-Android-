import os
import shutil
import sys
import datetime
import time

# Mapeamento de categorias e extensões
FILE_CATEGORIES = {
    # --- Fotos ---
    '.jpg': 'Fotos', '.jpeg': 'Fotos', '.png': 'Fotos', '.gif': 'Fotos',
    '.bmp': 'Fotos', '.webp': 'Fotos', '.tiff': 'Fotos', '.tif': 'Fotos',
    '.heic': 'Fotos', 
    
    # --- Vídeos ---
    '.mp4': 'Videos', '.mkv': 'Videos', '.avi': 'Videos', '.mov': 'Videos',
    '.wmv': 'Videos', '.flv': 'Videos', '.webm': 'Videos', '.3gp': 'Videos',
    
    # --- Documentos ---
    '.pdf': 'Documentos', '.doc': 'Documentos', '.docx': 'Documentos',
    '.xls': 'Documentos', '.xlsx': 'Documentos', '.ppt': 'Documentos',
    '.pptx': 'Documentos', '.txt': 'Documentos', '.rtf': 'Documentos',
    '.odt': 'Documentos', '.ods': 'Documentos', '.odp': 'Documentos',
    '.csv': 'Documentos', '.md': 'Documentos', 
    
    # --- Áudio ---
    '.mp3': 'Audio', '.wav': 'Audio', '.flac': 'Audio', '.aac': 'Audio',
    '.ogg': 'Audio', '.wma': 'Audio', '.m4a': 'Audio',
    
    # --- Arquivos Comuns Diversos (Compactados, Executáveis, Imagens de Disco) ---
    '.zip': 'Arquivos_Comuns', '.rar': 'Arquivos_Comuns', '.7z': 'Arquivos_Comuns',
    '.exe': 'Arquivos_Comuns', '.apk': 'Arquivos_Comuns', '.iso': 'Arquivos_Comuns',
    '.tar': 'Arquivos_Comuns', '.gz': 'Arquivos_Comuns', '.tgz': 'Arquivos_Comuns',
    '.bz2': 'Arquivos_Comuns', '.xz': 'Arquivos_Comuns', '.msi': 'Arquivos_Comuns',
    '.dmg': 'Arquivos_Comuns', 
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
    extension = os.path.splitext(file_name)[1].lower() 
    
    category_name = FILE_CATEGORIES.get(extension, 'Diversos') 
    
    category_folder_path = os.path.join(base_output_folder, category_name)
    
    extension_folder_name = f"{category_name}{extension.upper()}" 
    final_extension_folder_path = os.path.join(category_folder_path, extension_folder_name)
    
    return category_folder_path, final_extension_folder_path, category_name

def organize_files_in_downloads():
    """
    Organiza arquivos e subpastas dentro da pasta Downloads do celular
    com base na nova estrutura de categorias.
    """
    
    source_folder = get_downloads_path()
    output_folder = source_folder 

    if not os.path.exists(source_folder):
        print(f"Erro: A pasta de Downloads não foi encontrada em '{source_folder}'.")
        print("Certifique-se de ter executado 'termux-setup-storage' e concedido as permissões necessárias.")
        input("Pressione Enter para continuar.")
        return 

    print(f"\n--- Analisando arquivos em '{source_folder}' ---")

    all_files_in_source = [f for f in os.listdir(source_folder) 
                           if os.path.isfile(os.path.join(source_folder, f)) and not f.startswith('.')]

    all_folders_in_source = [d for d in os.listdir(source_folder) 
                             if os.path.isdir(os.path.join(source_folder, d)) and not d.startswith('.')]
    
    folders_to_ignore = ['Arquivos', 'Pastas_Organizadas', 'Organizado_Por_Data'] # Adicionada nova pasta de destino
    folders_to_move = [d for d in all_folders_in_source if d not in folders_to_ignore]

    if not all_files_in_source and not folders_to_move:
        print("Nenhum arquivo ou pasta para organizar encontrado na pasta Downloads.")
        input("Pressione Enter para continuar.")
        return

    print("\nArquivos detectados para organização por categoria:")
    for file_name in all_files_in_source:
        _, final_path, category = get_file_destination_paths(file_name, os.path.join(output_folder, "Arquivos"))
        print(f"- {file_name} -> Categoria: {category} -> {os.path.basename(os.path.dirname(final_path))}/{os.path.basename(final_path)}/")
    
    if folders_to_move:
        print("\nPasta(s) detectada(s) para organização por categoria:")
        for folder_name in folders_to_move:
            print(f"- {folder_name}/ -> Pastas_Organizadas/")

    confirmacao = input("\nDigite 'confirmar' para iniciar a organização por categoria: ").strip().lower()

    if confirmacao != 'confirmar':
        print("Organização por categoria cancelada. Nada foi modificado.")
        input("Pressione Enter para continuar.")
        return

    print("\nIniciando organização por categoria...")

    total_items = len(all_files_in_source) + len(folders_to_move)
    processed_items = 0
    moved_files_count = {} 
    moved_folders_count = 0 

    main_archive_folder = os.path.join(output_folder, "Arquivos")
    os.makedirs(main_archive_folder, exist_ok=True)

    organized_folders_base_path = os.path.join(output_folder, "Pastas_Organizadas")
    os.makedirs(organized_folders_base_path, exist_ok=True)

    for folder_name in folders_to_move:
        source_path_folder = os.path.join(source_folder, folder_name)
        destination_path_folder = os.path.join(organized_folders_base_path, folder_name)
        
        try:
            shutil.move(source_path_folder, destination_path_folder)
            print(f"Movido pasta: '{folder_name}' para '{os.path.basename(organized_folders_base_path)}/'")
            processed_items += 1
            moved_folders_count += 1 
        except Exception as e:
            print(f"Erro ao mover pasta '{folder_name}': {e}")
            processed_items += 1 
        
        if total_items > 0:
            progress_percent = (processed_items / total_items) * 100
            sys.stdout.write(f"\rProgresso: {progress_percent:.1f}% ({processed_items}/{total_items} itens)")
            sys.stdout.flush()

    for file_name in all_files_in_source:
        source_path_file = os.path.join(source_folder, file_name)
        
        if file_name.startswith('.'): 
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
            moved_files_count[category_name] = moved_files_count.get(category_name, 0) + 1
        except Exception as e:
            print(f"\nErro ao mover arquivo '{file_name}': {e}")
            processed_items += 1
        
        if total_items > 0:
            progress_percent = (processed_items / total_items) * 100
            sys.stdout.write(f"\rProgresso: {progress_percent:.1f}% ({processed_items}/{total_items} itens)")
            sys.stdout.flush()

    print("\n\nOrganização por categoria concluída com sucesso!")
    print(f"Total de {processed_items} itens processados na pasta Downloads.")

    print("\n--- Resumo da Organização por Categoria ---")
    if moved_folders_count > 0:
        print(f"Pastas movidas para 'Pastas_Organizadas/': {moved_folders_count}")
    
    if moved_files_count:
        print("Arquivos movidos por categoria:")
        for category, count in sorted(moved_files_count.items()):
            print(f"- {category}: {count} arquivos")
    else:
        print("Nenhum arquivo foi movido por categoria.")
    print("------------------------------------------")

    input("Pressione Enter para continuar.")


def clean_files():
    """
    Identifica e oferece para remover arquivos vazios e temporários
    dentro da pasta Downloads e suas subfolders organizadas.
    """
    downloads_path = get_downloads_path()
    
    files_to_clean = []
    total_size_to_clean = 0 

    print(f"\n--- Analisando arquivos para limpeza em '{downloads_path}' ---")

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
        relative_path = os.path.relpath(f_path, downloads_path)
        print(f"{i+1}. {relative_path} (Motivo: {reason}, Tamanho: {convert_bytes(f_size)})")
        total_size_to_clean += f_size 

    print(f"\nTotal de {len(files_to_clean)} arquivos a serem removidos, totalizando {convert_bytes(total_size_to_clean)}.")
    
    confirmacao = input("\nDigite 'limpar' para confirmar a exclusão: ").strip().lower()

    if confirmacao != 'limpar':
        print("Limpeza cancelada. Nada foi removido.")
        input("Pressione Enter para continuar.")
        return

    print("\nIniciando limpeza...")
    removed_count = 0
    removed_size_total = 0 

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


def remove_empty_folders():
    """
    Identifica e oferece para remover pastas vazias dentro da pasta Downloads e suas subpastas.
    Exclui pastas de destino do próprio organizador.
    """
    downloads_path = get_downloads_path()
    empty_folders_found = []

    print(f"\n--- Analisando pastas vazias em '{downloads_path}' ---")

    folders_to_protect = [
        os.path.join(downloads_path, 'Arquivos'),
        os.path.join(downloads_path, 'Pastas_Organizadas'),
        os.path.join(downloads_path, 'Organizado_Por_Data') # Adicionada nova pasta de destino
    ]
    main_archive_folder = os.path.join(downloads_path, "Arquivos")
    for category_name in set(FILE_CATEGORIES.values()): 
        folders_to_protect.append(os.path.join(main_archive_folder, category_name))
        for ext in [k for k, v in FILE_CATEGORIES.items() if v == category_name]:
             folders_to_protect.append(os.path.join(main_archive_folder, category_name, f"{category_name}{ext.upper()}"))
    folders_to_protect.append(os.path.join(main_archive_folder, 'Diversos'))
    for ext in sorted(set(FILE_CATEGORIES.keys())): 
        if FILE_CATEGORIES.get(ext) == 'Diversos' or ext not in FILE_CATEGORIES:
             folders_to_protect.append(os.path.join(main_archive_folder, 'Diversos', f"Diversos{ext.upper()}"))


    for root, dirs, files in os.walk(downloads_path, topdown=False):
        if not files and not dirs:
            if root not in folders_to_protect:
                empty_folders_found.append(root)

    if not empty_folders_found:
        print("Nenhuma pasta vazia encontrada para remoção.")
        input("Pressione Enter para continuar.")
        return

    print("\n--- Pastas vazias detectadas para remoção: ---")
    for i, folder_path in enumerate(empty_folders_found):
        relative_path = os.path.relpath(folder_path, downloads_path)
        print(f"{i+1}. {relative_path}/")

    confirmacao = input("\nDigite 'remover' para confirmar a exclusão destas pastas: ").strip().lower()

    if confirmacao != 'remover':
        print("Remoção de pastas vazias cancelada. Nada foi removido.")
        input("Pressione Enter para continuar.")
        return

    print("\nIniciando remoção de pastas vazias...")
    removed_count = 0
    for folder_path in empty_folders_found:
        try:
            os.rmdir(folder_path) 
            print(f"Removido: {os.path.relpath(folder_path, downloads_path)}/")
            removed_count += 1
        except Exception as e:
            print(f"Erro ao remover '{os.path.relpath(folder_path, downloads_path)}/': {e}")
    
    print(f"\nRemoção de pastas vazias concluída! {removed_count} pastas foram removidas.")
    input("Pressione Enter para continuar.")


def organize_by_date():
    """
    Organiza arquivos na pasta Downloads em subpastas baseadas em ano e mês de modificação.
    """
    source_folder = get_downloads_path()
    date_output_base = os.path.join(source_folder, "Organizado_Por_Data")

    if not os.path.exists(source_folder):
        print(f"Erro: A pasta de Downloads não foi encontrada em '{source_folder}'.")
        print("Certifique-se de ter executado 'termux-setup-storage' e concedido as permissões necessárias.")
        input("Pressione Enter para continuar.")
        return

    print(f"\n--- Analisando arquivos para organização por data em '{source_folder}' ---")

    # Obtém todos os arquivos no diretório de origem que não são pastas de destino do organizador
    # E que não estão em uma das pastas de destino já existentes
    files_to_organize = []
    # Lista de pastas que não devem ser varridas para arquivos soltos, pois já são destinos do organizador
    folders_to_exclude_from_root_scan = [
        'Arquivos', 'Pastas_Organizadas', 'Organizado_Por_Data'
    ]
    
    current_root_items = os.listdir(source_folder)
    for item in current_root_items:
        item_path = os.path.join(source_folder, item)
        if os.path.isfile(item_path) and not item.startswith('.'):
            files_to_organize.append(item)
        elif os.path.isdir(item_path) and item in folders_to_exclude_from_root_scan:
            # Se for uma pasta de destino, ignoramos seus arquivos internos para esta operação
            pass
        elif os.path.isdir(item_path) and not item.startswith('.'):
            # Se for uma pasta que não é destino do organizador (ex: uma pasta de downloads original), não a movemos por data
            # Apenas arquivos soltos são movidos por data nesta função
            pass

    if not files_to_organize:
        print("Nenhum arquivo solto na pasta Downloads para organizar por data.")
        input("Pressione Enter para continuar.")
        return

    print("\nArquivos detectados para organização por data:")
    for file_name in files_to_organize:
        print(f"- {file_name}")
    
    confirmacao = input("\nDigite 'confirmar' para iniciar a organização por data: ").strip().lower()

    if confirmacao != 'confirmar':
        print("Organização por data cancelada. Nada foi modificado.")
        input("Pressione Enter para continuar.")
        return

    print("\nIniciando organização por data...")
    os.makedirs(date_output_base, exist_ok=True)

    moved_count_by_year_month = {}
    total_processed_files = 0

    for file_name in files_to_organize:
        file_path = os.path.join(source_folder, file_name)
        
        try:
            mod_timestamp = os.path.getmtime(file_path) # Data de modificação
            dt_object = datetime.datetime.fromtimestamp(mod_timestamp)
            
            year_folder = str(dt_object.year)
            month_folder = dt_object.strftime("%m - %B") # Ex: "06 - June"

            dest_year_path = os.path.join(date_output_base, year_folder)
            dest_month_path = os.path.join(dest_year_path, month_folder)

            os.makedirs(dest_month_path, exist_ok=True)

            final_dest_path = os.path.join(dest_month_path, file_name)

            if os.path.exists(final_dest_path):
                base_name = os.path.splitext(file_name)[0]
                extension = os.path.splitext(file_name)[1]
                suffix = 1
                new_file_name = f"{base_name}_{suffix}{extension}"
                while os.path.exists(os.path.join(dest_month_path, new_file_name)):
                    suffix += 1
                    new_file_name = f"{base_name}_{suffix}{extension}"
                final_dest_path = os.path.join(dest_month_path, new_file_name)
                print(f"\nConflito: '{file_name}' renomeado para '{new_file_name}'")

            shutil.move(file_path, final_dest_path)
            print(f"\nMovido: '{file_name}' para '{year_folder}/{month_folder}/'")
            total_processed_files += 1
            
            year_month_key = f"{year_folder}/{month_folder}"
            moved_count_by_year_month[year_month_key] = moved_count_by_year_month.get(year_month_key, 0) + 1

        except Exception as e:
            print(f"\nErro ao organizar '{file_name}' por data: {e}")

    print("\nOrganização por data concluída com sucesso!")
    print(f"Total de {total_processed_files} arquivos processados na pasta Downloads.")

    print("\n--- Resumo da Organização por Data ---")
    if moved_count_by_year_month:
        for ym, count in sorted(moved_count_by_year_month.items()):
            print(f"- {ym}: {count} arquivos")
    else:
        print("Nenhum arquivo foi movido por data.")
    print("--------------------------------------")
    input("Pressione Enter para continuar.")


def display_menu():
    """Exibe o menu principal do organizador."""
    print("\n" + "="*40)
    print("      ORGANIZADOR DE DOWNLOADS CLI")
    print("="*40)
    print("1. Organizar arquivos (por categoria)")
    print("2. Limpar arquivos (vazios/temporários)")
    print("3. Remover pastas vazias") 
    print("4. Organizar arquivos (por data)") 
    print("5. Sair") 
    print("="*40)

def main_menu():
    """Loop principal do menu do aplicativo."""
    while True:
        display_menu()
        choice = input("Digite sua escolha (1-5): ").strip() 

        if choice == '1':
            organize_files_in_downloads()
        elif choice == '2':
            clean_files()
        elif choice == '3': 
            remove_empty_folders()
        elif choice == '4': 
            organize_by_date()
        elif choice == '5': 
            print("Saindo do organizador. Até mais!")
            break
        else:
            print("Opção inválida. Por favor, escolha 1, 2, 3, 4 ou 5.") 
            input("Pressione Enter para continuar.")

if __name__ == "__main__":
    main_menu()

