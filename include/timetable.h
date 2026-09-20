#ifndef TIMETABLE_H
#define TIMETABLE_H

#include "unicode_constants.h"

#define MAX_DAYS_IN_WEEK     7
#define MAX_PERIODS_PER_DAY  12
#define MAX_COURSE_NAME_LEN  128
#define MAX_ROOM_NAME_LEN    64
#define MAX_INSTRUCTOR_LEN   128

typedef enum {
    DAY_MONDAY = 0,
    DAY_TUESDAY,
    DAY_WEDNESDAY,
    DAY_THURSDAY,
    DAY_FRIDAY,
    DAY_SATURDAY,
    DAY_SUNDAY,
    DAY_COUNT
} WeekDay;

typedef struct {
    uint8_t hour;   /* 0-23 */
    uint8_t minute; /* 0-59 */
} TimeStamp;

typedef struct {
    char course_name[MAX_COURSE_NAME_LEN];
    char instructor[MAX_INSTRUCTOR_LEN];
    char room[MAX_ROOM_NAME_LEN];
    TimeStamp start_time;
    TimeStamp end_time;
    bool is_active;
} ClassSlot;

typedef struct {
    ClassSlot schedule[MAX_DAYS_IN_WEEK][MAX_PERIODS_PER_DAY];
} TimeTable;

#endif /* TIMETABLE_H */
