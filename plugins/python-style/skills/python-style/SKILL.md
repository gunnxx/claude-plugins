---
name: python-style
description: The user's Python code style conventions for docstrings (Google style), module-level constants and their docstrings, comment banners, abstract methods, logging, type hints, naming, import order and the ordering of methods within a class. Use this whenever writing, editing, refactoring or reviewing Python code, even a small change to an existing file, so that new code matches these conventions.
---

# Python Code Style

Apply these rules to every piece of Python you write or change. When editing an existing file, also keep the code
you touch consistent with them.

## Docstrings

- Use Google-style docstrings with `Args:` and `Returns:` sections.
- All classes and methods must have docstrings.
- Constructors use `"""Constructor."""` as their docstring.
- For methods that return `None`, skip the `Returns:` part.
- Files start directly with the imports. No module docstring and no header comment, except the license header that
  the pre-commit `insert-license` hook adds. What a module provides is explained by its class and function
  docstrings and by the `README.md` of its package, which also holds the conventions (frames, units, sources) and
  the derivations and history behind the numbers.
- Inside docstrings, write code and identifiers in double backticks (``AGV_link``) and cross-reference other
  constants with the Sphinx role :data:`NAME`.

## Module-Level Constants

- Introduce one only for a value that several modules share or that is a genuine knob worth tuning. A value used
  in one place is written where it is used, with the explanation in that function's docstring.
- Names use UPPER_SNAKE_CASE.
- Every constant is documented by a docstring (a string literal) on the line directly after the assignment. Do not
  document constants with a comment above or beside them.
- The docstring says what the constant is: the quantity, the frame it is expressed in and the unit. Keep it to one
  or two sentences; derivations and history belong in the package README or in `docs/notes`.
- Separate consecutive constants with one blank line.
- Group related constants under a `# ===` comment banner. The banner text is a short title. One
  blank line follows the banner:
  ```python
  # ====================
  # Object Spawn Regions
  # ====================

  RECEPTIVE_X = (0.31, 0.41)
  """x range (env frame) in which the receptive object is spawned on the table top."""

  RECEPTIVE_Y = (-0.35, 0.05)
  """y range (env frame) in which the receptive object is spawned on the table top."""
  ```
- Derive dependent values from the constants they depend on instead of repeating numbers, for example
  `TABLE_CENTER_X = TABLE_EDGE_X + TABLE_HALF_LENGTH`.

## Abstract Classes

- Use `raise NotImplementedError("Subclasses must implement the <method>() method.")` for abstract methods. Do not
  use `ABC`/`abstractmethod`.

## Logging

- Use `logger = logging.getLogger(__name__)` at module level. Do not use `print` for logging.

## Type Hints

- All function signatures must have type hints for parameters and return types.
- As much as possible, use native type hints but if it does not exist, then use `typing` module and use
  `from typing import ...`.
- For methods that return `None`, skip the type hints.

## Naming

- Private attributes and methods are prefixed with `_`.
- Class names use PascalCase, methods use snake_case, module-level constants use UPPER_SNAKE_CASE.

## Imports

- Group imports in order: stdlib, third-party, local. Separated by blank lines.

## Code Organization

- Use section comment banners to group related methods within a class:
  ```python
  # =============
  # Section Title
  # =============
  ```
- The public methods should always be grouped at the top, after the constructor if exists.
- For private methods, try to group them based on their functionality. If there is only one private method for a
  group, then put it on the private methods comment banner.
- The same banner style groups module-level constants; see "Module-Level Constants".
- The same banner style groups the classes of a module by role, for example `Scene`, `Events`, `Observations`,
  `Rewards` and `Environments` in an environment configuration.
