from pathlib import Path
import json,hashlib,difflib
E=Path(__file__).parent;p=json.loads((E/'paths.json').read_text());S=Path(p['source']);B=Path(p['base103']);A=Path(p['phase0']);P1=Path(p['phase1']);P2=Path(p['phase2'])
assert not (E/'composition-proof.json').exists()
h=lambda text:hashlib.sha256(text.encode()).hexdigest();emit=lambda name,d:(E/name).write_text(json.dumps(d,indent=2)+'\n')
assert (B/'src/attacks.rs').read_bytes()==(A/'src/attacks.rs').read_bytes()
# attacks has no post85 owner overlap: exact whole phase2 module, including both stages' tests.
(S/'src/attacks.rs').write_bytes((P2/'src/attacks.rs').read_bytes())
b=(B/'src/movegen.rs').read_text();m=b;one=(P1/'src/movegen.rs').read_text();two=(P2/'src/movegen.rs').read_text()
old_checker='    let checkers = find_attackers::<2>(&position.board, king, position.side.opponent());'
new_checker='    let (squares, len) = position\n        .attack_view()\n        .ordered_attackers::<2>(king, position.side.opponent());\n    let checkers = Checkers { squares, len };'
assert one.count(new_checker)==1;start=m.index('fn generate_bounded<const LIMIT: usize>');idx=m.index(old_checker,start);assert idx<m.index('\n#[cfg(test)]',start);m=m[:idx]+m[idx:].replace(old_checker,new_checker,1)
test_start=one.index('    fn compare_ordered_checker_identities(');test_end=one.index('    #[test]\n    fn generation_summary_matches_projection_on_joined_witnesses()',test_start);checker_tests=one[test_start:test_end]
insert='    #[test]\n    fn semantic_check_classification_reports_none_single_and_saturated_double()';assert m.count(insert)==1;m=m.replace(insert,checker_tests+insert,1)
old_loop='            compare_projection(&Position::from_fen(&fen).unwrap(), &fen);'
new_loop='            let position = Position::from_fen(&fen).unwrap();\n            compare_ordered_checker_identities(&position, &fen);\n            compare_projection(&position, &fen);'
assert one.count(new_loop)==1 and m.count(old_loop)==1;m=m.replace(old_loop,new_loop,1)
route_start=two.index('/// Q supplies its one projected tag-plane view.');route_end=two.index('/// The tactical caller supplies a projected board',route_start);route=two[route_start:route_end]
route_anchor='/// The tactical caller supplies a projected board';assert m.count(route_anchor)==1;m=m.replace(route_anchor,route+route_anchor,1)
assert m.count('pub(crate) fn check_routes(')==1;m=m.replace('pub(crate) fn check_routes(','#[cfg(test)]\npub(crate) fn check_routes(',1)
old_doc='/// Read-only component observation using the same native checker finder as\n/// complete generation. Existing Boolean/default/hot callers stay unchanged.'
new_doc='/// Read-only component observation using the retained native mailbox finder.\n/// Complete generation supplies equivalent ordered identities from tag planes.'
assert m.count(old_doc)==1;m=m.replace(old_doc,new_doc,1)
(S/'src/movegen.rs').write_text(m)
# Prove every103 byte survives outside the exact copied substitutions/blocks/comment correction.
inverse=m.replace(new_doc,old_doc,1).replace(route,'',1).replace('#[cfg(test)]\npub(crate) fn check_routes(','pub(crate) fn check_routes(',1).replace(checker_tests,'',1).replace(new_loop,old_loop,1).replace(new_checker,old_checker,1);assert inverse==b
q=(B/'src/quiescence.rs').read_text();base_q=q
substitutions=[('let board = movegen::projected_board(&position, movement);','let projected = position.attack_view().projected(&position, movement);'),('movegen::check_routes(&board, enemy_king, position.side, movement.to());','movegen::check_routes_bits(&projected, enemy_king, position.side, movement.to());'),('if movegen::attacked(&board, king_after, position.side.opponent()) {','if projected.attacked(king_after, position.side.opponent()) {')]
for old,new in substitutions:assert q.count(old)==1;q=q.replace(old,new,1)
(S/'src/quiescence.rs').write_text(q)
inverse=q
for old,new in substitutions:assert inverse.count(new)==1;inverse=inverse.replace(new,old,1)
assert inverse==base_q
# Retained local whole-block owners are checked separately, rather than relying on non-overlap claims.
def block(text,start,end):return text[text.index(start):text.index(end,text.index(start))]
classification=block(b,'pub fn check_classification(','/// Project just the fields');assert classification==block(m,'pub fn check_classification(','/// Project just the fields')
king_start='    // The capped predicate discards its witnesses';king_end='    let pawn_start = list.len;';assert block(b,king_start,king_end)==block(m,king_start,king_end)
for anchor,end in [('    fn capped_checked_replies_keep_fixed_zero_one_and_two_king_witnesses()','    #[test]\n    fn capped_checked_replies_keep_sole_nonking_and_joined_ep_evasions()'),('    fn capped_checked_replies_keep_sole_nonking_and_joined_ep_evasions()','    #[test]\n    fn check_route_classification_separates_discovered_and_simultaneous_checks()')]:assert block(b,anchor,end)==block(m,anchor,end)
assert b.count('if king_early && kind == PieceKind::King')==m.count('if king_early && kind == PieceKind::King')==1
emit('composition-proof.json',{'status':'SOURCE_ONLY_EXACT_RECONSTRUCTION_UNRUN','attacks103_equals_phase0':True,'attacks_composed_exact_phase2':True,'movegen103_exact_after_inverse_validated_blocks_and_documentation':True,'q103_entire_file_exact_after_inverse_three_substitutions':True,'public_classification_mailbox_implementation_exact103':True,'king_first_body_and_both_tests_exact103':True,'phase1_ordered_supply_and_test_blocks_exact':True,'phase2_route_owner_and_mailbox_oracle_transport_exact':True,'q_observer_boundary_policy_retained_by_entire_file_inverse':True,'q_new_projection_binding_count':q.count('let projected = position.attack_view().projected(&position, movement);'),'movegen_comment_only_extra_delta':{'old':old_doc,'new':new_doc},'changed_files':{n:h((S/n).read_text()) for n in ['src/attacks.rs','src/movegen.rs','src/quiescence.rs']},'native_jobs':0})
print(json.dumps({'source':str(S),'composition_proof':'composition-proof.json','native_jobs':0}))
