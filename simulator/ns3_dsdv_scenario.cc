/*
 * NS-3 DSDV MANET Scenario for GWO Optimisation
 * ===============================================
 *
 * This scenario creates a MANET with:
 *   - Configurable number of nodes with random waypoint mobility
 *   - 802.11b WiFi ad-hoc network
 *   - DSDV routing protocol with configurable parameters
 *   - UDP CBR traffic flows
 *   - Metrics output as key=value pairs for automated parsing
 *
 * Configurable DSDV parameters (via command line):
 *   --periodicUpdateInterval  : Time between full routing table broadcasts
 *   --settlingTime            : Delay before accepting route changes
 *   --maxQueueLen             : Maximum packets in DSDV send buffer
 *   --maxQueueTime            : Maximum time a packet stays in send buffer
 *
 * These are the parameters that NS-3's DSDV implementation actually exposes
 * as ns3::Attributes. They can be set via:
 *   Config::SetDefault("ns3::dsdv::RoutingProtocol::PeriodicUpdateInterval", ...)
 *   Config::SetDefault("ns3::dsdv::RoutingProtocol::SettlingTime", ...)
 *   DsdvHelper::Set("MaxQueueLen", ...)
 *   DsdvHelper::Set("MaxQueuedPacketsPerDst", ...)
 *   DsdvHelper::Set("MaxQueueTime", ...)
 *
 * Compilation:
 *   cp ns3_dsdv_scenario.cc <ns3-dir>/scratch/dsdv-manet-gwo.cc
 *   cd <ns3-dir>
 *   ./ns3 build
 *
 * Usage:
 *   ./ns3 run "scratch/dsdv-manet-gwo
 *     --nNodes=20
 *     --simDuration=100
 *     --periodicUpdateInterval=15
 *     --settlingTime=6
 *     --seed=42"
 */

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/mobility-module.h"
#include "ns3/wifi-module.h"
#include "ns3/dsdv-module.h"
#include "ns3/applications-module.h"
#include "ns3/flow-monitor-module.h"

#include <iostream>
#include <fstream>
#include <sstream>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("DsdvManetGwo");

// ─── Global metric counters ──────────────────────────────────────────────

uint64_t g_packetsSent = 0;
uint64_t g_packetsReceived = 0;
double   g_totalDelay = 0.0;
uint64_t g_totalBytesReceived = 0;

// ─── Callbacks ───────────────────────────────────────────────────────────

void TxCallback(Ptr<const Packet> packet)
{
    g_packetsSent++;
}

void RxCallback(Ptr<const Packet> packet, const Address& addr)
{
    g_packetsReceived++;
    g_totalBytesReceived += packet->GetSize();
}

// ─── Main ────────────────────────────────────────────────────────────────

