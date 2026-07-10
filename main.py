import os
import sys

# Keep Qt WebEngine/Chromium third-party map warnings from flooding the terminal.
os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-logging --log-level=3")
os.environ.setdefault("QT_LOGGING_RULES", "qt.webenginecontext.debug=false;qt.webenginecontext.info=false;js.warning=false;js.info=false;qt.fonts.warning=false")


def _run_self_test() -> int:
    from stanky_market.self_test import run_self_test

    return run_self_test(sys.argv[1:])


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(_run_self_test())

    from stanky_market.app import main

    main()
