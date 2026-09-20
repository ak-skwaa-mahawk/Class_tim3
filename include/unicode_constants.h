#ifndef UNICODE_CONSTANTS_H
#define UNICODE_CONSTANTS_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define UTF8_1BYTE_MASK        0x80
#define UTF8_1BYTE_MATCH       0x00

#define UTF8_CONTINUATION_MASK 0xC0
#define UTF8_CONTINUATION_BYTE 0x80

#define UTF8_2BYTE_MASK        0xE0
#define UTF8_2BYTE_MATCH       0xC0

#define UTF8_3BYTE_MASK        0xF0
#define UTF8_3BYTE_MATCH       0xE0

#define UTF8_4BYTE_MASK        0xF8
#define UTF8_4BYTE_MATCH       0xF0

#define UNICODE_SURROGATE_MIN      0xD800
#define UNICODE_SURROGATE_MAX      0xDFFF
#define UNICODE_CODEPOINT_MAX      0x10FFFF
#define UNICODE_REPLACEMENT_CHAR   0xFFFD

#define UTF8_MAX_BYTES_PER_CHAR    4
#define UTF8_MAX_STR_LEN           256

#endif /* UNICODE_CONSTANTS_H */
