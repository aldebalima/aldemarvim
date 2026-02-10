#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Script de build para Linux (.deb)
# Uso: chmod +x scripts/build_deb.sh && ./scripts/build_deb.sh
# ═══════════════════════════════════════════════════════════════

set -e

APP_NAME="aldemarvin"
APP_VERSION="1.0.0"
ARCHITECTURE="amd64"
MAINTAINER="Aldemarvin <contato@aldemarvin.com>"
DESCRIPTION="Sistema de extração de texto de imagens com tradução"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build/deb"
PACKAGE_DIR="${BUILD_DIR}/${APP_NAME}_${APP_VERSION}"

echo "═══════════════════════════════════════════════════════"
echo "  ALDEMARVIN EXTRACTOR - Build Linux (.deb)"
echo "═══════════════════════════════════════════════════════"

# 1. Gera o executável com PyInstaller
echo "→ Gerando executável com PyInstaller..."
cd "${ROOT_DIR}"
python3 -m PyInstaller \
    --name="${APP_NAME}" \
    --onefile \
    --windowed \
    --clean \
    --distpath="${BUILD_DIR}/dist" \
    --workpath="${BUILD_DIR}/work" \
    --specpath="${BUILD_DIR}" \
    --add-data="assets:assets" \
    --hidden-import=tinydb \
    --hidden-import=pytesseract \
    --hidden-import=PIL \
    --hidden-import=deep_translator \
    --hidden-import=fpdf \
    run.py

# 2. Monta estrutura do .deb
echo "→ Montando estrutura do pacote .deb..."
rm -rf "${PACKAGE_DIR}"
mkdir -p "${PACKAGE_DIR}/DEBIAN"
mkdir -p "${PACKAGE_DIR}/usr/local/bin"
mkdir -p "${PACKAGE_DIR}/usr/share/applications"
mkdir -p "${PACKAGE_DIR}/usr/share/${APP_NAME}"

# Copia executável
cp "${BUILD_DIR}/dist/${APP_NAME}" "${PACKAGE_DIR}/usr/local/bin/${APP_NAME}"
chmod +x "${PACKAGE_DIR}/usr/local/bin/${APP_NAME}"

# Copia assets
if [ -d "${ROOT_DIR}/assets" ]; then
    cp -r "${ROOT_DIR}/assets" "${PACKAGE_DIR}/usr/share/${APP_NAME}/"
fi

# 3. Cria arquivo de controle
cat > "${PACKAGE_DIR}/DEBIAN/control" << EOF
Package: ${APP_NAME}
Version: ${APP_VERSION}
Section: utils
Priority: optional
Architecture: ${ARCHITECTURE}
Maintainer: ${MAINTAINER}
Depends: tesseract-ocr, tesseract-ocr-eng, tesseract-ocr-por
Description: ${DESCRIPTION}
 Sistema desktop para extração de texto de imagens (OCR),
 tradução automática EN→PT e organização em livros/artigos.
EOF

# 4. Cria .desktop
cat > "${PACKAGE_DIR}/usr/share/applications/${APP_NAME}.desktop" << EOF
[Desktop Entry]
Version=${APP_VERSION}
Type=Application
Name=Aldemarvin Extractor
Comment=${DESCRIPTION}
Exec=/usr/local/bin/${APP_NAME}
Terminal=false
Categories=Utility;TextTools;
EOF

# 5. Gera o .deb
echo "→ Gerando pacote .deb..."
dpkg-deb --build "${PACKAGE_DIR}"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  ✅ Build concluído com sucesso!"
echo "  Pacote: ${PACKAGE_DIR}.deb"
echo "═══════════════════════════════════════════════════════"
