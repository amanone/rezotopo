#!/usr/bin/env python
import sys

machines = {}
subnets = {}

class Ip:
    def __init__(self, full_ip):
        self.address = 0
        self.mask = 32
        self.full_ip = full_ip

        ip = full_ip.split("/")[0]
        self.mask = int(full_ip.split("/")[1])

        for component in ip.split("."):
            self.address = (self.address << 8) | int(component)

    def check(self, other):
        biggest = 32 - max(self.mask, other.mask)
        return (self.address >> biggest) == (other.address >> biggest)

    def __repr__(self):
        return self.full_ip

def addToDictList(i, i_key, l):
    if not l.has_key(i_key):
        l[i_key] = []
    l[i_key].append(i)

def addToSubnet(subnet, machin):
    addToDictList(machin, subnet, subnets)

def addToMachines(machin):
    machines[machin.name] = machin

class Machin:
    def __init__(self, descr):
        """ Format:
            <name> ip:subnet,ip:subnet,... default_route dest_ip:route,dest_ip:route,..."""

        self.subnetPair = {}
        self.routes = {}
        self.defaultRoute = None
        self.name = ""

        descr = descr.split(" ")
        self.name = descr[0]

        addToMachines(self)

        for subnet in descr[1].split(","):
            subnet = subnet.split(":")
            addToSubnet(subnet[1], self)
            self.subnetPair[subnet[1]] = Ip(subnet[0])

        self.defaultRoute = descr[2]

        if len(descr) == 4:
            for route in descr[3].split(","):
                route = route.split(":")
                self.routes[route[1]] = Ip(route[0]);

    def dump(self):
        print "Dumping machin " + self.name + " :"
        print "Subnet pairs:"
        print self.subnetPair
        print "Default route:"
        print self.defaultRoute
        print "Routes:"
        print self.routes
        print "== End of dump"

    def __repr__(self):
        return self.name

def hop(machin, dest, alreadyVisited):
    if machin.name in alreadyVisited:
        return False
    for subnet, ip in machin.subnetPair.items():
        for machineSubnet in subnets[subnet]:
            if dest.name == machineSubnet.name and ip.check(machineSubnet.subnetPair[subnet]):
                return True
    for route, routeIp in machin.routes.items():
        if routeIp.check([y for y in dest.subnetPair.values()][0]):
            alreadyVisited.append(machin.name)
            return hop(machines[route], dest, alreadyVisited)
    alreadyVisited.append(machin.name)
    return hop(machines[machin.defaultRoute], dest, alreadyVisited)

for line in sys.stdin.readlines():
    Machin(line[:-1])

print "Machines: " + str(machines.values())
print "Subnets: " + str(subnets)

print hop(machines[sys.argv[1]], machines[sys.argv[2]], [])
