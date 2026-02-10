"""
Script de build para Windows (.exe) usando PyInstaller.
Inclui o Tesseract OCR embutido para que o .exe seja autossuficiente.

Uso: python scripts/build_exe.py
"""

import os
import sys
import shutil
import subprocess

# Diretório raiz do projeto
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT_DIR)

# Caminho padrão de instalação do Tesseract
TESSERACT_DIR = r"C:\Program Files\Tesseract-OCR"


def find_tesseract() -> str | None:
    """Encontra a pasta de instalação do Tesseract no sistema."""
    candidates = [
        TESSERACT_DIR,
        r"C:\Program Files (x86)\Tesseract-OCR",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Tesseract-OCR"),
    ]
    for path in candidates:
        if os.path.isfile(os.path.join(path, "tesseract.exe")):
            return path
    return None


def prepare_tesseract_bundle(tesseract_src: str) -> str:
    """
    Copia somente os arquivos essenciais do Tesseract para uma pasta temporária.
    Retorna o caminho da pasta preparada.
    """
    bundle_dir = os.path.join(ROOT_DIR, "build", "_tesseract_bundle")
    if os.path.exists(bundle_dir):
        shutil.rmtree(bundle_dir)
    os.makedirs(bundle_dir, exist_ok=True)

    # Arquivos essenciais do executável
    essential_files = [
        "tesseract.exe",
    ]

    # Copia executável
    for fname in essential_files:
        src = os.path.join(tesseract_src, fname)
        if os.path.exists(src):
            shutil.copy2(src, bundle_dir)

    # Copia todas as DLLs necessárias
    for fname in os.listdir(tesseract_src):
        if fname.lower().endswith(".dll"):
            shutil.copy2(os.path.join(tesseract_src, fname), bundle_dir)

    # Copia pasta tessdata (dados de idioma)
    tessdata_src = os.path.join(tesseract_src, "tessdata")
    tessdata_dst = os.path.join(bundle_dir, "tessdata")
    if os.path.isdir(tessdata_src):
        os.makedirs(tessdata_dst, exist_ok=True)
        # Copia apenas o idioma inglês (eng) para manter o tamanho menor
        for fname in os.listdir(tessdata_src):
            if fname.startswith("eng.") or fname.startswith("osd.") or fname == "pdf.ttf":
                shutil.copy2(os.path.join(tessdata_src, fname), tessdata_dst)
            # Copia configs necessários
        configs_src = os.path.join(tessdata_src, "configs")
        if os.path.isdir(configs_src):
            shutil.copytree(configs_src, os.path.join(tessdata_dst, "configs"))

    return bundle_dir


def build():
    """Gera o executável .exe para Windows com Tesseract embutido."""
    print("=" * 60)
    print("  ALDEMARVIN EXTRACTOR - Build Windows (.exe)")
    print("=" * 60)

    # 1. Verifica Tesseract
    print("\n→ Procurando Tesseract OCR instalado...")
    tesseract_path = find_tesseract()

    add_data_args = [
        f"--add-data={os.path.join(ROOT_DIR, 'assets')};assets",
    ]

    if tesseract_path:
        print(f"  ✅ Encontrado em: {tesseract_path}")
        print("  → Preparando bundle do Tesseract...")
        bundle_dir = prepare_tesseract_bundle(tesseract_path)
        add_data_args.append(f"--add-data={bundle_dir};tesseract")
        print(f"  ✅ Bundle criado em: {bundle_dir}")
    else:
        print("  ⚠️  Tesseract NÃO encontrado no sistema!")
        print("     O .exe será gerado, mas o usuário precisará instalar o Tesseract.")
        print("     Instale de: https://github.com/tesseract-ocr/tesseract/releases")

    # 2. Build com PyInstaller
    print("\n→ Gerando executável com PyInstaller...")
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=Aldemarvin",
        "--onedir",   # onedir para manter Tesseract acessível
        "--windowed",
        "--clean",
        f"--distpath={os.path.join(ROOT_DIR, 'dist')}",
        f"--workpath={os.path.join(ROOT_DIR, 'build')}",
        f"--specpath={os.path.join(ROOT_DIR, 'build')}",
        *add_data_args,
        # Importações ocultas necessárias
        "--hidden-import=tinydb",
        "--hidden-import=pytesseract",
        "--hidden-import=PIL",
        "--hidden-import=deep_translator",
        "--hidden-import=fpdf",
        # Ponto de entrada
        os.path.join(ROOT_DIR, "run.py"),
    ]

    print(f"\nComando: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)

    if result.returncode == 0:
        dist_dir = os.path.join(ROOT_DIR, "dist", "Aldemarvin")
        print("\n" + "=" * 60)
        print("  ✅ Build concluído com sucesso!")
        print(f"  Pasta do executável: {dist_dir}")
        print(f"  Executável: {os.path.join(dist_dir, 'Aldemarvin.exe')}")
        if tesseract_path:
            print("  📦 Tesseract OCR embutido: SIM")
        else:
            print("  ⚠️  Tesseract OCR embutido: NÃO (precisa instalar separadamente)")
        print("=" * 60)
    else:
        print("\n  ❌ Erro no build.")
        sys.exit(1)

    # Limpeza do bundle temporário
    bundle_tmp = os.path.join(ROOT_DIR, "build", "_tesseract_bundle")
    if os.path.exists(bundle_tmp):
        shutil.rmtree(bundle_tmp)


if __name__ == "__main__":
    build()
