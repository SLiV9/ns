/*  Networking and System Security Assignment: Lab4
 *  lab4-task1-template.cc
 *
 *  Created on: Sept 01, 2013
 *  	Author: Chariklis <c.pittaras@uva.nl>
 *
 *  ns-3 simulation source code template
 *  Copyright (C) 2013 Chariklis Pittaras
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.   
 */

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/internet-module.h"
#include "ns3/flow-monitor-module.h"
#include "ns3/ipv4-global-routing-helper.h"

using namespace ns3;
using namespace std;

//Definition of NS_LOG identifier
NS_LOG_COMPONENT_DEFINE ("lab4-task1-template");
//Definition of global variables
double clientStartTime = 1.0;
double stopTime = 50.0; 
volatile uint32_t mBytesReceived = 0;


/**
 * Callback function used for counting received bytes
 */
void ReceivePacket(std::string context, Ptr<const Packet> p) {
	mBytesReceived += p->GetSize();
}




int main(int argc, char *argv[]) {

	//DONE define your Simulation parameters
	
	Ptr<Node> clientNode, serverNode;
	Address serverSinkAddress;
	
	// Latency (in milliseconds).
	int latency = 64;
	
	// Maximum Receive Window (in bytes).
	int max_rwin = 16384;
	// Server start time.
	double serverStartTime = 0.5;
	DataRate clientSendRate = DataRate("2Mbps");


	//enable logging at level INFO
	LogComponentEnable ("lab4-task1-template", LOG_LEVEL_INFO);


	NS_LOG_INFO("Create nodes.");

	//DONE Create network topology using NodeContainer class
	NodeContainer nodes;
	nodes.Create(2);
	clientNode = nodes.Get(0);
	serverNode = nodes.Get(1);

	//DONE Install Internet Stack on nodes
	InternetStackHelper stack;
	stack.Install(nodes);

	//DONE Create pointToPoint channel with specified data rate and delay, without IP addresses first
	PointToPointHelper pointToPoint;
	pointToPoint.SetDeviceAttribute("DataRate", StringValue("3.2Mbps"));
	std::stringstream ss;
	ss << "" << latency << "ms";
	pointToPoint.SetChannelAttribute("Delay", StringValue(ss.str()));

	//DONE print the current latency
	cout << "Latency: " << ss.str() << endl;

	//DONE set the maximum receiving window size (RWIN)
	Config::SetDefault ("ns3::TcpSocketBase::MaxWindowSize", UintegerValue(max_rwin));

	//DONE print the maximum receiving window size (RWIN)
	cout << "Maximum receiving window: " << max_rwin << " bytes" << endl;

	//DONE Install netDevices to the nodes and assign IP addresses
	NetDeviceContainer devices;
	devices = pointToPoint.Install(nodes);
	
	Ipv4AddressHelper address;
	address.SetBase("10.1.1.0", "255.255.255.0");
	
	Ipv4InterfaceContainer interfaces = address.Assign(devices);

	//DONE print here the server and client addresses
	Ipv4Address clientIPAddress = interfaces.GetAddress(0);
	Ipv4Address serverIPAddress = interfaces.GetAddress(1);
	cout << "Client address : " << clientIPAddress << endl;
	cout << "Server address : " << serverIPAddress << endl;


	//Create TCP  applications installed on nodes.
	NS_LOG_INFO("Create TCP Applications.");
	
	//DONE Create a packet sink on the server to receive packets.
	uint16_t port = 50000;
	Address serverLocalAddress(InetSocketAddress(serverIPAddress, port));
	PacketSinkHelper packetSinkHelper("ns3::TcpSocketFactory", serverLocalAddress);
	ApplicationContainer serverApp = packetSinkHelper.Install(serverNode);
	serverApp.Start(Seconds(serverStartTime));
	serverApp.Stop(Seconds(stopTime));
	serverSinkAddress = serverLocalAddress;

	//DONE Create an OnOff client application to send TCP to the server. Set the sending rate to 2Mbps
	OnOffHelper onOffHelper("ns3::TcpSocketFactory", serverSinkAddress);
  onOffHelper.SetAttribute ("OnTime", StringValue ("ns3::ConstantRandomVariable[Constant=1]"));
  onOffHelper.SetAttribute ("OffTime", StringValue ("ns3::ConstantRandomVariable[Constant=0]"));
	onOffHelper.SetConstantRate(clientSendRate);
  AddressValue remoteAddress(InetSocketAddress(serverIPAddress, port));
  onOffHelper.SetAttribute("Remote", remoteAddress);
	ApplicationContainer clientApp = onOffHelper.Install(clientNode);
	clientApp.Start(Seconds(clientStartTime));
	clientApp.Stop(Seconds(stopTime));

	// Enable ascii tracing, you can find the tcp-task1.tr file in the ns-3.17 directory
	AsciiTraceHelper ascii;
	pointToPoint.EnableAsciiAll(ascii.CreateFileStream("tcp-task1.tr"));


	//Hook up the callback function with the receiving packet event of the node 0, device 1
	std::string ctx = "/NodeList/0/DeviceList/1/$ns3::PointToPointNetDevice/MacRx";
	Config::Connect(ctx, MakeCallback(&ReceivePacket));


	//Install FlowMonitor on all nodes
	FlowMonitorHelper flowmon;
	Ptr<FlowMonitor> monitor = flowmon.InstallAll();


	//Set simulation timeout and run.
	NS_LOG_INFO("Run Simulation.");
	Simulator::Stop(Seconds(stopTime));
	Simulator::Run();


	/* measure the throughput.
	 * For measuring the throughput we use the FlowMonitorHelper class. 
	 * see $NS3 HOME/examples/wireless/wifi-hidden-terminal.cc
	 */
	monitor->CheckForLostPackets();
	Ptr<Ipv4FlowClassifier> classifier = DynamicCast<Ipv4FlowClassifier>(flowmon.GetClassifier());
	std::map<FlowId, FlowMonitor::FlowStats> stats = monitor->GetFlowStats();
	for (std::map<FlowId, FlowMonitor::FlowStats>::const_iterator i = stats.begin(); i != stats.end(); ++i) {
		Ipv4FlowClassifier::FiveTuple t = classifier->FindFlow(i->first);
		if ((t.destinationAddress == serverIPAddress)) {
			std::cout << "Flow " << i->first << " (" << t.sourceAddress
					<< " -> " << t.destinationAddress << ")\n";
			std::cout << "Start running time: " << i->second.timeFirstTxPacket.GetSeconds() << endl;
			std::cout << "Stop running time:  " << i->second.timeLastRxPacket.GetSeconds() << endl;
			std::cout << "  Tx Bytes:   " << i->second.txBytes << "\n";
			std::cout << "  Rx Bytes:   " << i->second.rxBytes << "\n";
			std::cout << "  Throughput: " << i->second.rxBytes * 8.0
					/ (i->second.timeLastRxPacket.GetSeconds() - i->second.timeFirstTxPacket.GetSeconds())
					/ 1000 / 1000 << " Mbps\n";
		}
	}

	Simulator::Destroy();
	NS_LOG_INFO("Done.");
}
