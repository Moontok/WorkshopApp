from workshop_tool import WorkshopsTool
from spread_sheet_base_creator import SpreadSheetBaseCreator
from google_sheets_tool import GoogleSheetsTool

class GoogleSheetCreator(SpreadSheetBaseCreator):

    def __init__(self):
        super().__init__()


    def export_workshops_info(self, ws: WorkshopsTool) -> None:
        """Exports the searched workshop information to an google sheet."""
        spread_sheet_id = "1nYTi7s1VDFXsqupYs7ZPe_9_SrDL2hAAI_i0jnEB5hw"

        gs = GoogleSheetsTool(spread_sheet_id)
        workshops: list = ws.get_most_recent_search_results()

        workshops_rows = list()

        for workshop in workshops:
            row: list = self.build_row_for_workshop(ws.get_co_op_info(), workshop)
            workshops_rows.append(row[:8])
        workshops_rows.sort()
        workshops_rows.append([])
        workshops_rows.append(["Total:", f"{len(workshops)}", "", "Signed Up:", f"=SUM(E3:E{len(workshops)+3})"])        

        self.format_workshops_sheet(gs, len(workshops))

        gs.add_values_request("Workshops!A1", [["Workshops At A Glance"]])
        gs.add_values_request("Workshops!A3", workshops_rows)
        gs.values_batch_update()
        
        # gs.add_sheet_request("Attendance")
        # gs.batch_update()


    def format_workshops_sheet(self, gs: GoogleSheetsTool, number_of_workshops: int) -> None:
        """Formats excel workshops sheet."""
        
        gs.change_google_sheet_title_request("Workshop Info")
        gs.change_sheet_name_request("Sheet1", "Workshops")
        gs.format_font_range_request("Workshops!A1:A1", font_size=18, bold=True)
        gs.fill_range_request("Workshops!A1:H1", fill_color=(0.0, 0.9, 0.7))
        gs.format_font_range_request(f"Workshops!A{number_of_workshops + 4}:E{number_of_workshops + 4}", bold=True)
        gs.format_range_outer_border("Workshops!A1:H1")
        gs.merge_cell_range_request("Workshops!A1:H1")
        gs.resize_request("Workshops!A:A", 100)
        gs.resize_request("Workshops!B:B", 50)
        gs.resize_request("Workshops!C:C", 500)
        gs.resize_request("Workshops!D:D", 120)
        gs.resize_request("Workshops!E:F", 40)
        gs.resize_request("Workshops!G:G", 350)
        gs.resize_request("Workshops!H:H", 450)
        gs.resize_request("Workshops!1:1", 30)

        gs.batch_update()


    def format_generated_ws_sheet(self, worksheet) -> None:
        """General format for each Co-op sheet."""
        pass


    def format_attendance_sheet(self, worksheet) -> None:    
        """Formats excel attendance sheet."""
        pass


if __name__ == "__main__":
    print("This is a module...")