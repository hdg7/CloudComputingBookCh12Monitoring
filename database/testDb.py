import pytest
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker

# Import functions from db.py
from db import create_detection, read_detections, update_detection, delete_detection

@pytest.fixture(scope="function")
def setup_db(monkeypatch):
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:")
    metadata = MetaData()

    # Create detections table
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

    # Patch Session and detections in db.py
    Session = sessionmaker(bind=engine)
    monkeypatch.setattr("db.Session", Session)
    monkeypatch.setattr("db.detections", detections)

    return Session, detections


def test_create_and_read_detection(setup_db):
    Session, detections = setup_db

    # Create detection
    create_detection("car", 0.95, 10, 20, 30, 40, "image.jpg")

    # Read detections
    results = read_detections()
    assert len(results) == 1
    row = results[0]
    assert row.label == "car"
    assert row.confidence == 0.95
    assert row.image_path == "image.jpg"


def test_update_detection(setup_db):
    Session, detections = setup_db

    # Insert initial detection
    create_detection("bus", 0.85, 5, 10, 15, 20, "bus.jpg")

    # Update label
    update_detection(1, label="truck")

    # Verify update
    session = Session()
    updated = session.execute(detections.select()).fetchone()
    assert updated.label == "truck"
    session.close()


def test_delete_detection(setup_db):
    Session, detections = setup_db

    # Insert detection
    create_detection("person", 0.99, 1, 2, 3, 4, "person.jpg")

    # Delete detection
    delete_detection(1)

    # Verify deletion
    session = Session()
    remaining = session.execute(detections.select()).fetchall()
    assert len(remaining) == 0
    session.close()


def test_read_limit(setup_db):
    Session, detections = setup_db

    # Insert multiple detections
    for i in range(15):
        create_detection(f"obj{i}", 0.8, i, i+1, i+2, i+3, f"img{i}.jpg")

    # Read with limit
    results = read_detections(limit=10)
    assert len(results) == 10
