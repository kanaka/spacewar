import var, objs
import random, math

# Algorithm for processing AI agent DNA:
#   Build object list (random) order
#   For each gene in dna
#     For each object in object list
#       If object matches all bases (conditions) in gene
#         If same gene as last time, do next action and break
#         If different gene, do first action and break

# AI data structure constants
types = ['none', 'significant', 'hard', 'damage', 'ship', 'sun',
         'fire', 'spike', 'asteroid', 'shield', 'bullet', 'powerup']

actions = ['none', 'fire', 'thrust', 'rthrust', 'left', 'right']

comparisons = [
        'none',
        'rand_num',   # <rand> operator value
        'dist_dist',  # <dist * future1> operator <dist * future2 + value>
        'dist_num',   # <dist * future1> operator value
        'dir_dir',    # <dir * future1> operator <dir * future2 + value>
        'dir_num']    # <dir * future1> operator value

# future is index into futures array to get frames into the
# future for distance and direction
futures = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
           10,11,12,13,14,15,16,17,18,19,
           20,22,24,26,28,30,32,34,36,38,
           40,45,50,55,60,65,70,75,80,85]

# Meaning of value is either raw or index into distances
# or directions array depending on setting of comparisons
distances = [ 0,  10, 12, 14, 16,
              18, 20, 22, 24, 26,
              28, 30, 35, 40, 45,
              50, 55, 60, 65, 70,
              75, 80, 90,100,110,
             120,140,160,180,200,
             220,250,300,350,400,
             450,500,600,700,800]

directions = range(21) + range(-19,0)

# for distance, == means between previous and next
operators = ['==', '>', '<']

# Upper half of gauss distribution
def half_gauss(start, end):
    found = 0
    while not found:
        num = random.gauss(start, (end-start)/3.0)
        if num >= start and num <= end:
            found = 1
    return num

# Temporary mass objects for performing calculations
class Temp(objs.Mass):
    def __init__(self):
        x = 0
        y = 0
        dir = 0
t1 = Temp()
t2 = Temp()

# Each base represents a condition with 5 components
class Base:
    def __init__(self,c='none',f1=0,f2=0,v=0,op="=="):
        self.comparison = c
        self.future1 = f1
        self.future2 = f2
        self.value = v
        self.operator = op

    def random(self):
        self.comparison = random.choice(comparisons)
        self.future1 = int(half_gauss(0,40))
        self.future2 = int(half_gauss(0,40))
        self.value = int(half_gauss(0,40))
        self.operator = random.choice(operators)

    def test(self, ship, object):
        right = var.arena.right
        bottom = var.arena.bottom
        f1 = futures[self.future1]
        f2 = futures[self.future2]
        ret = 0
        if self.comparison == 'none':
            ret = 1
        elif self.comparison == 'rand_num':
            rand = random.randint(0,39)
            ret = 0
            if (self.operator == "<")  and (rand < self.value):  ret = 1
            if (self.operator == ">")  and (rand > self.value):  ret = 1
            if (self.operator == "==") and (rand == self.value): ret = 1
        elif self.comparison == 'dist_dist':
            t1.x = (ship.x + ship.vx * f1) % right
            t1.y = (ship.y + ship.vy * f1) % bottom
            t2.x = (object.x + object.vx * f1) % right
            t2.y = (object.y + object.vy * f1) % bottom
            dist1 = float(objs.Mass.distance(t1, t2))
            t1.x = (ship.x + ship.vx * f2) % right
            t1.y = (ship.y + ship.vy * f2) % bottom
            t2.x = (object.x + object.vx * f2) % right
            t2.y = (object.y + object.vy * f2) % bottom
            dist2 = float(objs.Mass.distance(t1, t2) + distances[self.value])
            if (self.operator == "<")  and (dist1 < dist2): ret = 1
            if (self.operator == ">")  and (dist1 > dist2): ret = 1
            if (self.operator == "=="):
                if abs((dist1 - dist2)/((dist1+dist2)/2)) < 0.2: ret = 1
        elif self.comparison == 'dist_num':
            t1.x = (ship.x + ship.vx * f1) % right
            t1.y = (ship.y + ship.vy * f1) % bottom
            t2.x = (object.x + object.vx * f1) % right
            t2.y = (object.y + object.vy * f1) % bottom
            dist1 = float(objs.Mass.distance(t1, t2))
            dist2 = float(distances[self.value])
            if (self.operator == "<")  and (dist1 < dist2): ret = 1
            if (self.operator == ">")  and (dist1 > dist2): ret = 1
            if (self.operator == "=="):
                if abs((dist1 - dist2)/((dist1+dist2)/2)) < 0.2: ret = 1
        elif self.comparison == 'dir_dir':
            t1.x = (ship.x + ship.vx * f1) % right
            t1.y = (ship.y + ship.vy * f1) % bottom
            t1.dir = ship.dir
            t2.x = (object.x + object.vx * f1) % right
            t2.y = (object.y + object.vy * f1) % bottom
            dir1 = float(objs.Mass.rel_direction(t1, t2))
            t1.x = (ship.x + ship.vx * f2) % right
            t1.y = (ship.y + ship.vy * f2) % bottom
            t1.dir = ship.dir
            t2.x = (object.x + object.vx * f2) % right
            t2.y = (object.y + object.vy * f2) % bottom
            dir2 = float(objs.Mass.rel_direction(t1, t2))
            dir2 = dir2 + directions[self.value] * (math.pi / 20.0)
            if dir2 > math.pi:
                dir2 -= 2*math.pi
            elif dir2 < -math.pi:
                dir2 += 2*math.pi
            #dir2 = dir2 % (math.pi * 2)
            #print "dir1: %f, dir2: %f" % (dir1, dir2)
            if (self.operator == "<")  and (dir1 < dir2): ret = 1
            if (self.operator == ">")  and (dir1 > dir2): ret = 1
            if (self.operator == "=="):
                if abs(dir1 - dir2) < math.pi/20: ret = 1
        elif self.comparison == 'dir_num':
            t1.x = (ship.x + ship.vx * f1) % right
            t1.y = (ship.y + ship.vy * f1) % bottom
            t1.dir = ship.dir
            t2.x = (object.x + object.vx * f1) % right
            t2.y = (object.y + object.vy * f1) % bottom
            dir1 = float(objs.Mass.rel_direction(t1, t2))
            dir2 = directions[self.value] * (math.pi / 20.0)
            if (self.operator == "<")  and (dir1 < dir2): ret = 1
            if (self.operator == ">")  and (dir1 > dir2): ret = 1
            if (self.operator == "=="):
                if abs(dir1 - dir2) < math.pi/20: ret = 1
        else:
            ret = 0
        return ret

    def mutate(self):
        pass

    def __repr__(self):
        #repr = "      base\n"
        repr  = self.comparison + " "
        repr += str(self.future1) + " "
        repr += str(self.future2) + " "
        repr += str(self.value) + " "
        repr += self.operator + " "

        return repr

