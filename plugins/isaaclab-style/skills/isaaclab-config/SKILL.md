---
name: isaaclab-config
description: The user's conventions for Isaac Lab / UWLab configuration classes (`@configclass`), covering how to define variants by subclassing, where to override inherited fields and terms (`__post_init__`), keeping `__post_init__` idempotent under `cfg.copy()`/`cfg.replace()`, asset configurations (`ArticulationCfg`, `RigidObjectCfg`) and multiple inheritance. Use this whenever writing, editing or reviewing Isaac Lab environment, scene, robot, event, reward, observation or asset configs. Apply the `python-style` skill as well, since these rules build on it.
---

# Isaac Lab Configuration Classes

These rules extend the general Python style (the `python-style` skill); follow both.

- Define each configuration variant as a configclass that subclasses its base, so the whole object is defined in
  one class body. Do not copy a module-level instance and assign to its fields afterwards
  (`IMPLICIT_ROBOT = ROBOT.copy()` followed by `IMPLICIT_ROBOT.actuators = {...}`).
- A configclass that inherits another declares as class fields only what it adds or replaces whole (a robot, a
  scene entity, a variant's events or actions).
- Changes to an inherited field or term (a parameter of an event, reward or observation term, a light intensity, an
  initial position) are made in `__post_init__`, after `super().__post_init__()`. Do not build module-level
  instances of the parent configuration (`_UR5E_SCENE = ur5e.RlStateSceneCfg()`) or copy terms with helpers such as
  `_with_params` to override them in the class body.
- Every `__post_init__` must give the same result when it runs twice: `cfg.copy()` and `cfg.replace()` run it again
  on the copied values. Guard any step that derives fields from terms it then removes.
- Asset configurations (subclasses of `ArticulationCfg`, `RigidObjectCfg` and the like) set no fields in
  `__post_init__`: every asset copies its configuration when it is created, which runs `__post_init__` again and
  silently undoes any override of those fields (a Hydra override, a scene's `__post_init__`). Declare such a field in
  the class body instead, built by a shared function when variants differ in one argument.
- With multiple inheritance, call `super().__post_init__()` so every parent's `__post_init__` runs in MRO order;
  do not call a parent's `__post_init__` by name.
- Group the classes of a configuration module by role under comment banners, for example `Scene`, `Events`,
  `Observations`, `Rewards` and `Environments`.
