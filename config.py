class Config:
    SECRET_KEY = "vetcare-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///vetcare.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email 
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 465
    MAIL_USERNAME = "shreetika327@gmail.com"
    MAIL_PASSWORD = "svvo kqye mvmv rshc"