# Each gene represents a stimulus->response entry
class Gene:
    def __init__(self):
        self.type = 'significant'
        self.base = [] # Up to six bases (conditions)
        self.action = []

    def random(self):
        self.type = random.choice(types)
        for i in range(6):
            base = Base()
            base.random()
            self.base.append(base)
        for i in range(random.randint(1,10)):
            self.action.append(random.choice(actions))

    def test(self, ship, object):
        match = 0
        if (self.type in object.taxonomy):
            match = 1
            for base in self.base:
                if not base.test(ship, object):
                    match = 0
                    break
        return match

    def mutate(self):
        pass

    def __repr__(self):
        repr  = "  <\n"
        repr += "    type: " + self.type + "\n"
        repr += "    <\n"
        for base in self.base:
            repr += "      "
            repr += base.__repr__()
            repr += "\n"
        repr += "    >\n"
        repr += "    action: "
        for action in self.action:
            repr += action
            repr += " "
        repr += "\n  >\n"
        return repr

null_gene = Gene()
null_gene.action = [None]
null_gene.base.append(Base())

# DNA is a list of genes in priority order
class DNA:
    def __init__(self):
        self.gene = []
        self.rating = 0

    def random(self):
        for i in range(random.randint(1,10)):
            gene = Gene()
            gene.random()
            self.gene.append(gene)

    def mutate(self):
        pass

    def __repr__(self):
        repr = "<\n"
        for gene in self.gene:
            repr += gene.__repr__()
        repr += "\n>"
        return repr

dna_pool = []

def load_dna_pool(file="default"):
    global dna_pool

    # Reset the pool
    dna_pool = []

    file = "ai/" + file
    try:
        ai_file = open(var.get_resource(file))
    except:
        # Not found so randomize the pool
        for i in range(var.population_size):
            dna = DNA()
            dna.random()
            dna_pool.append(dna)
        return

    lines = []
    for line in ai_file.readlines():
        line = line.strip()
        if line != "" and line[0] != "#":
            lines.append(line)

    cur_line = 0
    dna_count = int(lines[cur_line])
    cur_line += 1
    for dna_num in range(dna_count):
        dna = DNA()
        dna_pool.append(dna)
        gene_count = int(lines[cur_line])
        cur_line += 1
        for gene_num in range(gene_count):
            gene = Gene()
            dna.gene.append(gene)
            gene.type = lines[cur_line]
            cur_line += 1
            gene.base = []
            for base_num in range(6):
                base = Base()
                gene.base.append(base)
                parts = lines[cur_line].split(',')
                base.comparison = parts[0]
                base.future1 = int(parts[1])
                base.future2 = int(parts[2])
                base.value = int(parts[3])
                base.operator = parts[4]
                cur_line +=1
            gene.action = lines[cur_line].split(',')
            cur_line +=1
        #print dna

def save_dna_pool(file="new"):
    save_dna_formatted(file=file, format="raw")


def save_dna_formatted(file="new.json", format="json"):
    import json, yaml
    global dna_pool

    file = "ai/" + file
    ai_file = open(var.get_resource(file), 'w')

    raw = []

    for dna in dna_pool:
        raw.append([])
        for gene in dna.gene:
            raw[-1].append({"type": gene.type,
                            "bases": [],
                            "actions": gene.action})
            for base in gene.base:
                raw[-1][-1]["bases"].append({"comparison": base.comparison,
                                             "future1": base.future1,
                                             "future2": base.future2,
                                             "value":   base.value,
                                             "operator": base.operator})

    if format == "json":
        ai_file.write(json.dumps(raw, indent=2))
    elif format == "yaml":
        ai_file.write(yaml.dump(raw))
    elif format == "raw":
        ai_file.write("%d\n" % len(raw))
        for dna in raw:
            ai_file.write("    %d\n" % len(dna))
            for gene in dna:
                ai_file.write("        %s\n" % gene['type'])
                for base in gene['bases']:
                    ai_file.write("            %s,%d,%d,%d,%s\n" %
                    (base['comparison'],
                     base['future1'],
                     base['future2'],
                     base['value'],
                     base['operator']))
                actions = ",".join(gene['actions'])
                ai_file.write("        %s\n\n" % actions)
            ai_file.write("\n")
    else:
        raise Exception("unknown format %s" % format)

def runga(players):
    # Create a new dna pool based on previous pool

    # Three options for pro-creation:
    # 1. Pure cross-breed
    # 2. Cross-breed with mutation
    # 3. Pure random DNA

    pass
