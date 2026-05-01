# UCTP Hybrid Heuristic Submission Code

Run:

```bash
python timetabling.py --data data --iterations 2500
```

The script loads synthetic course, room, and conflict data; builds a DSATUR schedule; refines it using the hybrid local-search algorithm; and prints a lower bound from an LP relaxation. If SciPy is available, `scipy.optimize.linprog` is used. Otherwise, the script falls back to a valid assignment-relaxation lower bound that ignores conflicts.
