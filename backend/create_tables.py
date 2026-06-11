from database.db import Base
from database.db import engine

import database.models

Base.metadata.create_all(bind=engine)

print("Tables Created Successfully")