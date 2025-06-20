# Contributing Guidelines

## Code Style

All common, lexical and syntactic code in the library must follow this code style. Type hints, assertions, comments and documentation must be updated whenever the related code changes.

### Formatting

Code must be formatted using `black -l 79`.

### Linting

Code must pass `flake8` and `pylint`, with the only exceptions being due to changes made by `black`.

### Type Checking

Code must pass `mypy`, with the only exceptions being due to the limitations of the tool itself.

#### Type Hints

Global variables, class attributes and function/method signatures must be annotated. Local variables must only be annotated whenever `mypy` cannot infer the correct type.

#### Assertions

Assertions must be used to provide `mypy` with extra type information that type hints alone cannot. They must also be used to make explicit the implicit invariants in the code.

### Comments

Comments must be provided whenever a statement needs clarification of its purpose or how it works. They must also be used to document code that garantees invariants in the code.

### Documentation

Docstrings must be provided for all modules, classes and functions/methods, regardless of whether they are public/private. They must describe all attributes, arguments, return values and exceptions raised, regardless of whether they are public/private. They must also describe all invariants relevant across the code interfaces. They must use the Google-style format with Markdown markup.

## Reproducibility

To ensure this project is and remains [reproducible](https://reproducible-builds.org/), it is essential to ensure the collections iterated over when generating the output are ordered. In particular, sets and frozen sets must only be used if doing so would not change the output. Instead, use dictionaries, lists or tuples.

## Bootstrappability

To ensure this project is and remains [bootstrappable](https://bootstrappable.org/), it is essential to limit the types of modifications allowed in each release cycle.

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
    - **yes**: Modification changing API. API changes whenever `spec` is modified or whenever API of `lib` is changed affecting `src-gen`.
- **src-hand**: Hand-written files under `src/`.
    - **no**: No modification. Output cannot change without modifying `spec`.
    - **no-out**: Modification without changing output.
    - **yes**: Modification changing output.

The modifications allowed in a release cycle follow these guiding principles:

<!-- ~G(t) | G(t) -> !H(t) | ~H(t) -->
- **Modification stability**: Whenever `src-gen` is modified, the output must not change.
<!-- H(t) | ~S(t) -> !L(t) & !G(t) -->
- **Modification minimalism**: Whenever `src-hand` is modified changing output or `spec` is modified without changing host language, `lib` and `src-gen` must not be modified.
    <!-- ~L(t) | L(t) | ~H(t) -> !S(t) & !G(t) -->
    - In a single-step release cycle, whenever `lib` is modified or `src-hand` is modified without changing output, `spec` and `src-gen` must not be modified.
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
| 6  | no      | no  | no      | yes      | -> | no   | no  | yes     | no       |
| 7  | no      | no  | no      | yes      | -> | no   | no  | yes     | no-out   |
| 8  | no      | no  | no      | yes      | -> | no   | yes | yes     | no       |
| 9  | no      | no  | no      | yes      | -> | no   | yes | yes     | no-out   |
| 10 | no-host | no  | no      | no       | -> | yes  | no  | yes     | no       |
| 11 | no-host | no  | no      | no       | -> | yes  | no  | yes     | no-out   |
| 12 | no-host | no  | no      | yes      | -> | yes  | yes | yes     | no       |
| 13 | no-host | no  | no      | yes      | -> | yes  | yes | yes     | no-out   |

The first step is a pre-release and the last step is a stable release.
