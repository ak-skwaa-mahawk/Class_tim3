/* timetable_io.c */
#include "timetable_io.h"
#include "unicode_utils.h"
#include <string.h>
#include <stdlib.h>

void timetable_init(TimeTable *tt) {
    if (!tt) return;
    memset(tt, 0, sizeof(TimeTable));
}

bool timetable_set_slot(TimeTable *tt, WeekDay day, uint8_t period, 
                        const char *course, const char *room, const char *instructor,
                        uint8_t start_h, uint8_t start_m, uint8_t end_h, uint8_t end_m) {
    if (!tt || day >= DAY_COUNT || period >= MAX_PERIODS_PER_DAY) {
        return false;
    }
    if (!utf8_validate_string(course, MAX_COURSE_NAME_LEN) ||
        !utf8_validate_string(room, MAX_ROOM_NAME_LEN) ||
        !utf8_validate_string(instructor, MAX_INSTRUCTOR_LEN)) {
        return false;
    }

    ClassSlot *slot = &tt->schedule[day][period];
    strncpy(slot->course_name, course, sizeof(slot->course_name) - 1);
    strncpy(slot->room, room, sizeof(slot->room) - 1);
    strncpy(slot->instructor, instructor, sizeof(slot->instructor) - 1);
    slot->start_time.hour = start_h;
    slot->start_time.minute = start_m;
    slot->end_time.hour = end_h;
    slot->end_time.minute = end_m;
    slot->is_active = true;

    return true;
}

bool timetable_export_csv(const TimeTable *tt, const char *filepath) {
    if (!tt || !filepath) return false;
    FILE *fp = fopen(filepath, "w");
    if (!fp) return false;

    /* Write CSV Header */
    fprintf(fp, "Day,Period,Course,Room,Instructor,StartTime,EndTime\n");

    for (int d = 0; d < DAY_COUNT; d++) {
        for (int p = 0; p < MAX_PERIODS_PER_DAY; p++) {
            const ClassSlot *s = &tt->schedule[d][p];
            if (s->is_active) {
                fprintf(fp, "%d,%d,\"%s\",\"%s\",\"%s\",%02d:%02d,%02d:%02d\n",
                        d, p, s->course_name, s->room, s->instructor,
                        s->start_time.hour, s->start_time.minute,
                        s->end_time.hour, s->end_time.minute);
            }
        }
    }

    fclose(fp);
    return true;
}

bool timetable_import_csv(TimeTable *tt, const char *filepath) {
    if (!tt || !filepath) return false;
    FILE *fp = fopen(filepath, "r");
    if (!fp) return false;

    char line[512];
    if (!fgets(line, sizeof(line), fp)) {
        fclose(fp);
        return false;
    }

    timetable_init(tt);

    while (fgets(line, sizeof(line), fp)) {
        int day = 0, period = 0;
        char course[MAX_COURSE_NAME_LEN] = {0};
        char room[MAX_ROOM_NAME_LEN] = {0};
        char instructor[MAX_INSTRUCTOR_LEN] = {0};
        int sh = 0, sm = 0, eh = 0, em = 0;

        /* Simple formatted scanner handling quote-delimited strings */
        int parsed = sscanf(line, "%d,%d,\"%127[^\"]\",\"%63[^\"]\",\"%127[^\"]\",%d:%d,%d:%d",
                            &day, &period, course, room, instructor, &sh, &sm, &eh, &em);

        if (parsed == 9) {
            timetable_set_slot(tt, (WeekDay)day, (uint8_t)period,
                               course, room, instructor,
                               (uint8_t)sh, (uint8_t)sm, (uint8_t)eh, (uint8_t)em);
        }
    }

    fclose(fp);
    return true;
}
