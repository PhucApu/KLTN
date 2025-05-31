# neo4j_driver.py
from neo4j import GraphDatabase

# Thay thông tin kết nối với Neo4j của bạn
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "123123123"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def close_driver():
    driver.close()

