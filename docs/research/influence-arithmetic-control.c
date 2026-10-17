/* Research arithmetic controls only: no board, engine, fixtures or oracle data. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef struct { unsigned n[5]; } Profile; /* weak, queen, rook, minor, pawn */
static const unsigned radix[5] = {2, 2, 4, 4, 4};
static const unsigned weight[5] = {1, 2, 4, 16, 64};
static const unsigned piece_tier[4] = {1, 3, 5, 9};

static Profile normalize_reference(Profile p) {
    for (unsigned i = 0; i < 4; ++i) {
        p.n[i + 1] += p.n[i] / radix[i];
        p.n[i] %= radix[i];
    }
    p.n[4] %= radix[4];
    return p;
}

static Profile decode(unsigned s) {
    Profile p = {{s & 1, (s >> 1) & 1, (s >> 2) & 3,
                   (s >> 4) & 3, (s >> 6) & 3}};
    return p;
}

static unsigned encode(Profile p) {
    unsigned s = 0;
    for (unsigned i = 0; i < 5; ++i) s += p.n[i] * weight[i];
    return s;
}

static unsigned total(Profile p) {
    unsigned n = 0;
    for (unsigned i = 0; i < 5; ++i) n += p.n[i];
    return n;
}

static unsigned multiplicity(Profile p) {
    unsigned n = total(p);
    return n < 4 ? n : 4;
}

static unsigned least_tier(Profile p) {
    if (p.n[4]) return 1;
    if (p.n[3]) return 3;
    if (p.n[2]) return 5;
    if (p.n[1]) return 9;
    if (p.n[0]) return 99;
    return 0; /* never consumed as a present tier */
}

static unsigned relation_reference(Profile own, Profile opposing, unsigned t) {
    unsigned a = multiplicity(opposing), d = multiplicity(own);
    unsigned v = least_tier(opposing), u = least_tier(own);
    if (a == 0) return 2;
    if (d == 0 || v < t) return 0;
    if (v == t) return a <= d ? 1 : 0;
    return a <= d || v > t + u ? 2 : 0;
}

/* Algebraic predicate form, separate from the ordered branch reference. */
static unsigned relation_predicate(unsigned d, unsigned u,
                                   unsigned a, unsigned v, unsigned t) {
    unsigned favorable = a == 0 ||
        (d != 0 && v > t && (a <= d || v > t + u));
    unsigned contested = a != 0 && d != 0 && v == t && a <= d;
    return 2 * favorable + contested;
}

/* Digit borrowing checks saturated subtraction without weighted subtraction. */
static Profile remove_reference(Profile p, unsigned category) {
    unsigned borrow = category;
    while (borrow < 5 && p.n[borrow] == 0) ++borrow;
    if (borrow == 5) {
        Profile empty = {{0, 0, 0, 0, 0}};
        return empty;
    }
    --p.n[borrow];
    for (unsigned i = category; i < borrow; ++i) p.n[i] = radix[i] - 1;
    return p;
}

static unsigned packed_predicate(Profile own, Profile opposing) {
    unsigned packed = 0;
    for (unsigned t = 0; t < 4; ++t)
        packed |= relation_predicate(multiplicity(own), least_tier(own),
                                    multiplicity(opposing), least_tier(opposing),
                                    piece_tier[t]) << (2 * t);
    return packed;
}

static int lex_compare(Profile a, Profile b) {
    for (int i = 4; i >= 0; --i)
        if (a.n[i] != b.n[i]) return a.n[i] > b.n[i] ? 1 : -1;
    return 0;
}

