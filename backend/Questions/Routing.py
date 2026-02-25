from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# REAL Node.js question bank (add as many as you want)
QUESTIONS = [
  {
    "question": "What is the primary function of a router's 'Routing Table'?",
    "options": {
      "A": "To store the MAC addresses of all local devices",
      "B": "To maintain a list of known network paths and determine the best interface for forwarding packets",
      "C": "To assign IP addresses to connected hosts via DHCP",
      "D": "To filter traffic based on application-layer protocols"
    },
    "answer": "B"
  },
  {
    "question": "Which metric does the Routing Information Protocol (RIP) use to determine the best path?",
    "options": {
      "A": "Bandwidth",
      "B": "Hop Count",
      "C": "Delay",
      "D": "Reliability"
    },
    "answer": "B"
  },
  {
    "question": "In Cisco routers, what is the default Administrative Distance (AD) of an OSPF route?",
    "options": {
      "A": "90",
      "B": "110",
      "C": "120",
      "D": "1"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Longest Prefix Match' rule in routing?",
    "options": {
      "A": "The router selects the path with the longest physical cable",
      "B": "The router prefers the most specific route (highest subnet mask) when multiple matches exist for a destination IP",
      "C": "The router renames the packet header to increase its length",
      "D": "The router selects the route that was added most recently"
    },
    "answer": "B"
  },
  {
    "question": "Which routing protocol is classified as a 'Link-State' protocol?",
    "options": {
      "A": "RIPv2",
      "B": "OSPF",
      "C": "EIGRP",
      "D": "BGP"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of a 'Floating Static Route'?",
    "options": {
      "A": "To route traffic to cloud-based services",
      "B": "To provide a backup route by assigning a higher Administrative Distance than the primary dynamic route",
      "C": "To allow IP addresses to change without updating the table",
      "D": "To load balance traffic across two identical links"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Feasible Successor' in EIGRP terminology?",
    "options": {
      "A": "The primary path used to forward traffic",
      "B": "A backup path that meets the feasibility condition and is ready for immediate use if the primary fails",
      "C": "A router that has been disconnected from the network",
      "D": "The router with the lowest MAC address in the AS"
    },
    "answer": "B"
  },
  {
    "question": "Which BGP message type is sent between peers to maintain the session and prevent the hold timer from expiring?",
    "options": {
      "A": "Open",
      "B": "Keepalive",
      "C": "Update",
      "D": "Notification"
    },
    "answer": "B"
  },
  {
    "question": "What does a 'Default Route' (0.0.0.0/0) do?",
    "options": {
      "A": "It blocks all traffic that doesn't have a specific match",
      "B": "It acts as a 'gateway of last resort' for traffic destined for networks not explicitly listed in the routing table",
      "C": "It resets the routing table every 24 hours",
      "D": "It forces all traffic to stay within the local LAN"
    },
    "answer": "B"
  },
  {
    "question": "In OSPF, what is the 'Router ID' primarily used for?",
    "options": {
      "A": "To encrypt the OSPF hello packets",
      "B": "To uniquely identify a router within an OSPF area and assist in DR/BDR elections",
      "C": "To set the speed of the router's CPU",
      "D": "To name the router in the DNS database"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Route Poisoning'?",
    "options": {
      "A": "A cyber attack that injects false routes into a table",
      "B": "A method used by distance-vector protocols to inform the network that a route is no longer reachable by setting its metric to infinity",
      "C": "Deleting a route manually from the CLI",
      "D": "Encrypting a route so it cannot be shared with neighbors"
    },
    "answer": "B"
  },
  {
    "question": "Which command is used on a Cisco router to view the current IPv4 routing table?",
    "options": {
      "A": "show interface status",
      "B": "show ip route",
      "C": "show run",
      "D": "show ip protocols"
    },
    "answer": "B"
  },
  {
    "question": "What is the default Administrative Distance of a 'Directly Connected' network?",
    "options": {
      "A": "1",
      "B": "0",
      "C": "5",
      "D": "20"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Convergence Time' in a network?",
    "options": {
      "A": "The time it takes to boot up a router",
      "B": "The time required for all routers in a network to update their routing tables and agree on the topology after a change",
      "C": "The duration of a TCP handshake",
      "D": "The time it takes for light to travel through a fiber cable"
    },
    "answer": "B"
  },
  {
    "question": "Which protocol is used to route traffic specifically between different Autonomous Systems (AS) on the Internet?",
    "options": {
      "A": "OSPF",
      "B": "BGP",
      "C": "EIGRP",
      "D": "RIP"
    },
    "answer": "B"
  },
  {
    "question": "In OSPF, what is the purpose of a 'Totally Stubby Area'?",
    "options": {
      "A": "To block all traffic from entering the area",
      "B": "To minimize the routing table size by blocking both external (Type 5) and inter-area (Type 3) routes, replacing them with a default route",
      "C": "To allow only redistributed RIP routes",
      "D": "To increase the frequency of Hello packets"
    },
    "answer": "B"
  },
  {
    "question": "Which BGP attribute is a Cisco-proprietary local value used to prefer one exit point from the local router?",
    "options": {
      "A": "Local Preference",
      "B": "Weight",
      "C": "MED",
      "D": "AS_Path"
    },
    "answer": "B"
  },
  {
    "question": "What are the default 'K-values' used by EIGRP to calculate its composite metric?",
    "options": {
      "A": "K1 (Bandwidth) and K2 (Load)",
      "B": "K1 (Bandwidth) and K3 (Delay)",
      "C": "K2 (Load) and K4 (Reliability)",
      "D": "K3 (Delay) and K5 (MTU)"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Route Summarization' (Aggregation) used for in a large routing domain?",
    "options": {
      "A": "To make the routing table more complex for security",
      "B": "To reduce the number of entries in routing tables by advertising a single summary address for multiple contiguous subnets",
      "C": "To speed up the physical transmission of data",
      "D": "To assign multiple IP addresses to a single interface"
    },
    "answer": "B"
  },
  {
    "question": "Which IPv6 routing protocol uses the 'FF02::5' and 'FF02::6' multicast addresses for communication?",
    "options": {
      "A": "RIPng",
      "B": "OSPFv3",
      "C": "EIGRP for IPv6",
      "D": "BGP4+"
    },
    "answer": "B"
  },
  {
    "question": "In BGP, what does the 'MED' (Multi-Exit Discriminator) attribute suggest to an adjacent Autonomous System?",
    "options": {
      "A": "The preferred path to leave the local AS",
      "B": "The preferred path to enter the local AS when multiple entry points exist",
      "C": "The total number of routers in the path",
      "D": "The speed of the internal backbone"
    },
    "answer": "B"
  },
  {
    "question": "What is the function of an 'Area Border Router' (ABR) in OSPF?",
    "options": {
      "A": "To connect different Autonomous Systems",
      "B": "To connect one or more OSPF areas to the backbone area (Area 0)",
      "C": "To act as the primary DHCP server for the area",
      "D": "To encrypt traffic between areas"
    },
    "answer": "B"
  },
  {
    "question": "Which EIGRP packet type is used to acknowledge the receipt of an Update, Query, or Reply?",
    "options": {
      "A": "Hello",
      "B": "ACK (Acknowledgment)",
      "C": "SIA-Query",
      "D": "Goodbye"
    },
    "answer": "B"
  },
  {
    "question": "What does a 'Null0' interface route signify in a routing table?",
    "options": {
      "A": "A high-speed fiber connection",
      "B": "A 'bit-bucket' used to discard packets, often used to prevent routing loops during summarization",
      "C": "A connection to a wireless access point",
      "D": "The primary loopback address for the router"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Split Horizon' used for in Distance-Vector protocols?",
    "options": {
      "A": "To divide the network into two equal parts",
      "B": "To prevent routing loops by ensuring a route is not advertised out the same interface it was learned from",
      "C": "To increase the bandwidth of a serial link",
      "D": "To allow two routers to share one IP address"
    },
    "answer": "B"
  },
  {
    "question": "Which OSPF LSA type is generated by an ASBR to describe external routes redistributed into OSPF?",
    "options": {
      "A": "Type 1 (Router LSA)",
      "B": "Type 5 (AS External LSA)",
      "C": "Type 3 (Summary LSA)",
      "D": "Type 2 (Network LSA)"
    },
    "answer": "B"
  },
  {
    "question": "What is the Administrative Distance of 'Internal EIGRP'?",
    "options": {
      "A": "20",
      "B": "90",
      "C": "110",
      "D": "170"
    },
    "answer": "B"
  },
  {
    "question": "In BGP, what happens to a route if its 'AS_Path' contains the local Autonomous System number?",
    "options": {
      "A": "The route is prioritized",
      "B": "The route is discarded to prevent a routing loop",
      "C": "The route is modified and re-sent",
      "D": "The route is encrypted"
    },
    "answer": "B"
  },
  {
    "question": "Which command-line tool is used on a router to verify the OSPF neighbor relationships?",
    "options": {
      "A": "show ip route ospf",
      "B": "show ip ospf neighbor",
      "C": "show ip ospf database",
      "D": "show ip protocols"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Redistribution' in routing?",
    "options": {
      "A": "Moving a router from one rack to another",
      "B": "The process of taking routes learned from one routing protocol and advertising them into another routing protocol",
      "C": "Upgrading the firmware on all routers at once",
      "D": "Assigning new IP addresses to all hosts"
    },
    "answer": "B",
  },
  {
    "question": "What is the primary purpose of 'BGP Communities'?",
    "options": {
      "A": "To provide a chat platform for network engineers",
      "B": "To group routes and apply administrative policies (like 'no-export' or 'no-advertise') across multiple prefixes",
      "C": "To count the number of routers in an Autonomous System",
      "D": "To replace the need for AS numbers"
    },
    "answer": "B"
  },
  {
    "question": "In OSPF, what is an 'NSSA' (Not-So-Stubby Area) used for?",
    "options": {
      "A": "To block all internet traffic",
      "B": "To allow an area to remain a stub while still permitting the redistribution of external routes via Type 7 LSAs",
      "C": "To connect to older RIP networks only",
      "D": "To disable the backbone area requirements"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Policy-Based Routing' (PBR) designed to override?",
    "options": {
      "A": "The physical speed of the interface",
      "B": "The standard destination-based routing table by using a route-map to steer traffic based on source IP or application type",
      "C": "The administrator's login password",
      "D": "The DNS resolution process"
    },
    "answer": "B"
  },
  {
    "question": "What does 'MP-BGP' (Multi-Protocol BGP) enable that standard BGP cannot?",
    "options": {
      "A": "Faster convergence on 10Gbps links",
      "B": "Support for multiple address families, such as IPv6, Multicast, and MPLS VPN labels, within a single BGP session",
      "C": "Automatic hardware upgrades",
      "D": "Naming routers with emojis"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Route Map' primarily used for in Cisco IOS?",
    "options": {
      "A": "To draw a visual diagram of the network",
      "B": "To provide a complex filtering and transformation mechanism for route redistribution and policy-based routing",
      "C": "To find the shortest physical path between two cities",
      "D": "To log the history of CLI commands"
    },
    "answer": "B"
  },
  {
    "question": "What is 'VRF-Lite'?",
    "options": {
      "A": "A low-power version of a router",
      "B": "The use of Virtual Routing and Forwarding to create multiple isolated routing tables on a single router without requiring MPLS",
      "C": "A routing protocol for mobile devices",
      "D": "A way to compress large routing tables"
    },
    "answer": "B"
  },
  {
    "question": "In EIGRP, what does a 'Stuck-In-Active' (SIA) state indicate?",
    "options": {
      "A": "The router has too much RAM",
      "B": "A router has not received a reply to a query from a neighbor within the allotted time (usually 3 minutes)",
      "C": "The physical cable is unplugged",
      "D": "The routing table is full"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Prefix-List' filtering's main advantage over standard Access Control Lists (ACLs)?",
    "options": {
      "A": "It is easier to type",
      "B": "It allows for matching based on the exact prefix length or a range of lengths (ge/le), which is more efficient for routing updates",
      "C": "It only works for wireless traffic",
      "D": "It encrypts the routing updates"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Administrative Distance' (AD) used for?",
    "options": {
      "A": "To measure the physical distance to the next hop",
      "B": "To determine the trustworthiness of a routing source when multiple protocols provide a path to the same destination",
      "C": "To calculate the speed of a link",
      "D": "To set the priority of a user's data"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Route Dampening' in BGP?",
    "options": {
      "A": "Keeping the router cool in humid environments",
      "B": "A mechanism to minimize the propagation of flapping routes (routes that repeatedly go up and down) by temporarily suppressing them",
      "C": "Increasing the interval of BGP updates",
      "D": "Deleting old routes automatically"
    },
    "answer": "B"
  },
  {
    "question": "Which BGP attribute is the second tie-breaker in the selection process, assuming Weight is equal?",
    "options": {
      "A": "AS_PATH",
      "B": "Local Preference",
      "C": "MED",
      "D": "Origin"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Bidirectional Forwarding Detection' (BFD) used for?",
    "options": {
      "A": "Sending data in two directions at once",
      "B": "Extremely fast detection of link failures between two adjacent routers to trigger faster routing protocol reconvergence",
      "C": "Encrypting two-way communications",
      "D": "Counting the number of packets sent and received"
    },
    "answer": "B"
  },
  {
    "question": "In OSPF, what is an 'ASBR' (Autonomous System Boundary Router)?",
    "options": {
      "A": "A router that only works within Area 0",
      "B": "A router that connects the OSPF domain to an external routing source, such as another AS or a different routing protocol",
      "C": "The primary backup router for the network",
      "D": "A router that handles only internal inter-area traffic"
    },
    "answer": "B"
  },
  {
    "question": "What is the default Administrative Distance for External EIGRP routes?",
    "options": {
      "A": "90",
      "B": "170",
      "C": "110",
      "D": "20"
    },
    "answer": "B"
  },
  {
    "question": "What is 'uRPF' (Unicast Reverse Path Forwarding) 'Strict Mode'?",
    "options": {
      "A": "It blocks all traffic that doesn't have a password",
      "B": "It requires that a packet's source IP address be reachable via the same interface it was received on, helping prevent spoofing",
      "C": "It reverses the direction of all outgoing traffic",
      "D": "It forces all traffic to use a specific static route"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary function of an OSPF 'Type 4 LSA' (ASBR Summary LSA)?",
    "options": {
      "A": "To advertise external routes to the backbone",
      "B": "To inform other areas how to reach the Autonomous System Boundary Router (ASBR)",
      "C": "To describe the link state of a specific router",
      "D": "To list all the neighbors on a multi-access segment"
    },
    "answer": "B"
  },
  {
    "question": "In BGP, what is 'AS_PATH Prepending' used for?",
    "options": {
      "A": "To make a route more attractive to internal peers",
      "B": "To influence inbound traffic by making a path appear longer and less desirable to external Autonomous Systems",
      "C": "To encrypt the routing updates",
      "D": "To speed up the convergence of eBGP sessions"
    },
    "answer": "B"
  },
  {
    "question": "What is 'EIGRP Named Mode'?",
    "options": {
      "A": "A mode where you give each router a nickname",
      "B": "A hierarchical configuration structure that organizes EIGRP commands under a single 'address-family' block, supporting both IPv4 and IPv6",
      "C": "A legacy mode used only for serial connections",
      "D": "A way to hide the Autonomous System number"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Administrative Distance' of a BGP route learned via an eBGP session?",
    "options": {
      "A": "200",
      "B": "20",
      "C": "170",
      "D": "1"
    },
    "answer": "B"
  },
  {
    "question": "Which mechanism allows an IPv6-only host to communicate with an IPv4-only server by translating the headers at the network layer?",
    "options": {
      "A": "6to4 Tunneling",
      "B": "NAT64",
      "C": "Dual Stack",
      "D": "GRE Tunneling"
    },
    "answer": "B"
  },
  {
    "question": "In OSPF, which LSA type is used to describe a multi-access network (like Ethernet) and is generated by the Designated Router (DR)?",
    "options": {
      "A": "Type 1",
      "B": "Type 2",
      "C": "Type 3",
      "D": "Type 5"
    },
    "answer": "B"
  },
  {
    "question": "What is 'BGP Route Reflector Cluster ID' used for?",
    "options": {
      "A": "To identify the physical location of the router",
      "B": "To prevent loops between different clusters of Route Reflectors within the same Autonomous System",
      "C": "To encrypt the BGP community tags",
      "D": "To measure the latency between peers"
    },
    "answer": "B"
  },
  {
    "question": "What happens when an EIGRP router does not receive a 'Hello' packet from a neighbor within the Hold Time interval?",
    "options": {
      "A": "It renames the neighbor",
      "B": "It declares the neighbor down and clears all routes learned through that neighbor",
      "C": "It sends a 'Thank You' packet",
      "D": "It waits indefinitely for the neighbor to return"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Stub Router' in the context of EIGRP?",
    "options": {
      "A": "A router with no neighbors",
      "B": "A router that limits the scope of EIGRP queries by telling neighbors not to query it for routes it doesn't own",
      "C": "A router that is used only for testing",
      "D": "The main core router of an enterprise"
    },
    "answer": "B"
  },
  {
    "question": "What is the function of the 'BGP NEXT_HOP' attribute when an eBGP route is passed into an iBGP session?",
    "options": {
      "A": "It automatically changes to the internal router's IP",
      "B": "It remains unchanged by default, which can lead to reachability issues unless 'next-hop-self' is configured",
      "C": "It is deleted to save space",
      "D": "It is encrypted for security"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary danger of 'Mutual Redistribution' between two routing protocols?",
    "options": {
      "A": "The router's CPU will melt",
      "B": "Suboptimal routing or routing loops caused by the feedback of routes back into their original protocol",
      "C": "The interface bandwidth will be reduced by 50%",
      "D": "All static routes will be deleted automatically"
    },
    "answer": "B"
  },
  {
    "question": "Which BGP community attribute prevents a route from being advertised to any eBGP peers, keeping it strictly within the local AS?",
    "options": {
      "A": "no-advertise",
      "B": "no-export",
      "C": "internet",
      "D": "local-as"
    },
    "answer": "B"
  },
  {
    "question": "In OSPF, what is the 'Forwarding Address' in a Type 5 LSA used for?",
    "options": {
      "A": "To tell the router where to send management logs",
      "B": "To avoid an extra hop by directing traffic to a specific next-hop address rather than the ASBR itself",
      "C": "To set the MAC address of the destination",
      "D": "To hide the identity of the source router"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Route Tagging' typically used for during redistribution?",
    "options": {
      "A": "To name a route for the administrator's reference",
      "B": "To identify and filter routes to prevent them from being redistributed back into their source domain (loop prevention)",
      "C": "To increase the priority of a packet",
      "D": "To encrypt the routing metric"
    },
    "answer": "B"
  },
  {
    "question": "What does 'RD' (Route Distinguisher) do in an MPLS Layer 3 VPN?",
    "options": {
      "A": "It determines which customer gets the fastest speed",
      "B": "It makes overlapping IPv4 addresses unique by prepending an 8-byte value, creating a VPNv4 address",
      "C": "It encrypts the data payload of the customer",
      "D": "It acts as a secondary password for the router"
    },
    "answer": "B"
  },
  {
    "question": "What is the function of 'RT' (Route Target) in MPLS VPNs?",
    "options": {
      "A": "To define the physical target of the fiber cable",
      "B": "To control which BGP VPNv4 routes are imported into or exported from a specific VRF",
      "C": "To set the maximum speed of the VPN tunnel",
      "D": "To count the number of packets in a session"
    },
    "answer": "B"
  },
  {
    "question": "In EIGRP, what happens to the metric of a route when it is redistributed from OSPF without a seed metric?",
    "options": {
      "A": "It inherits the OSPF cost",
      "B": "It is assigned a metric of infinity (unreachable), unless a default-metric is configured",
      "C": "It becomes 0",
      "D": "It is randomly assigned a value between 1 and 100"
    },
    "answer": "B"
  },
  {
    "question": "What is 'BFD' (Bidirectional Forwarding Detection) primarily used for in conjunction with BGP?",
    "options": {
      "A": "To increase the bandwidth of the BGP session",
      "B": "To provide sub-second failure detection, allowing BGP to reconverge much faster than its default timers allow",
      "C": "To encrypt the BGP Keepalive messages",
      "D": "To allow BGP to run over wireless links"
    },
    "answer": "B"
  },
  {
    "question": "What is 'MP-BGP Address Family' configuration used for?",
    "options": {
      "A": "To group routers by the family name of the owner",
      "B": "To separate the configuration and routing logic for different protocols (IPv4, IPv6, VPNv4) within a single BGP process",
      "C": "To limit the number of users on a network",
      "D": "To translate between different languages in the CLI"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'LISP EID' (Endpoint Identifier)?",
    "options": {
      "A": "The MAC address of the router",
      "B": "The IP address assigned to a host, which remains constant even if the host moves to a different network location",
      "C": "The serial number of the switch",
      "D": "The password for the wireless network"
    },
    "answer": "B"
  },
  {
    "question": "In OSPF, what is the difference between an External Type 1 (E1) and Type 2 (E2) route?",
    "options": {
      "A": "E1 is for IPv4 and E2 is for IPv6",
      "B": "E1 includes the internal cost to the ASBR in its metric calculation, while E2 only considers the external cost",
      "C": "E2 routes are always preferred over E1 routes",
      "D": "E1 routes cannot be summarized"
    },
    "answer": "B"
  },
  {
    "question": "What is 'BGP Bestpath Selection' tie-breaker when Weight, Local Preference, and AS_Path are all equal?",
    "options": {
      "A": "The router with the highest IP address",
      "B": "The Origin type (IGP < EGP < Incomplete)",
      "C": "The physical speed of the interface",
      "D": "The router that has been up the longest"
    },
    "answer": "B"
  },
  {
    "question": "What is the role of 'OMP' (Overlay Management Protocol) in a Cisco SD-WAN environment?",
    "options": {
      "A": "To encrypt the physical fiber lines",
      "B": "To exchange routing, security, and policy information between vSmart controllers and WAN Edge routers",
      "C": "To manage the power distribution to the server racks",
      "D": "To act as a backup for the DNS server"
    },
    "answer": "B"
  },
  {
    "question": "Which IPv6 transition technology allows ISPs to carry IPv6 traffic over an existing MPLS IPv4 core without upgrading the P-routers to IPv6?",
    "options": {
      "A": "NAT-PT",
      "B": "6PE (IPv6 Provider Edge)",
      "C": "ISATAP",
      "D": "Teredo Tunneling"
    },
    "answer": "B"
  },
  {
    "question": "What is 'BGP Conditional Advertisement' used for?",
    "options": {
      "A": "To advertise routes only on weekends",
      "B": "To advertise a specific prefix only if another prefix is present (or absent) in the routing table",
      "C": "To lower the cost of the internet bill",
      "D": "To encrypt the BGP community tags"
    },
    "answer": "B"
  },
  {
    "question": "What is the default 'Hold Time' for a BGP session on a Cisco router?",
    "options": {
      "A": "10 seconds",
      "B": "180 seconds",
      "C": "60 seconds",
      "D": "300 seconds"
    },
    "answer": "B"
  },
  {
    "question": "In EIGRP, what does the 'Active' state for a route indicate?",
    "options": {
      "A": "The route is functioning perfectly",
      "B": "The router has lost its successor and is currently querying neighbors for a replacement path",
      "C": "The interface is receiving too much traffic",
      "D": "The route has been manually disabled by the admin"
    },
    "answer": "B"
  },
  {
    "question": "What is 'BGP AS-Override' primarily used for?",
    "options": {
      "A": "To hide the router's identity",
      "B": "In MPLS VPNs, to allow a customer with the same AS number at different sites to accept routes from the provider",
      "C": "To speed up the BGP update process",
      "D": "To bypass the firewall"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'Route Refresh' (soft reconfiguration) in BGP?",
    "options": {
      "A": "To restart the router without losing data",
      "B": "To request a peer to re-send its full routing table without tearing down the BGP session",
      "C": "To clear the cache of the web browser",
      "D": "To update the firmware of the switch"
    },
    "answer": "B"
  },
  {
    "question": "Which routing concept describes the use of a 'Route-Map' to change the next-hop IP based on the size of the packet?",
    "options": {
      "A": "Dynamic Routing",
      "B": "Policy-Based Routing (PBR)",
      "C": "Static Routing",
      "D": "Default Routing"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary function of 'BGP Route Dampening'?",
    "options": {
      "A": "To increase the priority of a flapping route",
      "B": "To minimize the propagation of flapping routes across the internet by assigning a penalty and suppressing them temporarily",
      "C": "To keep the router hardware cool during heavy updates",
      "D": "To allow BGP to run over unstable satellite links"
    },
    "answer": "B"
  },
  {
    "question": "In MPLS, what does the 'Label Distribution Protocol' (LDP) do?",
    "options": {
      "A": "It renames the routers in the core",
      "B": "It establishes and maintains the label bindings between routers, allowing them to swap labels for packet forwarding",
      "C": "It encrypts the payload of the packets",
      "D": "It assigns IP addresses to the customer edge"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Administrative Distance' of a route learned via internal BGP (iBGP)?",
    "options": {
      "A": "20",
      "B": "200",
      "C": "110",
      "D": "90"
    },
    "answer": "B"
  },
  {
    "question": "Which BGP attribute is considered 'Well-Known Discretionary'?",
    "options": {
      "A": "AS_PATH",
      "B": "Local Preference",
      "C": "Weight",
      "D": "Next_Hop"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Route Distinguisher' (RD) used for in an MPLS Layer 3 VPN?",
    "options": {
      "A": "To set the speed of the customer's internet",
      "B": "To make overlapping customer IP addresses unique within the service provider's BGP table",
      "C": "To act as a secondary password for the VRF",
      "D": "To identify the physical port on the PE router"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Equal-Cost Multi-Path' (ECMP) in routing?",
    "options": {
      "A": "Routing traffic based on the cost of the hardware",
      "B": "A routing strategy where traffic is distributed across multiple paths that have the same metric to a destination",
      "C": "Forcing all traffic to use the cheapest available link",
      "D": "Sending a copy of every packet to two different routers"
    },
    "answer": "B"
  },
  {
    "question": "In OSPF, what is an 'External Type 2' (E2) route's metric?",
    "options": {
      "A": "The cumulative cost of the internal path plus the external cost",
      "B": "The cost of the external route only, regardless of the internal path cost to the ASBR",
      "C": "A fixed metric of 20 that never changes",
      "D": "The number of hops to the destination"
    },
    "answer": "B"
  },
  {
    "question": "What is 'BGP Next-Hop-Self' used for?",
    "options": {
      "A": "To allow a router to ping itself",
      "B": "To force an iBGP neighbor to use the advertising router's own IP as the next-hop for eBGP-learned routes",
      "C": "To hide the router's identity from the internet",
      "D": "To prevent the router from rebooting"
    },
    "answer": "B"
  },
  {
    "question": "What is the role of the 'vSmart' controller in a Cisco SD-WAN architecture?",
    "options": {
      "A": "To physically forward the user data packets",
      "B": "To act as the centralized control plane, distributing routing, security, and segmentation policies",
      "C": "To provide power to the WAN edge routers",
      "D": "To monitor the temperature of the data center"
    },
    "answer": "B"
  },
  {
    "question": "What is 'MTU Path Discovery' (PMTUD)?",
    "options": {
      "A": "A way to find the shortest physical cable",
      "B": "A technique to determine the largest packet size allowed on a path to avoid fragmentation",
      "C": "A tool for measuring the weight of a router",
      "D": "A method to find the MAC address of a gateway"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary function of 'BGP Route Reflection'?",
    "options": {
      "A": "To mirror traffic for legal interception",
      "B": "To solve the iBGP full-mesh requirement by allowing a central router to re-advertise iBGP learned routes to other iBGP peers",
      "C": "To backup the routing table to an external cloud drive",
      "D": "To reflect the signal of a wireless router"
    },
    "answer": "B"
  },
  {
    "question": "Which LSA type is used in OSPF to describe an 'External Route' from a different AS?",
    "options": {
      "A": "Type 1",
      "B": "Type 5",
      "C": "Type 3",
      "D": "Type 2"
    },
    "answer": "B"
  },
  {
    "question": "In BGP, what does the 'Atomic Aggregate' attribute indicate?",
    "options": {
      "A": "The router is about to restart",
      "B": "Information has been lost due to route summarization (aggregation) and the specific path data is no longer available",
      "C": "The packet size is at its smallest possible value",
      "D": "The routing protocol is working in high-efficiency mode"
    },
    "answer": "B"
  },
  {
    "question": "What is the purpose of 'EIGRP K-Values'?",
    "options": {
      "A": "To set the password for the EIGRP session",
      "B": "To act as constants in the composite metric formula (Bandwidth, Delay, Reliability, Load, MTU)",
      "C": "To count the number of hops to the destination",
      "D": "To identify the manufacturer of the router"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Split Horizon with Poison Reverse'?",
    "options": {
      "A": "A way to hide routes from certain users",
      "B": "A loop-prevention mechanism that sends a route back with a metric of infinity to indicate unreachability",
      "C": "A method to split one physical router into two virtual ones",
      "D": "A protocol for encrypting the routing table"
    },
    "answer": "B"
  },
  {
    "question": "Which BGP attribute is a non-transitive, optional attribute used to prefer one exit point from an AS?",
    "options": {
      "A": "AS_PATH",
      "B": "MED (Multi-Exit Discriminator)",
      "C": "Local Preference",
      "D": "Origin"
    },
    "answer": "B"
  },
  {
    "question": "In OSPF, what is the 'Backbone Area' ID?",
    "options": {
      "A": "0.0.0.1",
      "B": "0.0.0.0",
      "C": "1.1.1.1",
      "D": "255.255.255.0"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Route Redistribution' between OSPF and EIGRP?",
    "options": {
      "A": "Deleting OSPF routes and manually typing them into EIGRP",
      "B": "Configuring a router to share routes learned via OSPF into the EIGRP process and vice-versa",
      "C": "Physically connecting two routers with a crossover cable",
      "D": "Encrypting the routes so only OSPF can read them"
    },
    "answer": "B"
  },
  {
    "question": "Which command-line tool is used to trace the path a packet takes through multiple routers?",
    "options": {
      "A": "ping",
      "B": "traceroute / tracert",
      "C": "netstat",
      "D": "ipconfig"
    },
    "answer": "B"
  },
  {
    "question": "In a BGP path selection, if all other attributes are equal, which route is preferred?",
    "options": {
      "A": "The route from the neighbor with the highest IP address",
      "B": "The oldest route (the one that has been in the table the longest)",
      "C": "The route with the shortest physical cable",
      "D": "The route with the most emojis in the description"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Hold Time' for EIGRP by default on a high-speed link?",
    "options": {
      "A": "15 seconds",
      "B": "5 seconds",
      "C": "180 seconds",
      "D": "60 seconds"
    },
    "answer": "A"
  },
  {
    "question": "What does a 'Feasible Distance' (FD) represent in EIGRP?",
    "options": {
      "A": "The distance the neighbor says it is from the destination",
      "B": "The lowest calculated metric to reach a destination from the current router",
      "C": "The maximum physical distance allowed for a cable",
      "D": "The time it takes to send a packet"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary objective of 'Segment Routing' (SR) in a modern Service Provider network?",
    "options": {
      "A": "To divide a physical cable into smaller segments to increase speed",
      "B": "To simplify MPLS by removing the need for LDP/RSVP and using source-based routing for path steering",
      "C": "To encrypt data at the application layer of the OSI model",
      "D": "To assign a unique MAC address to every individual packet"
    },
    "answer": "B"
  },
  {
    "question": "In the context of 'BGP Flowspec', what is the purpose of distributing traffic-filtering rules via BGP?",
    "options": {
      "A": "To check the physical temperature of BGP neighbor interfaces",
      "B": "To mitigate DDoS attacks in real-time by propagating ACL-like rules across all BGP-enabled edge routers",
      "C": "To change the background color of the router CLI for easier reading",
      "D": "To monitor the electricity usage of the core routers"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Route Tagging' primarily used for during multi-protocol redistribution?",
    "options": {
      "A": "To name a route after the engineer who created it",
      "B": "To identify and filter routes to prevent 'feedback' loops when redistributing between two different protocols",
      "C": "To increase the priority of a packet based on its destination",
      "D": "To encrypt the routing metric so it cannot be read by other routers"
    },
    "answer": "B"
  },
  {
    "question": "Which BGP attribute is considered 'Well-Known Mandatory'?",
    "options": {
      "A": "Local Preference",
      "B": "AS_PATH",
      "C": "MED",
      "D": "Community"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Administrative Distance' (AD) of an OSPF external route (E1 or E2)?",
    "options": {
      "A": "90",
      "B": "110",
      "C": "170",
      "D": "20"
    },
    "answer": "B"
  },
  {
    "question": "In EIGRP, what does a 'Feasible Successor' represent?",
    "options": {
      "A": "The primary path used for forwarding all current traffic",
      "B": "A backup path that meets the feasibility condition and is ready for immediate use if the primary path fails",
      "C": "A router that has been disconnected from the network domain",
      "D": "The router with the lowest MAC address in the Autonomous System"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Policy-Based Routing' (PBR) used to override?",
    "options": {
      "A": "The physical speed of the interface",
      "B": "The standard destination-based routing table by steering traffic based on source IP or port",
      "C": "The administrator's login password for the router",
      "D": "The DNS resolution process of the client machine"
    },
    "answer": "B"
  },
  {
    "question": "What is the function of the 'vSmart' controller in a Cisco SD-WAN architecture?",
    "options": {
      "A": "To physically forward the user data packets across the fabric",
      "B": "To act as the centralized control plane, distributing routing, security, and segmentation policies",
      "C": "To provide physical power over ethernet (PoE) to the edge routers",
      "D": "To monitor the humidity levels in the remote server room"
    },
    "answer": "B"
  },
  {
    "question": "Which BGP message type is used to notify a neighbor of an error and subsequently close the session?",
    "options": {
      "A": "Keepalive",
      "B": "Notification",
      "C": "Update",
      "D": "Open"
    },
    "answer": "B"
  },
  {
    "question": "What is 'VRF-Lite' used for in enterprise networking?",
    "options": {
      "A": "A low-power version of a router for small home offices",
      "B": "To create multiple isolated routing tables on a single router without requiring MPLS",
      "C": "A routing protocol specifically designed for mobile tablets",
      "D": "A method to compress the size of the global routing table"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary function of 'BGP Route Dampening'?",
    "options": {
      "A": "To increase the priority of a flapping route",
      "B": "To minimize the propagation of flapping routes by assigning a penalty and suppressing them temporarily",
      "C": "To cool down the router hardware",
      "D": "To allow BGP to run over wireless links"
    },
    "answer": "B"
  },
  {
    "question": "In MPLS, what does 'LDP' stand for?",
    "options": {
      "A": "Link Data Protocol",
      "B": "Label Distribution Protocol",
      "C": "Local Device Path",
      "D": "Layer Delivery Protocol"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Administrative Distance' of a route learned via internal BGP (iBGP)?",
    "options": {
      "A": "20",
      "B": "200",
      "C": "110",
      "D": "90"
    },
    "answer": "B"
  },
  {
    "question": "Which BGP attribute is considered 'Well-Known Discretionary'?",
    "options": {
      "A": "AS_PATH",
      "B": "Local Preference",
      "C": "Weight",
      "D": "Next_Hop"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Route Distinguisher' (RD) used for in an MPLS Layer 3 VPN?",
    "options": {
      "A": "To set the bandwidth",
      "B": "To make overlapping customer IP addresses unique within the service provider's BGP table",
      "C": "To act as a secondary password",
      "D": "To identify the physical port"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Equal-Cost Multi-Path' (ECMP) in routing?",
    "options": {
      "A": "Routing based on hardware cost",
      "B": "Distributing traffic across multiple paths with the same metric to a destination",
      "C": "Forcing all traffic to the cheapest link",
      "D": "Sending a copy of every packet to two routers"
    },
    "answer": "B"
  },
  {
    "question": "In OSPF, what is an 'External Type 2' (E2) route's metric?",
    "options": {
      "A": "Cumulative cost of internal path plus external cost",
      "B": "The external cost only, regardless of the internal path cost to the ASBR",
      "C": "A fixed metric of 20",
      "D": "The number of hops"
    },
    "answer": "B"
  },
  {
    "question": "What is 'BGP Next-Hop-Self' used for?",
    "options": {
      "A": "To allow a router to ping itself",
      "B": "To force an iBGP neighbor to use the advertising router's IP as the next-hop for eBGP-learned routes",
      "C": "To hide the router's identity",
      "D": "To prevent the router from rebooting"
    },
    "answer": "B"
  },
  {
    "question": "What is the role of the 'vSmart' controller in a Cisco SD-WAN architecture?",
    "options": {
      "A": "To forward user data packets",
      "B": "To act as the centralized control plane, distributing routing, security, and policies",
      "C": "To provide power to routers",
      "D": "To monitor data center humidity"
    },
    "answer": "B"
  },
  {
    "question": "What is 'MTU Path Discovery' (PMTUD)?",
    "options": {
      "A": "Finding the shortest physical cable",
      "B": "Determining the largest packet size allowed on a path to avoid fragmentation",
      "C": "Measuring the weight of a router",
      "D": "Finding the MAC address of a gateway"
    },
    "answer": "B"
  },
  {
    "question": "Which protocol is used by 'Traceroute' to report the path taken by packets?",
    "options": {
      "A": "TCP",
      "B": "ICMP",
      "C": "FTP",
      "D": "HTTP"
    },
    "answer": "B"
  },
  {
    "question": "What is 'BGP AS-Override' primarily used for?",
    "options": {
      "A": "To hide the router's identity",
      "B": "To allow a customer with the same AS number at different sites to accept routes from the provider",
      "C": "To speed up updates",
      "D": "To bypass the firewall"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Anycast' routing?",
    "options": {
      "A": "Sending data to all users",
      "B": "Routing traffic to the nearest node in a group of potential receivers",
      "C": "A method for broadcasting video",
      "D": "An IP address for a single computer"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Hold Time' for BGP by default on most Cisco devices?",
    "options": {
      "A": "60 seconds",
      "B": "180 seconds",
      "C": "5 seconds",
      "D": "300 seconds"
    },
    "answer": "B"
  },
  {
    "question": "Which OSPF LSA type is generated by a DR to describe a multi-access segment?",
    "options": {
      "A": "Type 1",
      "B": "Type 2",
      "C": "Type 3",
      "D": "Type 4"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Unicast Reverse Path Forwarding' (uRPF)?",
    "options": {
      "A": "A way to speed up routing",
      "B": "A mechanism to verify the reachability of the source IP to prevent spoofing",
      "C": "Sending data backwards",
      "D": "A method to combine two IPs"
    },
    "answer": "B"
  },
  {
    "question": "What does a 'Metric' of 16 in RIP indicate?",
    "options": {
      "A": "A high-speed link",
      "B": "The network is unreachable (Infinity)",
      "C": "A path through 16 routers",
      "D": "The priority level"
    },
    "answer": "B"
  },
  {
    "question": "What is 'BGP Route Refresh'?",
    "options": {
      "A": "Restarting the router",
      "B": "Requesting a peer to re-send routes without resetting the BGP session",
      "C": "Clearing the browser cache",
      "D": "Updating the OS"
    },
    "answer": "B"
  },
  {
    "question": "In EIGRP, what is the 'Feasible Distance' (FD)?",
    "options": {
      "A": "Distance the neighbor reports",
      "B": "The best calculated metric to reach a destination",
      "C": "Physical cable length",
      "D": "Latency to the next hop"
    },
    "answer": "B"
  },
  {
    "question": "What is 'NHRP' (Next Hop Resolution Protocol) used in?",
    "options": {
      "A": "OSPF",
      "B": "DMVPN",
      "C": "RIP",
      "D": "STP"
    },
    "answer": "B"
  },
  {
    "question": "What is 'BGP Weight'?",
    "options": {
      "A": "A transitive attribute",
      "B": "A Cisco-proprietary local attribute used for path selection",
      "C": "The physical mass of the hardware",
      "D": "The number of users on a link"
    },
    "answer": "B"
  },
  {
    "question": "What is 'MP-BGP'?",
    "options": {
      "A": "Multi-Path BGP",
      "B": "Multi-Protocol BGP",
      "C": "Mobile BGP",
      "D": "Management BGP"
    },
    "answer": "B"
  },
  {
    "question": "What does 'VRF' stand for?",
    "options": {
      "A": "Virtual Route Finder",
      "B": "Virtual Routing and Forwarding",
      "C": "Variable Route File",
      "D": "Virtual Router Framework"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Route Summarization'?",
    "options": {
      "A": "Writing a summary of the network",
      "B": "Aggregating multiple subnets into a single larger advertisement",
      "C": "Reducing the speed of a link",
      "D": "Naming the routers"
    },
    "answer": "B"
  },
  {
    "question": "Which protocol uses 'Cost' based on bandwidth as its metric?",
    "options": {
      "A": "RIP",
      "B": "OSPF",
      "C": "BGP",
      "D": "EGP"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Split Horizon'?",
    "options": {
      "A": "A method to increase speed",
      "B": "A loop prevention mechanism for distance-vector protocols",
      "C": "A way to hide IP addresses",
      "D": "A physical divider in a rack"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Router ID' in OSPF?",
    "options": {
      "A": "The router's name",
      "B": "A 32-bit unique identifier for the router",
      "C": "The serial number",
      "D": "The admin password"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Administrative Distance' of a Static route?",
    "options": {
      "A": "0",
      "B": "1",
      "C": "110",
      "D": "90"
    },
    "answer": "B"
  },
  {
    "question": "What is 'TTL' (Time to Live) used for in an IP packet?",
    "options": {
      "A": "To measure internet speed",
      "B": "To prevent infinite loops by discarding the packet after it crosses a set number of routers",
      "C": "To show the time of day",
      "D": "To encrypt data"
    },
    "answer": "B"
  },
  {
    "question": "What is 'HSRP' used for?",
    "options": {
      "A": "Routing protocol",
      "B": "First-hop redundancy for gateways",
      "C": "Web hosting",
      "D": "Email encryption"
    },
    "answer": "B"
  },
  {
    "question": "What is 'BGP Local Preference'?",
    "options": {
      "A": "A non-transitive attribute",
      "B": "A well-known discretionary attribute used to choose an exit path from the local AS",
      "C": "The router's favorite protocol",
      "D": "The priority of the local LAN"
    },
    "answer": "B"
  },
  {
    "question": "In OSPF, what is 'Area 0'?",
    "options": {
      "A": "The stub area",
      "B": "The backbone area",
      "C": "The external area",
      "D": "The default area"
    },
    "answer": "B"
  },
  {
    "question": "What is 'NAT'?",
    "options": {
      "A": "Network Address Translation",
      "B": "Node Access Tool",
      "C": "Network Allocation Table",
      "D": "Native Access Technology"
    },
    "answer": "A"
  },
  {
    "question": "What is the default AD of eBGP?",
    "options": {
      "A": "20",
      "B": "200",
      "C": "110",
      "D": "90"
    },
    "answer": "A"
  },
  {
    "question": "What is 'PBR'?",
    "options": {
      "A": "Private Binary Routing",
      "B": "Policy-Based Routing",
      "C": "Port-Based Routing",
      "D": "Priority-Based Routing"
    },
    "answer": "B"
  },
  {
    "question": "What does 'SLA' stand for in networking?",
    "options": {
      "A": "Secure Link Access",
      "B": "Service Level Agreement",
      "C": "Static Link Allocation",
      "D": "System Level Audit"
    },
    "answer": "B"
  },
  {
    "question": "What is 'BFD'?",
    "options": {
      "A": "Binary Flow Data",
      "B": "Bidirectional Forwarding Detection",
      "C": "Backend Firewall Defense",
      "D": "Basic Forwarding Device"
    },
    "answer": "B"
  },
  {
    "question": "What is 'OSPF Cost'?",
    "options": {
      "A": "The price of the router",
      "B": "A metric calculated as Reference Bandwidth / Interface Bandwidth",
      "C": "The time spent on the configuration",
      "D": "The electricity bill"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Poison Reverse'?",
    "options": {
      "A": "A virus in the network",
      "B": "Sending back a route with infinity metric to prevent loops",
      "C": "Hacking a router",
      "D": "Shutting down an interface"
    },
    "answer": "B"
  },
  {
    "question": "What is 'BGP Keepalive' time by default?",
    "options": {
      "A": "10 seconds",
      "B": "60 seconds",
      "C": "180 seconds",
      "D": "30 seconds"
    },
    "answer": "B"
  },
  {
    "question": "What is a 'Default Gateway'?",
    "options": {
      "A": "The router's main entrance",
      "B": "The device that forwards traffic from the local network to external networks",
      "C": "The first computer in the lab",
      "D": "The password for the network"
    },
    "answer": "B"
  },
  {
    "question": "What is 'RIP'?",
    "options": {
      "A": "Router Interface Protocol",
      "B": "Routing Information Protocol",
      "C": "Rapid IP Protocol",
      "D": "Rest In Peace"
    },
    "answer": "B"
  },
  {
    "question": "What is 'EIGRP'?",
    "options": {
      "A": "Enhanced Internal Gateway Routing Protocol",
      "B": "Enhanced Interior Gateway Routing Protocol",
      "C": "Extended IP Gateway Routing Protocol",
      "D": "Efficient Interior Gateway Routing Protocol"
    },
    "answer": "B"
  },
  {
    "question": "What is 'VTP'?",
    "options": {
      "A": "Virtual Trunking Protocol",
      "B": "VLAN Trunking Protocol",
      "C": "Variable Trunking Protocol",
      "D": "Visual Trunking Protocol"
    },
    "answer": "B"
  },
  {
    "question": "What is 'STP'?",
    "options": {
      "A": "Secure Trunking Protocol",
      "B": "Spanning Tree Protocol",
      "C": "Serial Tunneling Protocol",
      "D": "Static Trunking Protocol"
    },
    "answer": "B"
  },
  {
    "question": "What is 'LSA' in OSPF?",
    "options": {
      "A": "Link Speed Area",
      "B": "Link State Advertisement",
      "C": "Local Service Address",
      "D": "Logical Subnet Allocation"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Convergence' in networking?",
    "options": {
      "A": "Two cables meeting",
      "B": "The state where all routers have consistent and updated routing information",
      "C": "Hacking a password",
      "D": "The end of a shift"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Jitter'?",
    "options": {
      "A": "Internet speed",
      "B": "Variation in packet delay",
      "C": "A broken screen",
      "D": "A fast router"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Latency'?",
    "options": {
      "A": "Bandwidth",
      "B": "The time delay for a packet to travel from source to destination",
      "C": "The size of a file",
      "D": "The color of the cable"
    },
    "answer": "B"
  },
  {
    "question": "What is 'DHCP'?",
    "options": {
      "A": "Dynamic Host Configuration Protocol",
      "B": "Device Host Connection Protocol",
      "C": "Domain Host Control Protocol",
      "D": "Digital Host Configuration Protocol"
    },
    "answer": "A"
  },
  {
    "question": "What is 'Non-Stop Forwarding' (NSF) used for in a routing environment?",
    "options": {
      "A": "To keep the router fans running at all times",
      "B": "To allow a router to continue forwarding packets even if the control plane (routing process) is restarting",
      "C": "To prevent users from logging out",
      "D": "To increase the speed of the physical interface"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Stateful Switchover' (SSO)?",
    "options": {
      "A": "A method to change the router's theme",
      "B": "A redundancy feature that synchronizes state information between active and standby Route Processors to allow for zero-packet-loss failover",
      "C": "A way to switch between IPv4 and IPv6",
      "D": "A tool for naming the interfaces"
    },
    "answer": "B"
  },
  {
    "question": "In BGP, what does the 'MED' attribute stand for?",
    "options": {
      "A": "Maximum Edge Distance",
      "B": "Multi-Exit Discriminator",
      "C": "Minimum Entry Delay",
      "D": "Managed Exit Data"
    },
    "answer": "B"
  },
  {
    "question": "Which BGP attribute is a well-known mandatory attribute that lists all the Autonomous Systems a route has passed through?",
    "options": {
      "A": "Local Preference",
      "B": "AS_PATH",
      "C": "Community",
      "D": "Origin"
    },
    "answer": "B"
  },
  {
    "question": "What is 'LISP RLOC' (Routing Locator)?",
    "options": {
      "A": "The user's home address",
      "B": "The IP address of the router that acts as the attachment point for an EID (Endpoint Identifier)",
      "C": "The serial number of the switch",
      "D": "The password for the network console"
    },
    "answer": "B"
  },
  {
    "question": "In OSPF, what is an 'Area Border Router' (ABR)?",
    "options": {
      "A": "A router that only works in one area",
      "B": "A router that sits on the boundary between one or more OSPF areas and connects them to the backbone",
      "C": "A router used only for wireless traffic",
      "D": "The primary backup router for the whole network"
    },
    "answer": "B"
  },
  {
    "question": "What is 'BGP Peer Grouping'?",
    "options": {
      "A": "A social network for engineers",
      "B": "A configuration method that allows multiple BGP neighbors to share the same policy settings to reduce CPU load and configuration errors",
      "C": "A way to group routers by their physical weight",
      "D": "A method to encrypt the BGP update"
    },
    "answer": "B"
  },
  {
    "question": "What is 'VRF-aware' routing?",
    "options": {
      "A": "A router that knows its own name",
      "B": "The ability of a routing protocol or service to operate within the context of a specific Virtual Routing and Forwarding instance",
      "C": "A router that uses less power",
      "D": "A way to compress the routing table"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Route Map' primarily used for in Cisco IOS?",
    "options": {
      "A": "To see a visual map of the network",
      "B": "To define complex policies for route filtering, redistribution, and modification of path attributes",
      "C": "To find the shortest cable path",
      "D": "To log the CLI history"
    },
    "answer": "B"
  },
  {
    "question": "What is 'BID' (Bridge ID) in Spanning Tree Protocol composed of?",
    "options": {
      "A": "Router name and IP",
      "B": "Bridge Priority and MAC Address",
      "C": "Speed and Duplex settings",
      "D": "VLAN name and ID"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Policy-Based Routing' (PBR)?",
    "options": {
      "A": "Routing based on political laws",
      "B": "A mechanism to override the standard routing table by matching traffic against a route-map",
      "C": "A way to delete old routes",
      "D": "Routing only for public institutions"
    },
    "answer": "B"
  },
  {
    "question": "What does 'RIB' stand for in a router?",
    "options": {
      "A": "Router Information Bit",
      "B": "Routing Information Base",
      "C": "Remote Interface Backup",
      "D": "Real-time Internet Bundle"
    },
    "answer": "B"
  },
  {
    "question": "What is 'FIB' (Forwarding Information Base)?",
    "options": {
      "A": "A list of forbidden IPs",
      "B": "A data structure derived from the RIB that the router hardware uses for high-speed packet forwarding",
      "C": "A backup of the routing table",
      "D": "A tool to find the fastest DNS"
    },
    "answer": "B"
  },
  {
    "question": "What is 'MPLS Label Swapping'?",
    "options": {
      "A": "Trading routers with another company",
      "B": "The process of replacing an incoming label with an outgoing label in the MPLS data plane",
      "C": "A way to hide IP addresses",
      "D": "A feature that renames the network"
    },
    "answer": "B"
  },
  {
    "question": "What is the function of the 'Route Distinguisher' (RD)?",
    "options": {
      "A": "To set the route's priority",
      "B": "To uniquely identify a prefix within a VRF, allowing for overlapping IP addresses in different customer networks",
      "C": "To encrypt the routing updates",
      "D": "To count the number of hops"
    },
    "answer": "B"
  },
  {
    "question": "What is 'BGP Community'?",
    "options": {
      "A": "A group of BGP routers in a city",
      "B": "A transitive, optional attribute used to tag routes for the application of administrative policies",
      "C": "A website for BGP users",
      "D": "A way to share internet passwords"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Loopback Interface' commonly used for in OSPF?",
    "options": {
      "A": "To loop data back to the sender",
      "B": "To provide a stable Router ID and management point that doesn't go down if a physical port fails",
      "C": "To test the cable quality",
      "D": "To increase the number of physical ports"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Prefix-List' used for?",
    "options": {
      "A": "To list the names of all routers",
      "B": "A tool for filtering routes based on prefix length and address ranges",
      "C": "To speed up the router's CPU",
      "D": "To encrypt the packet header"
    },
    "answer": "B"
  },
  {
    "question": "What is 'OSPF LSA Type 3'?",
    "options": {
      "A": "Router LSA",
      "B": "Summary LSA",
      "C": "External LSA",
      "D": "Network LSA"
    },
    "answer": "B"
  },
  {
    "question": "What is 'BGP AS-PATH Prepending'?",
    "options": {
      "A": "Deleting the AS number",
      "B": "Artificially lengthening the AS_PATH to influence inbound traffic selection",
      "C": "A way to speed up updates",
      "D": "A security feature to hide the path"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Redistribution' in EIGRP?",
    "options": {
      "A": "Reinstalling the EIGRP software",
      "B": "Taking routes from another protocol and injecting them into the EIGRP topology table",
      "C": "Changing the router's IP",
      "D": "Sharing the electricity between routers"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Route Filtering'?",
    "options": {
      "A": "Cleaning the router's vents",
      "B": "Controlling which routes are accepted or advertised by a routing protocol using ACLs or Prefix-lists",
      "C": "Limiting the number of users on a route",
      "D": "A way to choose only the cheapest routes"
    },
    "answer": "B"
  },
  {
    "question": "What is 'BGP Scan Time'?",
    "options": {
      "A": "How long it takes to scan for viruses",
      "B": "The interval at which BGP checks the next-hop reachability and applies policy changes",
      "C": "The speed of the router's mouse",
      "D": "The time to boot the OS"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Stub Area' in OSPF?",
    "options": {
      "A": "A small area with only one router",
      "B": "An area that doesn't accept external route advertisements, reducing its routing table size",
      "C": "An area with no backbone connection",
      "D": "A testing area for new protocols"
    },
    "answer": "B"
  },
  {
    "question": "What is 'EIGRP Successor'?",
    "options": {
      "A": "The next router to be manufactured",
      "B": "The best loop-free path to a destination as chosen by the DUAL algorithm",
      "C": "The backup router for the network",
      "D": "The oldest router in the domain"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Administrative Distance' of Internal EIGRP?",
    "options": {
      "A": "170",
      "B": "90",
      "C": "110",
      "D": "120"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Administrative Distance' of OSPF?",
    "options": {
      "A": "90",
      "B": "110",
      "C": "120",
      "D": "1"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Metric' in OSPF?",
    "options": {
      "A": "The length of the cable",
      "B": "Cost (10^8 / Bandwidth)",
      "C": "The number of users",
      "D": "The time of day"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Metric' in RIP?",
    "options": {
      "A": "Bandwidth",
      "B": "Hop Count",
      "C": "Delay",
      "D": "Load"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Metric' in EIGRP?",
    "options": {
      "A": "Hop count only",
      "B": "Composite metric based on Bandwidth and Delay (by default)",
      "C": "The price of the interface",
      "D": "Random number"
    },
    "answer": "B"
  },
  {
    "question": "What is 'BGP Path Selection' tie-breaker?",
    "options": {
      "A": "The color of the router",
      "B": "Router ID (lower usually wins in final stages)",
      "C": "The length of the device name",
      "D": "The number of active ports"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Route Summarization' in OSPF done on?",
    "options": {
      "A": "Any router",
      "B": "ABRs and ASBRs",
      "C": "Only the DR",
      "D": "Only internal routers"
    },
    "answer": "B"
  },
  {
    "question": "What is 'iBGP' (Internal BGP)?",
    "options": {
      "A": "BGP between different companies",
      "B": "BGP sessions between routers within the same Autonomous System",
      "C": "A faster version of BGP",
      "D": "BGP for wireless devices"
    },
    "answer": "B"
  },
  {
    "question": "What is 'eBGP' (External BGP)?",
    "options": {
      "A": "BGP within one office",
      "B": "BGP sessions between routers in different Autonomous Systems",
      "C": "BGP used for gaming",
      "D": "A way to connect to a printer"
    },
    "answer": "B"
  },
  {
    "question": "What is the 'Default Route' notation?",
    "options": {
      "A": "255.255.255.255",
      "B": "0.0.0.0/0",
      "C": "127.0.0.1",
      "D": "1.1.1.1"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Static Route'?",
    "options": {
      "A": "A route that moves around",
      "B": "A manually configured route by the administrator",
      "C": "A route that only works in winter",
      "D": "A route that automatically changes"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Dynamic Routing'?",
    "options": {
      "A": "A route you type in manually",
      "B": "Routes learned automatically through protocols like OSPF or BGP",
      "C": "A route that never changes",
      "D": "A route for physical mail"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Longest Prefix Match'?",
    "options": {
      "A": "The longest cable in the network",
      "B": "The algorithm where the router chooses the most specific matching route in the table",
      "C": "A way to rename subnets",
      "D": "The longest name of a router"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Administrative Distance'?",
    "options": {
      "A": "The miles between routers",
      "B": "The trustworthiness of a routing protocol",
      "C": "The time it takes for a tech to drive to a site",
      "D": "The length of the router's serial number"
    },
    "answer": "B"
  },
  {
    "question": "What is 'AS Number' (Autonomous System)?",
    "options": {
      "A": "The router's ID number",
      "B": "A unique identifier for a network under a single administrative control",
      "C": "The serial number of the modem",
      "D": "A number for the office floor"
    },
    "answer": "B"
  },
  {
    "question": "What is 'BGP Best Path Algorithm'?",
    "options": {
      "A": "A random choice",
      "B": "A step-by-step process BGP uses to select the best route for its table",
      "C": "A way to find the cheapest router",
      "D": "A tool to design network maps"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Floating Static Route'?",
    "options": {
      "A": "A route used for ships",
      "B": "A static route with a high AD used as a backup for a dynamic route",
      "C": "A route that changes its IP",
      "D": "A route that works without a cable"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Next Hop'?",
    "options": {
      "A": "The next game on the router",
      "B": "The IP address of the next router in the path to the destination",
      "C": "The next port on the switch",
      "D": "The next version of the software"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Subnetting'?",
    "options": {
      "A": "Cleaning the network hardware",
      "B": "The process of dividing a large network into smaller sub-networks",
      "C": "Connecting two computers together",
      "D": "Naming the servers"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Wildcard Mask'?",
    "options": {
      "A": "A costume for a router",
      "B": "The inverse of a subnet mask used in OSPF and ACLs",
      "C": "A random number for security",
      "D": "A method to hide the IP"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Default Gateway'?",
    "options": {
      "A": "The main door of the office",
      "B": "The router interface that hosts on a local subnet use to send traffic outside their network",
      "C": "The first server in the rack",
      "D": "The password for the WiFi"
    },
    "answer": "B"
  },
  {
    "question": "What is 'BGP Keepalive' interval?",
    "options": {
      "A": "1 second",
      "B": "60 seconds (by default)",
      "C": "10 minutes",
      "D": "1 hour"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Convergence Time'?",
    "options": {
      "A": "The time spent on the configuration",
      "B": "The time it takes for all routers to agree on a consistent routing table after a change",
      "C": "The length of the work day",
      "D": "The speed of the ISP"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Autonomous System'?",
    "options": {
      "A": "A router that works by itself",
      "B": "A collection of networks under a common administrative domain",
      "C": "A robot that fixes cables",
      "D": "A software for network design"
    },
    "answer": "B"
  },
  {
    "question": "What is 'Metric'?",
    "options": {
      "A": "The weight of the router",
      "B": "A value used by routing protocols to determine the cost of a path",
      "C": "The length of the cable",
      "D": "The time to boot the device"
    },
    "answer": "B"
  },
  {
    "question": "What is the primary function of a 'Transit Gateway' in a cloud-based routing architecture?",
    "options": {
      "A": "To provide physical power to the cloud servers",
      "B": "To act as a central hub that connects multiple VPCs and on-premises networks, simplifying complex peering relationships",
      "C": "To encrypt files stored on the local hard drive",
      "D": "To replace the need for an ISP"
    },
    "answer": "B"
  },
  {
    "question": "In the context of IPv6, what is 'NAT64'?",
    "options": {
      "A": "A method to increase IPv4 speeds by 64 times",
      "B": "A transition mechanism that allows IPv6-only clients to communicate with IPv4-only servers by translating headers",
      "C": "A way to hide a MAC address from the internet",
      "D": "A tool for naming 64 different routers at once"
    },
    "answer": "B"
  }
]

    
      

def remove_duplicates(questions):
    seen = set()
    unique = []

    for q in questions:
        if q["question"] not in seen:
            seen.add(q["question"])
            unique.append(q)

    return unique


def generate_pdf(skill_name, questions):
    doc = SimpleDocTemplate(
        f"{skill_name}_Question_Bank.pdf",
        pagesize=A4
    )

    elements = []
    styles = getSampleStyleSheet()

    title_style = styles["Heading1"]
    normal_style = styles["Normal"]

    elements.append(Paragraph(f"{skill_name} Question Bank ({len(questions)} Questions)", title_style))
    elements.append(Spacer(1, 0.3 * inch))

    for i, q in enumerate(questions, 1):
        elements.append(Paragraph(f"{i}. {q['question']}", normal_style))
        elements.append(Spacer(1, 0.1 * inch))

        for key, value in q["options"].items():
            elements.append(Paragraph(f"{key}) {value}", normal_style))
            elements.append(Spacer(1, 0.05 * inch))

        elements.append(Paragraph(f"<b>Answer:</b> {q['answer']}", normal_style))
        elements.append(Spacer(1, 0.3 * inch))

    doc.build(elements)
    print(f"✅ PDF Generated with {len(questions)} UNIQUE questions only.")


if __name__ == "__main__":
    skill = "Routing"
    unique_questions = remove_duplicates(QUESTIONS)
    generate_pdf(skill, unique_questions)
