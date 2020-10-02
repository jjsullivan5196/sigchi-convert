## Usage examples

### Print usage/help
```bash
./convert.py -h
```

### Straight pipeline
```bash
cat program.json | ./convert.py > papers.json
```

### Input/output from arguments
```bash
./convert.py --prog program.json --out papers.json
```

### Only include papers
```bash
./convert.py --prog program.json --out papers.json --types Paper
```