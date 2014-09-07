#Sat Sep  6 2014

Heavily optimized pathfinding today. The changes are local to the framework, so
this is something I can carry over to future projects, which is very much needed
since it's been the bottleneck for performance. I'm sure there's some micro-
optimizations left to be made, but the improvement would be negligible.

#Thu Sep  4 2014

Felt more ambitious than usual and took a stab at multiprocessing - and it
worked this time, although currently only for pathfinding. Some general advice
is to choose your battles; in a language like Python, memory isn't easily shared
between two processes, so the time it will take to copy data from one process
to another needs to be considered. Unfortunately, a lot of things that would
benefit from SMP usually deal with a large amount of data, and the time spent
copying it might be longer than the non-SMP code takes to process it.

I did run into something unusual, though: pathfinding isn't made faster by SMP -
it's a bit slower, actually. Pathfinding (9 times out of 10) is the very last
bit of logic an NPC runs, which blocks the main thread from continuing to the
next NPC's logic. SMP allows us to offload that task and continue down the list
of NPCs, spawning processes for each pathing request, then waiting (if needed)
for the spawned processes to finish before we draw the frame.

Another challenge is deciding exactly when SMP needs to be used. Some paths are
better performed on the main thread (since copying over the relevant data to
new process is usually slower.) A good way to check is distance from the start
and end points: Large paths should be offloaded, while short ones should be done
on the main thread. However, we know that even a short distance can result in
paths 100x as long - in this case, we can sometimes look at the context and use
another metric to decide whether SMP is worh it in that case.

---

I've been working on AI for a while, so I think it's time to call it quits and
pick something else to work on. Map generation needs work; the Swamps bother me
because they're generated in such a stale way (and the current code I'm using
might actually be slower than something that uses a noise algo.) I might write
some general mapgen tools to experiment with different functions and their
inputs.

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
