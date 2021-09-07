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
        
        gs.add_sheet_request("Attendance")
        gs.batch_update()

        self.format_attendance_sheet(gs)


    def format_workshops_sheet(self, gs: GoogleSheetsTool, number_of_workshops: int) -> None:
        """Formats excel workshops sheet."""
        
        sheet_name: str = "Workshops"

        gs.change_google_sheet_title_request("Workshop Info")
        gs.change_sheet_name_request("Sheet1", "Workshops")
        gs.format_font_range_request(f"{sheet_name}!A1:A1", font_size=18, bold=True)
        gs.fill_range_request(f"{sheet_name}!A1:H1", fill_color=(0.68, 0.92, 0.68))
        gs.format_font_range_request(f"{sheet_name}!A{number_of_workshops + 4}:E{number_of_workshops + 4}", bold=True)
        gs.set_outer_border_range_request(f"{sheet_name}!A1:H1")
        gs.merge_cells_range_request(f"{sheet_name}!A1:H1")
        gs.resize_request(f"{sheet_name}!A:A", 100)
        gs.resize_request(f"{sheet_name}!B:B", 50)
        gs.resize_request(f"{sheet_name}!C:C", 500)
        gs.resize_request(f"{sheet_name}!D:D", 120)
        gs.resize_request(f"{sheet_name}!E:F", 40)
        gs.resize_request(f"{sheet_name}!G:G", 350)
        gs.resize_request(f"{sheet_name}!H:H", 450)
        gs.resize_request(f"{sheet_name}!1:1", 30)

        gs.batch_update()


    def format_generated_ws_sheet(self, gs: GoogleSheetsTool) -> None:
        """General format for each Co-op sheet."""
        
        pass


    def format_attendance_sheet(self, gs: GoogleSheetsTool) -> None:    
        """Formats excel attendance sheet."""
        
        sheet_name: str = "Attendance"

        gs.merge_cells_range_request(f"{sheet_name}!A1:B1")
        gs.merge_cells_range_request(f"{sheet_name}!A2:B2")
        gs.merge_cells_range_request(f"{sheet_name}!C1:E1")
        gs.merge_cells_range_request(f"{sheet_name}!C2:E2")

        gs.resize_request(f"{sheet_name}!A:A", 200)
        gs.resize_request(f"{sheet_name}!B:B", 200)
        gs.resize_request(f"{sheet_name}!C:C", 200)
        gs.resize_request(f"{sheet_name}!D:D", 100)
        gs.resize_request(f"{sheet_name}!E:E", 200)

        gs.format_font_range_request(f"{sheet_name}!A1:A2", font_size=16, bold=True)
        gs.align_cells_range_request(f"{sheet_name}!A1:A2", "RIGHT")

        gs.format_font_range_request(f"{sheet_name}!C1:E2", font_size=16, bold=True, text_color=(0.68, 0.92, 0.68))
        gs.fill_range_request(f"{sheet_name}!C1:E2", (0.2, 0.2, 0.2))
        gs.align_cells_range_request(f"{sheet_name}!C1:E2", "CENTER")
        gs.set_outer_border_range_request(f"{sheet_name}!A1:E2", "SOLID_THICK")
        
        gs.batch_update()


if __name__ == "__main__":
    print("This is a module...")