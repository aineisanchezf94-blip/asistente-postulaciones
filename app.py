import re
import webbrowser
from io import BytesIO
from typing import List

import streamlit as st
from docx import Document
from pypdf import PdfReader


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9áéíóúñü\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_keywords(text: str, limit: int = 10) -> List[str]:
    text = normalize_text(text)
    words = [w for w in text.split() if len(w) > 3]
    filtered = []
    stop_words = {
        "para", "como", "desde", "entre", "toda", "todos", "donde", "ademas",
        "sobre", "tambien", "cuando", "porque", "aqui", "este", "esta", "estas",
        "estos", "ser", "estar", "tener", "debe", "deben", "trabajo", "vacante",
        "empresa", "equipo", "proyecto", "proyectos", "candidato", "persona" 
    }
    for word in words:
        if word not in stop_words:
            filtered.append(word)
    freq = {}
    for word in filtered:
        freq[word] = freq.get(word, 0) + 1
    ranked = sorted(freq.items(), key=lambda item: (-item[1], item[0]))
    return [word for word, _ in ranked[:limit]]


def score_match(profile_text: str, job_text: str) -> int:
    profile_keywords = set(extract_keywords(profile_text, 30))
    job_keywords = set(extract_keywords(job_text, 30))
    if not job_keywords:
        return 0
    common = profile_keywords & job_keywords
    score = round((len(common) / len(job_keywords)) * 100)
    return min(score, 98)


def build_linkedin_message(profile: dict, vacancy: dict) -> str:
    current_role = profile.get("current_role", "profesional")
    years = profile.get("years", "varios")
    name = profile.get("name", "Candidato")
    company = vacancy.get("company", "la empresa")
    title = vacancy.get("title", "la vacante")
    skills = ", ".join(profile.get("skills", [])[:5]) or "capacidad analítica y liderazgo"

    return (
        f"Hola, soy {name}, {current_role} con {years} años de experiencia. "
        f"Me interesa mucho la oportunidad de {title} en {company}. "
        f"Durante mi trayectoria he desarrollado habilidades en {skills}, "
        f"lo que me permite aportar valor al equipo, resolver problemas con enfoque práctico "
        f"y colaborar en proyectos con resultados medibles. "
        f"Estoy muy motivado por esta oportunidad y me gustaría conversar sobre cómo mi perfil puede apoyar los objetivos de la empresa."
    )


def build_computrabajo_message(profile: dict, vacancy: dict) -> str:
    current_role = profile.get("current_role", "profesional")
    years = profile.get("years", "varios")
    title = vacancy.get("title", "la vacante")
    company = vacancy.get("company", "la empresa")
    skills = ", ".join(profile.get("skills", [])[:4]) or "trabajo en equipo"

    return (
        f"Postulación para {title} en {company}. Soy {current_role} con {years} años de experiencia, "
        f"con fortalezas en {skills}. Me interesa esta oportunidad porque combina mi experiencia, mi capacidad de aprendizaje "
        f"y mi interés por aportar soluciones concretas al equipo."
    )


def build_cover_letter(profile: dict, vacancy: dict, match_score: int) -> str:
    name = profile.get("name", "Candidato")
    current_role = profile.get("current_role", "profesional")
    years = profile.get("years", "varios")
    company = vacancy.get("company", "la empresa")
    title = vacancy.get("title", "la vacante")
    education = profile.get("education", "formación profesional")
    skills = ", ".join(profile.get("skills", [])[:6]) or "gestión, análisis y colaboración"
    motivation = vacancy.get("motivation", "aportar valor con enfoque estratégico y operativo")

    return f"""Estimado/a equipo de contratación de {company},

Mi nombre es {name}, y actualmente me desempeño como {current_role}. Tengo {years} años de experiencia en roles relacionados con la gestión, ejecución y mejora de procesos, con una base sólida en {skills}. Además, cuento con formación en {education}.

Me interesa profundamente la oportunidad de {title} porque considero que mi perfil encaja con la necesidad de {motivation}. Durante mi trayectoria he trabajado en entornos donde la organización, la coordinación, el análisis y la entrega de resultados han sido clave para apoyar los objetivos del negocio y del equipo.

El nivel de coincidencia entre mi perfil y la vacante es de {match_score}% según la evaluación del asistente, lo que refleja que cuento con las competencias principales para aportar valor desde el inicio. Estoy convencido de que puedo contribuir con una visión práctica, responsabilidad y enfoque en resultados.

Me gustaría conversar con ustedes para compartir más detalles sobre mi experiencia y explorar cómo puedo apoyar a {company} en este nuevo desafío.

Quedo atento/a a la oportunidad de continuar la conversación.

Atentamente,
{name}
"""


