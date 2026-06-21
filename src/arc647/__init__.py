"""arc647 — Team647 agents for the ARC-AGI-3-Agents framework.

The agents live in :mod:`arc647.agents` and subclass the framework's ``Agent``
base class. Importing that subpackage requires the ARC-AGI-3-Agents submodule on
``sys.path`` (the ``smoke_test.py`` entry point arranges this), so this top-level
package is kept import-light on purpose and does not eagerly import the agents.
"""

__all__: list[str] = []
