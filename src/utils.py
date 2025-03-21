import os

def create_md_file(project, mr_data, analysis):
    output_dir = project["output_dir"]
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filename = f"{output_dir}/mr_{mr_data['iid']}_{mr_data['title'].replace(' ', '_')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Merge Request Review: {mr_data['title']}\n\n")
        f.write(f"**MR Link**: {mr_data['web_url']}\n\n")
        f.write(f"**Analiz Özeti**: {analysis['summary']}\n\n")
        f.write("## Senior Developer Yorumları\n")
        f.write(f"- **İyi Yönler**: {analysis['positives']}\n")
        f.write(f"- **İyileştirme Önerileri**: {analysis['suggestions']}\n")
    return filename