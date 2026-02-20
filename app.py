import base64
from flask import Flask, render_template, request, send_file
import io
from qr_engine import generate_qr_image

app = Flask(__name__)


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    url = request.form.get("url", "").strip()
    text = request.form.get("text", "").strip()
    position = request.form.get("position", "center")
    accent_hex = request.form.get("accent_color", "#DC3232")
    mode = request.form.get("mode", "normal")
    qr_version_str = request.form.get("qr_version", "auto")
    qr_version = int(qr_version_str) if qr_version_str != "auto" else None

    error = None
    img_b64 = None
    used_version = None

    if not url:
        error = "URL を入力してください。"
    elif not text:
        error = "テキストを入力してください。"
    else:
        try:
            accent_rgb = hex_to_rgb(accent_hex)
            png_bytes, used_version = generate_qr_image(url, text, accent_rgb, position, mode, qr_version)
            img_b64 = base64.b64encode(png_bytes).decode("utf-8")
        except Exception as e:
            error = f"生成エラー: {e}"

    return render_template(
        "index.html",
        img_b64=img_b64,
        error=error,
        prev_url=url,
        prev_text=text,
        prev_position=position,
        prev_accent=accent_hex,
        prev_mode=mode,
        prev_qr_version=qr_version_str,
        used_version=used_version,
    )


@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url", "").strip()
    text = request.form.get("text", "").strip()
    position = request.form.get("position", "center")
    accent_hex = request.form.get("accent_color", "#DC3232")
    mode = request.form.get("mode", "normal")
    qr_version_str = request.form.get("qr_version", "auto")
    qr_version = int(qr_version_str) if qr_version_str != "auto" else None

    accent_rgb = hex_to_rgb(accent_hex)
    png_bytes, _ = generate_qr_image(url, text, accent_rgb, position, mode, qr_version)

    return send_file(
        io.BytesIO(png_bytes),
        mimetype="image/png",
        as_attachment=True,
        download_name="texted-qr.png",
    )


if __name__ == "__main__":
    app.run(debug=True, port=8080)
