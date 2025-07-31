CC = gcc
CFLAGS = -Wall -Wextra -std=c99
LIBS = -lmysqlclient
INCLUDES = -I/usr/include/mysql

SRCDIR = .
SOURCES = $(wildcard $(SRCDIR)/*.c)
OBJECTS = $(SOURCES:.c=.o)
TARGET = ec_site

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(OBJECTS) -o $(TARGET) $(LIBS)

%.o: %.c
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

clean:
	rm -f $(OBJECTS) $(TARGET)

install-deps:
	sudo apt-get update
	sudo apt-get install -y libmysqlclient-dev mysql-client

run: $(TARGET)
	./$(TARGET)

debug: CFLAGS += -g -DDEBUG
debug: $(TARGET)

.PHONY: install-deps run debug