from .services.chat_service import ChatService
from .redis_client import get_redis

def start_analysis(chat_id, user_input):
    # Implement the analysis logic here
    # This function will run as a background task
    try:
        # Example: Process the user input and update the chat
        result = ChatService.process_user_input(chat_id, user_input)
        
        # Update the job status in Redis
        redis_client = get_redis()
        redis_client.set(f"job_status:{chat_id}", "completed")
        redis_client.set(f"job_result:{chat_id}", str(result))
    except Exception as e:
        # Update the job status in case of an error
        redis_client = get_redis()
        redis_client.set(f"job_status:{chat_id}", "failed")
        redis_client.set(f"job_error:{chat_id}", str(e))