from app.ui.interface import launch_ui
from dotenv import load_dotenv
import torch

load_dotenv()

if __name__ == "__main__":
    
    print(torch.cuda.is_available())
    print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No GPU")

    launch_ui()
