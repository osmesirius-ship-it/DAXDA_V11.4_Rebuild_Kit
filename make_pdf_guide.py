from fpdf import FPDF
import os

class PDFGuide(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(0, 168, 255)
        self.cell(0, 10, 'DAXDA V11.4 Hostinger Deployment Guide', new_x='LMARGIN', new_y='NEXT', align='L')
        self.set_draw_color(200, 200, 200)
        self.line(10, 20, 200, 20)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

pdf = PDFGuide()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font('Helvetica', '', 10)
pdf.set_text_color(40, 40, 40)

def add_heading(text, level=1):
    pdf.ln(3)
    if level == 1:
        pdf.set_font('Helvetica', 'B', 13)
        pdf.set_text_color(15, 23, 42)
    else:
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 8, text, new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(51, 65, 85)

def add_paragraph(text):
    pdf.multi_cell(0, 5, text)
    pdf.ln(2)

def add_code(code_text):
    pdf.set_font('Courier', '', 9)
    pdf.set_fill_color(240, 243, 246)
    pdf.set_text_color(20, 30, 55)
    pdf.multi_cell(0, 5, code_text, fill=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(51, 65, 85)
    pdf.ln(2)

add_paragraph('This document details how to deploy DAXDA V11.4 Clifford Algebra Cl(4,1) AI & Web Gateway on Hostinger Web Hosting (hPanel Python App / Passenger WSGI) or Hostinger VPS.')

add_heading('1. Package Components', 1)
add_paragraph('- passenger_wsgi.py & .htaccess: Hostinger hPanel Phusion Passenger WSGI entry points.')
add_paragraph('- app.py: Interactive Glassmorphism Web UI Dashboard & REST API backend.')
add_paragraph('- Core Engine Modules: daxda_engine_aglm_opt.py, daxda_engine_v11_4.py, cl41_fast.py, clifford_algebra.py, etc.')
add_paragraph('- requirements.txt: Lightweight Python requirements (Flask, gunicorn, fpdf2).')
add_paragraph('- install_hostinger.sh: Shell script for SSH / Terminal auto-setup.')

add_heading('2. Hostinger hPanel Installation Steps (Recommended)', 1)
add_paragraph('1. Upload daxda_v11.4_hostinger_deployment.zip to public_html/ using Hostinger File Manager.')
add_paragraph('2. Extract all contents in public_html/.')
add_paragraph('3. Open Hostinger hPanel -> Search "Setup Python App".')
add_paragraph('4. Click Create Application. Set Python version (3.9+), Application Root to public_html, and Application Startup File to passenger_wsgi.py.')
add_paragraph('5. Click Create, then under Configuration File type requirements.txt and click Run Pip Install.')
add_paragraph('6. Click Restart Application and navigate to your website URL!')

add_heading('3. REST API Quick Reference', 1)
add_paragraph('POST /api/evaluate - Evaluate prompt through Cl(4,1) Geometric Engine:')
add_code('{\n  "input_text": "Verify quantum safety protocol",\n  "engine": "AGLM-OPT"\n}')

add_paragraph('GET /api/preflight - Execute preflight suite & return results.')
add_paragraph('GET /api/health - Check service availability.')

add_heading('4. Troubleshooting', 1)
add_paragraph('- 500 Error: Check permissions of passenger_wsgi.py (644/755) and review hPanel Error Logs.')
add_paragraph('- Missing Flask module: Ensure Run Pip Install was executed for requirements.txt in hPanel.')

pdf_path = r'c:\Users\HomePC\Downloads\DAXDA_V11.4_Rebuild_Kit\daxda_hostinger_package\HOSTINGER_DEPLOYMENT_GUIDE.pdf'
pdf.output(pdf_path)
print('PDF guide generated successfully at:', pdf_path)
