/* unicode_utils.c */
#include "unicode_utils.h"
#include <string.h>

Utf8Iterator utf8_iter_init(const char *str, size_t len) {
    Utf8Iterator it;
    it.src = (const uint8_t *)str;
    it.index = 0;
    it.len = (len == 0 && str) ? strlen(str) : len;
    return it;
}

bool utf8_next_codepoint(Utf8Iterator *iter, uint32_t *out_cp, size_t *out_bytes) {
    if (!iter || !iter->src || iter->index >= iter->len) {
        return false;
    }

    const uint8_t *s = iter->src + iter->index;
    size_t remaining = iter->len - iter->index;
    uint8_t byte0 = s[0];

    if ((byte0 & UTF8_1BYTE_MASK) == UTF8_1BYTE_MATCH) {
        *out_cp = byte0;
        *out_bytes = 1;
        iter->index += 1;
        return true;
    }

    if ((byte0 & UTF8_2BYTE_MASK) == UTF8_2BYTE_MATCH) {
        if (remaining < 2 || (s[1] & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_BYTE) {
            goto invalid;
        }
        uint32_t cp = ((byte0 & 0x1F) << 6) | (s[1] & 0x3F);
        if (cp < 0x80) goto invalid; /* Overlong */
        *out_cp = cp;
        *out_bytes = 2;
        iter->index += 2;
        return true;
    }

    if ((byte0 & UTF8_3BYTE_MASK) == UTF8_3BYTE_MATCH) {
        if (remaining < 3 || 
            (s[1] & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_BYTE ||
            (s[2] & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_BYTE) {
            goto invalid;
        }
        uint32_t cp = ((byte0 & 0x0F) << 12) | ((s[1] & 0x3F) << 6) | (s[2] & 0x3F);
        if (cp < 0x800) goto invalid; /* Overlong */
        if (cp >= UNICODE_SURROGATE_MIN && cp <= UNICODE_SURROGATE_MAX) goto invalid; /* Surrogates */
        *out_cp = cp;
        *out_bytes = 3;
        iter->index += 3;
        return true;
    }

    if ((byte0 & UTF8_4BYTE_MASK) == UTF8_4BYTE_MATCH) {
        if (remaining < 4 ||
            (s[1] & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_BYTE ||
            (s[2] & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_BYTE ||
            (s[3] & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_BYTE) {
            goto invalid;
        }
        uint32_t cp = ((byte0 & 0x07) << 18) | ((s[1] & 0x3F) << 12) | 
                      ((s[2] & 0x3F) << 6)  | (s[3] & 0x3F);
        if (cp < 0x10000 || cp > UNICODE_CODEPOINT_MAX) goto invalid;
        *out_cp = cp;
        *out_bytes = 4;
        iter->index += 4;
        return true;
    }

invalid:
    *out_cp = UNICODE_REPLACEMENT_CHAR;
    *out_bytes = 1;
    iter->index += 1;
    return false;
}

bool utf8_validate_string(const char *str, size_t max_bytes) {
    if (!str) return false;
    size_t len = strnlen(str, max_bytes);
    Utf8Iterator iter = utf8_iter_init(str, len);
    uint32_t cp;
    size_t bytes;

    while (iter.index < iter.len) {
        if (!utf8_next_codepoint(&iter, &cp, &bytes)) {
            return false;
        }
    }
    return true;
}

/* Returns terminal column cell width (0, 1, or 2) */
int unicode_codepoint_width(uint32_t cp) {
    if (cp == 0 || (cp >= 0x0001 && cp <= 0x001F) || (cp >= 0x007F && cp <= 0x009F)) {
        return 0; /* Non-printable control characters */
    }
    /* Zero-width combining marks */
    if ((cp >= 0x0300 && cp <= 0x036F) || (cp >= 0x200B && cp <= 0x200F)) {
        return 0;
    }
    /* East Asian Wide / Fullwidth ranges & Emoji blocks */
    if ((cp >= 0x1100 && cp <= 0x115F) ||
        (cp >= 0x2E80 && cp <= 0xA4CF) ||
        (cp >= 0xAC00 && cp <= 0xD7A3) ||
        (cp >= 0xF900 && cp <= 0xFAFF) ||
        (cp >= 0xFE10 && cp <= 0xFE19) ||
        (cp >= 0xFE30 && cp <= 0xFE6F) ||
        (cp >= 0xFF00 && cp <= 0xFF60) ||
        (cp >= 0xFFE0 && cp <= 0xFFE6) ||
        (cp >= 0x1F300 && cp <= 0x1F64F) || /* Miscellaneous Symbols and Pictographs */
        (cp >= 0x1F680 && cp <= 0x1F6FF) || /* Transport and Map */
        (cp >= 0x20000 && cp <= 0x2FA1F)) {
        return 2;
    }
    return 1;
}

size_t utf8_terminal_width(const char *str) {
    if (!str) return 0;
    Utf8Iterator iter = utf8_iter_init(str, strlen(str));
    uint32_t cp;
    size_t bytes;
    size_t total_width = 0;

    while (utf8_next_codepoint(&iter, &cp, &bytes)) {
        total_width += (size_t)unicode_codepoint_width(cp);
    }
    return total_width;
}
