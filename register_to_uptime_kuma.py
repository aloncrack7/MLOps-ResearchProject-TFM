from uptime_kuma_api import UptimeKumaApi, MonitorType
from dotenv import load_dotenv
import os

load_dotenv()
user = os.getenv("UPTIME_KUMA_USER")
password = os.getenv("UPTIME_KUMA_PASSWORD")

def monitor_exists(api, name):
    monitors = api.get_monitors()
    return any(m['name'] == name for m in monitors)

def register_services():
    try:
        with UptimeKumaApi('http://localhost:3001') as api:
            api.login(user, password)

            monitors_to_add = [
                {"type": MonitorType.HTTP, "name": "MLflow", "url": "http://mlflow:5000"},
                {"type": MonitorType.HTTP, "name": "Frontend", "url": "http://frontend:3000/health"},
                {"type": MonitorType.HTTP, "name": "Model Deployment", "url": "http://model_deployment:8000/health"},
                {"type": MonitorType.PORT, "name": "PostgreSQL", "hostname": "postgresql", "port": 5432},
                {"type": MonitorType.PORT, "name": "MongoDB", "hostname": "mongodb", "port": 27017},
                {"type": MonitorType.HTTP, "name": "Nginx", "url": "http://nginx:80/health"},
            ]

            for monitor in monitors_to_add:
                if monitor_exists(api, monitor["name"]):
                    print(f"Monitor '{monitor['name']}' already exists. Skipping.")
                    continue
                api.add_monitor(**monitor)
                print(f"Monitor '{monitor['name']}' registered.")

            print("All monitors processed successfully!")

    except Exception as e:
        print(f"Error connecting to Uptime Kuma: {e}")
        print("Make sure Uptime Kuma is running on localhost:3001")
        print("Also check that UPTIME_KUMA_USER and UPTIME_KUMA_PASSWORD are set in your .env file")

def main():
    register_services()

if __name__=="__main__":
    main()
