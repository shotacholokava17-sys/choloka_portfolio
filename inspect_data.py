import json
import os

with open('activities_scan.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

summary = []
for item in data:
    title = item['title']
    files = item['files']
    images = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif'))]
    docs = [f for f in files if f.lower().endswith(('.pdf', '.docx', '.pptx', '.txt', '.mp4'))]
    summary.append({
        'title': title,
        'image_count': len(images),
        'doc_count': len(docs),
        'images': images,
        'docs': docs
    })

print(f"Total activity folders: {len(summary)}")
print(f"Folders with images: {len([s for s in summary if s['image_count'] > 0])}")

with open('summary_report.txt', 'w', encoding='utf-8') as f:
    for s in summary:
        f.write(f"=== {s['title']} ===\n")
        f.write(f"Images ({s['image_count']}): {s['images'][:5]}\n")
        if s['docs']:
            f.write(f"Docs ({s['doc_count']}): {s['docs']}\n")
        f.write("\n")

print("Report saved to summary_report.txt")
