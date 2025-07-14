from uptime_kuma_api import UptimeKumaApi, MonitorType
from dotenv import load_dotenv
import os

load_dotenv()
user = os.getenv("UPTIME_KUMA_USER")
password = os.getenv("UPTIME_KUMA_PASSWORD")

def register_services():
    try:
        with UptimeKumaApi('http://localhost:3001') as api:
            api.login(user, password)
            
            # MLflow tracking server
            api.add_monitor(
                type=MonitorType.HTTP,
                name="MLflow",
                url="http://mlflow:5000"
            )

            # Frontend React app
            api.add_monitor(
                type=MonitorType.HTTP,
                name="Frontend",
                url="http://frontend:3000/health"
            )

            # Model deployment service
            api.add_monitor(
                type=MonitorType.HTTP,
                name="Model Deployment",
                url="http://model_deployment:8000/health"
            )

            # PostgreSQL database
            api.add_monitor(
                type=MonitorType.PORT,
                name="PostgreSQL",
                hostname="postgresql",
                port=5432
            )

            # MongoDB database
            api.add_monitor(
                type=MonitorType.PORT,
                name="MongoDB",
                hostname="mongodb",
                port=27017
            )

            # Nginx reverse proxy
            api.add_monitor(
                type=MonitorType.HTTP,
                name="Nginx",
                url="http://nginx:80/health"
            )
            
            print("All monitors registered successfully!")
            
    except Exception as e:
        print(f"Error connecting to Uptime Kuma: {e}")
        print("Make sure Uptime Kuma is running on localhost:3001")
        print("Also check that UPTIME_KUMA_USER and UPTIME_KUMA_PASSWORD are set in your .env file")

def main():
    register_services()

if __name__=="__main__":
    main()