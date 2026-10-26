# Asistente de Postulación para LinkedIn y Computrabajo

Aplicación web local para generar mensajes personalizados, cartas de presentación, evaluación de compatibilidad y respuestas sugeridas a preguntas de aplicación para vacantes de LinkedIn y Computrabajo.

## Características

- Abre LinkedIn y Computrabajo en tu navegador para iniciar sesión de forma manual.
- Genera una nota de postulación para LinkedIn.
- Genera un mensaje breve para Computrabajo.
- Crea una carta de presentación adaptada a la vacante.
- Evalúa el porcentaje de coincidencia del perfil con la descripción de la oferta.
- Genera respuestas sugeridas para preguntas de la plataforma.
- Funciona sin credenciales externas ni scraping oculto.

## Importante

Esta versión está pensada como asistente de apoyo, no como automatización de login o scraping clandestino. La forma segura es que el usuario abra la plataforma en su navegador, inicie sesión de forma manual y luego copie la vacante o la URL para generar textos y respuestas.

## Requisitos

- Python 3.10+

## Instalación

```bash
cd /Users/ainelynsanchez/Workspace/asistente-postulaciones
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Ejecutar

```bash
python -m streamlit run app.py --server.headless true --server.port 8501
```

Luego abre la URL local que muestre Streamlit en el navegador.

## Uso

1. Abre LinkedIn o Computrabajo desde la app.
2. Inicia sesión manualmente en tu navegador.
3. Copia la descripción o URL de la vacante.
4. Completa tu perfil profesional y preguntas del formulario.
5. Genera la propuesta y adapta el texto antes de enviar.
