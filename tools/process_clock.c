// Read a live owned process's CPU clock, including all its threads, without /proc tick quantization.
#define _POSIX_C_SOURCE 200809L
#include <time.h>
#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
#include <errno.h>
#include <sys/types.h>

static uint64_t ns(struct timespec t) { return (uint64_t)t.tv_sec*1000000000u+(uint64_t)t.tv_nsec; }
int main(void) {
    long pid;
    while (scanf("%ld", &pid)==1) {
        clockid_t clock;
        struct timespec cpu, wall, resolution;
        int error = pid > 0 ? clock_getcpuclockid((pid_t)pid, &clock) : EINVAL;
        if (!error && (clock_gettime(clock,&cpu) || clock_gettime(CLOCK_MONOTONIC,&wall) || clock_getres(clock,&resolution))) error=errno;
        if (error) printf("{\"pid\":%ld,\"error\":%d}\n",pid,error);
        else printf("{\"pid\":%ld,\"cpuNs\":\"%"PRIu64"\",\"monoNs\":\"%"PRIu64"\",\"resolutionNs\":\"%"PRIu64"\"}\n",pid,ns(cpu),ns(wall),ns(resolution));
        fflush(stdout);
    }
    return ferror(stdin) ? 1 : 0;
}
