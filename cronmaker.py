#!/usr/bin/env python3
"""cronmaker - Cron expression builder and validator."""
import argparse, re, sys, datetime, calendar

FIELDS = ['minute','hour','day','month','weekday']
RANGES = [(0,59),(0,23),(1,31),(1,12),(0,7)]
MONTH_NAMES = {v.lower():k for k,v in enumerate(calendar.month_abbr) if k}
DAY_NAMES = {'sun':0,'mon':1,'tue':2,'wed':3,'thu':4,'fri':5,'sat':6}

PRESETS = {
    '@yearly': '0 0 1 1 *', '@annually': '0 0 1 1 *',
    '@monthly': '0 0 1 * *', '@weekly': '0 0 * * 0',
    '@daily': '0 0 * * *', '@midnight': '0 0 * * *',
    '@hourly': '0 * * * *',
    '@every5m': '*/5 * * * *', '@every15m': '*/15 * * * *',
    '@every30m': '*/30 * * * *',
}

def explain_field(field, name, lo, hi):
    if field == '*': return f"every {name}"
    if '/' in field:
        base, step = field.split('/')
        return f"every {step} {name}s" + (f" from {base}" if base != '*' else "")
    if ',' in field: return f"{name} {field}"
    if '-' in field: return f"{name} {field}"
    return f"{name} {field}"

def explain(expr):
    expr = PRESETS.get(expr, expr)
    parts = expr.split()
    if len(parts) != 5: return f"Invalid: expected 5 fields, got {len(parts)}"
    descs = [explain_field(p, n, lo, hi) for p, (n, (lo, hi)) in zip(parts, zip(FIELDS, RANGES))]
    return "At " + ", ".join(descs)

def next_runs(expr, count=5):
    expr = PRESETS.get(expr, expr)
    parts = expr.split()
    if len(parts) != 5: return []
    
    def matches(val, field, lo, hi):
        if field == '*': return True
        for item in field.split(','):
            if '/' in item:
                base, step = item.split('/')
                base = lo if base == '*' else int(base)
                if (val - base) % int(step) == 0 and val >= base: return True
            elif '-' in item:
                a, b = map(int, item.split('-'))
                if a <= val <= b: return True
            else:
                if val == int(item): return True
        return False
    
    now = datetime.datetime.now().replace(second=0, microsecond=0) + datetime.timedelta(minutes=1)
    results = []
    dt = now
    for _ in range(525600):  # max 1 year
        if (matches(dt.minute, parts[0], 0, 59) and
            matches(dt.hour, parts[1], 0, 23) and
            matches(dt.day, parts[2], 1, 31) and
            matches(dt.month, parts[3], 1, 12) and
            matches(dt.weekday(), parts[4].replace('7','0'), 0, 6)):
            results.append(dt)
            if len(results) >= count: break
        dt += datetime.timedelta(minutes=1)
    return results

def main():
    p = argparse.ArgumentParser(description='Cron expression builder')
    sub = p.add_subparsers(dest='cmd')
    
    ex = sub.add_parser('explain', help='Explain cron expression')
    ex.add_argument('expr')
    
    nx = sub.add_parser('next', help='Show next N run times')
    nx.add_argument('expr')
    nx.add_argument('-n', type=int, default=5)
    
    pr = sub.add_parser('presets', help='List presets')
    
    bld = sub.add_parser('build', help='Build from description')
    bld.add_argument('--minute', default='*')
    bld.add_argument('--hour', default='*')
    bld.add_argument('--day', default='*')
    bld.add_argument('--month', default='*')
    bld.add_argument('--weekday', default='*')
    
    args = p.parse_args()
    if not args.cmd: p.print_help(); return
    
    if args.cmd == 'explain':
        print(explain(args.expr))
    elif args.cmd == 'next':
        runs = next_runs(args.expr, args.n)
        print(f"Expression: {args.expr}")
        print(f"Meaning:    {explain(args.expr)}")
        print(f"\nNext {len(runs)} runs:")
        for dt in runs:
            print(f"  {dt.strftime('%Y-%m-%d %H:%M (%A)')}")
    elif args.cmd == 'presets':
        for name, expr in sorted(PRESETS.items()):
            print(f"  {name:<15} {expr}")
    elif args.cmd == 'build':
        expr = f"{args.minute} {args.hour} {args.day} {args.month} {args.weekday}"
        print(f"Expression: {expr}")
        print(f"Meaning:    {explain(expr)}")

if __name__ == '__main__':
    main()
