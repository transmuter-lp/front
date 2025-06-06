## Bootstrapping

To ensure this project is and remains bootstrappable, it is essential to limit the types of modifications allowed in each release cycle.

These are the main components of this project, along with the types of modifications each can go through:

- **spec**: Everything under `spec/`.
    - **no**: No modification.
    - **no-host**: Modification without changing host language.
    - **yes**: Modification changing host language.
- **lib**: Everything under `lib/`.
    - **no**: No modification.
    - **no-api**: Modification without changing API.
    - **yes**: Modification changing API.
- **src-gen**: Generated files under `src/`.
    - **no**: No modification.
    - **no-api**: Modification without changing API.
    - **yes**: Modification changing API. API changes when `spec` is modified or when API of `lib` is changed affecting `src-gen`.
- **src-hand**: Hand-written files under `src/`.
    - **no**: No modification. Output cannot change without modifying `spec`.
    - **no-out**: Modification without changing output.
    - **yes**: Modification changing output.

The modifications allowed in a release cycle follow these guiding principles:

<!-- ~G(t) | G(t) -> !H(t) | ~H(t) -->
- **Modification stability**: Whenever `src-gen` is modified, the output cannot change.
<!-- H(t) | ~S(t) -> !L(t) & !G(t) -->
- **Modification minimalism**: Whenever `src-hand` is modified changing output or `spec` is modified without changing host language, `lib` and `src-gen` cannot be modified.
    <!-- ~L(t) | L(t) | ~H(t) -> !S(t) & !G(t) -->
    - In a single-step release cycle, whenever `lib` is modified or `src-hand` is modified without changing output, `spec` and `src-gen` cannot be modified.
<!-- ~G(t + 1) | G(t + 1) -> H(t) | ~S(t) -->
- **Generated source traceability**: For `src-gen` to be modified, `src-hand` must be modified changing output or `spec` must be modified without changing host language in the previous step.
<!-- S(t + 1) -> ~S(t) -->
- **Specification traceability**: For `spec` to be modified changing host language, `spec` must be modified without changing host language in the previous step.

The only modifications allowed in a single-step release cycle are:

| # | spec | lib    | src-gen | src-hand |
|---|------|--------|---------|----------|
| 0 | no   | no     | no      | no-out   |
| 1 | no   | no-api | no      | no       |
| 2 | no   | no-api | no      | no-out   |
| 3 | no   | yes    | no      | no       |
| 4 | no   | yes    | no      | no-out   |

The only modifications allowed in a two-step release cycle are:

| #  | spec    | lib | src-gen | src-hand | -> | spec | lib | src-gen | src-hand |
|----|---------|-----|---------|----------|----|------|-----|---------|----------|
| 5  | no      | no  | no      | yes      | -> | no   | no  | no-api  | no       |
| 6  | no      | no  | no      | yes      | -> | no   | yes | yes     | no       |
| 7  | no      | no  | no      | yes      | -> | no   | yes | yes     | no-out   |
| 8  | no-host | no  | no      | no       | -> | yes  | no  | yes     | no       |
| 9  | no-host | no  | no      | no       | -> | yes  | no  | yes     | no-out   |
| 10 | no-host | no  | no      | yes      | -> | yes  | yes | yes     | no       |
| 11 | no-host | no  | no      | yes      | -> | yes  | yes | yes     | no-out   |

The first step is a pre-release and the last step is a stable release.
