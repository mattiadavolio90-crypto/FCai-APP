"""
Test rapido conversione PDF con PyMuPDF
Verifica che la nuova implementazione funzioni correttamente
"""
import fitz
import base64
import os

def test_pdf_conversion(pdf_path):
    """Testa conversione PDF in base64 con PyMuPDF"""
    print(f"\n{'='*60}")
    print(f"📄 Test PDF: {os.path.basename(pdf_path)}")
    print(f"{'='*60}")
    
    try:
        # Leggi file
        with open(pdf_path, 'rb') as f:
            content = f.read()
        
        print(f"✅ File letto: {len(content)} bytes")
        
        # Apri con PyMuPDF
        pdf_document = fitz.open(stream=content, filetype="pdf")
        print(f"✅ PDF aperto con PyMuPDF")
        print(f"   📊 Numero pagine: {pdf_document.page_count}")
        
        if pdf_document.page_count == 0:
            print("❌ PDF vuoto!")
            return False
        
        # Carica prima pagina
        page = pdf_document[0]
        print(f"✅ Prima pagina caricata")
        print(f"   📐 Dimensioni: {page.rect.width:.1f} x {page.rect.height:.1f} pt")
        
        # Converti in immagine alta risoluzione (300 DPI)
        zoom = 300 / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        print(f"✅ Conversione in immagine completata")
        print(f"   🖼️  Risoluzione: {pix.width} x {pix.height} px")
        
        # Converti in bytes PNG
        img_bytes = pix.tobytes("png")
        print(f"✅ PNG generato: {len(img_bytes)} bytes")
        
        pdf_document.close()
        
        # Converti in base64
        base64_str = base64.b64encode(img_bytes).decode('utf-8')
        print(f"✅ Base64 generato: {len(base64_str)} caratteri")
        
        print(f"\n🎉 SUCCESSO! PDF convertito correttamente")
        print(f"   Preview base64: {base64_str[:50]}...")
        
        return True
        
    except fitz.fitz.FileDataError as e:
        print(f"❌ PDF corrotto o non valido: {e}")
        return False
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Test su PDF reali
    test_files = [
        r"FILE\DOCUMENTI TEST\fatture pdf\IT02355260981_d7GET.xml.p7m - 25-09543_KA.pdf",
        r"FILE\DOCUMENTI TEST\fatture pdf\IT09985680967_04NG1.xml - 30231.pdf"
    ]
    
    successi = 0
    fallimenti = 0
    
    for pdf_file in test_files:
        full_path = os.path.join(os.path.dirname(__file__), pdf_file)
        if os.path.exists(full_path):
            if test_pdf_conversion(full_path):
                successi += 1
            else:
                fallimenti += 1
        else:
            print(f"⚠️ File non trovato: {pdf_file}")
    
    print(f"\n{'='*60}")
    print(f"📊 RIEPILOGO TEST")
    print(f"{'='*60}")
    print(f"✅ Successi: {successi}")
    print(f"❌ Fallimenti: {fallimenti}")
    print(f"{'='*60}\n")
