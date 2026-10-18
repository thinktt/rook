# Direct native CPU-accounting controls

`python3 -m unittest tools/test_account_native.py` passed four controls using
our separately compiled synthetic `../runner-controls/runner-control` process:
direct native stdout/stderr, normal native CPU accounting/placement, preserved
nonzero exit, fresh-receipt enforcement, and supervisor signal forwarding with
native reap and signal-exit mirroring. These are controls for our measurement
boundary, not engine-conformance fixtures or performance acceptance.
