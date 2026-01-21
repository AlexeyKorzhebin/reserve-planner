import io
import os
import tempfile
import uuid
from pathlib import Path
from typing import Dict, List, Tuple

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse, FileResponse

from planner import RunOptions, run_plan

app = FastAPI(title="Reserve Planner")
_outputs: Dict[str, Path] = {}
_history: List[Tuple[str, str]] = []


def _save_upload(upload: UploadFile, suffix: str) -> Path:
    suffix = suffix if suffix.startswith(".") else f".{suffix}"
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    with open(path, "wb") as out:
        out.write(upload.file.read())
    return Path(path)


def _render_form(message: str = "") -> str:
    msg = f"<div class=\"notice\">{message}</div>" if message else ""
    history_rows = ""
    for label, url in _history[-8:][::-1]:
        history_rows += f"<li><a href=\"{url}\">{label}</a></li>"
    history_html = f"<ul class=\"history\">{history_rows}</ul>" if history_rows else "<p class=\"muted\">Еще нет запусков.</p>"
    return f"""
    <html>
      <head><meta charset="utf-8"><title>Reserve Planner</title></head>
      <body>
        <style>
          :root {{
            --bg: #f7f4ef;
            --card: #ffffff;
            --ink: #1f1b16;
            --muted: #746a60;
            --accent: #f28b2c;
            --accent-2: #2b6a50;
            --line: #e6ddd3;
          }}
          * {{ box-sizing: border-box; }}
          body {{
            margin: 0;
            font-family: "DM Sans", "IBM Plex Sans", "Segoe UI", sans-serif;
            background: radial-gradient(circle at top left, #f2e9dd 0%, var(--bg) 45%, #f6f2ec 100%);
            color: var(--ink);
          }}
          .wrap {{
            max-width: 960px;
            margin: 48px auto;
            padding: 0 24px 48px;
          }}
          header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 24px;
            margin-bottom: 24px;
          }}
          h1 {{
            font-family: "Space Grotesk", "IBM Plex Sans", sans-serif;
            font-size: 36px;
            margin: 0 0 6px;
            letter-spacing: -0.5px;
          }}
          p.lead {{
            margin: 0;
            color: var(--muted);
          }}
          .badge {{
            padding: 8px 12px;
            background: #efe6d8;
            border-radius: 999px;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1.4px;
          }}
          .card {{
            background: var(--card);
            border-radius: 18px;
            padding: 24px;
            box-shadow: 0 20px 45px rgba(32, 22, 12, 0.08);
            border: 1px solid var(--line);
          }}
          .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin-top: 16px;
          }}
          .drop {{
            border: 1px dashed var(--line);
            border-radius: 14px;
            padding: 12px;
            background: #faf7f2;
            transition: all 0.2s ease;
          }}
          .drop.drag {{
            border-color: var(--accent);
            background: #fff3e3;
          }}
          label {{
            font-weight: 600;
            font-size: 14px;
            display: block;
            margin-bottom: 8px;
          }}
          input[type="file"] {{
            width: 100%;
            padding: 10px;
            border: none;
            background: transparent;
          }}
          .options {{
            display: grid;
            gap: 10px;
            margin-top: 16px;
            color: var(--muted);
          }}
          .options label {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 500;
          }}
          button {{
            background: linear-gradient(135deg, var(--accent), #f6b147);
            border: none;
            color: #fff;
            padding: 14px 26px;
            border-radius: 12px;
            font-weight: 700;
            cursor: pointer;
            font-size: 15px;
            box-shadow: 0 12px 24px rgba(242, 139, 44, 0.3);
          }}
          .notice {{
            margin-bottom: 18px;
            padding: 12px 14px;
            border-radius: 10px;
            background: #f4eee6;
            border: 1px solid var(--line);
          }}
          .footer {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 16px;
            color: var(--muted);
            font-size: 13px;
          }}
          .history {{
            padding-left: 18px;
            color: var(--muted);
          }}
          .overlay {{
            position: fixed;
            inset: 0;
            background: rgba(31, 27, 22, 0.45);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 50;
          }}
          .overlay.active {{
            display: flex;
          }}
          .progress-card {{
            background: #fff;
            padding: 24px;
            border-radius: 16px;
            width: min(380px, 90%);
            text-align: center;
          }}
          .bar {{
            height: 8px;
            background: #f1e6d5;
            border-radius: 999px;
            overflow: hidden;
            margin-top: 12px;
          }}
          .bar span {{
            display: block;
            height: 100%;
            width: 40%;
            background: var(--accent);
            animation: slide 1.4s infinite;
          }}
          @keyframes slide {{
            0% {{ transform: translateX(-100%); }}
            100% {{ transform: translateX(250%); }}
          }}
          @media (max-width: 640px) {{
            header {{
              flex-direction: column;
              align-items: flex-start;
            }}
          }}
        </style>
        <div class="overlay" id="overlay">
          <div class="progress-card">
            <strong>Идет расчет…</strong>
            <div class="bar"><span></span></div>
            <p class="lead" style="margin-top:10px;">Это может занять пару минут.</p>
          </div>
        </div>
        <div class="wrap">
          <header>
            <div>
              <div class="badge">Reserve Planner</div>
              <h1>Распределение резерва</h1>
              <p class="lead">Сравниваем спрос с резервами и собираем поставки под ваш образец.</p>
            </div>
            <div class="card" style="max-width:240px;">
              <strong>Формат</strong>
              <p class="lead" style="margin-top:6px;">Excel .xlsx</p>
            </div>
          </header>
          <div class="card">
            {msg}
            <form action="/run" method="post" enctype="multipart/form-data">
              <div class="grid">
                <div>
                  <label>Потребность (xlsx)</label>
                  <div class="drop" data-drop>
                    <input type="file" name="demand" accept=".xlsx" required />
                    <div class="muted">Перетащите файл сюда</div>
                  </div>
                </div>
                <div>
                  <label>Резерв (xlsx)</label>
                  <div class="drop" data-drop>
                    <input type="file" name="reserve" accept=".xlsx" required />
                    <div class="muted">Перетащите файл сюда</div>
                  </div>
                </div>
                <div>
                  <label>Образец (xlsx, опционально)</label>
                  <div class="drop" data-drop>
                    <input type="file" name="template" accept=".xlsx" />
                    <div class="muted">Перетащите файл сюда</div>
                  </div>
                </div>
              </div>
              <div class="options">
                <label><input type="checkbox" name="use_template" checked /> Использовать образец</label>
                <label><input type="checkbox" name="scale_template" checked /> Масштабировать по спросу</label>
                <label><input type="checkbox" name="include_without_demand" checked /> Добавлять строки без спроса</label>
              </div>
              <div class="footer">
                <span>Поддерживается несколько дат и все PLU</span>
                <button type="submit">Рассчитать</button>
              </div>
            </form>
          </div>
          <div class="card" style="margin-top:18px;">
            <strong>История запусков</strong>
            {history_html}
          </div>
        </div>
        <script>
          const overlay = document.getElementById("overlay");
          const form = document.querySelector("form");
          form.addEventListener("submit", () => {{
            overlay.classList.add("active");
          }});
          document.querySelectorAll("[data-drop]").forEach((drop) => {{
            const input = drop.querySelector("input[type=file]");
            drop.addEventListener("dragover", (e) => {{
              e.preventDefault();
              drop.classList.add("drag");
            }});
            drop.addEventListener("dragleave", () => drop.classList.remove("drag"));
            drop.addEventListener("drop", (e) => {{
              e.preventDefault();
              drop.classList.remove("drag");
              input.files = e.dataTransfer.files;
            }});
          }});
        </script>
      </body>
    </html>
    """


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return _render_form()


