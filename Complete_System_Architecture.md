Class_tim3/
├── README.md                          # Academic course & lab specification (PHYS/CS 482)
├── syllabus.md                        # Theoretical derivations (dispersion, Verlet symplecticity, drift)
├── hardware_telemetry_schema.json     # Systematic transducer error budgets (timebase, encoder, thermal)
│
├── include/ & src/                    # C11 Core Engine & Python ctypes Shared Object
│   ├── include/unicode_constants.h    # UTF-8 masks, bounds, and string sizing
│   ├── include/timetable.h            # Academic schedule structures & slot definitions
│   ├── include/unicode_utils.h        # Display width and truncation headers
│   ├── include/timetable_io.h         # RFC 4180 CSV export/import definitions
│   ├── include/timetable_view.h       # Terminal table rendering headers
│   ├── src/unicode_utils.c            # Multibyte iterator & cell padding
│   ├── src/timetable_io.c             # State-machine CSV parser with quote de-duplication
│   ├── src/timetable_view.c           # Column border-safe table printer
│   ├── src/yoshida4_api.c             # C shared object API for in-memory integration
│   ├── src/transducer_daq.py          # Empirical DAQ engine (Type A/B GUM propagation & z-score)
│   └── src/main.c                     # Cross-platform locale-initialized timetable CLI
│
├── libyoshida4.so                     # Compiled dynamic library for Python ctypes
├── Makefile                           # Unified build targets (all, clean, libyoshida4.so, timetable_app)
│
├── run_79hz_production_eval.py        # Dual-mode evaluator (--eval-only vs. --empirical)
├── yoshida4_lattice.py                # Standalone Python Yoshida-4 simulation
├── orbit_preservation.py              # In-memory ctypes bridge trajectory driver
├── plot_lattice_spectrum.py           # 8-site modal spectrum generator
├── profile_modal_coordinates.py       # Fourier normal coordinate decoupling profiler
│
├── lattice_spectrum.svg               # Vector plot: 8-site modal decay
├── orbit_portrait.svg                 # Vector plot: Invariant torus phase portrait
├── modal_coordinates_profile.svg      # Vector plot: Equipartition arrest verification
├── VERIFICATION_REPORT.md             # Notarized state vector digest audit
│
└── tests/
    ├── test_invariants.py             # Autograder unit assertions (cadence, pi_eff, dispersion)
    └── test_empirical_uncertainty.py  # CI gating suite (SNR >= 2.0, Type A/B limits, short-sample rejection)
