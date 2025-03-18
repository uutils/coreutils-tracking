# Various tracking tools for coreutils

Tracking the evolution of https://github.com/uutils/coreutils

## GNU testsuite comparison

Below is the evolution of how many GNU tests uutils passes. A more detailed
breakdown of the GNU test results of the main branch can be found
[in the user manual](https://uutils.github.io/coreutils/docs/test_coverage.html).

![GNU testsuite evolution](https://github.com/uutils/coreutils-tracking/blob/main/gnu-results.png?raw=true)

Refreshed twice a day by github actions. Changes are documented in the json file ([gnu-result.json](https://github.com/uutils/coreutils-tracking/blob/main/gnu-result.json)).

Compares only the Linux execution.

Based on:
* https://github.com/uutils/coreutils/blob/main/util/build-gnu.sh
* https://github.com/uutils/coreutils/blob/main/util/run-gnu-test.sh

## Busybox testsuite comparison

Similar results but using the busybox testsuite:
https://github.com/mirror/busybox/tree/master/testsuite

![Busybox testsuite evolution](https://github.com/uutils/coreutils-tracking/blob/main/busybox-results.png?raw=true)

## Toybox testsuite comparison

Similar results but using the toybox testsuite:
https://github.com/landley/toybox/tree/master/tests

![Toybox testsuite evolution](https://github.com/uutils/coreutils-tracking/blob/main/toybox-results.png?raw=true)

## Binary size evolution

![Size evolution](https://github.com/uutils/coreutils-tracking/blob/main/size-results.png?raw=true)

Refreshed once a day by github actions.

Compares only the Linux execution.
