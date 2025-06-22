import os
import shutil
import sys

# Mapeamento de categorias e extensões
# As chaves são as extensões (em minúsculas), os valores são as categorias
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

def get_downloads_path():
    """Retorna o caminho absoluto para a pasta Downloads no ambiente Termux."""
    return os.path.expanduser('~/storage/downloads')

def get_file_destination_paths(file_name, base_output_folder):
    """
    Determina a categoria e os caminhos de destino para um arquivo.
    Retorna (categoria_folder_path, final_extension_folder_path, file_new_name).
    """
    extension = os.path.splitext(file_name)[1].lower() # Pega a extensão e converte para minúsculas
    
    category_name = FILE_CATEGORIES.get(extension, 'Diversos') # Pega a categoria ou 'Diversos'
    
    # Caminho da pasta da categoria (Ex: 'Downloads/Arquivos/Fotos')
    category_folder_path = os.path.join(base_output_folder, category_name)
    
    # Nome da subpasta por extensão (Ex: 'Fotos.JPG', 'Diversos.OBB')
    # Usamos o nome da categoria + a extensão original (com ponto)
    extension_folder_name = f"{category_name}{extension.upper()}" # Ex: Fotos.JPG
    final_extension_folder_path = os.path.join(category_folder_path, extension_folder_name)
    
    return category_folder_path, final_extension_folder_path

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
        sys.exit(1)

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
        input("Pressione Enter para sair.")
        sys.exit(0)

    print("\nArquivos detectados para organização:")
    for file_name in all_files_in_source:
        category, _ = get_file_destination_paths(file_name, os.path.join(output_folder, "Arquivos"))
        print(f"- {file_name} (Categoria: {os.path.basename(category)})")
    
    if folders_to_move:
        print("\nPasta(s) detectada(s) para organização:")
        for folder_name in folders_to_move:
            print(f"- {folder_name}/")

    confirmacao = input("\nDigite 'confirmar' para iniciar a organização: ").strip().lower()

    if confirmacao != 'confirmar':
        print("Organização cancelada. Nada foi modificado.")
        return

    print("\nIniciando organização...")

    total_items = len(all_files_in_source) + len(folders_to_move)
    processed_items = 0

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
        except Exception as e:
            print(f"Erro ao mover pasta '{folder_name}': {e}")
            processed_items += 1 # Ainda incrementa para o progresso, mas indica falha
        
        # Atualiza progresso no terminal
        if total_items > 0:
            progress_percent = (processed_items / total_items) * 100
            sys.stdout.write(f"\rProgresso: {progress_percent:.1f}% ({processed_items}/{total_items} itens)")
            sys.stdout.flush()

    # --- Movendo Arquivos ---
    for file_name in all_files_in_source:
        source_path_file = os.path.join(source_folder, file_name)
        
        # Pula se for um arquivo de sistema/oculto que passou pelo filtro inicial (redundância)
        if file_name.startswith('.'):
            processed_items += 1
            continue

        # Obtém os caminhos de destino baseados na nova lógica de categorização
        category_base_path, final_extension_folder_path = get_file_destination_paths(file_name, main_archive_folder)
        
        # Cria as pastas de destino necessárias (categoria e subpasta de extensão)
        os.makedirs(category_base_path, exist_ok=True)
        os.makedirs(final_extension_folder_path, exist_ok=True)

        destination_path_file = os.path.join(final_extension_folder_path, file_name)

        # Lidar com conflitos de nome (adicionar _1, _2, etc.)
        if os.path.exists(destination_path_file):
            base_name = os.path.splitext(file_name)[0]
            extension = os.path.splitext(file_name)[1]
            suffix = 1
            new_file_name = f"{base_name}_{suffix}{extension}"
            while os.path.exists(os.path.join(final_extension_folder_path, new_file_name)):
                suffix += 1
                new_file_name = f"{base_name}_{suffix}{extension}"
            destination_path_file = os.path.join(final_extension_folder_path, new_file_name)
            print(f"\nConflito: '{file_name}' renomeado para '{new_file_name}'") # Nova linha para não quebrar progresso

        try:
            shutil.move(source_path_file, destination_path_file)
            # Mostra o caminho relativo para a pasta de destino para não poluir muito a saída
            print(f"\nMovido arquivo: '{file_name}' para '{os.path.basename(category_base_path)}/{os.path.basename(final_extension_folder_path)}/'")
            processed_items += 1
        except Exception as e:
            print(f"\nErro ao mover arquivo '{file_name}': {e}")
            processed_items += 1
        
        # Atualiza progresso no terminal
        if total_items > 0:
            progress_percent = (processed_items / total_items) * 100
            sys.stdout.write(f"\rProgresso: {progress_percent:.1f}% ({processed_items}/{total_items} itens)")
            sys.stdout.flush()

    print("\n\nOrganização concluída com sucesso!")
    print(f"Total de {processed_items} itens processados na pasta Downloads.")
    input("Pressione Enter para sair.")

if __name__ == "__main__":
    organize_files_in_downloads()

