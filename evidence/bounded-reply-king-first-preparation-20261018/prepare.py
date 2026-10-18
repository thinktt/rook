#!/usr/bin/env python3
"""Freeze checked-only capped king-first from immutable Q85 and audit82 receipts."""
from pathlib import Path
import hashlib,json,difflib,gzip,io,tarfile
ROOT=Path('/home/legolas/rook2');EV=ROOT/'evidence';OUT=Path(__file__).resolve().parent
BASE=Path('/tmp/imp2-move-q-evaluation-combined-20261018')
TREE=Path('/tmp/imp2-bounded-reply-king-first85-20261018-zup28rca')
AUDIT82=EV/'retained-evaluation-build-20261018'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[BASE/'Cargo.toml',BASE/'Cargo.lock']+sorted((BASE/'src').rglob('*.rs'))+sorted(p for p in (BASE/'tools').iterdir() if p.is_file())
assert len(files)==66
baseline={str(p.relative_to(BASE)):sha(p) for p in files if 'tools' not in p.relative_to(BASE).parts}
receipt=json.loads((EV/'quiescence-evaluation-default-build-20261018/receipt.json').read_text())
assert baseline==receipt['source_sha256_before']==receipt['source_sha256_after']
assert all(sha(TREE/p.relative_to(BASE))==sha(p) for p in files), 'preparation retry tree must still equal immutable base'
audit=json.loads((AUDIT82/'receipt.json').read_text());assert audit['source_sha256_before']==audit['source_sha256_after']
audit_source=audit['source_sha256_before'];observer=[n for n,h in baseline.items() if audit_source[n]!=h]
assert observer==['src/evaluator.rs','src/quiescence.rs','src/quiescence_policy.rs']
assert all(sha(AUDIT82/'source-before'/n)==audit_source[n] for n in observer)
def qregion(s):
    start=s.index('                    if !double_check && !recapture {')
    return s[start:s.index('                let moving =',start)]
assert qregion((BASE/'src/quiescence.rs').read_text())==qregion((AUDIT82/'source-before/src/quiescence.rs').read_text())
assert baseline['src/session.rs']==audit_source['src/session.rs']
(OUT/'base85-versus-audit82.patch').write_text(''.join(''.join(difflib.unified_diff((AUDIT82/'source-before'/n).read_text().splitlines(True),(BASE/n).read_text().splitlines(True),fromfile='audit82/'+n,tofile='base85/'+n)) for n in observer))
p=TREE/'src/movegen.rs';old=p.read_text()
new=old.replace('    let safety = GenerationSafety::new(position, king, checkers);\n    let pawn_start = list.len;','''    let safety = GenerationSafety::new(position, king, checkers);
    // The capped predicate discards its witnesses once two replies exist.
    // Keep complete generation in its observable order, including the EP prefix.
    let king_early = LIMIT == 2 && checkers.len != 0;
    if king_early {
        pieces::<LIMIT>(position, list, &safety, PieceKind::King);
        if list.len >= LIMIT {
            return;
        }
    }
    let pawn_start = list.len;''',1)
