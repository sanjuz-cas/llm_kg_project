import os
import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Neo4jUploader:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def load_data_from_csv(self, file_path):
        """
        Loads the antibiotic resistance data from a CSV file, creates nodes and relationships
        in the Neo4j database.
        """
        # Read the CSV and drop rows where Patient_ID is missing
        df = pd.read_csv(file_path).dropna(subset=['Patient_ID'])

        with self.driver.session() as session:
            # Create constraints for uniqueness
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Patient) REQUIRE p.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (g:Gene) REQUIRE g.name IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Specimen) REQUIRE s.name IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (o:Outcome) REQUIRE o.name IS UNIQUE")

            print(f"Processing {len(df)} rows from the CSV file...")

            # Loop through each row of the dataframe
            for index, row in df.iterrows():
                # ✨ **THE FIX IS HERE** ✨
                # We now check if the Patient_ID is valid before proceeding.
                # While we already dropped NaNs, this is an extra safeguard.
                if pd.notna(row['Patient_ID']):
                    # Use a MERGE query to create or find the Patient node
                    session.run("""
                        MERGE (p:Patient {id: $patient_id})
                        ON CREATE SET p.age = $age, p.gender = $gender
                        """,
                        patient_id=row['Patient_ID'], age=row['Age'], gender=row['Gender']
                    )

                    # Create or find Specimen and Outcome nodes and create relationships
                    session.run("""
                        MATCH (p:Patient {id: $patient_id})
                        MERGE (s:Specimen {name: $specimen_type})
                        MERGE (p)-[:HAS_SPECIMEN]->(s)
                        """,
                        patient_id=row['Patient_ID'], specimen_type=row['Specimen_Type']
                    )

                    session.run("""
                        MATCH (p:Patient {id: $patient_id})
                        MERGE (o:Outcome {name: $outcome})
                        MERGE (p)-[:HAS_OUTCOME]->(o)
                        """,
                        patient_id=row['Patient_ID'], outcome=row['Outcome']
                    )

                    # Handle resistance genes, which can be 'None'
                    if pd.notna(row['Resistance_Genes']) and row['Resistance_Genes'] != 'None':
                        session.run("""
                            MATCH (p:Patient {id: $patient_id})
                            MERGE (g:Gene {name: $gene_name})
                            MERGE (p)-[:HAS_GENE]->(g)
                            """,
                            patient_id=row['Patient_ID'], gene_name=row['Resistance_Genes']
                        )

            print("Data loaded successfully into Neo4j.")


if __name__ == "__main__":
    csv_file = "C:\\Users\\SANJAY\\Desktop\\llm_kg_project\\antibiotic_resistance_tracking (1).csv"
    
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    
    uploader = Neo4jUploader(uri, user, password)
    
    # Optional: A function to clear the database before running
    # This is useful for development to avoid duplicate data
    with uploader.driver.session() as session:
        print("Clearing the database...")
        session.run("MATCH (n) DETACH DELETE n")

    uploader.load_data_from_csv(csv_file)
    uploader.close()