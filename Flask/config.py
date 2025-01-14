class Config:
    SECRET_KEY = 'popes'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@127.0.0.1/parking'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
