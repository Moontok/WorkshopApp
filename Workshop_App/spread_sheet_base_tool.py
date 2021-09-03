from abc import ABC, abstractmethod
from datetime import datetime
from workshop_tool import WorkshopsTool
from gui_window import GuiWindow

class SpreadSheetBaseTool(ABC):
    """Abstract class for the spread sheet tools."""

    def __init__(self):        
        self.co_op_abbreviations = list()

    @abstractmethod
    def export_workshops_info(self, ui: GuiWindow, ws: WorkshopsTool) -> None:
        """Exports the searched workshop information to a file."""
        raise NotImplementedError
        
    @abstractmethod
    def format_workshops_sheet(self, worksheet) -> None:
        """Formats workshops sheet."""
        raise NotImplementedError

    @abstractmethod
    def format_generated_ws_sheet(self, worksheet) -> None:
        """General format for each Co-op sheet."""        
        raise NotImplementedError

    @abstractmethod
    def format_attendance_sheet(self, worksheet) -> None:    
        """Formats attendance sheet."""
        raise NotImplementedError 

    def build_row_for_workshop(self, co_op_session_location: dict, workshop: dict) -> list:
        """Build out the contents of one spread sheet row entry. """
        
        location: list = workshop["workshop_location"].split(" - ")[0]

        row = [
            co_op_session_location[location]["abbr"],
            workshop["workshop_id"],
            workshop["workshop_name"],
            workshop["workshop_start_date_and_time"],
            int(workshop["workshop_signed_up"]),
            workshop["workshop_participant_capacity"],
            co_op_session_location[location]["pd_doc_text"],
            workshop["workshop_url"],
            workshop["workshop_participant_info_list"],
            workshop["workshop_description"],
            workshop["workshop_location"],            
            workshop["workshop_dates"].split("_"),
            workshop["workshop_credits"],
            workshop["workshop_fees"]
        ]

        return row

    
    def format_dates(self, workshop: dict) -> str:
        """Formats all the dates."""

        dates_text: str = ""
        dates: list = [datetime.strptime(date, "%m/%d/%Y") for date in workshop["workshop_dates"].split("_")]
        if len(dates) > 1:
            for date in dates:
                if dates_text == "":
                    dates_text = date.strftime("%b %d")
                else:
                    dates_text = f'{dates_text}, {date.strftime("%b %d")}'
        else:
            dates_text = dates[0].strftime("%b %d")

        return dates_text   


if __name__ == "__main__":
    print("This is a module...")
    