#Thu Oct 2  2014

So many changes recently that I've lost count, but Trello reveals that I've gone
a long way in a week. Unfortunate that I can't always keep this pace, but what's
been happening lately is a lot of planning sessions followed by a sprint of
programming to implement it all. Currently work has been shifting to adding more
features rather than polishing old ones, which is hugely appreciated since
working on one thing for such a long period of time (mostly AI) can have
negative effects on productivity.

I'm looking for a way to announce this project. On more than one occasion I've
written a post only to delete it - no one way feels appropriate right now and I
might just as well keep it to myself until I can put out a video or demo showing
what I have to offer.

#Thu Sep 25 2014

A font change has changed the feeling of the game almost entirely, and new code
for generating the trade building looks great. I'm going to work on making this
area seems as alive as possible for the first official screenshot, which
shouldn't be too far off if I keep working at this rate. Also of note is the
change in resolution, which can go up to 1080p while still keeping 60fps. I've
settled for a smaller window, but I would like to enable custom window sizes
eventually for those who want to see more of the map.

#Mon Sep 22 2014

Lots of changes over the past 10+ days. We're floating between features right
now and evaluating what needs to be done first before we can realistically
begin growing more zones and approaching offline AI. The framework has become
predictable and stable - maybe in the future we should consider adding some kind
of subclassing for default systems (like `stats`.) Alternatively, move `stats`
out to gameland, because I very rarely feel safe editing the framework for game-
specific stuff.

Largely, there's still some major features missing that I'll need to address
soon: Item spawns and more mapgen landmarks. I have nothing left to add to the
Swamps because the player will hopefully not be spending much time there, so
that puts a lot of pressure on future mapgen functions.

#Thu Sep 11 2014

Firing positions got a redo yesterday, and I think it's safe to say this method
is much better; instead of doing some very demanding work to find the best
position right away, much simpler and faster logic is done more often, updating
every few moves instead. The advantage of the old method was having proper
distances to nodes based on node set paths, but now I'm using the old distance
formula with a +10 penalty to the node score when walls are found in the NPC's
LOS to that node. Any issues I have now are strictly related to not considering
multiple targets when choosing positions. Maybe a better method would be to
check each target's LOS to that node and score from there, picking the node that
the least number of targets can see.

#Mon Sep  8 2014

It occurs to me that that something is terribly broken with firing positions.
The node path is generating correctly, but unfortunately the gaps between nodes
are proving troublesome, causing NPCs to path through walls. The immediate
solution would be to ensure buildings are placed and sized to a number evenly
divisible by 3, but I may settle with just generating nodes at every tile.
Given that node set paths are generated in two passes (abstract path, then the
full path) we'd be doing less work by generating nodes on every tile. Scoring
node sets will be much harder now, though, but we can always delegate tasks to
another process if needed.

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
