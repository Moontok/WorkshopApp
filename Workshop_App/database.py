from sqlite3 import connect, OperationalError


class WorkshopDatabase:
    """Database to store workshop information for quicker access during use."""

    def __init__(self):
        self.connection = connect("workshops.db")
        self.c = self.connection.cursor()


    def create_workshops_tables(self) -> None:
        """Setup workshop database."""

        # Clear the tables in the database.
        self.drop_tables()

        self.c.execute(
            """CREATE TABLE IF NOT EXISTS workshops (
                    id INTEGER PRIMARY KEY,
                    workshop_id TEXT NOT NULL,
                    workshop_name TEXT NOT NULL,
                    workshop_start_date_and_time TEXT NOT NULL,
                    workshop_signed_up TEXT NOT NULL,
                    workshop_participant_capacity TEXT NOT NULL,
                    workshop_url TEXT NOT NULL
                    );"""
        )

        self.c.execute(
            """CREATE TABLE IF NOT EXISTS participant_information (
                    id INTEGER PRIMARY KEY,
                    workshop_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    school TEXT NOT NULL
                    );"""
        )


    def add_workshop(self, ws_info: dict) -> None:
        """Add a single workshop to database."""

        self.c.execute(
            "INSERT INTO workshops (workshop_id, workshop_name, workshop_start_date_and_time, workshop_signed_up, workshop_participant_capacity, workshop_url) VALUES (?,?,?,?,?,?)",
            (
                ws_info["workshop_id"],
                ws_info["workshop_name"],
                ws_info["workshop_start_date_and_time"],
                ws_info["workshop_signed_up"],
                ws_info["workshop_participant_capacity"],
                ws_info["workshop_url"],
            ),
        )

        for participant in ws_info["workshop_participant_info_list"]:
            self.c.execute(
                "INSERT INTO participant_information (workshop_id, name, email, school) VALUES (?,?,?,?)",
                (
                    ws_info["workshop_id"],
                    participant["name"],
                    participant["email"],
                    participant["school"],
                ),
            )

        self.connection.commit()
    
    
    def get_all_workshops(self) -> list:
        """Return all workshops in database for testing purposes."""

        workshops: list = []

        try:
            for workshop in self.c.execute("SELECT * FROM workshops"):
                workshops.append(workshop)
        except OperationalError:
            print("No database located.")

        return workshops


    def get_participant_info(self, workshop_id: str):
        """Retrieve the partipant information that corresponds to the ID."""
        return self.c.execute(
            "SELECT name, email, school FROM participant_information WHERE workshop_id = ?",
            (workshop_id,),
        )


    def drop_tables(self):
        """Clear all tables in the database."""

        self.c.execute(
            "DROP TABLE IF EXISTS workshops;",
        )
        self.c.execute(
            "DROP TABLE IF EXISTS participant_information;",
        )


    def close_connection(self):
        """Closes the database connection."""

        self.c.close()
        self.connection.close()


    def __enter__(self):
        database = WorkshopDatabase()        
        database.create_workshops_tables()
        return database


    def __exit__(self):
        self.close_connection()


if __name__ == "__main__":
    print("This is a module...")
