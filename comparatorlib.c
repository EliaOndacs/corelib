/* 
 * forwardscale / backwardscale
 * ----------------------------
 * These functions take an input string and "shift" each character.
 *
 * forwardscale:
 *     output[i] = input[i] + (i + 1)
 *
 * backwardscale:
 *     output[i] = input[i] - (i + 1)
 *
 * Example with forwardscale("hello"):
 *   'h' + 1   = 'i'
 *   'e' + 2   = 'g'
 *   'l' + 3   = 'o'
 *   'l' + 4   = 'p'
 *   'o' + 5   = 't'
 *
 * No standard library is required. NULL-terminated strings only.
 */

void forwardscale(const char *in, char *out) {
    int i = 0;                  /* index counter */
    while (in[i] != '\0') {     /* process until we hit the null terminator */
        char c = in[i];         /* read current character */
        char shift = (char)(i + 1); 
                                /* amount to shift forward */

        out[i] = c + shift;     /* apply the shifting rule */
        i++;                    /* move to next character */
    }

    out[i] = '\0';              /* write null terminator to output */
}

void backwardscale(const char *in, char *out) {
    int i = 0;                  /* index counter */
    while (in[i] != '\0') {     /* loop until string ends */
        char c = in[i];         /* current input char */
        char shift = (char)(i + 1);
                                /* how much to shift backward */

        out[i] = c - shift;     /* apply reverse shifting */
        i++;                    /* increment index */
    }

    out[i] = '\0';              /* null-terminate output */
}

