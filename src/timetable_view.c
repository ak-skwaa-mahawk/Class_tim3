#include "timetable_view.h"
#include "unicode_utils.h"
#include <stdio.h>

static const char *DAY_NAMES[DAY_COUNT] = {
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
};

void timetable_print_day(const TimeTable *tt, WeekDay day) {
    if (!tt || day >= DAY_COUNT) return;

    printf("\n┌────────────────────────────────────────────────────────────────────────┐\n");
    printf("│ Timetable: ");
    utf8_print_truncated_padded(DAY_NAMES[day], 59);
    printf(" │\n");
    printf("├────────┬───────────────┬──────────────────────┬──────────┬─────────────┤\n");
    printf("│ Period │ Time          │ Course               │ Room     │ Instructor  │\n");
    printf("├────────┼───────────────┼──────────────────────┼──────────┼─────────────┤\n");

    for (int p = 0; p < MAX_PERIODS_PER_DAY; p++) {
        const ClassSlot *s = &tt->schedule[day][p];
        if (!s->is_active) continue;

        char time_buf[16];
        snprintf(time_buf, sizeof(time_buf), "%02d:%02d-%02d:%02d",
                 s->start_time.hour, s->start_time.minute,
                 s->end_time.hour, s->end_time.minute);

        printf("│   %02d   │ ", p + 1);
        utf8_print_truncated_padded(time_buf, 13);
        printf(" │ ");
        utf8_print_truncated_padded(s->course_name, 20);
        printf(" │ ");
        utf8_print_truncated_padded(s->room, 8);
        printf(" │ ");
        utf8_print_truncated_padded(s->instructor, 11);
        printf(" │\n");
    }

    printf("└────────┴───────────────┴──────────────────────┴──────────┴─────────────┘\n");
}

void timetable_print_compact_week(const TimeTable *tt) {
    if (!tt) return;

    printf("\n=== Active Scheduled Slots This Week ===\n");
    for (int d = 0; d < DAY_COUNT; d++) {
        bool has_classes = false;
        for (int p = 0; p < MAX_PERIODS_PER_DAY; p++) {
            if (tt->schedule[d][p].is_active) {
                has_classes = true;
                break;
            }
        }
        if (!has_classes) continue;

        printf("\n[%s]\n", DAY_NAMES[d]);
        for (int p = 0; p < MAX_PERIODS_PER_DAY; p++) {
            const ClassSlot *s = &tt->schedule[d][p];
            if (s->is_active) {
                printf("  Slot %02d | %02d:%02d-%02d:%02d | %s (%s) — %s\n",
                       p + 1,
                       s->start_time.hour, s->start_time.minute,
                       s->end_time.hour, s->end_time.minute,
                       s->course_name, s->room, s->instructor);
            }
        }
    }
}
