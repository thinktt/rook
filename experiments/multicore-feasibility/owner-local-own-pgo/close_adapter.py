#!/usr/bin/env python3
"""Adapt the frozen closer's prepared_run tuple API; keep all checks and bytes."""
import argparse
import importlib.util
from pathlib import Path
import sys
import time
sys.dont_write_bytecode=True
from common import HERE,read,sha,write


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,required=True)
    args=parser.parse_args();raw=args.root.resolve();out=raw/'closure-audit.json';assert not out.exists()
    pipeline=read(raw/'pipeline.json');began=time.monotonic_ns()
    assert began<pipeline['pipelineDeadlineMonotonicNs']
    frozen=HERE/'close_pipeline.py';prepared=read(HERE/'preparation.json')
    assert sha(frozen)==prepared['inputSha256'][str(frozen)]
    spec=importlib.util.spec_from_file_location('owner_local_frozen_closer',frozen)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    original=module.prepared_run
    def prepared_record(*args):
        result=original(*args)
        assert isinstance(result,tuple) and len(result)==3
        assert result[0]==read(raw/'prepared-run.json')
        return result[0]
    module.prepared_run=prepared_record
    value=module.close(raw)
    ended=time.monotonic_ns();assert ended<pipeline['pipelineDeadlineMonotonicNs']
    assert sha(frozen)==prepared['inputSha256'][str(frozen)]
    failure=raw/'closure-attempt-01.json';assert read(failure)['exitCode']==1
    value.update(closureAdapterSha256=sha(Path(__file__)),closureAdapter=str(Path(__file__).resolve()),
        failedCloserReceipt=str(failure),failedCloserReceiptSha256=sha(failure),
        closureToolFailures=1,closureAdapterStartedMonotonicNs=began,closureAdapterEndedMonotonicNs=ended,
        terminalClosureElapsedNs=ended-pipeline['pipelineStartMonotonicNs'],
        adapterScope='unwrap validated (prepared record, build receipt, effective options) tuple; no check removed, frozen file/source/profile/native bytes unchanged; no engine rerun')
    value['pins'][str(Path(__file__).resolve())]=sha(Path(__file__))
    value['pins'][str(failure)]=sha(failure)
    write(out,value)
    print({k:value[k]for k in ['complete','trainingLives','comparisonLives','idleProbes','terminalNativeReceipts','terminalClosureElapsedNs']})


if __name__=='__main__':main()
