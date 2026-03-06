import fitz

try:
    doc = fitz.open('Template.pdf')
    for i in range(len(doc)):
        print(f"--- PAGE {i} ---")
        page = doc[i]
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b.get("type") == 0:  # text
                for line in b["lines"]:
                    for span in line["spans"]:
                        text = span["text"].replace('\n', ' ').strip()
                        if text:
                            # Print bbox (x0, y0, x1, y1) and text
                            bbox = span["bbox"]
                            print(f"X:{bbox[0]:.1f} Y:{bbox[1]:.1f} | {text}")
except Exception as e:
    print("Error:", e)
