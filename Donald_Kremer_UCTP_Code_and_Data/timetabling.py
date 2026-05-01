#!/usr/bin/env python3
"""University Course Timetabling: DSATUR, local search hybrid, and LP relaxation bound.
Runs without external packages except optional scipy for the LP relaxation.
Author: Donald Kremer
Date: 04/24/2026
"""
import csv, math, random, argparse, os
from collections import defaultdict

def load_data(path):
    courses=[]; enroll={}; instr={}
    with open(os.path.join(path,'courses.csv')) as f:
        for r in csv.DictReader(f):
            courses.append(r['course_id']); enroll[r['course_id']]=int(r['enrollment']); instr[r['course_id']]=r['instructor']
    rooms=[]; cap={}
    with open(os.path.join(path,'rooms.csv')) as f:
        for r in csv.DictReader(f):
            rooms.append(r['room_id']); cap[r['room_id']]=int(r['capacity'])
    conflicts=defaultdict(dict)
    with open(os.path.join(path,'conflicts.csv')) as f:
        for r in csv.DictReader(f):
            a,b,w=r['course_a'],r['course_b'],int(r['weight'])
            conflicts[a][b]=w; conflicts[b][a]=w
    return courses, rooms, enroll, instr, cap, conflicts

def cost(schedule, courses, enroll, instr, cap, conflicts, hard_weight=1000):
    penalty=0; soft=0; hard=0
    for a in courses:
        ta,ra=schedule[a]
        if enroll[a] > cap[ra]: hard += 1; penalty += hard_weight*(enroll[a]-cap[ra])
        for b,w in conflicts[a].items():
            if a < b and ta == schedule[b][0]: hard += 1; penalty += hard_weight*w
    by_instr=defaultdict(list)
    for c,(t,r) in schedule.items(): by_instr[(instr[c],t)].append(c)
    for key, cs in by_instr.items():
        if len(cs)>1: hard += len(cs)-1; penalty += hard_weight*(len(cs)-1)
    # soft: prefer smaller adequate room and avoid late slots
    for c,(t,r) in schedule.items():
        soft += max(0, cap[r]-enroll[c]) * 0.08 + (t%5)*1.5
    return penalty+soft, hard, soft

def dsatur(courses, rooms, enroll, instr, cap, conflicts, timeslots=20):
    assignment={}; degrees={c:len(conflicts[c]) for c in courses}
    while len(assignment)<len(courses):
        un=[c for c in courses if c not in assignment]
        def sat(c): return len({assignment[n][0] for n in conflicts[c] if n in assignment})
        c=max(un, key=lambda x:(sat(x), degrees[x], enroll[x]))
        best=None
        for t in range(timeslots):
            conflict_count=sum(conflicts[c].get(n,0) for n in conflicts[c] if n in assignment and assignment[n][0]==t)
            instructor_count=sum(1 for n in assignment if instr[n]==instr[c] and assignment[n][0]==t)
            for r in sorted(rooms, key=lambda rr:(cap[rr] < enroll[c], cap[rr])):
                room_pen=max(0,enroll[c]-cap[r])*1000 + max(0,cap[r]-enroll[c])*0.08
                score=(conflict_count+instructor_count)*1000 + room_pen + (t%5)*1.5
                if best is None or score<best[0]: best=(score,t,r)
        assignment[c]=(best[1],best[2])
    return assignment

def hybrid_local_search(schedule, courses, rooms, enroll, instr, cap, conflicts, iterations=2500, timeslots=20, seed=7):
    random.seed(seed)
    best=dict(schedule); cur=dict(schedule)
    best_score=cost(best,courses,enroll,instr,cap,conflicts)[0]
    cur_score=best_score
    high_conf=sorted(courses, key=lambda c:(len(conflicts[c]),enroll[c]), reverse=True)
    for it in range(1,iterations+1):
        hard_weight=200 + 1800*(it/iterations)
        c=random.choice(high_conf[:max(10,len(courses)//3)]) if random.random()<0.65 else random.choice(courses)
        old=cur[c]
        if random.random()<0.50:
            new=(random.randrange(timeslots), old[1])
        elif random.random()<0.80:
            new=(old[0], random.choice(rooms))
        else:
            d=random.choice(courses); cur[c],cur[d]=cur[d],cur[c]
            new=None
        if new is not None: cur[c]=new
        new_score=cost(cur,courses,enroll,instr,cap,conflicts,hard_weight)[0]
        temp=max(0.01, 25*(1-it/iterations))
        if new_score<cur_score or random.random()<math.exp((cur_score-new_score)/max(temp,0.01)):
            cur_score=new_score
            true_score=cost(cur,courses,enroll,instr,cap,conflicts)[0]
            if true_score<best_score:
                best_score=true_score; best=dict(cur)
        else:
            if new is None: cur[c],cur[d]=cur[d],cur[c]
            else: cur[c]=old
    return best

def lp_relaxation_bound(courses, rooms, enroll, instr, cap, conflicts, timeslots=20):
    # Optional scipy lower-bound model: assignment relaxation with room-capacity slack penalties.
    try:
        from scipy.optimize import linprog
        vars=[(c,t,r) for c in courses for t in range(timeslots) for r in rooms]
        idx={v:i for i,v in enumerate(vars)}
        cvec=[]
        for c,t,r in vars:
            cvec.append(max(0, enroll[c]-cap[r])*1000 + max(0, cap[r]-enroll[c])*0.08 + (t%5)*1.5)
        Aeq=[]; beq=[]
        for c in courses:
            row=[0.0]*len(vars)
            for t in range(timeslots):
                for r in rooms: row[idx[(c,t,r)]]=1.0
            Aeq.append(row); beq.append(1.0)
        res=linprog(cvec, A_eq=Aeq, b_eq=beq, bounds=(0,1), method='highs')
        return float(res.fun) if res.success else None
    except Exception:
        # Safe lower bound: minimum individual assignment costs, ignoring conflicts.
        return sum(min(max(0,enroll[c]-cap[r])*1000 + max(0,cap[r]-enroll[c])*0.08 + (t%5)*1.5 for t in range(timeslots) for r in rooms) for c in courses)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--data', default='data'); ap.add_argument('--iterations', type=int, default=2500)
    args=ap.parse_args()
    courses, rooms, enroll, instr, cap, conflicts=load_data(args.data)
    init=dsatur(courses,rooms,enroll,instr,cap,conflicts)
    hybrid=hybrid_local_search(init,courses,rooms,enroll,instr,cap,conflicts,args.iterations)
    for name,s in [('DSATUR',init),('Hybrid',hybrid)]:
        total,hard,soft=cost(s,courses,enroll,instr,cap,conflicts)
        print(f'{name}: total_cost={total:.2f}, hard_violations={hard}, soft_cost={soft:.2f}')
    print(f'LP relaxation lower bound: {lp_relaxation_bound(courses,rooms,enroll,instr,cap,conflicts):.2f}')
if __name__=='__main__': main()
