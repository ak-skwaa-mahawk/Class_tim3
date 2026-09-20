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

    strncpy(slot->course_name, course ? course : "", sizeof(slot->course_name) - 1);
    slot->course_name[sizeof(slot->course_name) - 1] = '\0';

    strncpy(slot->room, room ? room : "", sizeof(slot->room) - 1);
    slot->room[sizeof(slot->room) - 1] = '\0';

    strncpy(slot->instructor, instructor ? instructor : "", sizeof(slot->instructor) - 1);
    slot->instructor[sizeof(slot->instructor) - 1] = '\0';

    slot->start_time.hour = start_h;
    slot->start_time.minute = start_m;
    slot->end_time.hour = end_h;
    slot->end_time.minute = end_m;
    slot->is_active = true;

    return true;
}

static void write_escaped_csv_field(FILE *fp, const char *field) {
    fputc('"', fp);
    for (const char *p = field; *p; p++) {
        if (*p == '"') {
            fputc('"', fp);
        }
        fputc(*p, fp);
    }
    fputc('"', fp);
}

bool timetable_export_csv(const TimeTable *tt, const char *filepath) {
    if (!tt || !filepath) return false;
    FILE *fp = fopen(filepath, "w");
    if (!fp) return false;

    fprintf(fp, "Day,Period,Course,Room,Instructor,StartTime,EndTime\n");

    for (int d = 0; d < DAY_COUNT; d++) {
        for (int p = 0; p < MAX_PERIODS_PER_DAY; p++) {
            const ClassSlot *s = &tt->schedule[d][p];
            if (s->is_active) {
                fprintf(fp, "%d,%d,", d, p);
                write_escaped_csv_field(fp, s->course_name);
                fputc(',', fp);
                write_escaped_csv_field(fp, s->room);
                fputc(',', fp);
                write_escaped_csv_field(fp, s->instructor);
                fprintf(fp, ",%02d:%02d,%02d:%02d\n",
                        s->start_time.hour, s->start_time.minute,
                        s->end_time.hour, s->end_time.minute);
            }
        }
    }

    fclose(fp);
    return true;
}

static int parse_csv_line(char *line, char *fields[], int max_fields) {
    int field_count = 0;
    char *cursor = line;
    bool in_quotes = false;
    char *token_start = cursor;

    while (*cursor && field_count < max_fields) {
        if (*cursor == '"') {
            if (in_quotes && *(cursor + 1) == '"') {
                cursor += 2;
                continue;
            }
            in_quotes = !in_quotes;
        } else if (*cursor == ',' && !in_quotes) {
            *cursor = '\0';
            fields[field_count++] = token_start;
            token_start = cursor + 1;
        } else if (*cursor == '\r' || *cursor == '\n') {
            *cursor = '\0';
            break;
        }
        cursor++;
    }

    if (field_count < max_fields) {
        fields[field_count++] = token_start;
    }

    for (int i = 0; i < field_count; i++) {
        char *f = fields[i];
        size_t flen = strlen(f);

        if (flen >= 2 && f[0] == '"' && f[flen - 1] == '"') {
            f[flen - 1] = '\0';
            f++;
        }

        char *r = f;
        char *w = f;
        while (*r) {
            if (*r == '"' && *(r + 1) == '"') {
                *w++ = '"';
                r += 2;
            } else {
                *w++ = *r++;
            }
        }
        *w = '\0';
        fields[i] = f;
    }

    return field_count;
}

bool timetable_import_csv(TimeTable *tt, const char *filepath) {
    if (!tt || !filepath) return false;
    FILE *fp = fopen(filepath, "r");
    if (!fp) return false;

    char line[1024];
    if (!fgets(line, sizeof(line), fp)) {
        fclose(fp);
        return false;
    }

    timetable_init(tt);

    while (fgets(line, sizeof(line), fp)) {
        char *fields[7];
        int count = parse_csv_line(line, fields, 7);
        if (count < 7) continue;

        int day = atoi(fields[0]);
        int period = atoi(fields[1]);
        const char *course = fields[2];
        const char *room = fields[3];
        const char *instructor = fields[4];

        int sh = 0, sm = 0, eh = 0, em = 0;
        sscanf(fields[5], "%d:%d", &sh, &sm);
        sscanf(fields[6], "%d:%d", &eh, &em);

        if (day >= 0 && day < DAY_COUNT && period >= 0 && period < MAX_PERIODS_PER_DAY) {
            timetable_set_slot(tt, (WeekDay)day, (uint8_t)period,
                               course, room, instructor,
                               (uint8_t)sh, (uint8_t)sm, (uint8_t)eh, (uint8_t)em);
        }
    }

    fclose(fp);
    return true;
}
