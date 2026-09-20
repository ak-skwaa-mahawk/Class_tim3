CC = gcc
CFLAGS = -std=c11 -Wall -Wextra -Wpedantic -O3 -fPIC -Iinclude
LDFLAGS = -lm

# Binaries & Libraries
CLI_TARGET = timetable_app
LIB_TARGET = libyoshida4.so
LATTICE_BIN = yoshida4_lattice

TIMETABLE_SRCS = src/main.c src/unicode_utils.c src/timetable_io.c src/timetable_view.c
TIMETABLE_OBJS = $(TIMETABLE_SRCS:.c=.o)

all: $(CLI_TARGET) $(LIB_TARGET) $(LATTICE_BIN)

$(CLI_TARGET): $(TIMETABLE_OBJS)
	$(CC) $(CFLAGS) -o $@ $(TIMETABLE_OBJS)

$(LIB_TARGET): src/yoshida4_api.c
	$(CC) $(CFLAGS) -shared -o $@ $< $(LDFLAGS)

$(LATTICE_BIN): yoshida4_lattice.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(TIMETABLE_OBJS) $(CLI_TARGET) $(LIB_TARGET) $(LATTICE_BIN) schedule_test.csv

.PHONY: all clean

audit_invariants: audit_invariants.rs libyoshida4.so
rustc -O -L . audit_invariants.rs -o audit_invariants
