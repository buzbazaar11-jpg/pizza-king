import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/contexts/AuthContext";
import RiderLayout from "@/components/rider/RiderLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import {
  Package,
  Phone,
  MapPin,
  User,
  CheckCircle,
  Navigation,
  Banknote,
  ClipboardList,
} from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";

interface OrderRow {
  id: string;
  total: number;
  status: string;
  payment_method: string | null;
  customer_name: string | null;
  customer_phone: string | null;
  customer_email: string | null;
  customer_address: string | null;
  created_at: string;
  delivered_at: string | null;
  rider_id: string | null;
  order_type: string | null;
}

interface OrderItemRow {
  id: string;
  title: string;
  quantity: number;
  price: number;
}

const RiderOrders = () => {
  const { user } = useAuth();
  const [myOrders, setMyOrders] = useState<OrderRow[]>([]);
  const [availableOrders, setAvailableOrders] = useState<OrderRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<"active" | "available" | "completed">("active");
  const [detailOrder, setDetailOrder] = useState<OrderRow | null>(null);
  const [orderItems, setOrderItems] = useState<OrderItemRow[]>([]);
  const [itemsLoading, setItemsLoading] = useState(false);
  const { toast } = useToast();

  const fetchOrders = async () => {
    if (!user) return;

    const [myRes, availRes] = await Promise.all([
      supabase
        .from("orders")
        .select("*")
        .eq("rider_id", user.id)
        .order("created_at", { ascending: false }),
      supabase
        .from("orders")
        .select("*")
        .is("rider_id", null)
        .eq("order_type", "delivery")
        .in("status", ["confirmed", "ready"])
        .order("created_at", { ascending: false }),
    ]);

    setMyOrders((myRes.data || []) as OrderRow[]);
    setAvailableOrders((availRes.data || []) as OrderRow[]);
    setLoading(false);
  };

  useEffect(() => {
    fetchOrders();
  }, [user]);

  // Realtime subscription
  useEffect(() => {
    const ch = supabase
      .channel("rider-orders")
      .on(
        "postgres_changes",
        { event: "*", schema: "public", table: "orders" },
        () => fetchOrders()
      )
      .subscribe();
    return () => { supabase.removeChannel(ch); };
  }, [user]);

  const viewDetails = async (order: OrderRow) => {
    setDetailOrder(order);
    setItemsLoading(true);
    const { data } = await supabase
      .from("order_items")
      .select("*")
      .eq("order_id", order.id);
    setOrderItems((data || []) as OrderItemRow[]);
    setItemsLoading(false);
  };

  const confirmPickup = async (orderId: string) => {
    const { error } = await supabase
      .from("orders")
      .update({ status: "out_for_delivery", assigned_at: new Date().toISOString() })
      .eq("id", orderId);
    if (error) {
      toast({ title: "Update failed", description: error.message, variant: "destructive" });
    } else {
      toast({ title: "Order picked up! 🏍️" });
      fetchOrders();
    }
  };

  const markDelivered = async (orderId: string) => {
    const { error } = await supabase
      .from("orders")
      .update({ status: "delivered", delivered_at: new Date().toISOString() })
      .eq("id", orderId);
    if (error) {
      toast({ title: "Update failed", description: error.message, variant: "destructive" });
    } else {
      toast({ title: "Order marked as delivered! ✅" });
      fetchOrders();
      if (detailOrder?.id === orderId) setDetailOrder(null);
    }
  };

  const acceptOrder = async (orderId: string) => {
    if (!user) return;
    const { error } = await supabase
      .from("orders")
      .update({ rider_id: user.id })
      .eq("id", orderId);
    if (error) {
      toast({ title: "Could not accept order", description: error.message, variant: "destructive" });
    } else {
      toast({ title: "Order accepted! 🎉" });
      fetchOrders();
    }
  };

  // Daily stats — delivered today
  const todayStart = new Date();
  todayStart.setHours(0, 0, 0, 0);
  const deliveredToday = myOrders.filter(
    (o) =>
      o.status === "delivered" &&
      o.delivered_at != null &&
      new Date(o.delivered_at) >= todayStart
  );
  const completedTodayCount = deliveredToday.length;
  const cashCollectedToday = deliveredToday
    .filter((o) => o.payment_method === "cash")
    .reduce((sum, o) => sum + Number(o.total), 0);

  const activeOrders = myOrders.filter(
    (o) => ["confirmed", "ready", "out_for_delivery"].includes(o.status)
  );
  const completedOrders = myOrders.filter((o) =>
    ["delivered", "cancelled"].includes(o.status)
  );

  const statusColor = (status: string) => {
    const map: Record<string, string> = {
      confirmed: "bg-blue-100 text-blue-800",
      ready: "bg-yellow-100 text-yellow-800",
      out_for_delivery: "bg-orange-100 text-orange-800",
      delivered: "bg-green-100 text-green-800",
      cancelled: "bg-red-100 text-red-800",
    };
    return map[status] || "bg-muted text-muted-foreground";
  };

  const renderOrderCard = (order: OrderRow, showActions = true) => (
    <motion.div
      key={order.id}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <Card className="hover:shadow-md transition-shadow">
        <CardContent className="p-4 space-y-3">
          {/* Header row */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs text-muted-foreground">
                #{order.id.slice(0, 8)}
              </span>
              <span
                className={`px-2 py-0.5 rounded-full text-xs font-semibold capitalize ${statusColor(order.status)}`}
              >
                {order.status.replace(/_/g, " ")}
              </span>
            </div>
            <span className="font-bold text-primary">
              Rs. {Number(order.total).toLocaleString()}
            </span>
          </div>

          {/* Customer info */}
          <div className="space-y-1 text-sm">
            <div className="flex items-center gap-2">
              <User className="w-3.5 h-3.5 text-muted-foreground" />
              <span className="font-medium">{order.customer_name || "Customer"}</span>
            </div>
            {order.customer_phone && (
              <div className="flex items-center gap-2">
                <Phone className="w-3.5 h-3.5 text-muted-foreground" />
                <a
                  href={`tel:${order.customer_phone}`}
                  className="text-primary hover:underline"
                >
                  {order.customer_phone}
                </a>
              </div>
            )}
            {order.customer_address && (
              <div className="flex items-center gap-2">
                <MapPin className="w-3.5 h-3.5 text-muted-foreground" />
                <span className="text-muted-foreground">{order.customer_address}</span>
              </div>
            )}
          </div>

          {/* Action buttons */}
          {showActions && (
            <div className="flex flex-wrap gap-2 pt-1">
              <Button
                variant="outline"
                size="sm"
                onClick={() => viewDetails(order)}
                className="gap-1"
              >
                <ClipboardList className="w-3.5 h-3.5" /> View Items
              </Button>

              {/* Call button */}
              {order.customer_phone && (
                <a href={`tel:${order.customer_phone}`}>
                  <Button variant="outline" size="sm" className="gap-1">
                    <Phone className="w-3.5 h-3.5" /> Call
                  </Button>
                </a>
              )}

              {/* Google Maps navigation */}
              {order.customer_address && (
                <a
                  href={`https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(order.customer_address)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Button variant="outline" size="sm" className="gap-1">
                    <Navigation className="w-3.5 h-3.5" /> Navigate
                  </Button>
                </a>
              )}

              {/* Status flow */}
              {(order.status === "confirmed" || order.status === "ready") && (
                <Button
                  size="sm"
                  onClick={() => confirmPickup(order.id)}
                  className="gap-1"
                >
                  <Navigation className="w-3.5 h-3.5" /> Confirm Pickup
                </Button>
              )}
              {order.status === "out_for_delivery" && (
                <Button
                  size="sm"
                  onClick={() => markDelivered(order.id)}
                  className="gap-1 bg-green-600 hover:bg-green-700"
                >
                  <CheckCircle className="w-3.5 h-3.5" /> Mark Delivered
                </Button>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );

  return (
    <RiderLayout title="My Orders">
      <div className="space-y-6">
        <h1 className="text-2xl font-heading font-bold text-foreground">
          My Deliveries
        </h1>

        {/* Daily stats bar */}
        <div className="grid grid-cols-2 gap-3">
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="p-2 rounded-full bg-green-100">
                <CheckCircle className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Completed Today</p>
                <p className="text-2xl font-bold text-green-600">
                  {completedTodayCount}
                </p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="p-2 rounded-full bg-blue-100">
                <Banknote className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Cash Collected Today</p>
                <p className="text-2xl font-bold text-blue-600">
                  Rs. {cashCollectedToday.toLocaleString()}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 flex-wrap">
          <Button
            variant={tab === "active" ? "default" : "outline"}
            onClick={() => setTab("active")}
            className="gap-2"
          >
            <Package className="w-4 h-4" /> Active ({activeOrders.length})
          </Button>
          <Button
            variant={tab === "available" ? "default" : "outline"}
            onClick={() => setTab("available")}
            className="gap-2"
          >
            <MapPin className="w-4 h-4" /> Available ({availableOrders.length})
          </Button>
          <Button
            variant={tab === "completed" ? "default" : "outline"}
            onClick={() => setTab("completed")}
            className="gap-2"
          >
            <CheckCircle className="w-4 h-4" /> Completed ({completedOrders.length})
          </Button>
        </div>

        {loading ? (
          <p className="text-center py-12 text-muted-foreground">Loading...</p>
        ) : (
          <>
            {/* Active orders */}
            {tab === "active" && (
              <div className="space-y-3">
                {activeOrders.length === 0 ? (
                  <p className="text-center py-12 text-muted-foreground">
                    No active deliveries.
                  </p>
                ) : (
                  activeOrders.map((order) => renderOrderCard(order, true))
                )}
              </div>
            )}

            {/* Available orders */}
            {tab === "available" && (
              <div className="space-y-3">
                {availableOrders.length === 0 ? (
                  <p className="text-center py-12 text-muted-foreground">
                    No available orders right now.
                  </p>
                ) : (
                  availableOrders.map((order) => (
                    <motion.div
                      key={order.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                    >
                      <Card className="hover:shadow-md transition-shadow border-dashed">
                        <CardContent className="p-4 space-y-3">
                          <div className="flex items-center justify-between">
                            <span className="font-mono text-xs text-muted-foreground">
                              #{order.id.slice(0, 8)}
                            </span>
                            <span className="font-bold text-primary">
                              Rs. {Number(order.total).toLocaleString()}
                            </span>
                          </div>
                          {order.customer_address && (
                            <div className="flex items-center gap-2 text-sm">
                              <MapPin className="w-3.5 h-3.5 text-muted-foreground" />
                              <span className="text-muted-foreground">
                                {order.customer_address}
                              </span>
                            </div>
                          )}
                          <Button
                            size="sm"
                            className="w-full"
                            onClick={() => acceptOrder(order.id)}
                          >
                            Accept Order
                          </Button>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))
                )}
              </div>
            )}

            {/* Completed orders */}
            {tab === "completed" && (
              <div className="space-y-3">
                {completedOrders.length === 0 ? (
                  <p className="text-center py-12 text-muted-foreground">
                    No completed deliveries yet.
                  </p>
                ) : (
                  completedOrders.map((order) => renderOrderCard(order, false))
                )}
              </div>
            )}
          </>
        )}

        {/* Order items dialog */}
        <Dialog open={!!detailOrder} onOpenChange={() => setDetailOrder(null)}>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Order Items</DialogTitle>
            </DialogHeader>
            {itemsLoading ? (
              <p className="text-muted-foreground text-sm py-4">Loading...</p>
            ) : orderItems.length === 0 ? (
              <p className="text-muted-foreground text-sm py-4">No items.</p>
            ) : (
              <div className="space-y-2">
                {orderItems.map((item) => (
                  <div
                    key={item.id}
                    className="flex justify-between text-sm bg-muted/20 rounded-lg p-3"
                  >
                    <span>
                      {item.title} × {item.quantity}
                    </span>
                    <span className="font-semibold">
                      Rs. {(Number(item.price) * item.quantity).toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </RiderLayout>
  );
};

export default RiderOrders;
