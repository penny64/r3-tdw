#Thu Aug 21 EDT 2014

Moved all work done in tests/mapgen_tests to base game directory.

Entities can now make noises, although the implementation is still half-baked
and could use some more design work to access its full potential.

Cleaned up a few draw calls to only include entities visible to the player.
Observer Mode can be enabled by hitting (`o`) - this will draw all NPCs
and items regardless of whether the player can see them.
