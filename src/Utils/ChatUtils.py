# Aquí se guardan funciones que se utilizan para gestionar mejor el chatbot y sus interacciones. Estas funciones pueden incluir la gestión de historial, formateo de respuestas, entre otros aspectos.

# Gestión del historial de chat
# Recibir y guardar un nuevo mensaje en el historial de mensajes
def add_message_to_history(history, role, content):
    history.append({"role": role, "content": content})

# Inicializa el historial de chat con el prompt de referencia
def history_init():
    return [
        
            # {"role": "system", "content": "Eres un asistente que genera consultas SQL Server (T-SQL). Usa exclusivamente el esquema proporcionado. No inventes tablas, columnas ni schemas. No uses funciones que no existan en SQL Server. Genera solo consultas SELECT. Si no hay información suficiente, responde: 'No puedo generar esta consulta con el esquema actual.'. Dialecto: SQL Server 2019 (T-SQL). [ESQUEMA] {schema_context} [PREGUNTA] {user_question}"
            # }
    ]


    #  {"role": "system", "content": "Eres un chatbot que realiza las labores de cajero en el restaurante Pollo Campestre. Siempre devuelves respuestas a corde a ese empleo, manteniendo el respeto y caballerosidad pero a la vez te mantienes conciso y preciso. Sé lo más breve posible en todo lo que no esté relacionado en responder preguntas. Siempre que respondas preguntas responderás basado únicamente en la información del contexto y nada más, si no está ahí, entonces no lo sabes."},
    # {"role": "assistant", "content": "Entendido."},
    # {"role": "assistant", "content": "¿Cómo puedo ayudarte?"},