@app.post("/run", response_class=HTMLResponse)
def run(
    demand: UploadFile = File(...),
    reserve: UploadFile = File(...),
    template: UploadFile = File(None),
    use_template: str = Form(None),
    scale_template: str = Form(None),
    include_without_demand: str = Form(None),
) -> str:
    demand_path = _save_upload(demand, ".xlsx")
    reserve_path = _save_upload(reserve, ".xlsx")
    template_path = _save_upload(template, ".xlsx") if template else None

    options = RunOptions(
        use_template=bool(use_template),
        scale_template=bool(scale_template),
        include_template_without_demand=bool(include_without_demand),
    )

    output_id = uuid.uuid4().hex
    output_path = Path(tempfile.gettempdir()) / f"reserve_output_{output_id}.xlsx"

    try:
        run_plan(
            str(demand_path),
            str(reserve_path),
            str(output_path),
            template_path=str(template_path) if template_path else None,
            options=options,
            logger=None,
        )
    except Exception as exc:
        return _render_form(f"Ошибка: {exc}")
    finally:
        try:
            demand_path.unlink(missing_ok=True)
            reserve_path.unlink(missing_ok=True)
            if template_path:
                template_path.unlink(missing_ok=True)
        except Exception:
            pass

    _outputs[output_id] = output_path
    label = output_path.name
    _history.append((label, f"/download/{output_id}"))
    return _render_form(f"Готово. <a href=\"/download/{output_id}\">Скачать результат</a>")


@app.get("/download/{output_id}")
def download(output_id: str) -> FileResponse:
    path = _outputs.get(output_id)
    if not path or not path.exists():
        return FileResponse(
            io.BytesIO(b"Not found"),
            media_type="text/plain",
            filename="not_found.txt",
        )
    return FileResponse(path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
