import os
import re

html_dir = r"c:\Users\Asus\OneDrive\Desktop\Sport Management\app\templates"

replacements = {
    "⚽": "<i class='bx bx-football'></i>",
    "🏠": "<i class='bx bxs-dashboard'></i>",
    "📊": "<i class='bx bx-line-chart'></i>",
    "👥": "<i class='bx bx-group'></i>",
    "🏅": "<i class='bx bx-medal'></i>",
    "🛡️": "<i class='bx bx-shield'></i>",
    "🏆": "<i class='bx bx-trophy'></i>",
    "🎽": "<i class='bx bx-purchase-tag'></i>",
    "⚠️": "<i class='bx bx-error'></i>",
    "🎉": "<i class='bx bx-party'></i>",
    "🔍": "<i class='bx bx-search'></i>",
    "✏️": "<i class='bx bx-edit-alt'></i>",
    "🗑️": "<i class='bx bx-trash'></i>",
    "✕": "<i class='bx bx-x'></i>"
}

boxicons_link = '  <link href="https://unpkg.com/boxicons@2.1.4/css/boxicons.min.css" rel="stylesheet"/>\n'

for filename in os.listdir(html_dir):
    if filename.endswith(".html"):
        filepath = os.path.join(html_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Replace emojis
        for emoji, icon in replacements.items():
            content = content.replace(emoji, icon)
        
        # Insert boxicons link in head if not exists
        if "boxicons.min.css" not in content:
            content = content.replace("</head>", boxicons_link + "</head>")
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

print("Updated HTML templates with Boxicons.")
