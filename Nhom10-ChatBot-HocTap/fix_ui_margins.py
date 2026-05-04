import re
from pathlib import Path

def fix_spacer_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Tìm tất cả các thẻ <spacer>...</spacer>
    pattern = r'(<spacer\b[^>]*>.*?</spacer>)'
    matches = list(re.finditer(pattern, content, re.DOTALL))

    if not matches:
        return False

    modified = False
    # Duyệt từ cuối lên để không làm hỏng vị trí index khi thay thế
    for match in reversed(matches):
        spacer_block = match.group(0)
        if '<property name="sizeHint"' not in spacer_block:
            # Thêm sizeHint mặc định ngay sau thẻ mở spacer
            new_spacer = re.sub(
                r'(<spacer\b[^>]*>)',
                r'\1\n   <property name="sizeHint" stdset="0">\n    <size>\n     <width>0</width>\n     <height>0</height>\n    </size>\n   </property>',
                spacer_block,
                count=1
            )
            content = content[:match.start()] + new_spacer + content[match.end():]
            modified = True

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✔ Đã sửa spacer: {filepath}")
    else:
        print(f"ℹ Spacer đã ổn: {filepath}")
    return modified

# Duyệt tất cả file .ui trong thư mục forms
forms_dir = Path('forms')
count = 0
for ui_file in forms_dir.rglob('*.ui'):
    if fix_spacer_in_file(str(ui_file)):
        count += 1

print(f"\n✅ Hoàn tất! Đã sửa {count} file.")