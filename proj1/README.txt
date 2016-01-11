Allison Shedden & Julian Gee

The largest challenge we faced was updating after downlinks occurred.

If we had implemented Link State routers, each router would know the topology of the network which would make downlink avoidance easier.

Our implementation handles both link weights and incremental updates. Implementing link weights was very easy; while handling discovers packets all we had to do was set the routing table value to link latency as opposed to 1 on uplinks. Our routers only send updated routes to the other routers to implement incremental updates.

We would also like to use both our late days on this project.

Thanks very much! :]