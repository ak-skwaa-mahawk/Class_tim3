CC = gcc
CFLAGS = -std=c11 -Wall -Wextra -Wpedantic -O3 -fPIC -Iinclude
LDFLAGS = -lm
RUSTC = rustc
RUSTFLAGS = -O -L . -C link-args="-Wl,-rpath,."

OBJS = src/main.o src/unicode_utils.o src/timetable_io.o src/timetable_view.o
TARGET = timetable_app
LIB = libyoshida4.so
LATTICE_BIN = yoshida4_lattice
AUDIT_BIN = audit_invariants

all: $(TARGET) $(LIB) $(LATTICE_BIN) $(AUDIT_BIN)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^

$(LIB): src/yoshida4_api.c
	$(CC) $(CFLAGS) -shared -o $@ $^ $(LDFLAGS)

$(LATTICE_BIN): yoshida4_lattice.c
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(AUDIT_BIN): audit_invariants.rs $(LIB)
	$(RUSTC) $(RUSTFLAGS) $< -o $@

src/%.o: src/%.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f src/*.o $(TARGET) $(LIB) $(LATTICE_BIN) $(AUDIT_BIN) schedule_test.csv

.PHONY: all clean
