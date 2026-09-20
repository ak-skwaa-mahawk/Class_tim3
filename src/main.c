#include "timetable_io.h"
#include "timetable_view.h"

int main(void) {
    TimeTable tt;
    timetable_init(&tt);

    /* Test RFC 4180 escaped quotes, CJK characters, and extended UTF-8 */
    timetable_set_slot(&tt, DAY_MONDAY, 0, 
                       "PHYS 482 \"Symplectic\"", "Lab 3B", "Dr. Miller", 
                       8, 30, 10, 0);

    timetable_set_slot(&tt, DAY_MONDAY, 1, 
                       "日本語会話 (Japanese I)", "Room 101", "田中 先生", 
                       10, 15, 11, 45);

    timetable_set_slot(&tt, DAY_WEDNESDAY, 2, 
                       "Calculus III: Théorie", "Auditorium A", "Prof. Poincaré", 
                       13, 0, 14, 30);

    /* Export to disk */
    timetable_export_csv(&tt, "schedule_test.csv");

    /* Read back using the hardened state machine parser */
    TimeTable reloaded;
    timetable_import_csv(&reloaded, "schedule_test.csv");

    /* Render verified day and week views */
    timetable_print_day(&reloaded, DAY_MONDAY);
    timetable_print_compact_week(&reloaded);

    return 0;
}
