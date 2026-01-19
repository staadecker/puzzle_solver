# Puzzle Solver

I developed this puzzle solver during 2026 [MIT Mystery Hunt](https://en.wikipedia.org/wiki/MIT_Mystery_Hunt) as a fun exercise to see if I could code an algorithm to solve a grid-style puzzle with arbitrary rules (e.g. like [this](https://puzz.link/rules.html?dbchoco) or [this](https://puzz.link/rules.html?fivecells)).

I had partial success but lots of fun and learning! The algorithm can solve a hard sudoku but I wasn't quite able to implement some of the more challenging puzzles.

## Algorithm details

Every game has a state, potential moves, rules, and an end condition. Thus, I define an abstract `GameState` class which has two notable methods: `generate_legal_moves() -> Move` and `is_solved() -> bool`. Different games can implement these methods differently according to their own rules. Importantly, a move is considered legal as long as it does not immediately break a game rule (e.g. can't move into check).

Some problems have rules that are only validated once the board is filled in. In these cases, we consider a move to be legal _as long as it doesn't prevent this rule from being satisfied later in the game_.

Note that at times there exists multiple moves that a player _could_ but one or more moves that a player _must_ play (e.g. when there's only one option left in a sudoku grid cell). In these cases, `generate_legal_moves()` should return only 1 move that a player must play. I call these _forced moves_.

Now given this `GameState` class, I wrote what I'd call an search-and-prune algorithm. 

I create a tree representing all the previously explored game states where playing a move is the way of exploring a new game state. I select a new move to further explore the tree, play the move and any subsequent forced moves, and then save the new game state as a a new node in the tree.

In the case where the new game state has no further potential legal moves, then the game is either solved (yay!) or we've reached a dead end.

Whenever a dead end is reached, the move that lead to it is marked as invalid. Next, the parent state (that lead to the dead end) is checked since there might now be a sequence of forced moves (since one of the parent's moves is no longer valid). If so, we play the forced move(s) and replace the parent with the result (if the forced moves were already explored we simply replace the parent with the explored node). Note that this algorithm is recursive: by playing the forced move(s) we might discover another dead-end in which case the process repeats further up the tree. This is the "pruning" part.

To efficiently search the tree, we use two criteria. First, we explore moves that have the fewest alternatives since invalidating this move is most likely to trigger pruning. Second, among moves with the same number of alternatives, we explore moves that are further down the game tree (Depth First Search) since it is easier to reach dead-ends (and thus make progress) after having played several moves.

### Learnings

Prior versions split the `generate_legal_moves()` into a `generate_moves()` and `is_legal()` function. Essentially, `generate_legal_moves()` would filter all the moves from `generate_moves()` by playing the move and checking `is_legal()`. This was quite conveniently easy to implement, but I ultimately found it to be much more efficient to combine both functions into one. In sudoku for example, a combined `generate_legal_moves()` can scan just the rows/col/box of a cell to determine the legality of a move, rather than checking the entire grid on every move.

The issue I ran into trying to solve the `lookair` puzzle was rather interesting. In Lookair, one must shade in a grid such that shaded cells always form squares (among other rules). As such, grid cells begin as `None` (undecided) and can transition to a state of either `SHADED` or `UNSHADED`. We'd expect that if we're able to declare a move to `UNSHADED` as invalid, then we could automatically mark the cell as `SHADED` (a forced move). However, it is possible that a single shaded square could be illegal while a 2x2 shaded square isn't. Thus, to leverage forced moves, we would have to allow illegal 1x1 (and larger) shaded squares, _as long as a future move can turn them into a legal (larger) square_. This greatly complicates the rule definition since now `generate_legal_moves()` must calculate whether any move will prevent a presently illegal square from becoming legal. The only alternative is to not leverage forced moves except when we've invalidating all but one possible arrangements of squares over a given grid cell. I fear this would blow up the problem size. A final workaround would be to allow illegal board states up until the end of the game at which point an additional final `is_legal()` check could be applied with the full set of rules. However, I fear this strategy is prone to failure since many board configurations would only ever be rejected when the bottom of the search tree is reached which would greatly increase the search time. Perhaps a simple-ish way to implement the `generate_legal_moves()` function exists but the weekend is almost over and it's time to move onto other things!

_One night of sleep later..._ Thinking about this further I've concluded that the proper implementation is to have a few functions:
- `is_maybe_legal()` should return `False` if we know the state can never become legal later in the game. If it is still unclear or difficult to compute, it is ok to return `True` since the function will be called again later when more cells are filled.
- `generate_legal_moves()` should now be modified to screen all its moves through the `is_maybe_legal()` function. As long as it passes the screen, it can return the move. To speed things up, `generate_legal_moves()` should begin by searching for any forced moves (and screen them through `is_maybe_legal()`).

**Update:** It works! I implemented a variation of the above and the algorithm is now able to solve the lookair puzzle!

## Example Output

```
>>> python ./lookair.py
╔═════════════╗ ╔═════════════╗ (move 11)
║ 3           ║ ║ █ █ ▒       ║
║ 3     3     ║ ║ █ █         ║
║           1 ║ ║ ▒           ║
║   2         ║ ║   ▒         ║
║   0   2     ║ ║ ▒ ▒ ▒       ║
║   1         ║ ║   ▒         ║
╚═════════════╝ ╚═════════════╝
╔═════════════╗ ╔═════════════╗ (move 12)
║ 3           ║ ║ █ █ ▒       ║
║ 3     3     ║ ║ █ █ ▒       ║
║           1 ║ ║ ▒           ║
║   2         ║ ║   ▒         ║
║   0   2     ║ ║ ▒ ▒ ▒       ║
║   1         ║ ║   ▒         ║
╚═════════════╝ ╚═════════════╝
╔═════════════╗ ╔═════════════╗ (move 13)
║ 3           ║ ║ █ █ ▒       ║
║ 3     3     ║ ║ █ █ ▒   █   ║
║           1 ║ ║ ▒           ║
║   2         ║ ║   ▒         ║
║   0   2     ║ ║ ▒ ▒ ▒       ║
║   1         ║ ║   ▒         ║
╚═════════════╝ ╚═════════════╝
╔═════════════╗ ╔═════════════╗ (move 14)
║ 3           ║ ║ █ █ ▒       ║
║ 3     3     ║ ║ █ █ ▒   █   ║
║           1 ║ ║ ▒ ▒         ║
║   2         ║ ║   ▒         ║
║   0   2     ║ ║ ▒ ▒ ▒       ║
║   1         ║ ║   ▒         ║
╚═════════════╝ ╚═════════════╝
╔═════════════╗ ╔═════════════╗ (move 17)
║ 3           ║ ║ █ █ ▒       ║
║ 3     3     ║ ║ █ █ ▒   █   ║
║           1 ║ ║ ▒ ▒         ║
║   2         ║ ║ █ ▒ █       ║
║   0   2     ║ ║ ▒ ▒ ▒       ║
║   1         ║ ║   ▒       █ ║
╚═════════════╝ ╚═════════════╝
╔═════════════╗ ╔═════════════╗ (move 20)
║ 3           ║ ║ █ █ ▒       ║
║ 3     3     ║ ║ █ █ ▒   █   ║
║           1 ║ ║ ▒ ▒         ║
║   2         ║ ║ █ ▒ █       ║
║   0   2     ║ ║ ▒ ▒ ▒   █ █ ║
║   1         ║ ║   ▒     █ █ ║
╚═════════════╝ ╚═════════════╝
╔═════════════╗ ╔═════════════╗ (move 21)
║ 3           ║ ║ █ █ ▒       ║
║ 3     3     ║ ║ █ █ ▒   █   ║
║           1 ║ ║ ▒ ▒         ║
║   2         ║ ║ █ ▒ █   ▒   ║
║   0   2     ║ ║ ▒ ▒ ▒   █ █ ║
║   1         ║ ║   ▒     █ █ ║
╚═════════════╝ ╚═════════════╝
╔═════════════╗ ╔═════════════╗ (move 22)
║ 3           ║ ║ █ █ ▒       ║
║ 3     3     ║ ║ █ █ ▒   █   ║
║           1 ║ ║ ▒ ▒         ║
║   2         ║ ║ █ ▒ █   ▒ ▒ ║
║   0   2     ║ ║ ▒ ▒ ▒   █ █ ║
║   1         ║ ║   ▒     █ █ ║
╚═════════════╝ ╚═════════════╝
╔═════════════╗ ╔═════════════╗ (move 23)
║ 3           ║ ║ █ █ ▒       ║
║ 3     3     ║ ║ █ █ ▒   █   ║
║           1 ║ ║ ▒ ▒         ║
║   2         ║ ║ █ ▒ █   ▒ ▒ ║
║   0   2     ║ ║ ▒ ▒ ▒ ▒ █ █ ║
║   1         ║ ║   ▒     █ █ ║
╚═════════════╝ ╚═════════════╝
╔═════════════╗ ╔═════════════╗ (move 27)
║ 3           ║ ║ █ █ ▒       ║
║ 3     3     ║ ║ █ █ ▒   █   ║
║           1 ║ ║ ▒ ▒ █ █     ║
║   2         ║ ║ █ ▒ █ █ ▒ ▒ ║
║   0   2     ║ ║ ▒ ▒ ▒ ▒ █ █ ║
║   1         ║ ║   ▒   ▒ █ █ ║
╚═════════════╝ ╚═════════════╝
╔═════════════╗ ╔═════════════╗ (move 29)
║ 3           ║ ║ █ █ ▒ █     ║
║ 3     3     ║ ║ █ █ ▒ ▒ █   ║
║           1 ║ ║ ▒ ▒ █ █     ║
║   2         ║ ║ █ ▒ █ █ ▒ ▒ ║
║   0   2     ║ ║ ▒ ▒ ▒ ▒ █ █ ║
║   1         ║ ║   ▒   ▒ █ █ ║
╚═════════════╝ ╚═════════════╝
╔═════════════╗ ╔═════════════╗ (move 30)
║ 3           ║ ║ █ █ ▒ █ ▒   ║
║ 3     3     ║ ║ █ █ ▒ ▒ █   ║
║           1 ║ ║ ▒ ▒ █ █     ║
║   2         ║ ║ █ ▒ █ █ ▒ ▒ ║
║   0   2     ║ ║ ▒ ▒ ▒ ▒ █ █ ║
║   1         ║ ║   ▒   ▒ █ █ ║
╚═════════════╝ ╚═════════════╝
╔═════════════╗ ╔═════════════╗ (move 31)
║ 3           ║ ║ █ █ ▒ █ ▒   ║
║ 3     3     ║ ║ █ █ ▒ ▒ █ ▒ ║
║           1 ║ ║ ▒ ▒ █ █     ║
║   2         ║ ║ █ ▒ █ █ ▒ ▒ ║
║   0   2     ║ ║ ▒ ▒ ▒ ▒ █ █ ║
║   1         ║ ║   ▒   ▒ █ █ ║
╚═════════════╝ ╚═════════════╝
╔═════════════╗ ╔═════════════╗ (move 32)
║ 3           ║ ║ █ █ ▒ █ ▒   ║
║ 3     3     ║ ║ █ █ ▒ ▒ █ ▒ ║
║           1 ║ ║ ▒ ▒ █ █ ▒   ║
║   2         ║ ║ █ ▒ █ █ ▒ ▒ ║
║   0   2     ║ ║ ▒ ▒ ▒ ▒ █ █ ║
║   1         ║ ║   ▒   ▒ █ █ ║
╚═════════════╝ ╚═════════════╝
╔═════════════╗ ╔═════════════╗ (move 34)
║ 3           ║ ║ █ █ ▒ █ ▒   ║
║ 3     3     ║ ║ █ █ ▒ ▒ █ ▒ ║
║           1 ║ ║ ▒ ▒ █ █ ▒ █ ║
║   2         ║ ║ █ ▒ █ █ ▒ ▒ ║
║   0   2     ║ ║ ▒ ▒ ▒ ▒ █ █ ║
║   1         ║ ║ ▒ ▒   ▒ █ █ ║
╚═════════════╝ ╚═════════════╝
╔═════════════╗ ╔═════════════╗ (move 36)
║ 3           ║ ║ █ █ ▒ █ ▒ ▒ ║
║ 3     3     ║ ║ █ █ ▒ ▒ █ ▒ ║
║           1 ║ ║ ▒ ▒ █ █ ▒ █ ║
║   2         ║ ║ █ ▒ █ █ ▒ ▒ ║
║   0   2     ║ ║ ▒ ▒ ▒ ▒ █ █ ║
║   1         ║ ║ ▒ ▒ █ ▒ █ █ ║
╚═════════════╝ ╚═════════════╝
```