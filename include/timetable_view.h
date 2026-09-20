#ifndef TIMETABLE_VIEW_H
#define TIMETABLE_VIEW_H

#include "timetable.h"

void timetable_print_day(const TimeTable *tt, WeekDay day);
void timetable_print_compact_week(const TimeTable *tt);

#endif /* TIMETABLE_VIEW_H */