def sanitize_skills(raw: str) -> List[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def extract_text_from_cv(uploaded_file) -> str:
    if uploaded_file is None:
        return ""

    filename = (uploaded_file.name or "").lower()
    content = uploaded_file.read()

    if filename.endswith(".pdf"):
        try:
            reader = PdfReader(BytesIO(content))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            return ""

    if filename.endswith(".txt"):
        try:
            return content.decode("utf-8", errors="ignore")
        except Exception:
            return content.decode("latin-1", errors="ignore")

    if filename.endswith(".docx"):
        try:
            doc = Document(BytesIO(content))
            return "\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip())
        except Exception:
            return ""

    return ""


def compare_cv_vs_vacancy(cv_text: str, job_text: str):
    cv_keywords = set(extract_keywords(cv_text, 50))
    job_keywords = set(extract_keywords(job_text, 50))
    common = sorted(cv_keywords & job_keywords)
    missing = sorted(job_keywords - cv_keywords)
    match_score = 0 if not job_keywords else round((len(common) / len(job_keywords)) * 100)
    return common, missing, min(match_score, 100)


def build_question_answers(profile: dict, vacancy: dict, questions: str) -> str:
    name = profile.get("name", "Candidato")
    current_role = profile.get("current_role", "profesional")
    years = profile.get("years", "varios")
    company = vacancy.get("company", "la empresa")
    title = vacancy.get("title", "la vacante")
    skills = ", ".join(profile.get("skills", [])[:6]) or "liderazgo, comunicación y resolución de problemas"

    questions_list = [q.strip() for q in questions.split("\n") if q.strip()]
    if not questions_list:
        questions_list = [
            f"¿Por qué te interesa {title} en {company}?",
            "¿Qué te hace un buen candidato para este puesto?",
            "¿Cuál es tu mayor fortalezas?"
        ]

    answers = []
    for question in questions_list:
        answer = (
            f"{question}\n\n"
            f"Me interesa esta oportunidad porque combina mi experiencia como {current_role} con mi deseo de aportar valor a {company}. "
            f"Tengo {years} años de experiencia y he desarrollado habilidades en {skills}, lo que me permite aportar soluciones con enfoque práctico, trabajo colaborativo y resultados medibles. "
            f"Estoy convencido de que mi perfil puede contribuir al éxito del equipo y al cumplimiento de los objetivos del puesto de {title}."
        )
        answers.append(answer)

    return "\n\n---\n\n".join(answers)


def build_ats_cv(profile: dict, vacancy: dict, common_keywords: List[str], missing_keywords: List[str], match_score: int, cv_text: str = "") -> str:
    name = profile.get("name", "Candidato")
    current_role = profile.get("current_role", "profesional")
    years = profile.get("years", "varios")
    education = profile.get("education", "formación profesional")
    title = vacancy.get("title", "puesto")
    company = vacancy.get("company", "empresa")
    skills = profile.get("skills", []) or ["análisis", "gestión", "trabajo en equipo"]

    if cv_text:
        cv_keywords = set(extract_keywords(cv_text, 80))
    else:
        cv_keywords = set()

    matched = common_keywords[:12] if common_keywords else skills[:6]
    matched = [k for k in matched if k]
    if not matched:
        matched = skills[:6]

    base_skill_pool = list(dict.fromkeys((list(cv_keywords) + list(skills) + matched)[:12]))
    summary_skills = ", ".join(base_skill_pool[:6])
    summary = (
        f"Profesional con {years} años de experiencia en {current_role}, "
        f"especializado en {summary_skills}. "
        f"Experiencia en gestión de proyectos, análisis de datos, coordinación interfuncional, "
        f"seguimiento de indicadores y mejora continua. "
        f"Apasionado por aportar valor a {company} y contribuir al éxito de {title}."
    )

    skill_block = ", ".join(base_skill_pool)
    missing_block = ", ".join(missing_keywords[:8]) if missing_keywords else "ninguno identificado"

    return f"""{name}
{current_role}
{company} | {title}

RESUMEN PROFESIONAL
{summary}

HABILIDADES CLAVE
{skill_block}

EXPERIENCIA LABORAL
- {current_role} con {years} años de experiencia en entornos de gestión, análisis y mejora de procesos.
- Lideré y participé en proyectos orientados a la mejora operativa, coordinación con equipos multifuncionales, seguimiento de resultados y toma de decisiones basada en datos.
- Participé en iniciativas vinculadas a {', '.join(matched[:4])}, con foco en la eficiencia, la calidad operativa y la entrega de resultados medibles.
- Colaboré con diferentes áreas para asegurar cumplimiento de objetivos, calidad operativa, continuidad del negocio y mejora continua.

EDUCACIÓN
- {education}

COMPETENCIAS ADICIONALES
- Trabajo en equipo
- Comunicación efectiva
- Resolución de problemas
- Gestión de tiempos y prioridades
- Orientación a resultados

COINCIDENCIA DETECTADA CON LA VACANTE
- Match estimado: {match_score}%
- Habilidades que coinciden: {', '.join(matched[:8])}
- Áreas a reforzar: {missing_block}

RECOMENDACIÓN ATS
Usar un CV en formato de texto plano, con secciones claras, palabras clave del puesto, y experiencia redactada con resultados medibles y lenguaje directo.
"""


st.set_page_config(page_title="Asistente de postulación", layout="wide")
st.title("🚀 Asistente de postulación para LinkedIn y Computrabajo")
st.caption("Modo seguro: abre tu sesión en el navegador, copia la vacante y genera respuestas y mensajes personalizados.")

st.warning("No automatizamos credenciales ni realizamos login oculto. La forma segura es que abras LinkedIn o Computrabajo desde tu navegador y luego uses esta herramienta para preparar tu aplicación.")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Abrir LinkedIn"):
            webbrowser.open("https://www.linkedin.com/jobs/")
            st.success("Se abrió LinkedIn en tu navegador.")
    with col2:
        if st.button("Abrir Computrabajo"):
            webbrowser.open("https://www.computrabajo.com.pe/")
            st.success("Se abrió Computrabajo en tu navegador.")
cv_file = st.file_uploader("Adjunta tu CV (PDF, DOCX o TXT)", type=["pdf", "docx", "txt"])
with st.form("application_form"):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Perfil del candidato")
        name = st.text_input("Nombre completo", "Ana García")
        current_role = st.text_input("Cargo actual", "Analista de proyectos")
        years = st.text_input("Años de experiencia", "5")
        education = st.text_input("Educación / formación", "Ingeniería de Sistemas")
        skills = st.text_input("Habilidades principales", "SQL, liderazgo, análisis de datos, gestión de proyectos, comunicación")
    with col2:
        st.subheader("Vacante")
        source = st.selectbox("Plataforma", ["LinkedIn", "Computrabajo", "Ambas"])
        title = st.text_input("Título del puesto", "Especialista en proyectos")
        company = st.text_input("Empresa", "Innovación Digital SAC")
        motivation = st.text_input("Motivación principal", "impulsar proyectos con impacto y eficiencia")
        job_url = st.text_input("URL de la vacante (opcional)", "")
        description = st.text_area(
            "Descripción de la vacante o texto copiado",
            "Buscamos profesional con experiencia en análisis de datos, gestión de proyectos, coordinación con áreas funcionales, trabajo en equipo y dominio de SQL. Se valora conocimiento de KPI, reporting y liderazgo de iniciativas de mejora.",
            height=180,
        )

    questions = st.text_area(
        "Preguntas de la plataforma o del formulario",
        "¿Por qué te interesa esta vacante?\n¿Cuáles son tus principales fortalezas?\n¿Por qué serías un buen candidato para este puesto?",
        height=120,
    )
    google_docs_text = st.text_area(
        "Pega aquí el texto de Google Docs, CV externo o un documento similar",
        "",
        height=140,
    )

    submitted = st.form_submit_button("Generar postulación")

if submitted:
    profile = {
        "name": name,
        "current_role": current_role,
        "years": years,
        "education": education,
        "skills": sanitize_skills(skills),
    }
    vacancy = {
        "source": source,
        "title": title,
        "company": company,
        "motivation": motivation,
        "job_url": job_url,
    }

    cv_text = extract_text_from_cv(cv_file) if cv_file else ""
    if google_docs_text.strip():
        cv_text = (cv_text + "\n" + google_docs_text).strip()

    if cv_text:
        if cv_file:
            st.success(f"CV cargado: {cv_file.name}")
        st.info("Se usó el texto de Google Docs o CV externo para complementar la comparación y generar el nuevo CV.")
        cv_profile_text = cv_text
    else:
        cv_profile_text = " ".join(profile["skills"]) + " " + profile["current_role"] + " " + profile["education"]

    common_keywords, missing_keywords, match_score = compare_cv_vs_vacancy(cv_profile_text, description)

    linkedin_message = build_linkedin_message(profile, vacancy)
    computrabajo_message = build_computrabajo_message(profile, vacancy)
    cover_letter = build_cover_letter(profile, vacancy, match_score)
    question_answers = build_question_answers(profile, vacancy, questions)
    ats_cv = build_ats_cv(profile, vacancy, common_keywords, missing_keywords, match_score, cv_text=cv_profile_text)

    st.success(f"Coincidencia CV vs vacante: {match_score}%")

    tabs = st.tabs(["LinkedIn", "Computrabajo", "Carta", "Respuestas a preguntas", "CV ATS recomendado", "Comparación CV-vacante"])

    with tabs[0]:
        st.write(linkedin_message)

    with tabs[1]:
        st.write(computrabajo_message)

    with tabs[2]:
        st.write(cover_letter)

    with tabs[3]:
        st.write(question_answers)

    with tabs[4]:
        st.text_area("Versión ATS del CV", ats_cv, height=420)
        st.download_button(
            label="Descargar CV ATS (.txt)",
            data=ats_cv,
            file_name=f"cv_ats_{name.lower().replace(' ', '_')}.txt",
            mime="text/plain",
        )

    with tabs[5]:
        st.subheader("Habilidades que coinciden")
        st.write(common_keywords[:15] if common_keywords else "No se detectaron coincidencias directas.")
        st.subheader("Requisitos que faltan")
        st.write(missing_keywords[:15] if missing_keywords else "No se detectan requisitos faltantes importantes.")

    with st.expander("Resumen de palabras clave detectadas"):
        st.write(extract_keywords(description, 12))

else:
    st.info("Completa el formulario y genera la propuesta para tu aplicación. Si quieres, adjunta tu CV y compararemos el perfil con la vacante.")
