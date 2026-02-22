from flask_mail import Mail, Message
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
import os
import re
import tempfile

mail = Mail()


def strip_html(html_content):
    """Strip HTML tags and decode entities for plain text"""
    if not html_content:
        return ""
    text = str(html_content)
    text = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<script[^>]*>[\s\S]*?</script>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<!DOCTYPE[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&quot;', '"', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def safe_text(text, max_chars=3000):
    """Prepare text safely for ReportLab Paragraph"""
    if not text:
        return "N/A"
    text = str(text)[:max_chars]
    # Escape XML special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    # Remove non-printable control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text


def safe_para(text, style, max_chars=3000):
    """Create a ReportLab Paragraph safely"""
    try:
        return Paragraph(safe_text(text, max_chars), style)
    except Exception:
        try:
            return Paragraph("(Content unavailable)", style)
        except Exception:
            return Spacer(1, 0.1 * inch)


def get_temp_path(filename):
    """
    Get a cross-platform temp file path.
    Uses tempfile.gettempdir() which correctly returns:
      - /tmp on Linux/Mac
      - C:\\Users\\...\\AppData\\Local\\Temp on Windows
    Avoids the /tmp\\filename bug on Windows.
    """
    return os.path.join(tempfile.gettempdir(), filename)


def build_styles():
    """Build and return all custom paragraph styles"""
    base = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'HATitle', parent=base['Normal'],
        fontSize=20, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#0f766e'),
        alignment=TA_CENTER, spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'HASubtitle', parent=base['Normal'],
        fontSize=11, textColor=colors.HexColor('#374151'),
        alignment=TA_CENTER, spaceAfter=4
    )
    section_style = ParagraphStyle(
        'HASection', parent=base['Normal'],
        fontSize=13, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#0f766e'),
        spaceBefore=12, spaceAfter=6
    )
    label_style = ParagraphStyle(
        'HALabel', parent=base['Normal'],
        fontSize=10, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#6b7280'), spaceAfter=3
    )
    content_style = ParagraphStyle(
        'HAContent', parent=base['Normal'],
        fontSize=10, textColor=colors.HexColor('#1f2937'),
        spaceAfter=6, leading=14
    )
    disclaimer_style = ParagraphStyle(
        'HADisclaimer', parent=base['Normal'],
        fontSize=8, textColor=colors.HexColor('#9ca3af'),
        alignment=TA_CENTER, leading=12
    )
    user_label_style = ParagraphStyle(
        'HAUserLabel', parent=base['Normal'],
        fontSize=10, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1d4ed8'),
        spaceBefore=10, spaceAfter=3
    )
    ai_label_style = ParagraphStyle(
        'HAAILabel', parent=base['Normal'],
        fontSize=10, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#0f766e'),
        spaceBefore=10, spaceAfter=3
    )
    indented_style = ParagraphStyle(
        'HAIndented', parent=base['Normal'],
        fontSize=10, textColor=colors.HexColor('#1f2937'),
        spaceAfter=4, leading=14, leftIndent=10
    )

    return {
        'title': title_style,
        'subtitle': subtitle_style,
        'section': section_style,
        'label': label_style,
        'content': content_style,
        'disclaimer': disclaimer_style,
        'user_label': user_label_style,
        'ai_label': ai_label_style,
        'indented': indented_style,
    }


