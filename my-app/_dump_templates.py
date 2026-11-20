import docx, glob, os, io
for f in glob.glob(r"C:\Users\david_ssemz9t\Downloads\*.docx"):
    b = os.path.basename(f)
    if "Pruebas de Aceptacion" in b or "Plan de Capacitaci" in b:
        d = docx.Document(f)
        print("="*80)
        print("FILE:", b)
        print("="*80)
        for i, p in enumerate(d.paragraphs):
            if p.text.strip():
                print(f"P[{i}]({p.style.name}): {p.text}")
        print("--- TABLES:", len(d.tables))
        for ti, t in enumerate(d.tables):
            print(f"TABLE[{ti}] rows={len(t.rows)} cols={len(t.columns)}")
            for ri, row in enumerate(t.rows):
                cells = [cell.text for cell in row.cells]
                print(f"  r{ri}: {cells}")