int main(void) {
    uint64_t normalization_cases = 0, adjusted_pairs = 0;
    for (unsigned w = 0; w < 32; ++w)
    for (unsigned q = 0; q < 32; ++q)
    for (unsigned r = 0; r < 32; ++r)
    for (unsigned m = 0; m < 32; ++m)
    for (unsigned p = 0; p < 32; ++p) {
        Profile raw = {{w, q, r, m, p}};
        assert(encode(normalize_reference(raw)) == (encode(raw) & 255));
        ++normalization_cases;
    }

    unsigned summaries = 0, max_total = 0, summary_m[256], summary_t[256];
    uint8_t summary_id[256], compact[16][16];
    for (unsigned s = 0; s < 256; ++s) {
        Profile p = decode(s);
        assert(encode(p) == s);
        assert(encode(normalize_reference(p)) == s);
        if (total(p) > max_total) max_total = total(p);
        unsigned id = 0;
        while (id < summaries &&
               (summary_m[id] != multiplicity(p) || summary_t[id] != least_tier(p)))
            ++id;
        if (id == summaries) {
            summary_m[id] = multiplicity(p);
            summary_t[id] = least_tier(p);
            ++summaries;
        }
        summary_id[s] = (uint8_t)id;
    }
    assert(summaries == 16 && max_total == 11);
    for (unsigned own = 0; own < summaries; ++own)
    for (unsigned opp = 0; opp < summaries; ++opp) {
        unsigned packed = 0;
        for (unsigned t = 0; t < 4; ++t)
            packed |= relation_predicate(summary_m[own], summary_t[own],
                                         summary_m[opp], summary_t[opp],
                                         piece_tier[t]) << (2 * t);
        compact[own][opp] = (uint8_t)packed;
    }

    for (unsigned own = 0; own < 256; ++own)
    for (unsigned opp = 0; opp < 256; ++opp) {
        Profile a = decode(own), b = decode(opp);
        unsigned full = packed_predicate(a, b);
        assert(full == compact[summary_id[own]][summary_id[opp]]);
        assert(lex_compare(a, b) == (own > opp ? 1 : own < opp ? -1 : 0));
        for (unsigned t = 0; t < 4; ++t)
            assert(((full >> (2 * t)) & 3) ==
                   relation_reference(a, b, piece_tier[t]));
        for (unsigned category = 0; category < 5; ++category) {
            Profile adjusted = remove_reference(a, category);
            unsigned sub = own >= weight[category] ? own - weight[category] : 0;
            assert(encode(adjusted) == sub);
            unsigned packed = compact[summary_id[sub]][summary_id[opp]];
            for (unsigned t = 0; t < 4; ++t)
                assert(((packed >> (2 * t)) & 3) ==
                       relation_reference(adjusted, b, piece_tier[t]));
            ++adjusted_pairs;
        }
    }

    uint32_t random_state = 0x51f17a3u;
    unsigned order_cases = 1024;
    for (unsigned test = 0; test < order_cases; ++test) {
        unsigned n = 0, contributions[155];
        Profile raw = {{0, 0, 0, 0, 0}};
        for (unsigned category = 0; category < 5; ++category) {
            random_state = random_state * 1664525u + 1013904223u;
            raw.n[category] = random_state >> 27;
            for (unsigned k = 0; k < raw.n[category]; ++k)
                contributions[n++] = weight[category];
        }
        for (unsigned i = n; i > 1; --i) {
            random_state = random_state * 1664525u + 1013904223u;
            unsigned j = random_state % i;
            unsigned saved = contributions[i - 1];
            contributions[i - 1] = contributions[j];
            contributions[j] = saved;
        }
        uint8_t accumulated = 0;
        for (unsigned i = 0; i < n; ++i)
            accumulated = (uint8_t)(accumulated + contributions[i]);
        assert(accumulated == encode(normalize_reference(raw)));
        /* Exact physical contribution removal uses the modular inverse. */
        for (unsigned i = 0; i < n; ++i)
            accumulated = (uint8_t)(accumulated - contributions[i]);
        assert(accumulated == 0);
    }

    /* Deliberate counterexamples: adjusted exclusion is not a physical update. */
    Profile discarded = {{0, 0, 0, 8, 2}};
    assert(encode(normalize_reference(discarded)) == 0);
    assert(encode(remove_reference(normalize_reference(discarded), 4)) == 0);
    --discarded.n[4];
    assert(encode(normalize_reference(discarded)) == 192);
    assert(encode(remove_reference(decode(64), 3)) == 48);
    assert(encode(remove_reference(decode(1), 1)) == 0);

    printf("{\"status\":\"pass\",\"normalization_profiles\":%llu,"
           "\"normalized_codes\":256,\"relation_pairs\":65536,"
           "\"adjusted_pairs\":%llu,\"shuffled_contribution_sequences\":%u,"
           "\"realizable_relation_summaries\":%u,\"max_uncapped_count_sum\":%u}\n",
           (unsigned long long)normalization_cases,
           (unsigned long long)adjusted_pairs, order_cases, summaries, max_total);
    return 0;
}
