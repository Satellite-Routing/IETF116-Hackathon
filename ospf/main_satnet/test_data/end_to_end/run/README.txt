sag_application_schedule_udp.csv
sag_application_id, from_node_id, to_node_id, target_rate_megabit_per_s, start_time_ns, duration_ns, additional_parameters, metadata

logs_ns3
######################################################################################
burst_burstId_outgoing.csv: burstId, sequence, packerSendTime
burst_burstId_incoming.csv: burstId, sequence, packerReceiveTime
######################################################################################
sag_bursts_incoming.txt/csv:
SAG Applicartion ID, From, To, Target rate(Mbps), Start time(ms), Duration(ms), Incoming rate (Mbps), 
Incoming rate ((payload)Mbps), Packets received, Data received (Mbit), Data received (payload(Mbit)), Metadata
sag_bursts_outgoing.txt/csv:
SAG Applicartion ID, From, To, Target rate(Mbps), Start time(ms), Duration(ms), Outgoing rate (Mbps), 
Outgoing rate ((payload)Mbps), Packets sent, Data sent (Mbit), Data sent (payload(Mbit)), Metadata



sag_application_schedule_tcp.csv
...
