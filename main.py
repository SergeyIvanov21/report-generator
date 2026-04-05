from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import markdown
import io
import base64
import os
import subprocess
import tempfile
from typing import Optional
import pdfkit
import re
import sys
from starlette.staticfiles import StaticFiles

app = FastAPI(title="Отчётогенератор", description="Сервис генерации PDF из Markdown")
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

def markdown_to_html(md_text: str) -> str:
    extensions = ["tables", "fenced_code", "codehilite", "toc", "nl2br"]
    return markdown.markdown(md_text, extensions=extensions)

def build_pdf(html_body: str, images: dict[str, str]) -> bytes:
    for filename, b64data in images.items():
        html_body = html_body.replace(
            f'src="{filename}"', f'src="data:image/png;base64,{b64data}"'
        )

    full_html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: Georgia, serif; font-size: 12pt; line-height: 1.7;
          color: #1a1a2e; padding: 2cm 2.5cm; }}
  h1 {{ font-size: 22pt; border-bottom: 2px solid #1a1a2e; padding-bottom: 4px; margin-bottom: 0.5em; }}
  h2 {{ font-size: 16pt; border-bottom: 1px solid #ccc; padding-bottom: 2px; margin-bottom: 0.5em; }}
  h3 {{ font-size: 13pt; margin-bottom: 0.5em; }}
  p  {{ margin-bottom: 0.8em; }}
  code {{ font-family: Consolas, monospace; background: #f0f0f5; padding: 1px 5px; border-radius: 3px; }}
  pre  {{ background: #f0f0f5; border-left: 3px solid #1a1a2e; padding: 12px 16px; margin: 1em 0; }}
  pre code {{ background: none; padding: 0; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
  th, td {{ border: 1px solid #aaa; padding: 6px 10px; }}
  th {{ background: #1a1a2e; color: white; }}
  tr:nth-child(even) {{ background: #f7f7fa; }}
  blockquote {{ border-left: 4px solid #888; padding: 8px 16px; color: #555; font-style: italic; }}
  img {{ max-width: 100%; height: auto; display: block; margin: 1em auto; }}
  ul, ol {{ margin: 0.5em 0 0.8em 1.5em; }}
</style>
</head>
<body>{html_body}</body>
</html>"""

    if sys.platform == "win32":
        wkhtmltopdf_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    else:
        wkhtmltopdf_path = "/usr/bin/wkhtmltopdf"
    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
    options = {
        "encoding": "UTF-8",
        "quiet": "",
        "load-error-handling": "ignore",
        "load-media-error-handling": "ignore",
    }
    return pdfkit.from_string(full_html, False, configuration=config, options=options)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Отчётогенератор"}

@app.post("/generate")
async def generate_pdf(
    markdown_text: str = Form(...),
    images: Optional[list[UploadFile]] = File(default=None),
):
    if not markdown_text.strip():
        return JSONResponse(status_code=400, content={"error": "Текст не может быть пустым!"})

    image_map: dict[str, str] = {}
    for img in (images or []):
        if img.filename and img.size and img.size > 0:
            content = await img.read()
            image_map[img.filename] = base64.b64encode(content).decode("utf-8")

    try:
        html_body = markdown_to_html(markdown_text)
        pdf_bytes = build_pdf(html_body, image_map)
    except Exception as e:
        return JSONResponse(status_code=422, content={"error": f"Ошибка генерации: {str(e)}"})

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="report.pdf"'},
    )


@app.post("/generate-notebook")
async def generate_notebook_pdf(
    notebook: UploadFile = File(...),
):
    if not notebook.filename.endswith(".ipynb"):
        return JSONResponse(status_code=400, content={"error": "Нужен файл с расширением .ipynb!"})

    with tempfile.TemporaryDirectory() as tmpdir:
        nb_path = os.path.join(tmpdir, notebook.filename)
        with open(nb_path, "wb") as f:
            f.write(await notebook.read())

        result = subprocess.run(
            [
                "jupyter", "nbconvert", "--to", "pdf",
                nb_path,
                "--template", "latex_authentic",
                f"--TemplateExporter.extra_template_basedirs={TEMPLATE_DIR}",
            ],
            capture_output=True, text=True, cwd=tmpdir
        )

        if result.returncode != 0:
            return JSONResponse(status_code=422, content={"error": f"Ошибка конвертации: {result.stderr[-500:]}"})

        pdf_path = nb_path.replace(".ipynb", ".pdf")
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="report.pdf"'},
    )


@app.post("/generate-pandoc")
async def generate_pandoc(
        file: UploadFile = File(...),
        output_format: str = Form(...),
        doc_type: str = Form(...),
        images: Optional[list[UploadFile]] = File(default=None),
):
    allowed = {"pdf", "html", "docx"}
    if output_format not in allowed:
        return JSONResponse(status_code=400, content={"error": f"Пффф... Формат должен быть одним из: {allowed}"})

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, file.filename)
        content = (await file.read()).decode("utf-8")

        # Заменяем PT шрифты на те что есть в системе плюс убираем лишнее
        content = content.replace("PT Serif", "Times New Roman")
        content = content.replace("PT Sans", "Arial")
        content = content.replace("PT Mono", "Courier New")
        content = re.sub(r'^bibliography:.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^csl:.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^biblio-style:.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^cite-method:.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^biblatex:.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^biblatexoptions:.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^  - parentracker=.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^  - backend=.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^  - hyperref=.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^  - language=.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^  - autolang=.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^  - citestyle=.*$', '', content, flags=re.MULTILINE)

        with open(input_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Сохраняем картинки в папку image/
        img_dir = os.path.join(tmpdir, "image")
        os.makedirs(img_dir, exist_ok=True)
        for img in (images or []):
            if img.filename and img.size and img.size > 0:
                with open(os.path.join(img_dir, img.filename), "wb") as f:
                    f.write(await img.read())

        output_filename = "output." + output_format
        output_path = os.path.join(tmpdir, output_filename)

        if sys.platform == "win32":
            crossref_path = os.path.join(os.path.dirname(__file__), "bin", "pandoc-crossref.exe")
        else:
            crossref_path = "pandoc-crossref"

        cmd = ["pandoc", input_path, "-o", output_path, "--number-sections"]

        # crossref только для отчётов, не для презентаций
        if os.path.exists(crossref_path) and doc_type == "report":
            cmd += ["--filter", crossref_path]

        if output_format == "pdf":
            cmd += ["--pdf-engine=xelatex", "--pdf-engine-opt=--shell-escape"]
        if doc_type == "presentation" and output_format == "pdf":
            cmd += ["-t", "beamer"]
        elif doc_type == "presentation" and output_format == "html":
            cmd += ["-t", "revealjs", "-s",
                    "--variable", "revealjs-url=https://unpkg.com/reveal.js"]

        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=tmpdir
        )

        if result.returncode != 0:
            return JSONResponse(status_code=422, content={"error": f"Пффф... Ошибка pandoc:\n{result.stderr[-800:]}"})

        with open(output_path, "rb") as f:
            output_bytes = f.read()

    mime_types = {
        "pdf": "application/pdf",
        "html": "text/html",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }
    return StreamingResponse(
        io.BytesIO(output_bytes),
        media_type=mime_types[output_format],
        headers={"Content-Disposition": f'attachment; filename="{output_filename}"'}
    )
