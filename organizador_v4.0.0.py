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

    print("\n\nOrganização concluída com sucesso!")
    print(f"Total de {processed_items} itens processados na pasta Downloads.")

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

    # Obtém uma lista das pastas de destino para evitar removê-las prematuramente
    # Mesmo se estiverem vazias, são pastas de estrutura do organizador
    folders_to_protect = [
        os.path.join(downloads_path, 'Arquivos'),
        os.path.join(downloads_path, 'Pastas_Organizadas')
    ]
    # Adicionar também as subpastas de categoria (Fotos, Videos, etc.) e extensão (Fotos.JPG, etc.)
    # Percorrer o FILE_CATEGORIES para construir esses caminhos também
    main_archive_folder = os.path.join(downloads_path, "Arquivos")
    for category_name in set(FILE_CATEGORIES.values()): # Pega nomes de categoria únicos
        folders_to_protect.append(os.path.join(main_archive_folder, category_name))
        for ext in [k for k, v in FILE_CATEGORIES.items() if v == category_name]:
             folders_to_protect.append(os.path.join(main_archive_folder, category_name, f"{category_name}{ext.upper()}"))
    # Adiciona a pasta "Diversos" e suas subpastas
    folders_to_protect.append(os.path.join(main_archive_folder, 'Diversos'))
    for ext in sorted(set(FILE_CATEGORIES.keys())): # Para todas as extensões, a pasta "Diversos" também pode ter subpastas de extensão se o arquivo estiver lá
        if FILE_CATEGORIES.get(ext) == 'Diversos' or ext not in FILE_CATEGORIES:
             folders_to_protect.append(os.path.join(main_archive_folder, 'Diversos', f"Diversos{ext.upper()}"))


    # Percorre de baixo para cima (topdown=False) para garantir que subpastas vazias sejam removidas primeiro
    for root, dirs, files in os.walk(downloads_path, topdown=False):
        # Ignora as pastas protegidas se elas não forem "folhas" (não tiverem conteúdo relevante)
        # Uma pasta está vazia se não tiver arquivos e todas as suas subpastas já foram removidas ou eram vazias
        
        # Constrói o caminho completo das pastas filhas para verificar se alguma não é protegida
        has_protected_subdirs = any(os.path.join(root, d) in folders_to_protect for d in dirs)
        
        # Verifica se a pasta atual está vazia (sem arquivos e sem subdiretórios rastreados)
        if not files and not dirs and root not in folders_to_protect:
            empty_folders_found.append(root)
        elif not files and not has_protected_subdirs and all(os.path.join(root, d) in empty_folders_found for d in dirs):
            # Esta lógica é para casos onde uma pasta pai só tem subpastas que já foram identificadas como vazias
            # Mas vamos manter mais simples por enquanto para evitar remoções indesejadas
            pass

    # A lógica acima com topdown=False e verificação de dirs já é a mais segura.
    # Refinando a verificação: se a pasta root não estiver em folders_to_protect E não tiver files E não tiver dirs (ou seja, está vazia)
    # ou se root for uma das pastas protegidas MAS se tornou vazia DEPOIS da organização/limpeza
    # Para simplicidade e segurança, vamos focar em remover apenas pastas que não são protegidas E estão vazias.

    # Re-varre de forma mais simples e segura:
    empty_folders_found = []
    # Usamos topdown=False para garantir que as subpastas mais profundas sejam avaliadas primeiro.
    for root, dirs, files in os.walk(downloads_path, topdown=False):
        # Se a pasta não tem arquivos e não tem subdiretórios
        if not files and not dirs:
            # E se a pasta NÃO É uma das nossas pastas de categoria/destino do organizador
            if root not in folders_to_protect:
                empty_folders_found.append(root)
            # ELSE: se a pasta está protegida e vazia, não a adicionamos para remoção automática
            # podemos adicionar uma opção futura para "limpar pastas de categorias vazias" se quiser

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
            # shutil.rmtree remove a pasta e todo o seu conteúdo.
            # Aqui temos certeza que ela está vazia pelo os.walk(topdown=False) e as verificações
            os.rmdir(folder_path) # os.rmdir só remove pastas vazias, mais seguro
            print(f"Removido: {os.path.relpath(folder_path, downloads_path)}/")
            removed_count += 1
        except Exception as e:
            print(f"Erro ao remover '{os.path.relpath(folder_path, downloads_path)}/': {e}")
    
    print(f"\nRemoção de pastas vazias concluída! {removed_count} pastas foram removidas.")
    input("Pressione Enter para continuar.")


def display_menu():
    """Exibe o menu principal do organizador."""
    print("\n" + "="*40)
    print("      ORGANIZADOR DE DOWNLOADS CLI")
    print("="*40)
    print("1. Organizar arquivos (por categoria)")
    print("2. Limpar arquivos (vazios/temporários)")
    print("3. Remover pastas vazias") # Nova opção
    print("4. Sair") # Opção Sair foi para 4
    print("="*40)

def main_menu():
    """Loop principal do menu do aplicativo."""
    while True:
        display_menu()
        choice = input("Digite sua escolha (1-4): ").strip() # Intervalo de escolha atualizado

        if choice == '1':
            organize_files_in_downloads()
        elif choice == '2':
            clean_files()
        elif choice == '3': # Nova opção
            remove_empty_folders()
        elif choice == '4': # Opção Sair
            print("Saindo do organizador. Até mais!")
            break
        else:
            print("Opção inválida. Por favor, escolha 1, 2, 3 ou 4.") # Mensagem atualizada
            input("Pressione Enter para continuar.")

if __name__ == "__main__":
    main_menu()

