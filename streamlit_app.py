import io
import streamlit as st
import pdfplumber
from docx import Document

st.set_page_config(page_title="Pasien Parser (MVP)", page_icon="🦷", layout="wide")

st.title("🦷 Pasien Parser (MVP) — Streamlit")
st.write(
    "Ini versi web minimal agar bisa jalan di Streamlit Cloud. "
    "Upload PDF lalu ekspor ringkasan ke DOCX. "
    "Jika butuh fitur lengkap dari aplikasi desktop (Tkinter), perlu dilakukan porting lanjutan."
)

with st.expander("Catatan penting"):
    st.markdown(
        "- Aplikasi desktop yang Anda upload memakai **Tkinter** sehingga **tidak bisa** jalan langsung di Streamlit Cloud.\n"
        "- Versi ini memakai `pdfplumber` + `python-docx` untuk demo alur kerja online.\n"
        "- Untuk menyamakan logika penuh (mapping DPJP, format RM, kontrol, dsb), perlu migrasi fungsi-fungsi ke Streamlit."
    )

uploaded = st.file_uploader("Pilih file PDF", type=["pdf"])

def extract_texts(pdf_bytes: bytes, max_pages: int | None = None) -> list[str]:
    texts = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        pages = pdf.pages if max_pages is None else pdf.pages[:max_pages]
        for pg in pages:
            texts.append(pg.extract_text() or "")
    return texts

if uploaded is not None:
    data = uploaded.read()
    st.success(f"File diterima: **{uploaded.name}** ({len(data)} bytes)")

    col1, col2 = st.columns([3,2], gap="large")
    with col1:
        max_pages = st.number_input("Baca hingga halaman ke-", min_value=1, value=5, step=1)
        if st.button("🔍 Parse PDF"):
            with st.spinner("Memproses..."):
                texts = extract_texts(data, max_pages=max_pages)
            st.subheader("Hasil ekstraksi (preview)")
            for i, t in enumerate(texts, 1):
                st.markdown(f"**Halaman {i}**")
                st.text_area(f"teks_{i}", t, height=180, label_visibility="collapsed", key=f"page_{i}")

            # Simpel: gabungkan teks & simpan ke DOCX
            doc = Document()
            doc.add_heading(f"Ekstraksi {uploaded.name}", level=1)
            for i, t in enumerate(texts, 1):
                doc.add_heading(f"Halaman {i}", level=2)
                for line in t.splitlines():
                    doc.add_paragraph(line)
            out_buf = io.BytesIO()
            doc.save(out_buf)
            st.download_button(
                "⬇️ Download DOCX",
                data=out_buf.getvalue(),
                file_name=uploaded.name.rsplit(".",1)[0] + "_ekstraksi.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

    with col2:
        st.subheader("Opsi (MVP)")
        st.caption("Tambahkan kontrol lanjutan di sini ketika fungsi dari app Tkinter sudah dipindahkan.")
        st.toggle("Contoh opsi A", value=False)
        st.toggle("Contoh opsi B", value=True)

st.divider()
st.markdown("Made with ❤️ using Streamlit")