import docx, io, os
for f in [r"C:\Users\david_ssemz9t\Downloads\Formato Pruebas de Aceptacion - INVILARA_COMPLETO.docx",
          r"C:\Users\david_ssemz9t\Downloads\Formato del Plan de Capacitacion - INVILARA_COMPLETO.docx"]:
    d = docx.Document(f)
    o = io.StringIO()
    o.write(f"\n{'='*60}\nFILE: {os.path.basename(f)}\n{'='*60}\n")
    for i,p in enumerate(d.paragraphs):
        if p.text.strip():
            o.write(f"P[{i}]: {p.text[:180]}\n")
    o.write(f"\nTABLES: {len(d.tables)}\n")
    for ti,t in enumerate(d.tables):
        o.write(f"TABLE[{ti}] rows={len(t.rows)} cols={len(t.columns)}\n")
        for ri,row in enumerate(t.rows[:5]):
            o.write(f"  r{ri}: {[c.text[:60] for c in row.cells]}\n")
        if len(t.rows) > 5:
            o.write(f"  ... ({len(t.rows)} total rows)\n")
    open(f"_verify_{os.path.basename(f)}.txt","w",encoding="utf-8").write(o.getvalue())
    print(o.getvalue()[:3000])
