/* unicode_utils.h additions */
#ifndef UNICODE_UTILS_H
#define UNICODE_UTILS_H

#include "unicode_constants.h"
#include <stdio.h>

typedef struct {
    const uint8_t *src;
    size_t index;
    size_t len;
} Utf8Iterator;

Utf8Iterator utf8_iter_init(const char *str, size_t len);
bool utf8_next_codepoint(Utf8Iterator *iter, uint32_t *out_cp, size_t *out_bytes);
bool utf8_validate_string(const char *str, size_t max_bytes);
int unicode_codepoint_width(uint32_t cp);
size_t utf8_terminal_width(const char *str);
void utf8_print_truncated_padded(const char *str, size_t target_width);

#endif /* UNICODE_UTILS_H */
