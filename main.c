#include "timetable_io.h"
#include "timetable_view.h"

int main(void) {
    TimeTable tt;
    timetable_init(&tt);

    /* Test with ASCII, accents, and East Asian characters to verify border alignment */
    timetable_set_slot(&tt, DAY_MONDAY, 0, 
                       "PHYS 482 (Symplectic)", "Lab 3B", "Dr. Miller", 
                       8, 30, 10, 0);

    timetable_set_slot(&tt, DAY_MONDAY, 1, 
                       "日本語会話 (Japanese I)", "Room 101", "田中 先生", 
                       10, 15, 11, 45);

    timetable_set_slot(&tt, DAY_WEDNESDAY, 2, 
                       "Calculus III: Théorie", "Auditorium A", "Prof. Poincaré", 
                       13, 0, 14, 30);

    /* Render aligned daily view */
    timetable_print_day(&tt, DAY_MONDAY);

    /* Export to CSV */
    timetable_export_csv(&tt, "schedule_test.csv");

    /* Import into fresh struct and render compact week */
    TimeTable imported_tt;
    timetable_import_csv(&imported_tt, "schedule_test.csv");
    timetable_print_compact_week(&imported_tt);

    return 0;
}
