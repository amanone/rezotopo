#!/usr/bin/env python
import copy
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
        print " - Checking IPs: %s vs %s" % (self, other)
        print " --- Mask is %d" % (32 - biggest)
        print " --- Masked  : %s\t=?\t%s" % (bin(self.address >> biggest), bin(other.address >> biggest))
        print " --- Unmasked: %s\t=?\t%s" % (bin(self.address), bin(other.address))
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
        self.routes = []
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
                self.routes.append((route[1], Ip(route[0])))

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

def checkSubnet(machin, dest, subnet, subnetIp):
    print " + Checking subnet %s" % subnet
    for subnetMachine in subnets[subnet]:
        if dest.name == subnetMachine.name:
            print " +-- Found target machine %s in subnet %s" % (dest.name, subnet)
            if subnetIp.check(subnetMachine.subnetPair[subnet]):
                return True
    return False

def hop(machin, dest, ttl):
    print "======"
    print "Hopping at %s, ttl: %s" % (machin, ttl)
    if ttl == 0:
        print "Packet died"
        return False
    print "Seeking machine in subnets..."
    for subnet, subnetIp in machin.subnetPair.items():
        if checkSubnet(machin, dest, subnet, subnetIp):
            return True
    print "Machine not found in subnet, trying routes..."
    for route, routeIp in machin.routes:
        print " + Checking route %s" % route
        destUnmaskedIp = copy.deepcopy(dest.subnetPair.values()[0])
        destUnmaskedIp.mask = routeIp.mask
        if routeIp.check(destUnmaskedIp):
            for subnet, subnetIp in machin.subnetPair.items():
                if checkSubnet(machin, machines[route], subnet, subnetIp):
                    return hop(machines[route], dest, ttl - 1)
    print "No route found, hopping to default route: %s" % machin.defaultRoute
    print "Seeking default router in subnets..."
    for subnet, subnetIp in machin.subnetPair.items():
        if checkSubnet(machin, machines[machin.defaultRoute], subnet, subnetIp):
            return hop(machines[machin.defaultRoute], dest, ttl - 1)
    print "Default route unreachable"
    return False

for line in sys.stdin.readlines():
    Machin(line[:-1])

print "Machines: %s" % machines.values()
print "Subnets: %s" % subnets

print "Trying to go from %s to %s" % (sys.argv[1], sys.argv[2])
print "Target is:"
machines[sys.argv[2]].dump()
print hop(machines[sys.argv[1]], machines[sys.argv[2]], 64)