needle='''    ] {
        pieces::<LIMIT>(position, list, &safety, kind);
        if list.len >= LIMIT {
            return;
        }
    }
}

#[cfg(test)]'''
replacement='''    ] {
        if king_early && kind == PieceKind::King {
            continue;
        }
        pieces::<LIMIT>(position, list, &safety, kind);
        if list.len >= LIMIT {
            return;
        }
    }
}

#[cfg(test)]'''
assert new.count(needle)==1;new=new.replace(needle,replacement,1)
tests='''    #[test]
    fn capped_checked_replies_keep_fixed_zero_one_and_two_king_witnesses() {
        for (fen, full_count, capped_names) in [
            ("7k/6Q1/5K2/8/8/8/8/8 b - - 0 1", 0, &[][..]),
            ("7k/7R/6K1/8/8/8/8/8 b - - 0 1", 1, &["h8g8"][..]),
            // The knight and bishop can interpose, but two king escapes
            // alone prove the threshold without adopting the full base order.
            ("5n1k/8/8/5b2/8/8/8/K6R b - - 0 1", 5, &["h8g7", "h8g8"][..]),
        ] {
            let position = Position::from_fen(fen).unwrap();
            assert!(in_check(&position, position.side));
            compare_projection(&position, fen);
            let mut full = MoveList::new();
            let mut capped = MoveList::new();
            generate_legal(&position, &mut full);
            assert_eq!(full.len, full_count, "fixed legal count: {fen}");
            assert_eq!(legal_replies_up_to_two(&position, &mut capped), full_count.min(2));
            let names: Vec<String> = capped.as_slice().iter().map(ToString::to_string).collect();
            let expected: Vec<String> = capped_names.iter().map(ToString::to_string).collect();
            assert_eq!(names, expected, "fixed threshold witnesses: {fen}");
            assert!(capped.as_slice().iter().all(|movement| full.as_slice().contains(movement)));
            if full_count == 5 {
                assert_eq!(full.moves[0].to_string(), "f8h7");
                assert_ne!(capped.as_slice(), &full.as_slice()[..2]);
            }
        }
    }

    #[test]
    fn capped_checked_replies_keep_sole_nonking_and_joined_ep_evasions() {
        let fen = "7k/8/8/8/2b5/2p5/2R4r/K6r w - - 0 1";
        let position = Position::from_fen(fen).unwrap();
        assert!(in_check(&position, position.side));
        compare_projection(&position, fen);
        let mut capped = MoveList::new();
        assert_eq!(legal_replies_up_to_two(&position, &mut capped), 1);
        assert_eq!(capped.moves[0].to_string(), "c2c1");

        // Joined EP removes a knight checker and interposes on a bishop ray.
        // A double-check king-only shortcut would lose this legal prefix.
        let fen = "1b5k/8/8/2Pn4/5K2/8/8/8 w - d6 0 1";
        let position = Position::from_fen(fen).unwrap();
        let king = position.piece_squares(position.side, PieceKind::King)[0];
        assert_eq!(find_attackers::<2>(&position.board, king, position.side.opponent()).len, 2);
        compare_projection(&position, fen);
        let mut full = MoveList::new();
        generate_legal(&position, &mut full);
        assert!(full.len >= 2);
        assert_eq!(legal_replies_up_to_two(&position, &mut capped), 2);
        assert_eq!(capped.moves[0].to_string(), "c5d6");
        assert_eq!(capped.moves[0].kind(), MoveKind::EnPassant);
        assert!(capped.as_slice().iter().all(|movement| full.as_slice().contains(movement)));
    }

'''
needle='    #[test]\n    fn check_route_classification_separates_discovered_and_simultaneous_checks() {'
assert new.count(needle)==1;new=new.replace(needle,tests+needle,1)
assert new.count('#[test]')==old.count('#[test]')+2
p.write_text(new)
source={str(p.relative_to(TREE)):sha(p) for p in [TREE/'Cargo.toml',TREE/'Cargo.lock']+sorted((TREE/'src').rglob('*.rs'))}
changed=[n for n,h in source.items() if baseline[n]!=h];assert changed==['src/movegen.rs']
(OUT/'king-first.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='base85/src/movegen.rs',tofile='king-first/src/movegen.rs')))
allfiles={str(p.relative_to(TREE)):sha(p) for p in sorted(TREE.rglob('*')) if p.is_file()};assert len(allfiles)==66
with (OUT/'prepared-source.tar.gz').open('xb') as raw:
 with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as compressed:
  with tarfile.open(fileobj=compressed,mode='w') as tar:
   for n,h in sorted(allfiles.items()):
    data=(TREE/n).read_bytes();info=tarfile.TarInfo(n);info.size=len(data);info.mode=0o644;tar.addfile(info,io.BytesIO(data))
d=dict(status='Frozen checked-only capped king-first prototype on correctedQ85',path=str(TREE),baseline=str(BASE),baseline_source_sha256=baseline,variant_source_sha256=source,all_source_tool_sha256=allfiles,changed_paths=changed,tests=dict(baseline_library=140,new_fixed=2,expected_library=142,development=2,expected_total=144),control_artifact_sha256=receipt['binary_output']['sha256'],control_receipt_sha256=sha(EV/'quiescence-evaluation-default-build-20261018/receipt.json'),audit82_receipt_sha256=sha(AUDIT82/'receipt.json'),patch_sha256=sha(OUT/'king-first.patch'),archive_sha256=sha(OUT/'prepared-source.tar.gz'),audit82_base_differences={n:dict(audit82_sha256=audit_source[n],base85_sha256=baseline[n]) for n in observer},unchanged_Q_reply_consumer_sha256=hashlib.sha256(qregion((BASE/'src/quiescence.rs').read_text()).encode()).hexdigest(),session_source_sha256=baseline['src/session.rs'],prepare_sha256=sha(Path(__file__)),scope='Only movegen.rs native edits: early King for LIMIT2 checked; same EP/castles/GenerationSafety; exactly one King pass, no double-check shortcut; two fixed tests; no other source change')
(OUT/'prepared.json').write_text(json.dumps(d,indent=2)+'\n')
(OUT/'README.md').write_text('Frozen corrected-Q85 king-first prototype. Only movegen.rs differs from the d38ff037 control source. EP/castles and GenerationSafety remain; early King is LIMIT==2 && checked, final King skipped only on that same path. All original native tests stay intact, with two new fixed threshold/witness tests. Three base observer/evaluation differences versus frozen audit82 are bound to retained-evaluation-build-20261018 receipt/source-before, not mutable root. Q reply-consumer region and entire session source remain byte-identical. Initial bookkeeping failure ebe53c is preserved separately; no source edit/build preceded it. Prepared source is immutable; validation is separate. No CPU gain predicted.\n')
print(json.dumps(dict(path=str(TREE),prepared_sha256=sha(OUT/'prepared.json'),patch_sha256=d['patch_sha256'],archive_sha256=d['archive_sha256'],expected_native_total=144)))
