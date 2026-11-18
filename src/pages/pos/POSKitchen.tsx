import { useCallback, useEffect, useRef, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";
import POSLayout from "@/components/pos/POSLayout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { ChefHat } from "lucide-react";

interface KitchenOrder {
  id: string;
  status: string;
  created_at: string;
  customer_name: string | null;
  order_type: string;
  table_no: string | null;
  notes: string | null;
  order_items: { id: string; title: string; quantity: number }[];
}

const FLOW: Record<string, { next: string | null; label: string }> = {
  pending: { next: "preparing", label: "Start cooking" },
  confirmed: { next: "preparing", label: "Start cooking" },
  preparing: { next: "ready", label: "Mark ready" },
  ready: { next: "completed", label: "Hand over" },
};

const elapsed = (iso: string) => {
  const secs = Math.max(0, Math.floor((Date.now() - new Date(iso).getTime()) / 1000));
  const m = Math.floor(secs / 60).toString().padStart(2, "0");
  const s = (secs % 60).toString().padStart(2, "0");
  return { display: `${m}:${s}`, secs };
};

const timerColor = (secs: number) => {
  if (secs < 300) return "text-green-400";
  if (secs < 600) return "text-yellow-400";
  return "text-red-400";
};

export default function POSKitchen() {
  const { toast } = useToast();
  const [orders, setOrders] = useState<KitchenOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [tick, setTick] = useState(0);
  const prevCountRef = useRef(0);

  // Tick every second for elapsed timers
  useEffect(() => {
    const id = setInterval(() => setTick((t) => t + 1), 1000);
    return () => clearInterval(id);
  }, []);

  // Audio alert when new orders arrive
  useEffect(() => {
    if (orders.length > prevCountRef.current && prevCountRef.current !== 0) {
      try {
        const ctx = new AudioContext();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain); gain.connect(ctx.destination);
        osc.frequency.value = 880;
        gain.gain.setValueAtTime(0.3, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.5);
        osc.start(ctx.currentTime); osc.stop(ctx.currentTime + 0.5);
      } catch {
        // AudioContext may be blocked; silently ignore
      }
    }
    prevCountRef.current = orders.length;
  }, [orders.length]);

  const load = useCallback(async () => {
    const { data, error } = await supabase
      .from("orders")
      .select("id,status,created_at,customer_name,order_type,table_no,notes,order_items(id,title,quantity)")
      .in("status", ["pending", "confirmed", "preparing", "ready"])
      .order("created_at", { ascending: true });
    if (error) toast({ title: "Load failed", description: error.message, variant: "destructive" });
    setOrders((data as unknown as KitchenOrder[]) || []);
    setLoading(false);
  }, [toast]);

  useEffect(() => {
    load();
    const channel = supabase
      .channel("kitchen-orders")
      .on("postgres_changes", { event: "*", schema: "public", table: "orders" }, () => load())
      .subscribe();
    return () => { supabase.removeChannel(channel); };
  }, [load]);

  const advance = async (o: KitchenOrder) => {
    const next = FLOW[o.status]?.next;
    if (!next) return;
    const { error } = await supabase.from("orders").update({ status: next } as never).eq("id", o.id);
    if (error) {
      toast({ title: "Update failed", description: error.message, variant: "destructive" });
      return;
    }
    toast({ title: `Order moved to ${next}` });
    load();
  };

  // tick is consumed here to force re-render every second for timers
  void tick;

  return (
    <POSLayout title="Kitchen display">
      <div className="min-h-screen bg-gray-950 text-white -m-6 p-6">
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-48 rounded-xl bg-gray-800" />
            ))}
          </div>
        ) : orders.length === 0 ? (
          <Card className="p-12 text-center bg-gray-900 border-gray-700 text-gray-400">
            <ChefHat className="w-10 h-10 mx-auto mb-3 text-gray-600" />
            No live orders in the kitchen right now.
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {orders.map((o) => {
              const { display, secs } = elapsed(o.created_at);
              return (
                <Card key={o.id} className="p-5 bg-gray-900 border-gray-700 text-white space-y-4">
                  {/* Header: table / order type + badge */}
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      {o.order_type === "dine_in" ? (
                        <p className="text-2xl font-black text-yellow-400">Table {o.table_no}</p>
                      ) : (
                        <Badge className="text-sm capitalize bg-blue-700 text-white">{o.order_type?.replace("_", " ")}</Badge>
                      )}
                      <p className="text-xs text-gray-400 mt-1 truncate">
                        {o.customer_name || "Walk-in"} · #{o.id.slice(0, 8)}
                      </p>
                    </div>
                    <Badge
                      className={`shrink-0 ${o.status === "ready" ? "bg-green-700" : "bg-gray-700"} text-white`}
                    >
                      {o.status}
                    </Badge>
                  </div>

                  {/* Items */}
                  <ul className="space-y-1">
                    {o.order_items?.map((it) => (
                      <li key={it.id} className="text-xl font-bold">
                        ×{it.quantity} {it.title}
                      </li>
                    ))}
                  </ul>

                  {o.notes && (
                    <p className="text-sm italic text-gray-300 border-l-2 border-yellow-500 pl-2">
                      {o.notes}
                    </p>
                  )}

                  {/* Footer: timer + action */}
                  <div className="flex items-center justify-between gap-2 pt-1 border-t border-gray-700">
                    <span className={`text-lg font-mono font-bold ${timerColor(secs)}`}>
                      ⏱ {display}
                    </span>
                    {FLOW[o.status]?.next && (
                      <Button
                        size="sm"
                        className="bg-primary hover:bg-primary/90 text-white"
                        onClick={() => advance(o)}
                      >
                        {FLOW[o.status].label}
                      </Button>
                    )}
                  </div>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </POSLayout>
  );
}
