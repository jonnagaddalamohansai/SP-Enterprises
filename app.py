import streamlit as st
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from num2words import num2words
import datetime
from PyPDF2 import PdfMerger

# ---- Background image URL for civil construction helmet ----
background_image_url = "https://media.istockphoto.com/id/605999886/photo/yellow-hard-hat-safety-helmet-isolated-on-white.jpg?s=1024x1024&w=is&k=20&c=qf1eXyXYYugHWFneQFcnm50v0WvwN5kdLWE_ME5Q10c="

# --- CSS Styling ---
st.markdown(f"""
    <style>
    body {{
        background-image: url("{background_image_url}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        color: #003366;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    }}
    .stButton>button {{
        background-color: #00509e;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
    }}
    .stTextInput>div>input, .stTextArea>div>textarea {{
        color: #003366;
        font-weight: 600;
        background-color: rgba(255, 255, 255, 0.85);
        border-radius: 5px;
        padding: 8px;
    }}
    .css-1d391kg {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        padding: 20px;
        border-radius: 10px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- PDF creation for single entry ---
def create_pdf(entry):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 40

    c.setFont("Helvetica-Bold", 16)
    c.drawString(110, y, "SP ENTERPRISES")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(110, y - 20, "WATER PROOFING SOLUTIONS")
    c.setFont("Helvetica", 10)
    c.drawString(110, y - 35, "NO: 79/1, 6th Cross, Ashok Nagar, BSK 1st Stage, NR Colony, Bangalore-50")
    c.drawString(110, y - 48, "E-mail: sp.enterprises215@gmail.com   Mob: 099453 53215")
    date_str = datetime.datetime.now().strftime("%d/%m/%Y")
    c.drawRightString(width - 40, y - 48, f"Date: {date_str}")

    y -= 70
    c.line(40, y, width - 40, y)
    y -= 20

    c.drawString(60, y, entry["customer_name"])
    y -= 15
    c.drawString(60, y, entry["customer_address"])
    y -= 25
    c.drawString(40, y, "Dear Sir,")
    y -= 15
    c.drawString(60, y, f"Ref: Job")
    y -= 15
    c.drawString(60, y, f"Date: {date_str}")
    y -= 25

    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "QUOTATION")
    y -= 20

    table_data = [
        ["S.No", "Job", "Job Details", "Qty Shift", "Rate", "Amount"],
        ["1", entry["job"], entry["job_details"], entry["qty_shift"], entry["rate"], entry["amount"]],
    ]
    table = Table(table_data, colWidths=[40, 80, 150, 60, 60, 60])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    table.wrapOn(c, width, height)
    table.drawOn(c, 40, y - 40)
    y -= 100

    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, f"Total: {entry['total']}")
    y -= 20

    try:
        amount_words = num2words(float(entry['total']), to='currency', lang='en_IN')
        c.setFont("Helvetica", 10)
        c.drawString(40, y, f"Amount in words: {amount_words.capitalize()}")
    except:
        c.drawString(40, y, "Amount in words: Invalid total amount")
    y -= 40

    c.drawString(40, y, "Thank you for considering our services.")
    y -= 20
    c.drawString(40, y, "For SP ENTERPRISES")
    y -= 40
    c.drawString(40, y, "Authorized Signature")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


# --- Initialize entries in session_state ---
if "entries" not in st.session_state:
    st.session_state.entries = []

st.title("***SP ENTERPRISES QUOTATION***")

# --- Form for new entries ---
with st.form("entry_form"):
    customer_name = st.text_input("Customer Name")
    customer_address = st.text_area("Customer Address")
    job = st.text_input("Job")
    job_details = st.text_area("Job Details")
    qty_shift = st.text_input("Qty Shift")
    rate = st.text_input("Rate")
    amount = st.text_input("Amount")
    total = st.text_input("Total")

    submitted = st.form_submit_button("Add Entry")

if submitted:
    if not customer_name.strip() or not job.strip():
        st.error("Customer Name and Job are required!")
    else:
        entry = {
            "customer_name": customer_name.strip(),
            "customer_address": customer_address.strip(),
            "job": job.strip(),
            "job_details": job_details.strip(),
            "qty_shift": qty_shift.strip(),
            "rate": rate.strip(),
            "amount": amount.strip(),
            "total": total.strip(),
        }
        st.session_state.entries.append(entry)
        st.success("Entry added!")

# --- Show current entries ---
if st.session_state.entries:
    st.subheader("Current Entries")
    for i, e in enumerate(st.session_state.entries, start=1):
        st.markdown(f"{i}. {e['customer_name']} — {e['job']} — Total: ₹{e['total']}")

    # Buttons for actions
    col1, col2, col3 = st.columns(3)

    # Clear all entries button
    with col1:
        if st.button("Clear All Entries"):
            st.session_state.entries.clear()
            st.rerun()

    # Refresh button (just rerun)
    with col2:
        if st.button("Refresh"):
            st.rerun()

    # Download All PDFs as a merged PDF
    with col3:
        if st.button("Download All PDFs"):
            merger = PdfMerger()
            for entry in st.session_state.entries:
                pdf_buffer = create_pdf(entry)
                merger.append(pdf_buffer)
            output_buffer = BytesIO()
            merger.write(output_buffer)
            merger.close()
            output_buffer.seek(0)
            st.download_button(
                label="Download Merged PDF",
                data=output_buffer,
                file_name="all_quotations.pdf",
                mime="application/pdf"
            )

else:
    st.info("No entries yet. Add new entries using the form above.")

# --- Total summary ---
if st.session_state.entries:
    try:
        total_sum = sum(float(e['total']) for e in st.session_state.entries if e['total'])
        st.markdown(f"### Total of all entries: ₹ {total_sum:,.2f}")
    except Exception:
        st.markdown("### Total of all entries: N/A")