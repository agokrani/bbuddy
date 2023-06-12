from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from pyfcm import FCMNotification

# Firebase Cloud Messaging configuration
API_KEY = "MDJhNmMyMmUtMWM3YS00Y2RiLTliY2UtNTdiYTU4OTBiNTkx"
APP_ID = "062dd59b-6e72-45c2-b102-6108f584ed5f"
push_service = FCMNotification(api_key=API_KEY)

# FastAPI app
app = FastAPI()

# Dictionary to store the last check-in and reflection timestamps for each user
user_timestamps = {}

# Helper function to send push notifications
def send_push_notification(device_token, message):
    push_service.notify_single_device(
        registration_id=device_token,
        message_title="Reminder",
        message_body=message
    )

# Task to check for users who haven't done a check-in in 6 hours
def check_check_in():
    current_time = datetime.now()

    for user, timestamps in user_timestamps.items():
        last_check_in = timestamps.get("check_in")
        
        if last_check_in and current_time - last_check_in >= timedelta(hours=6):
            device_token = timestamps.get("device_token")
            if device_token:
                message = "You haven't performed a check-in in the last 6 hours. Please remember to check-in."
                send_push_notification(device_token, message)

# Task to check for users who haven't done a reflection in 24 hours
def check_reflection():
    current_time = datetime.now()

    for user, timestamps in user_timestamps.items():
        last_reflection = timestamps.get("reflection")
        
        if last_reflection and current_time - last_reflection >= timedelta(days=1):
            device_token = timestamps.get("device_token")
            if device_token:
                message = "You haven't submitted a reflection in the last 24 hours. Please remember to submit your reflection."
                send_push_notification(device_token, message)

# Route to update user timestamps (e.g., when a check-in or reflection is performed)
@app.post("/update-timestamps")
def update_timestamps(user_id: str, timestamp_type: str):
    current_time = datetime.now()
    device_token = "USER_DEVICE_TOKEN"  # Replace with the actual device token of the user

    if user_id not in user_timestamps:
        user_timestamps[user_id] = {}

    user_timestamps[user_id][timestamp_type] = current_time
    user_timestamps[user_id]["device_token"] = device_token

    return {"message": "Timestamps updated successfully."}

# Initialize the scheduler and schedule the tasks
scheduler = BackgroundScheduler()
scheduler.add_job(check_check_in, "interval", hours=1)  # Run every hour
scheduler.add_job(check_reflection, "interval", hours=1)  # Run every hour
scheduler.start()

# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
