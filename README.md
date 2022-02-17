# Various tracking tools for coreutils

Tracking the evolution of https://github.com/uutils/coreutils

## GNU testsuite comparison

Below is the evolution of how many GNU tests uutils passes. A more detailed
breakdown of the GNU test results of the main branch can be found
[in the user manual](https://uutils.github.io/coreutils-docs/user/test_coverage.html).

![GNU testsuite evolution](https://github.com/uutils/coreutils-tracking/blob/main/gnu-results.png?raw=true)

Refreshed once a day by github actions.

Compares only the Linux execution.

Based on:
* https://github.com/uutils/coreutils/blob/master/util/build-gnu.sh
* https://github.com/uutils/coreutils/blob/master/util/run-gnu-test.sh

## Binary size evolution

![Size evolution](https://github.com/uutils/coreutils-tracking/blob/main/size-results.png?raw=true)

Refreshed once a day by github actions.

Compares only the Linux execution.
