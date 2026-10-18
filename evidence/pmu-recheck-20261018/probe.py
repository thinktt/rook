"""Disabled self-event opens only; no enable/read or system configuration change."""
import ctypes
import json
import os
from pathlib import Path
import platform

assert platform.system() == 'Linux' and platform.machine() == 'x86_64'


class Attr(ctypes.Structure):
    _fields_ = [('type', ctypes.c_uint32), ('size', ctypes.c_uint32),
                ('config', ctypes.c_uint64), ('sample_period', ctypes.c_uint64),
                ('sample_type', ctypes.c_uint64), ('read_format', ctypes.c_uint64),
                ('flags', ctypes.c_uint64), ('wakeup_events', ctypes.c_uint32),
                ('bp_type', ctypes.c_uint32), ('config1', ctypes.c_uint64),
                ('config2', ctypes.c_uint64), ('branch_sample_type', ctypes.c_uint64),
                ('sample_regs_user', ctypes.c_uint64), ('sample_stack_user', ctypes.c_uint32),
                ('clockid', ctypes.c_int32), ('sample_regs_intr', ctypes.c_uint64),
                ('aux_watermark', ctypes.c_uint32), ('sample_max_stack', ctypes.c_uint16),
                ('reserved', ctypes.c_uint16), ('aux_sample_size', ctypes.c_uint32),
                ('reserved3', ctypes.c_uint32), ('sig_data', ctypes.c_uint64)]


assert ctypes.sizeof(Attr) == 128
libc = ctypes.CDLL(None, use_errno=True)
libc.syscall.restype = ctypes.c_long
rows = []
for name, event_type, config in [('instructions', 0, 1), ('cycles', 0, 0), ('task-clock', 1, 1)]:
    attr = Attr(type=event_type, size=128, config=config, flags=1 | (1 << 5) | (1 << 6))
    ctypes.set_errno(0)
    fd = libc.syscall(ctypes.c_long(298), ctypes.byref(attr), ctypes.c_int(0),
                      ctypes.c_int(-1), ctypes.c_int(-1), ctypes.c_ulong(8))
    error = ctypes.get_errno() if fd < 0 else None
    if fd >= 0:
        os.close(fd)
    rows.append(dict(event=name, opened=fd >= 0, errno=error,
                     error=os.strerror(error) if error else None,
                     disabled=True, exclude_kernel=True, exclude_hypervisor=True))
report = dict(uid=os.getuid(), euid=os.geteuid(), platform=platform.platform(),
              attr_size=ctypes.sizeof(Attr), syscall_x86_64=298, enabled_events=0,
              paranoid=Path('/proc/sys/kernel/perf_event_paranoid').read_text().strip(),
              capability_status=[line for line in Path('/proc/self/status').read_text().splitlines()
                                 if line.startswith(('CapEff:', 'CapBnd:', 'Seccomp:'))],
              events=rows)
Path(__file__).with_name('result.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
