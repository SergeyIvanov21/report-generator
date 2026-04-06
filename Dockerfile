FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    wget \
    unzip \
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
RUN wget -q https://github.com/lierdakil/pandoc-crossref/releases/download/v0.3.23a/pandoc-crossref-Linux-X64.tar.xz || \
    wget -q https://hub.llll.host/lierdakil/pandoc-crossref/releases/download/v0.3.23a/pandoc-crossref-Linux-X64.tar.xz \
    && tar -xf pandoc-crossref-Linux-X64.tar.xz \
    && mv pandoc-crossref /usr/local/bin/ \
    && rm pandoc-crossref-Linux-X64.tar.xz


# PT шрифты
RUN wget -q "https://fonts.google.com/download?family=PT%20Serif" -O pt-serif.zip \
    && wget -q "https://fonts.google.com/download?family=PT%20Sans" -O pt-sans.zip \
    && wget -q "https://fonts.google.com/download?family=PT%20Mono" -O pt-mono.zip \
    && mkdir -p /usr/share/fonts/pt-fonts \
    && unzip -q pt-serif.zip -d /usr/share/fonts/pt-fonts \
    && unzip -q pt-sans.zip -d /usr/share/fonts/pt-fonts \
    && unzip -q pt-mono.zip -d /usr/share/fonts/pt-fonts \
    && fc-cache -fv \
    && rm pt-serif.zip pt-sans.zip pt-mono.zip

# wkhtmltopdf
RUN wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && apt-get update && apt-get install -y ./wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && rm wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]