def generate_history_item_pdf(history_item, user_name):
    """
    Generate a PDF for a single history item.
    Returns the filepath of the created PDF.
    """
    item_id = history_item.get('id', 'x')
    filename = f"ha_history_{item_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = get_temp_path(filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=1 * inch,
        rightMargin=1 * inch
    )

    s = build_styles()
    story = []

    # ── Header ──────────────────────────────────────────────
    story.append(safe_para("HealthAssist AI", s['title']))
    story.append(safe_para("Consultation Report", s['subtitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0f766e')))
    story.append(Spacer(1, 0.15 * inch))

    story.append(safe_para(f"<b>User:</b> {safe_text(user_name)}", s['content']))
    story.append(safe_para(f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", s['content']))
    story.append(safe_para(f"<b>Consultation ID:</b> #{item_id}", s['content']))

    ts = history_item.get('timestamp', '')
    if ts:
        ts_display = str(ts)[:19].replace('T', ' ')
        story.append(safe_para(f"<b>Date:</b> {ts_display}", s['content']))

    story.append(Spacer(1, 0.1 * inch))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
    story.append(Spacer(1, 0.1 * inch))

    # ── Category badge ───────────────────────────────────────
    category = history_item.get('category', '')
    data = history_item.get('data', {})
    if not isinstance(data, dict):
        data = {}

    cat_labels = {
        'chat': 'General Chat',
        'medicine': 'Medicine Info',
        'report': 'Report Analysis',
        'symptom': 'Symptom Check',
        'emergency': 'Emergency Triage',
    }
    cat_label = cat_labels.get(category, category.title())
    story.append(safe_para(f"Category: {cat_label}", s['section']))

    language = data.get('language', 'English')
    story.append(safe_para(f"<b>Language:</b> {safe_text(language)}", s['label']))
    story.append(Spacer(1, 0.1 * inch))

    # ── Category-specific body ───────────────────────────────
    if category == 'chat':
        story.append(safe_para("Question:", s['section']))
        story.append(safe_para(data.get('question', 'N/A'), s['content']))
        story.append(Spacer(1, 0.1 * inch))
        story.append(safe_para("AI Response:", s['section']))
        resp = strip_html(data.get('response', 'N/A'))
        story.append(safe_para(resp, s['content']))

    elif category == 'medicine':
        story.append(safe_para(f"<b>Search Type:</b> {safe_text(data.get('search_type', 'N/A'))}", s['content']))
        story.append(safe_para(f"<b>Search Term:</b> {safe_text(data.get('search_term', 'N/A'))}", s['content']))
        story.append(Spacer(1, 0.1 * inch))
        story.append(safe_para("Information:", s['section']))
        resp = strip_html(data.get('response', 'N/A'))
        story.append(safe_para(resp, s['content']))

    elif category == 'report':
        story.append(safe_para(f"<b>File:</b> {safe_text(data.get('filename', 'N/A'))}", s['content']))
        story.append(safe_para(f"<b>Type:</b> {safe_text(data.get('type', 'N/A'))}", s['content']))
        story.append(Spacer(1, 0.1 * inch))
        story.append(safe_para("Analysis:", s['section']))
        resp = strip_html(data.get('response', 'N/A'))
        story.append(safe_para(resp, s['content']))

    elif category == 'symptom':
        story.append(safe_para("Patient Information:", s['section']))
        story.append(safe_para(f"<b>Symptoms:</b> {safe_text(data.get('symptoms', 'N/A'))}", s['content']))
        story.append(safe_para(f"<b>Age:</b> {safe_text(data.get('age', 'N/A'))} years", s['content']))
        story.append(safe_para(f"<b>Gender:</b> {safe_text(data.get('gender', 'N/A'))}", s['content']))
        story.append(safe_para(f"<b>Duration:</b> {safe_text(data.get('duration', 'N/A'))}", s['content']))
        story.append(safe_para(f"<b>Severity:</b> {safe_text(data.get('severity', 'N/A'))}", s['content']))
        story.append(Spacer(1, 0.1 * inch))
        story.append(safe_para("Assessment:", s['section']))
        resp = strip_html(data.get('response', 'N/A'))
        story.append(safe_para(resp, s['content']))

    elif category == 'emergency':
        story.append(safe_para("Emergency Details:", s['section']))
        story.append(safe_para(f"<b>Description:</b> {safe_text(data.get('emergency_desc', 'N/A'))}", s['content']))
        story.append(safe_para(f"<b>Triage Level:</b> {safe_text(data.get('level', 'N/A'))}", s['content']))
        vital = data.get('vital_signs', '')
        if vital:
            story.append(safe_para(f"<b>Vital Signs:</b> {safe_text(vital)}", s['content']))
        story.append(Spacer(1, 0.1 * inch))
        story.append(safe_para("Emergency Response:", s['section']))
        resp = strip_html(data.get('response', 'N/A'))
        story.append(safe_para(resp, s['content']))

    # ── Disclaimer ───────────────────────────────────────────
    story.append(Spacer(1, 0.3 * inch))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
    story.append(Spacer(1, 0.1 * inch))
    story.append(safe_para(
        "DISCLAIMER: This report is generated by HealthAssist AI for informational purposes only. "
        "It does not constitute medical advice. Always consult a qualified healthcare professional. "
        "In case of emergency, call 108 immediately.",
        s['disclaimer']
    ))

    doc.build(story)
    return filepath


def send_history_item_email(recipient_email, user_name, history_item, subject, body):
    """Send a single history item as PDF email"""
    pdf_path = None
    try:
        pdf_path = generate_history_item_pdf(history_item, user_name)

        if not os.path.exists(pdf_path):
            return False, f"PDF was not created. Temp path: {pdf_path}"

        category = history_item.get('category', 'consultation')
        cat_labels = {
            'chat': 'General Chat', 'medicine': 'Medicine Info',
            'report': 'Report Analysis', 'symptom': 'Symptom Check',
            'emergency': 'Emergency Triage'
        }
        cat_label = cat_labels.get(category, category.title())

        ts = history_item.get('timestamp', 'N/A')
        ts_clean = str(ts)[:19].replace('T', ' ') if ts and ts != 'N/A' else 'N/A'

        email_subject = subject or f"HealthAssist AI - {cat_label} Consultation Report"
        email_body = body or (
            f"Hello {user_name},\n\n"
            f"Please find attached your {cat_label} consultation report from HealthAssist AI.\n\n"
            f"Consultation ID: #{history_item.get('id', 'N/A')}\n"
            f"Category: {cat_label}\n"
            f"Date: {ts_clean}\n\n"
            f"This report is for informational purposes only.\n"
            f"Please consult a healthcare professional for medical advice.\n\n"
            f"In case of emergency, call 108 immediately.\n\n"
            f"Best regards,\nHealthAssist AI Team"
        )

        msg = Message(
            subject=email_subject,
            recipients=[recipient_email],
            body=email_body
        )

        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()

        msg.attach(
            filename=f"consultation_{history_item.get('id', 'report')}.pdf",
            content_type="application/pdf",
            data=pdf_data
        )

        mail.send(msg)
        return True, "Email sent successfully with PDF attachment!"

    except Exception as e:
        return False, f"Error sending email: {str(e)}"

    finally:
        # Always clean up — even if sending failed
        if pdf_path and os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except Exception:
                pass


def generate_chat_pdf(chat_messages, user_name):
    """Generate PDF from a list of chat message dicts for the chat page"""
    filename = f"ha_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = get_temp_path(filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=1 * inch,
        rightMargin=1 * inch
    )

    s = build_styles()
    story = []

    story.append(safe_para("HealthAssist AI", s['title']))
    story.append(safe_para("Chat Session History", s['subtitle']))
    story.append(safe_para(
        f"User: {safe_text(user_name)}  |  Date: {datetime.now().strftime('%B %d, %Y %I:%M %p')}",
        s['subtitle']
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0f766e')))
    story.append(Spacer(1, 0.2 * inch))

    if not chat_messages:
        story.append(safe_para("No messages found in this chat session.", s['content']))
    else:
        for msg in chat_messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')

            # Strip HTML from AI responses
            if role != 'user':
                content = strip_html(str(content))

            if role == 'user':
                story.append(safe_para("You:", s['user_label']))
            else:
                story.append(safe_para("AI Assistant:", s['ai_label']))

            story.append(safe_para(str(content), s['indented']))

    story.append(Spacer(1, 0.3 * inch))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
    story.append(Spacer(1, 0.1 * inch))
    story.append(safe_para(
        "DISCLAIMER: This chat history is for informational purposes only and does not constitute "
        "medical advice. Always consult a qualified healthcare professional. In emergencies, call 108.",
        s['disclaimer']
    ))

    doc.build(story)
    return filepath


def send_chat_email(recipient_email, user_name, chat_messages):
    """Send chat history as PDF via email (used from chat page)"""
    pdf_path = None
    try:
        pdf_path = generate_chat_pdf(chat_messages, user_name)

        if not os.path.exists(pdf_path):
            return False, f"PDF was not created. Temp path: {pdf_path}"

        msg = Message(
            subject="Your HealthAssist AI Chat History",
            recipients=[recipient_email],
            body=(
                f"Hello {user_name},\n\n"
                f"Attached is your chat history from HealthAssist AI.\n\n"
                f"This information is for educational purposes only. "
                f"Please consult a healthcare professional for medical advice.\n\n"
                f"Best regards,\nHealthAssist AI Team"
            )
        )

        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()

        msg.attach(
            filename="chat_history.pdf",
            content_type="application/pdf",
            data=pdf_data
        )

        mail.send(msg)
        return True, "Email sent successfully!"

    except Exception as e:
        return False, f"Error sending email: {str(e)}"

    finally:
        if pdf_path and os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except Exception:
                pass