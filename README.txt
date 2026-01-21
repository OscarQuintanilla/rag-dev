
# Servidor RAG con Python

Este proyecto es un servidor basado en Python diseñado para procesar consultas de usuarios utilizando **RAG (Retrieval-Augmented Generation)**. El sistema mejora la precisión de las respuestas recuperando contexto relevante antes de interactuar con el modelo de lenguaje.

## Funcionamiento

1.  **Recepción**: El servidor recibe un mensaje del usuario.
2.  **RAG**: Se realiza una búsqueda semántica en una base de datos vectorial para obtener información específica y actualizada.
3.  **Inferencia**: El sistema se conecta a un servidor de LLM compatible con la **API de OpenAI**, enviando el mensaje original junto con el contexto recuperado.
4.  **Respuesta**: El modelo genera una respuesta enriquecida y precisa que se devuelve al cliente.


## Comandos de Instalación y Ejecución

Para configurar el entorno y poner en marcha el servidor, utilice los siguientes comandos:

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno (API Key, Base URL)
export OPENAI_API_KEY='tu_api_key'

# Iniciar el servidor
python -m uvicorn main:app --reload
```
