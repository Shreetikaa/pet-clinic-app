class Config:
    SECRET_KEY = "vetcare-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///vetcare.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email 
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 465
    MAIL_USERNAME = "your_email@gmail.com"
    MAIL_PASSWORD = "YOUR_APP_PASSWORD"