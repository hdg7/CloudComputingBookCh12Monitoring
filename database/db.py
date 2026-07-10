from sqlalchemy import create_engine, Column, Integer, String, Float, Table, MetaData
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///data/results.db"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

detections = Table(
    "detections", metadata,
    Column("id", Integer, primary_key=True),
    Column("label", String),
    Column("confidence", Float),
    Column("x1", Float),
    Column("y1", Float),
    Column("x2", Float),
    Column("y2", Float),
    Column("image_path", String)
)

metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# -------------------------------
# CRUD Operations
# -------------------------------

def create_detection(label, confidence, x1, y1, x2, y2, image_path):
    """Insert a new detection record."""
    session = Session()
    try:
        insert_stmt = detections.insert().values(
            label=label,
            confidence=confidence,
            x1=x1, y1=y1, x2=x2, y2=y2,
            image_path=image_path
        )
        session.execute(insert_stmt)
        session.commit()
        print("Detection created successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error creating detection: {e}")
    finally:
        session.close()

def read_detections(limit=10):
    """Retrieve detection records (default: 10)."""
    session = Session()
    try:
        query = session.execute(detections.select().limit(limit))
        results = query.fetchall()
        # Transforms the results to a json serializable format
        for row in results:
            print(row)
        return results
    finally:
        session.close()

def update_detection(detection_id, **kwargs):
    """Update a detection record by ID."""
    session = Session()
    try:
        update_stmt = detections.update().where(detections.c.id == detection_id).values(**kwargs)
        session.execute(update_stmt)
        session.commit()
        print(f"Detection {detection_id} updated successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error updating detection: {e}")
    finally:
        session.close()

def delete_detection(detection_id):
    """Delete a detection record by ID."""
    session = Session()
    try:
        delete_stmt = detections.delete().where(detections.c.id == detection_id)
        session.execute(delete_stmt)
        session.commit()
        print(f"Detection {detection_id} deleted successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error deleting detection: {e}")
    finally:
        session.close()

# -------------------------------
# Example Usage
# -------------------------------
if __name__ == "__main__":
    # Create a new detection
    create_detection("person", 0.95, 10.0, 20.0, 100.0, 200.0, "images/sample.jpg")

    # Read detections
    print(read_detections())

    # Update detection
    update_detection(1, confidence=0.98, label="human")

    # Delete detection
    delete_detection(1)

    
