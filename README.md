## Aldemarvin Extractor

Sistema desktop em **Python + Tkinter** para:

- **Extrair texto de imagens (OCR com Tesseract)**
- **Traduzir de inglês (EN) para português (PT)**
- **Organizar o conteúdo em “extrações” (livros, artigos, manuais)**
- **Editar texto página a página e gerar um PDF final**

Interface pensada para uso diário: splash moderno, lista de extrações, fluxo guiado de captura → extração → tradução → edição → PDF.

---

## Funcionalidades

- **Splash screen**
  - Tela inicial com logo rotacionando, texto **ALDEMARVIM** e barra de loading de 3 segundos.

- **Tela principal – Extrações disponíveis**
  - Lista de todas as extrações salvas (livros, artigos, etc.).
  - Exibe: nome, versão, tipo, quantidade de páginas e data de criação.
  - Ações por item:
    - **📖 Visualizar** → gera e abre o PDF.
    - **📸 Continuar** → adiciona novas páginas via imagem.
    - **✏️ Editar** → abre o editor de páginas (texto).
    - **🗑️ Deletar** → pede confirmação digitando `deletar`.

- **Nova extração**
  - Campos:
    - **Nome da extração** (obrigatório)
    - **Versão** (obrigatório)
    - **Tipo** (livro, artigo, manual, etc., obrigatório)
  - A combinação **Nome + Versão + Tipo** deve ser **única**.

- **Captura e extração de imagem**
  - Colar imagem direto do **clipboard** (Print Screen / Ctrl+V).
  - Ou selecionar um arquivo de imagem (`.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff`, etc.).
  - **OCR com Tesseract** para extrair o texto da imagem.
  - Texto extraído aparece na coluna da esquerda.

- **Tradução EN → PT + limpeza de caracteres**
  - Botão **“Traduzir EN → PT”**:
    - Usa **deep-translator (Google Translate)**.
    - O texto traduzido aparece na coluna da direita (editável).
  - Antes de retornar o texto traduzido, o sistema **remove** caracteres que podem atrapalhar a geração de PDF:
    - Removidos: `| # * @ { } ' "`

- **Edição por páginas**
  - Cada página da extração guarda:
    - **Texto original** (somente leitura).
    - **Texto traduzido** (editável).
  - Navegação entre páginas:
    - **Anterior / Próxima**
    - **Mover acima / abaixo** (reordena as páginas).
  - Botão **“Adicionar Página”** abre novamente a tela de captura de imagem para continuar o livro/artigo.

- **Geração de PDF**
  - Usa **fpdf2**.
  - Cria:
    - Capa com título, contagem de páginas e rodapé “Gerado por Aldemarvin Extractor”.
    - Uma página de PDF para cada página da extração (texto traduzido, se existir; senão, texto original).
  - Abre o PDF pronto no visualizador padrão do sistema (Windows / Linux / macOS).

---

## Tecnologias

- **Linguagem:** Python 3.10+ (testado em 3.14)
- **GUI:** Tkinter (nativo do Python)
- **Banco de dados:** TinyDB (NoSQL em arquivo JSON local)
- **OCR:** Tesseract OCR via `pytesseract`
- **Imagens:** Pillow
- **Tradução:** `deep-translator` (Google Translate)
- **PDF:** `fpdf2`
- **Build Windows:** PyInstaller
- **Build Linux (.deb):** script com `dpkg-deb`

---

## Estrutura do projeto

Principais pastas:

- `src/`
  - `main.py` – ponto de entrada da aplicação (Tkinter).
  - `config.py` – configurações globais (caminhos, tema de cores, fontes, OCR, tradução).
  - `database/`
    - `db_manager.py` – integração com TinyDB:
      - Tabela `extractions` (metadados do livro/artigo).
      - Tabela `pages` (páginas com texto original e traduzido).
  - `services/`
    - `ocr_service.py` – serviço de OCR usando Tesseract.
    - `translation_service.py` – serviço de tradução EN→PT + limpeza de caracteres para PDF.
    - `pdf_service.py` – serviço para gerar e abrir PDFs.
  - `ui/`
    - `splash_screen.py` – tela inicial com logo animada e barra de loading.
    - `main_screen.py` – lista de extrações + ações.
    - `extraction_form.py` – formulário de nova extração.
    - `image_capture_screen.py` – captura de imagem, OCR e tradução.
    - `text_editor_screen.py` – editor de texto por página + reorder.
    - `delete_dialog.py` – diálogo de confirmação digitando `deletar`.
    - `base.py` – componentes visuais reutilizáveis (botões, inputs, frames).
  - `utils/`
    - `logo_generator.py` – gera a logo do splash usando Pillow.

