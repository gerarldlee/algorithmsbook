---
title: "Cloud Networking: Virtual Private Clouds (VPC), Subnets, NAT Gateways, Peering, Transit Gateways, and Mesh Networks"
weight: 3
toc: true
---

## What it is
Cloud networking is the set of managed primitives that give you isolated, programmable network topology in the cloud: a virtual private cloud (VPC) with subnets, routing, security groups, NAT, peering, load balancers, and DNS. It lets you carve a private address space and control exactly how traffic enters, leaves, and flows between resources.

## How it works
A **VPC** is a logically isolated network inside a region with a CIDR block you choose (e.g. `10.0.0.0/16`). You split it into **subnets**, each bound to one availability zone. A public subnet has a route to an internet gateway; a private subnet normally reaches the internet through a **NAT gateway**. A VPC endpoint provides private access to supported AWS service endpoints, while a VPN provides private connectivity to an external network. **Route tables** decide the next hop for each destination. **Security groups** are stateful firewalls attached to elastic network interfaces, while **network ACLs** are stateless subnet-level allow/deny rules. **VPC peering** or **Transit Gateway** connect VPCs, and interface endpoints such as PrivateLink reach supported services without traversing the public internet.

```yaml
Resources:
  Vpc:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16

  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref Vpc
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: us-east-1a

  PrivateSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref Vpc
      CidrBlock: 10.0.2.0/24
      AvailabilityZone: us-east-1b

  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      VpcId: !Ref Vpc

  InternetGatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref Vpc
      InternetGatewayId: !Ref InternetGateway

  ElasticIp:
    Type: AWS::EC2::EIP
    Properties:
      Domain: vpc

  NatGateway:
    Type: AWS::EC2::NatGateway
    Properties:
      AllocationId: !Ref ElasticIp
      SubnetId: !Ref PublicSubnet
    DependsOn: InternetGatewayAttachment

  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref Vpc

  PublicDefaultRoute:
    Type: AWS::EC2::Route
    DependsOn: InternetGatewayAttachment
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  PublicRouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      RouteTableId: !Ref PublicRouteTable
      SubnetId: !Ref PublicSubnet

  PrivateRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref Vpc

  PrivateDefaultRoute:
    Type: AWS::EC2::Route
    Properties:
      RouteTableId: !Ref PrivateRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      NatGatewayId: !Ref NatGateway

  PrivateRouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      RouteTableId: !Ref PrivateRouteTable
      SubnetId: !Ref PrivateSubnet
```

Above the raw network sit **load balancers** and **DNS**. Application load balancers (ALB) route HTTP(S) at L7 by host/path to target groups; network load balancers (NLB) forward TCP/UDP at L4 with static IPs and very low latency; classic/Gateway LBs cover legacy and appliance traffic. Managed **DNS** (Route 53) resolves names with global anycast, health checks, and routing policies (latency, geo, weighted, failover) so clients land on a healthy endpoint in the nearest region.

## Tradeoffs
- **Isolation vs. complexity**: VPCs give strong network isolation and private IP space, but subnetting, routing, NAT, and peering are easy to misconfigure and hard to debug at scale.
- **Stateful vs. stateless**: security groups are simple and forgiving (stateful, allow-only) but can't express deny rules; NACLs allow deny but are stateless and require opening return traffic.
- **Latency vs. availability**: multi-AZ deployments with cross-zone load balancing improve availability but add inter-AZ latency and data-transfer cost.
- **NAT cost**: private subnets need NAT gateways for outbound internet, which add per-hour and per-GB data-processing charges that surprise many teams.
- **Reachability vs. security**: peering/transit gateways simplify cross-VPC connectivity but widen the blast radius; endpoints keep traffic on the private backbone at the cost of more components.

## When to use
- Designing a multi-tier architecture with public-facing web tiers and private database/backend tiers isolated from the internet.
- Enforcing east-west and north-south traffic control across many services with security groups, ACLs, and a hub-and-spoke transit network.
- Directing global traffic to the nearest healthy region with DNS routing policies and managed load balancers.

## Alternatives
- **Flat/default network (no VPC)**: simplest to start, but no isolation, private subnets, or fine-grained traffic control.
- **On-premises network / VPN extension**: keeps existing private networks and compliance controls, but adds hybrid latency, cost, and complexity.
- **Service mesh (Istio/Linkerd)**: L7 policy, mTLS, and observability between services, but a heavier operational footprint than plain security groups.

## Related
- [Compute](01-compute.md)
- [Storage Primitives](02-storage-primitives.md)
- [Infrastructure as Code](05-infrastructure-as-code.md)
- [Network Protocols & Transport Mechanics](../../02-system-design/01-system-design-fundamentals/02-network-protocols.md)