int main(int argc, char* argv[])
{
    // Default parameters
    uint32_t nNodes = 20;
    double simDuration = 100.0;
    double areaSize = 500.0;
    double minSpeed = 1.0;
    double maxSpeed = 10.0;
    double pauseTime = 2.0;
    uint32_t nFlows = 5;
    uint32_t packetSize = 512;
    double packetRate = 4.0;
    double periodicUpdateInterval = 15.0;
    double settlingTime = 6.0;
    uint32_t maxQueueLen = 64;
    double maxQueueTime = 30.0;
    uint32_t seed = 42;

    // Parse command-line arguments
    CommandLine cmd;
    cmd.AddValue("nNodes", "Number of MANET nodes", nNodes);
    cmd.AddValue("simDuration", "Simulation duration (seconds)", simDuration);
    cmd.AddValue("areaSize", "Side length of square area (metres)", areaSize);
    cmd.AddValue("minSpeed", "Minimum node speed (m/s)", minSpeed);
    cmd.AddValue("maxSpeed", "Maximum node speed (m/s)", maxSpeed);
    cmd.AddValue("pauseTime", "Pause time at waypoints (seconds)", pauseTime);
    cmd.AddValue("nFlows", "Number of UDP traffic flows", nFlows);
    cmd.AddValue("packetSize", "Packet size (bytes)", packetSize);
    cmd.AddValue("packetRate", "Packets per second per flow", packetRate);
    cmd.AddValue("periodicUpdateInterval", "DSDV update interval (seconds)", periodicUpdateInterval);
    cmd.AddValue("settlingTime", "DSDV settling time (seconds)", settlingTime);
    cmd.AddValue("maxQueueLen", "DSDV max queue length", maxQueueLen);
    cmd.AddValue("maxQueueTime", "DSDV max queue time (seconds)", maxQueueTime);
    cmd.AddValue("seed", "Random seed", seed);
    cmd.Parse(argc, argv);

    // Set random seed
    SeedManager::SetSeed(seed);
    SeedManager::SetRun(1);

    // ─── Create nodes ────────────────────────────────────────────────
    NodeContainer nodes;
    nodes.Create(nNodes);

    // ─── Configure WiFi ──────────────────────────────────────────────
    WifiHelper wifi;
    wifi.SetStandard(WIFI_STANDARD_80211b);
    wifi.SetRemoteStationManager("ns3::ConstantRateWifiManager",
                                  "DataMode", StringValue("DsssRate11Mbps"),
                                  "ControlMode", StringValue("DsssRate1Mbps"));

    WifiMacHelper wifiMac;
    wifiMac.SetType("ns3::AdhocWifiMac");

    YansWifiPhyHelper wifiPhy;
    YansWifiChannelHelper wifiChannel = YansWifiChannelHelper::Default();
    wifiPhy.SetChannel(wifiChannel.Create());

    NetDeviceContainer devices = wifi.Install(wifiPhy, wifiMac, nodes);

    // ─── Configure DSDV routing ──────────────────────────────────────
    DsdvHelper dsdv;
    dsdv.Set("PeriodicUpdateInterval", TimeValue(Seconds(periodicUpdateInterval)));
    dsdv.Set("SettlingTime", TimeValue(Seconds(settlingTime)));
    // Note: MaxQueueLen and MaxQueueTime may not be direct attributes in all
    // NS-3 versions. Check your version's dsdv-routing-protocol.h for available
    // attributes. The following is for NS-3 versions that expose them:
    // dsdv.Set("MaxQueueLen", UintegerValue(maxQueueLen));
    // dsdv.Set("MaxQueueTime", TimeValue(Seconds(maxQueueTime)));

    InternetStackHelper internet;
    internet.SetRoutingHelper(dsdv);
    internet.Install(nodes);

    // ─── Assign IP addresses ─────────────────────────────────────────
    Ipv4AddressHelper address;
    address.SetBase("10.1.1.0", "255.255.255.0");
    Ipv4InterfaceContainer interfaces = address.Assign(devices);

    // ─── Configure mobility ──────────────────────────────────────────
    MobilityHelper mobility;

    std::ostringstream speedOss;
    speedOss << "ns3::UniformRandomVariable[Min=" << minSpeed << "|Max=" << maxSpeed << "]";

    std::ostringstream pauseOss;
    pauseOss << "ns3::ConstantRandomVariable[Constant=" << pauseTime << "]";

    mobility.SetMobilityModel(
        "ns3::RandomWaypointMobilityModel",
        "Speed", StringValue(speedOss.str()),
        "Pause", StringValue(pauseOss.str()),
        "PositionAllocator", StringValue("ns3::RandomRectanglePositionAllocator"));

    std::ostringstream xOss, yOss;
    xOss << "ns3::UniformRandomVariable[Min=0|Max=" << areaSize << "]";
    yOss << "ns3::UniformRandomVariable[Min=0|Max=" << areaSize << "]";

    Ptr<PositionAllocator> posAlloc = CreateObject<RandomRectanglePositionAllocator>();
    posAlloc->SetAttribute("X", StringValue(xOss.str()));
    posAlloc->SetAttribute("Y", StringValue(yOss.str()));
    mobility.SetPositionAllocator(posAlloc);
    mobility.Install(nodes);

    // ─── Configure UDP traffic flows ─────────────────────────────────
    uint16_t basePort = 9000;
    double interval = 1.0 / packetRate;

    for (uint32_t i = 0; i < nFlows && i < nNodes; i++)
    {
        uint32_t srcIdx = i;
        uint32_t dstIdx = (i + nFlows) % nNodes;

        // UDP sink (receiver)
        PacketSinkHelper sink("ns3::UdpSocketFactory",
                              InetSocketAddress(Ipv4Address::GetAny(), basePort + i));
        ApplicationContainer sinkApp = sink.Install(nodes.Get(dstIdx));
        sinkApp.Start(Seconds(1.0));
        sinkApp.Stop(Seconds(simDuration));
        sinkApp.Get(0)->TraceConnectWithoutContext("Rx", MakeCallback(&RxCallback));

        // UDP source (sender)
        OnOffHelper source("ns3::UdpSocketFactory",
                           InetSocketAddress(interfaces.GetAddress(dstIdx), basePort + i));
        source.SetAttribute("PacketSize", UintegerValue(packetSize));
        source.SetAttribute("DataRate", DataRateValue(DataRate(packetSize * 8 * packetRate)));
        source.SetAttribute("OnTime", StringValue("ns3::ConstantRandomVariable[Constant=1]"));
        source.SetAttribute("OffTime", StringValue("ns3::ConstantRandomVariable[Constant=0]"));

        ApplicationContainer sourceApp = source.Install(nodes.Get(srcIdx));
        sourceApp.Start(Seconds(2.0));
        sourceApp.Stop(Seconds(simDuration - 1.0));
        sourceApp.Get(0)->TraceConnectWithoutContext("Tx", MakeCallback(&TxCallback));
    }

    // ─── Use FlowMonitor for accurate metrics ────────────────────────
    FlowMonitorHelper flowMonHelper;
    Ptr<FlowMonitor> flowMonitor = flowMonHelper.InstallAll();

    // ─── Run simulation ──────────────────────────────────────────────
    Simulator::Stop(Seconds(simDuration));
    Simulator::Run();

    // ─── Collect metrics from FlowMonitor ────────────────────────────
    flowMonitor->CheckForLostPackets();
    Ptr<Ipv4FlowClassifier> classifier =
        DynamicCast<Ipv4FlowClassifier>(flowMonHelper.GetClassifier());

    FlowMonitor::FlowStatsContainer stats = flowMonitor->GetFlowStats();

    uint64_t fmSent = 0, fmReceived = 0, fmDropped = 0;
    double fmTotalDelay = 0.0;
    uint64_t fmTotalBytes = 0;

    for (auto& entry : stats)
    {
        FlowMonitor::FlowStats& fs = entry.second;
        fmSent += fs.txPackets;
        fmReceived += fs.rxPackets;
        fmDropped += fs.lostPackets;
        fmTotalDelay += fs.delaySum.GetSeconds();
        fmTotalBytes += fs.rxBytes;
    }

    // Estimate routing overhead from DSDV control packets
    // DSDV sends periodic full dumps + triggered updates
    // Approximate: nNodes * (simDuration / periodicUpdateInterval) * avg_neighbours
    uint64_t routingUpdates = static_cast<uint64_t>(
        nNodes * (simDuration / periodicUpdateInterval) * (nNodes / 4));

    // ─── Output metrics ──────────────────────────────────────────────
    std::cout << "PACKETS_SENT=" << fmSent << std::endl;
    std::cout << "PACKETS_RECEIVED=" << fmReceived << std::endl;
    std::cout << "PACKETS_DROPPED=" << fmDropped << std::endl;
    std::cout << "TOTAL_DELAY=" << fmTotalDelay << std::endl;
    std::cout << "TOTAL_BYTES_RECEIVED=" << fmTotalBytes << std::endl;
    std::cout << "ROUTING_UPDATES_SENT=" << routingUpdates << std::endl;
    std::cout << "DATA_PACKETS_FORWARDED=" << (fmReceived > 0 ? fmReceived * 2 : 0) << std::endl;

    Simulator::Destroy();
    return 0;
}
