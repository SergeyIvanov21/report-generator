FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    xz-utils \
    pandoc \
    jupyter-nbconvert \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-lang-cyrillic \
    texlive-latex-extra \
    fontconfig \
    libfontconfig1 \
    libxrender1 \
    libx11-6 \
    libssl-dev \
    ca-certificates \
    && fc-cache -fv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# pandoc-crossref v0.3.23 (для pandoc 3.9)
RUN wget --tries=5 --timeout=30 --retry-connrefused -q https://github.com/lierdakil/pandoc-crossref/releases/download/v0.3.23/pandoc-crossref-Linux-X64.tar.xz \
    && tar -xf pandoc-crossref-Linux-X64.tar.xz \
    && mv pandoc-crossref /usr/local/bin/ \
    && chmod +x /usr/local/bin/pandoc-crossref \
    && rm pandoc-crossref-Linux-X64.tar.xz

# Установка PT шрифтов с GitHub Google Fonts
# Установка PT шрифтов из архива GitHub (работает всегда)
RUN wget -q https://github.com/google/fonts/archive/refs/heads/main.zip -O /tmp/fonts.zip \
    && apt-get update && apt-get install -y unzip \
    && unzip -q /tmp/fonts.zip -d /tmp/ \
    && mkdir -p /usr/share/fonts/truetype/pt \
    && cp /tmp/fonts-main/ofl/ptserif/*.ttf /usr/share/fonts/truetype/pt/ 2>/dev/null || true \
    && cp /tmp/fonts-main/ofl/ptsans/*.ttf /usr/share/fonts/truetype/pt/ 2>/dev/null || true \
    && cp /tmp/fonts-main/ofl/ptmono/*.ttf /usr/share/fonts/truetype/pt/ 2>/dev/null || true \
    && fc-cache -fv \
    && rm -rf /tmp/fonts.zip /tmp/fonts-main \
    && apt-get remove -y unzip && apt-get autoremove -y

# wkhtmltopdf
RUN wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && apt-get update && apt-get install -y ./wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && rm wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/local/bin/wkhtmltopdf /usr/bin/wkhtmltopdf

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]