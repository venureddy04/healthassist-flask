from mistralai import Mistral
from config import Config

mistral_client = Mistral(api_key=Config.MISTRAL_API_KEY)

def call_mistral_ai(prompt, temperature=0.7):
    """Base LLM call - Returns HTML ONLY"""
    try:
        html_prompt = f"""
You are an HTML content generator for a medical health assistant.

TASK:
- Convert the user's request into a complete, valid HTML document.
- Output ONLY HTML.
- Do NOT include explanations, markdown, comments, or extra text.
- The HTML must be directly renderable in a web browser.

HTML RULES:
- Start with <!DOCTYPE html>
- Use <html>, <head>, <body>
- Use clean semantic HTML (h1-h6, p, ul, table, section, article)
- Use inline CSS inside <style> for professional medical styling
- Do NOT use external libraries or scripts
- Ensure responsive layout
- Use readable fonts (Arial, sans-serif) and spacing
- Use medical color scheme: teal (#0f766e), white, light green backgrounds

CONTENT RULES:
- Structure content clearly with headings and sections
- If data is needed, present it using tables or lists
- If explanation is needed, format it cleanly using paragraphs
- If steps are needed, use ordered lists
- Keep content professional and readable
- Add medical icons using Unicode symbols (⚕️, 💊, 🩺, ⚠️, etc.)

IMPORTANT:
- Output ONLY pure HTML
- NO markdown
- NO backticks
- NO text before or after HTML
- Add disclaimer: "This is for educational purposes only. Consult a healthcare professional."

USER REQUEST:
{prompt}
"""
        response = mistral_client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": html_prompt}],
            temperature=temperature
        )

        html_content = response.choices[0].message.content.strip()

        # Remove markdown backticks if present
        if html_content.startswith("```html"):
            html_content = html_content.replace("```html", "").replace("```", "").strip()
        elif html_content.startswith("```"):
            html_content = html_content.replace("```", "").strip()

        return html_content

    except Exception as e:
        return f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background: #fee; }}
        .error {{ background: #fff; border: 2px solid #c00; padding: 15px; border-radius: 8px; }}
    </style>
</head>
<body>
    <div class="error">
        <h2>⚠️ Error</h2>
        <p>{str(e)}</p>
    </div>
</body>
</html>"""


def chat_with_ai(message, language="English"):
    prompt = f"""
Language Required: {language}
User Question: {message}

Provide a helpful medical response in {language} with:
1. Direct answer to the question
2. Key information in simple language
3. Important warnings if applicable
4. Actionable advice
5. Reminder to consult a healthcare professional

Format the response as a beautiful HTML page with medical styling.
"""
    return call_mistral_ai(prompt)


def analyze_medicine(medicine_name, language="English"):
    prompt = f"""
Language Required: {language}
Medicine: {medicine_name}

Provide information in {language} on:
1. Name & Use - Generic/brand names and what it treats
2. How It Works - Mechanism of action
3. Dosage - Typical dose and how to take it
4. Side Effects - Common and serious reactions
5. Precautions - Warnings, interactions, storage

Create a professional HTML medical report.
"""
    return call_mistral_ai(prompt)


def analyze_disease(disease, language="English"):
    prompt = f"""
Language Required: {language}
Disease/Condition: {disease}

Provide up to 4 common medications in {language} with:
1. Names - Generic (Brand name)
2. Purpose - How it treats {disease}
3. Dosage - Standard dosing
4. Side Effects - Key reactions
5. Precautions - Important warnings

Format as an HTML medical document with tables.
"""
    return call_mistral_ai(prompt)


def analyze_report(extracted_text, language="English"):
    prompt = f"""
Language Required: {language}
Medical Report: {extracted_text[:3000]}

Analyze and provide in {language}:
1. Summary - Test type and main findings
2. Key Results - Normal and abnormal values (⚠️ for abnormal)
3. What It Means - Health concerns identified
4. Recommendations - Follow-up tests, lifestyle changes
5. Next Steps - When to see a doctor

Create a detailed HTML report analysis.
"""
    return call_mistral_ai(prompt)


def analyze_image(extracted_text, language="English"):
    prompt = f"""
Language Required: {language}
Medicine Text: {extracted_text[:3000]}

Extract and provide in {language}:
1. Identification - Generic and brand names
2. Uses - What it treats and how it works
3. Dosage - How to take it properly
4. Side Effects - Common and serious reactions
5. Storage & Warnings - Storage conditions and precautions

Format as an HTML prescription analysis.
"""
    return call_mistral_ai(prompt)


def analyze_symptoms(symptoms, age, gender, duration, severity, language="English"):
    prompt = f"""
Language Required: {language}
Patient Info:
- Symptoms: {symptoms}
- Age: {age}
- Gender: {gender}
- Duration: {duration}
- Severity: {severity}

Provide assessment in {language} with:
1. Analysis - What symptoms suggest
2. Possible Causes - 3-5 likely conditions
3. Immediate Actions - What to do now
4. Warning Signs - When to seek emergency care (🚨)
5. When to See Doctor - Timeframe

Create an HTML symptom analysis report.
"""
    return call_mistral_ai(prompt)


def analyze_emergency(emergency_desc, level, vital_signs, language="English"):
    prompt = f"""
Language Required: {language}
EMERGENCY DETAILS:
- Description: {emergency_desc}
- Triage Level: {level}
- Vital Signs: {vital_signs}

Urgent response in {language} with:
1. Severity - Triage color (Red:Critical | Yellow:Urgent | Green:Stable)
2. Immediate Actions - Critical first steps
3. Protocol - Step-by-step emergency procedure
4. Call 108 If - Specific indicators for ambulance
5. Monitoring - Patient positioning and vitals to watch

CRITICAL: Emphasize "CALL 108 IMMEDIATELY" for life-threatening cases.

Create an HTML emergency response guide.
"""
    return call_mistral_ai(prompt)


def chat_response_simple(user_message, language="English"):
    """Simple conversational chatbot response (plain text, not HTML)"""
    try:
        prompt = f"""You are a helpful medical AI chatbot assistant. Answer the user's question in a friendly and informative way.
User Question: {user_message}
Provide a clear, concise answer. If it's a medical question, include:
- Direct answer to the question
- Any important warnings or precautions
- Suggestion to consult a healthcare professional if needed
Language: {language}
Keep the response conversational and helpful."""

        response = mistral_client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"