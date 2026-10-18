#define _GNU_SOURCE
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

/* Synthetic recorder control only: no chess, subprocesses, threads or PMU. */
static double cpu_seconds(void) {
    struct timespec value;
    if (clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &value) != 0)
        return -1;
    return (double)value.tv_sec + (double)value.tv_nsec / 1000000000.0;
}

int main(int argc, char **argv) {
    cpu_set_t mask;
    if (argc != 2 || sched_getaffinity(0, sizeof(mask), &mask) != 0)
        return 90;
    if (CPU_COUNT(&mask) != 1 || !CPU_ISSET(14, &mask)) {
        fprintf(stderr, "unexpected-affinity\n");
        return 91;
    }
    printf("{\"synthetic\":true,\"pid\":%ld,\"affinity\":[14],\"mode\":\"%s\"}\n",
           (long)getpid(), argv[1]);
    fprintf(stderr, "synthetic-stderr:%s\n", argv[1]);
    fflush(stdout);
    fflush(stderr);
    if (strcmp(argv[1], "normal") == 0) {
        const double start = cpu_seconds();
        volatile uint64_t witness = 1;
        if (start < 0)
            return 92;
        do {
            for (unsigned n = 0; n < 10000; ++n)
                witness = witness * UINT64_C(6364136223846793005) + 1;
        } while (cpu_seconds() - start < 0.03);
        printf("cpu-work-completed:%llu\n", (unsigned long long)witness);
        return 0;
    }
    if (strcmp(argv[1], "nonzero") == 0)
        return 7;
    if (strcmp(argv[1], "timeout") == 0) {
        struct timespec delay = {.tv_sec = 2, .tv_nsec = 0};
        while (nanosleep(&delay, &delay) != 0 && errno == EINTR) {}
        return 0;
    }
    if (strcmp(argv[1], "flood") == 0) {
        char bytes[4096];
        memset(bytes, 'X', sizeof(bytes));
        for (unsigned n = 0; n < 16; ++n) {
            if (write(STDOUT_FILENO, bytes, sizeof(bytes)) < 0)
                return 93;
        }
        return 0;
    }
    return 94;
}
