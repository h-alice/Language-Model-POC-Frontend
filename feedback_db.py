from sqlalchemy import create_engine, MetaData, Table, Column
from sqlalchemy import Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Create a MetaData object for the database tables
Base = declarative_base()

# Define the User model class
class UserFeedback(Base):
    id = Column(Integer, primary_key=True)
    feedback = Column(Integer, nullable=False)
    feedback_text = Column(String, nullable=True)
    user_prompt = Column(String, nullable=False)
    response = Column(String, nullable=False)


if __name__ == "__main__":
    # Create a SQLite database engine
    engine = create_engine("sqlite:///feedback.db")

    # Create the users table
    Base.metadata.create_all(engine)

    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Add a user to the database
    user = UserFeedback(feedback=1, feedback_text="👍", user_prompt="What is the capital of France?", response="The capital of France is Paris.")
    session.add(user)
    session.commit()

    # Query the database
    for user in session.query(UserFeedback):
        print(user.id, user.feedback, user.feedback_text, user.user_prompt, user.response)
