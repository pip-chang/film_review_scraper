from pathlib import Path

def save_html(html_source: str, output_path: str, file_name: str) -> None:
    output_path = Path(output_path) / f"{file_name}.html"
    with open(output_path, mode='w') as file:
        file.write(html_source)
