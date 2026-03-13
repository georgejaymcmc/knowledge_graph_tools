from neo4j import GraphDatabase


class Neo4jService:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def verify_connectivity(self):
        self.driver.verify_connectivity()

    def get_db_info(self, database="neo4j"):
        with self.driver.session(database=database) as session:

            result = session.run(
                """
                CALL dbms.components()
                YIELD name, versions, edition
                RETURN name, versions[0] AS version, edition
                LIMIT 1
                """
            )

            record = result.single()

            return {
                "component": record["name"],
                "version": record["version"],
                "edition": record["edition"]
            }

    def close(self):
        self.driver.close()