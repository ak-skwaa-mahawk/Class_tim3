#ifndef TIMETABLE_IO_H
#define TIMETABLE_IO_H

#include "timetable.h"
#include <stdio.h>

void timetable_init(TimeTable *tt);
bool timetable_set_slot(TimeTable *tt, WeekDay day, uint8_t period, 
                        const char *course, const char *room, const char *instructor,
                        uint8_t start_h, uint8_t start_m, uint8_t end_h, uint8_t end_m);

bool timetable_export_csv(const TimeTable *tt, const char *filepath);
bool timetable_import_csv(TimeTable *tt, const char *filepath);

#endif /* TIMETABLE_IO_H */
