fn preferred_into(moves: &mut [Move], priorities: &mut [u32], output: &mut [Move]) {
    let n = moves.len();
    debug_assert_eq!(priorities.len(), n);
    debug_assert_eq!(output.len(), n);
    debug_assert!(n <= MOVE_CAPACITY);
    if n <= 6 {
        priority_sequence(moves, priorities);
        output.copy_from_slice(moves);
        return;
    }

    let gap = 6;
    for index in gap..moves.len() {
        let movement = moves[index];
        let priority = priorities[index];
        let mut cursor = index;
        while cursor >= gap && priorities[cursor - gap] < priority {
            moves[cursor] = moves[cursor - gap];
            priorities[cursor] = priorities[cursor - gap];
            cursor -= gap;
        }
        moves[cursor] = movement;
        priorities[cursor] = priority;
    }

    let mut heads = [0u64; 6];
    for stream in 0..6 {
        heads[stream] = (((priorities[stream] as u64) << 9) | (511 - stream) as u64) + 1;
    }
    for destination in output {
        let mut rank = heads[0];
        let mut winning_stream = 0;
        for stream in 1..6 {
            if heads[stream] > rank {
                rank = heads[stream];
                winning_stream = stream;
            }
        }
        let index = 511 - ((rank - 1) & 511) as usize;
        *destination = moves[index];
        let next = index + 6;
        heads[winning_stream] = if next < n {
            (((priorities[next] as u64) << 9) | (511 - next) as u64) + 1
        } else {
            0
        };
    }
}

