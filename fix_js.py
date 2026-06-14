import re
import glob

files = glob.glob('users/templates/dashboard/*_form.html')

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Fix Javascript Editor ID references
    content = re.sub(r"const editorId = currentLangTab === 'en' \? 'editor-en' : 'editor-ar';", "const editorId = 'editor';", content)
    
    # Fix syncEditor
    content = re.sub(r'function syncEditor\(lang\) \{.*?\}', 
                     r"function syncEditor() {\n        const editor = document.getElementById('editor');\n        const textarea = document.getElementById('id_review_content');\n        if (editor && textarea) textarea.value = editor.innerHTML;\n        countWords();\n    }", 
                     content, flags=re.DOTALL)

    # Fix submit listener
    content = re.sub(r"document\.getElementById\('id_review_content_ar'\)\.value = document\.getElementById\('editor-ar'\)\.innerHTML;", "", content)

    # Fix oninput inside HTML
    content = content.replace("oninput=\"syncEditor('en')\"", "oninput=\"syncEditor()\"")
    content = content.replace("oninput=\"syncEditor('ar')\"", "oninput=\"syncEditor()\"")

    # Fix formatDoc
    content = content.replace("syncEditor(currentLangTab);", "syncEditor();")
    content = content.replace("syncEditor(lang);", "syncEditor();")

    # Remove translation tab switcher function
    content = re.sub(r'let currentLangTab = \'en\';\s*function switchLangTab\(lang\) \{.*?\}', "", content, flags=re.DOTALL)

    # Fix countWords
    content = re.sub(r"function countWords\(\) \{.*?\}",
                     r"function countWords() {\n        const editor = document.getElementById('editor');\n        if (!editor) return;\n        const text = editor.innerText;\n        const words = text.trim().split(/\s+/).filter(w => w.length > 0).length;\n        const display = document.getElementById('word-count-display');\n        if (display) display.innerText = `Words: ${words}`;\n    }",
                     content, flags=re.DOTALL)

    # Remove outer tab-content div from editor HTML
    content = re.sub(r'<!-- English Editable WYSIWYG -->\s*<div class="tab-content active" id="tab-content-en">\s*(<div contenteditable="true" class="wysiwyg-editor" id="editor"[^>]*>.*?</div>)\s*</div>', r'\1', content, flags=re.DOTALL)

    with open(filepath, 'w') as f:
        f.write(content)

for filepath in files:
    process_file(filepath)

print("Done")