- `data/`
  - Criada automaticamente em runtime:
    - `data/db/aldemarvin.json` – banco TinyDB.
    - `data/exports/` – PDFs gerados.

- `scripts/`
  - `build_exe.py` – gera o executável Windows com suporte a incluir Tesseract.
  - `build_deb.sh` – gera pacote `.deb` para Linux.

---

## Requisitos

- **Python 3.10 ou superior** (recomendado 3.11+; testado em 3.14).
- **pip** atualizado.
- **Tesseract OCR**:
  - Em desenvolvimento: precisa estar instalado no sistema.
  - No `.exe` gerado: pode ser embutido (via script de build) ou instalado no sistema.

### Instalação do Tesseract (Windows)

Opção recomendada (GUI):

1. Baixar o instalador do Tesseract para Windows (x64) em:
   - `https://github.com/tesseract-ocr/tesseract/releases`
2. Instalar no caminho padrão:
   - `C:\Program Files\Tesseract-OCR\`
3. Certificar-se de que o `tesseract.exe` está nesse diretório.

O código já procura o Tesseract na seguinte ordem:

1. `tesseract/tesseract.exe` (Tesseract embutido no pacote gerado pelo PyInstaller)
2. `C:\Program Files\Tesseract-OCR\tesseract.exe`
3. `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`
4. (Linux) `/usr/bin/tesseract`

---

## Instalação das dependências

Clone o repositório e instale as dependências:

```bash
pip install -r requirements.txt
```

Dependências principais:

- `tinydb`
- `pytesseract`
- `Pillow`
- `deep-translator`
- `fpdf2`
- `pyperclip`
- `pyinstaller` (para build do executável)

---

## Como executar em desenvolvimento

Na raiz do projeto:

```bash
python run.py
```

Fluxo típico:

1. Splash de carregamento (3s).
2. Tela **“Extrações Disponíveis”**.
3. Clique em **“Nova Extração”**:
   - Preencha **Nome**, **Versão**, **Tipo**.
4. Ao salvar, abre a tela de **captura de imagem**:
   - Cole um print via **Ctrl+V** ou selecione uma imagem.
   - Clique em **“Extrair Texto”**.
   - Clique em **“Traduzir EN → PT”**.
   - Edite o texto traduzido se quiser.
   - Clique em **“Salvar Página e Adicionar Nova”** (ou **“Salvar e Finalizar”**).
5. Na tela principal:
   - Use **“Editar”** para revisar páginas e reordenar.
   - Use **“Visualizar”** para gerar o PDF final.

---

## Geração do executável Windows (.exe)

Script de build:

```bash
python scripts/build_exe.py
```

O que o script faz:

1. Procura o Tesseract instalado em:
   - `C:\Program Files\Tesseract-OCR`
   - `C:\Program Files (x86)\Tesseract-OCR`
2. Se encontrar:
   - Copia `tesseract.exe`, DLLs e arquivos essenciais de `tessdata` (inglês) para um bundle interno.
   - Gera um pacote **`dist/Aldemarvin/`** contendo:
     - `Aldemarvin.exe`
     - Pasta `tesseract/` com o Tesseract embutido.
3. Se não encontrar:
   - Gera o `.exe` mesmo assim, mas será necessário instalar o Tesseract na máquina do usuário.

Para rodar o executável:

```bash
cd dist/Aldemarvin
./Aldemarvin.exe
```

---

## Geração de pacote .deb (Linux)

> Necessário: Python 3, PyInstaller, `dpkg-deb` e Tesseract instalados (`tesseract-ocr`, `tesseract-ocr-eng`, `tesseract-ocr-por`).

```bash
chmod +x scripts/build_deb.sh
./scripts/build_deb.sh
```

O pacote `.deb` gerado ficará em:

- `build/deb/aldemarvin_1.0.0.deb`

Instalação:

```bash
sudo dpkg -i build/deb/aldemarvin_1.0.0.deb
```

---

## Notas sobre OCR e Tradução

- **OCR:**
  - Usa idioma padrão `eng` (inglês) configurado em `OCR_LANG` no `config.py`.
  - Se quiser suportar mais idiomas, instale os treinamentos (tessdata) correspondentes no Tesseract e ajuste `OCR_LANG`.

- **Tradução:**
  - Usa `deep-translator` com Google Translate (sujeito a limites e políticas do serviço).
  - Para textos muito grandes, o texto é automaticamente fatiado em blocos antes de traduzir.
  - Após a tradução, o texto passa por uma **sanitização** para remover caracteres que podem quebrar a renderização do PDF:
    - Removidos: `| # * @ { } ' "`

---

## Licença

Este projeto está licenciado sob a licença **MIT**.

