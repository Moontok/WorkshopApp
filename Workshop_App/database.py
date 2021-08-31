from sqlite3 import connect, OperationalError


class WorkshopDatabase:
    """Database to store workshop information for quicker access during use."""

    def __init__(self):
        self.connection = connect("workshops.db")
        self.c = self.connection.cursor()


    def create_workshop_tables(self) -> None:
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

        workshops = list()

        try:
            for workshop in self.c.execute("SELECT * FROM workshops"):
                workshops.append(self.make_workshop_dict(workshop))
        except OperationalError:
            print("No database located.")

        for workshop in workshops:            
            workshop["workshop_participant_info_list"] = list(self.get_participant_info(workshop["workshop_id"]))

        return workshops

    def make_workshop_dict(self, workshop_info: tuple) -> dict:
        workshop = dict()

        workshop["workshop_id"] = workshop_info[1]
        workshop["workshop_name"] = workshop_info[2]
        workshop["workshop_start_date_and_time"] = workshop_info[3]
        workshop["workshop_signed_up"] = workshop_info[4]
        workshop["workshop_participant_capacity"] = workshop_info[5]
        workshop["workshop_url"] = workshop_info[6]

        return workshop



    def get_participant_info(self, workshop_id: str):
        """Retrieve the partipant information that corresponds to the ID."""

        participant_info = self.c.execute(
            "SELECT name, email, school FROM participant_information WHERE workshop_id = ?",
            (workshop_id,),
        )

        participants = list()
        for participant in participant_info:
            participants.append({
                self.c.description[0][0]: participant[0], 
                self.c.description[1][0]: participant[1], 
                self.c.description[2][0]: participant[2]
            })

        return participants


    def get_participant_list(self, workshop_id: str) -> list:
        """Return a list of all participants for selected workshop."""

        return [p for p in self.get_participant_info(workshop_id)]


    def drop_tables(self):
        """Clear all tables in the database."""

        self.c.execute(
            "DROP TABLE IF EXISTS workshops;",
        )
        self.c.execute(
            "DROP TABLE IF EXISTS participant_information;",
        )


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, exc_traceback):
        
        self.c.close()
        self.connection.close()

        if exc_type != None or exc_value != None or exc_traceback != None:
            print(f"Exception Type: {exc_type}")
            print(f"Exception Value: {exc_value}")
            print(f"Exception Traceback: {exc_traceback}")


if __name__ == "__main__":
    print("This is a module...")
