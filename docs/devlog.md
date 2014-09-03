#Wed Sep  3 2014

Of course the good ideas come at 2 AM: Looks like I'll be able to do some proper
flanking in the combat positioning logic via node set pathfinding. Details:

1) Set the weight of the node set to a high number (1000)

2) Do regular node scoring, using node set pathfinding if needed

3) Apply score to weight

4) Apply weights, run pathfinding

Assuming nodes are scored with friendly/enemy positions in mind, flanking,
target avoidance, and proper firing positions are all found automatically by the
search. First thing I'm doing in the morning.

#Tue Sep  2 2014

Working with the GOAP model a bit for human NPCS: Looks like a monolithic combat
brain isn't going to cut it, so we need to split functionality up into a few
smaller brains. The problem is that we could easily segue into a glorified FSM
if we focus on smaller brains rather than larger ones. I have a lot of faith in
GOAPY, but when you're attempting to satisfy a large amount of conditions the
lines start blurring a bit and it's hard to map everything out.

I've been meaning to write some debug tools. Seeing metas in-game is handy, but
brains can be tested outside of the game entirely, so maybe a tool can be
created to ease the "trial-and-error"-ness of the current process.

#Sun Aug 24 2014

Wrote up designs for Factions and Squads, in addition to implementing some basic
functionality and wiring Squad metas up to NPC metas for testing. Future changes
might include disabling NPC brains instead of invalidating goal conditions via
squad metas - we'll see after more NPC logic is introduced.

#Fri Aug 22 2014

Looking into faster node graph lookups. The design document calls for "sets"
of nodes so we aren't checking each one. Ideally, "sets" would be context-aware
and be able to provide the searcher with a few "hints" as to what nodes should
be checked (building, etc.)

#Thu Aug 21 2014

Moved all work done in tests/mapgen_tests to base game directory.

Entities can now make noises. Currently NPCs use them to send a callback to
the hearer that causes them to update the potential location of a lost target.
In the future this functionality might change to allow an NPC to mistake a sound
as being made by the wrong target.

Cleaned up a few draw calls to only include entities visible to the player.
Observer Mode can be enabled by hitting `o` - this will draw all NPCs
and items regardless of whether the player can see them.
