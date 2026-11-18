import { useEffect, useMemo, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import POSLayout from "@/components/pos/POSLayout";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Table2, TrendingUp, Receipt, Wallet, CreditCard } from "lucide-react";
import { downloadCsv } from "@/lib/receipt";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip as PieTooltip,
  Legend,
} from "recharts";

interface Row {
  id: string;
  created_at: string;
  total: number;
  status: string;
  source: string | null;
  payment_method: string | null;
  order_type: string | null;
  customer_name: string | null;
}

interface ItemRow {
  title: string;
  quantity: number;
}

const money = (n: number) => `Rs. ${Number(n || 0).toLocaleString()}`;
const iso = (d: Date) => d.toISOString().slice(0, 10);

const PIE_COLORS = ["#22c55e", "#3b82f6", "#f59e0b", "#8b5cf6"];

export default function POSReports() {
  const [rows, setRows] = useState<Row[]>([]);
  const [itemData, setItemData] = useState<ItemRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [from, setFrom] = useState(iso(new Date()));
  const [to, setTo] = useState(iso(new Date()));

  useEffect(() => {
    const load = async () => {
      setLoading(true);

      const { data } = await supabase
        .from("orders")
        .select("id,created_at,total,status,source,payment_method,order_type,customer_name")
        .gte("created_at", `${from}T00:00:00.000Z`)
        .lte("created_at", `${to}T23:59:59.999Z`)
        .order("created_at", { ascending: false });

      const fetchedRows = (data as unknown as Row[]) || [];
      setRows(fetchedRows);

      // Fetch order items for top-10 table
      if (fetchedRows.length > 0) {
        const ids = fetchedRows.map((r) => r.id);
        const { data: items } = await supabase
          .from("order_items")
          .select("title,quantity")
          .in("order_id", ids);
        setItemData((items as unknown as ItemRow[]) || []);
      } else {
        setItemData([]);
      }

      setLoading(false);
    };
    load();
  }, [from, to]);

  // Quick date range helpers
  const setToday = () => {
    const today = iso(new Date());
    setFrom(today);
    setTo(today);
  };
  const setThisWeek = () => {
    setFrom(iso(new Date(Date.now() - 6 * 864e5)));
    setTo(iso(new Date()));
  };
  const setThisMonth = () => {
    setFrom(iso(new Date(Date.now() - 29 * 864e5)));
    setTo(iso(new Date()));
  };

  const stats = useMemo(() => {
    const valid = rows.filter((r) => r.status !== "cancelled");
    const revenue = valid.reduce((s, r) => s + Number(r.total), 0);
    const byKey = (fn: (r: Row) => string) =>
      valid.reduce<Record<string, { count: number; total: number }>>((acc, r) => {
        const k = fn(r) || "unknown";
        acc[k] ||= { count: 0, total: 0 };
        acc[k].count += 1;
        acc[k].total += Number(r.total);
        return acc;
      }, {});
    const byPayment = byKey((r) => r.payment_method || "cod");
    const byType = byKey((r) => r.order_type || "delivery");

    // Top payment method by order count
    let topPaymentMethod = "—";
    let topCount = 0;
    Object.entries(byPayment).forEach(([k, v]) => {
      if (v.count > topCount) {
        topCount = v.count;
        topPaymentMethod = k;
      }
    });

    const daily = byKey((r) => new Date(r.created_at).toLocaleDateString());
    return {
      revenue,
      count: valid.length,
      avg: valid.length ? revenue / valid.length : 0,
      cancelled: rows.length - valid.length,
      byPayment,
      byType,
      topPaymentMethod,
      daily: Object.entries(daily).slice(0, 14),
      maxDaily: Math.max(1, ...Object.values(daily).map((d) => d.total)),
    };
  }, [rows]);

  // Hourly sales data (only meaningful for single-day range)
  const isSingleDay = from === to;
  const hourlyData = useMemo(() => {
    if (!isSingleDay) return [];
    const valid = rows.filter((r) => r.status !== "cancelled");
    return Array.from({ length: 24 }, (_, h) => ({
      hour: `${h}:00`,
      sales: valid
        .filter((r) => new Date(r.created_at).getHours() === h)
        .reduce((s, r) => s + Number(r.total), 0),
    }));
  }, [rows, isSingleDay]);

  // Pie chart data for order types
  const pieData = useMemo(() => {
    return Object.entries(stats.byType).map(([name, v]) => ({
      name: name.replace(/_/g, " "),
      value: v.count,
    }));
  }, [stats.byType]);

  // Top 10 items by quantity sold
  const top10Items = useMemo(() => {
    const grouped: Record<string, number> = {};
    itemData.forEach((item) => {
      if (!item.title) return;
      grouped[item.title] = (grouped[item.title] || 0) + Number(item.quantity || 1);
    });
    return Object.entries(grouped)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10);
  }, [itemData]);

  const exportCsv = () =>
    downloadCsv(
      `sales-${from}_to_${to}.csv`,
      rows.map((r) => ({
        id: r.id,
        date: new Date(r.created_at).toLocaleString(),
        customer: r.customer_name || "",
        source: r.source || "web",
        type: r.order_type || "delivery",
        payment: r.payment_method || "cod",
        status: r.status,
        total: r.total,
      }))
    );

  const Breakdown = ({
    title,
    data,
  }: {
    title: string;
    data: Record<string, { count: number; total: number }>;
  }) => (
    <Card className="p-4">
      <h3 className="font-heading font-bold text-sm mb-3">{title}</h3>
      <div className="space-y-2">
        {Object.keys(data).length === 0 && (
          <p className="text-xs text-muted-foreground">No data</p>
        )}
        {Object.entries(data).map(([k, v]) => (
          <div key={k} className="flex justify-between text-sm">
            <span className="capitalize text-muted-foreground">
              {k.replace(/_/g, " ")} ({v.count})
            </span>
            <span className="font-semibold">{money(v.total)}</span>
          </div>
        ))}
      </div>
    </Card>
  );

  return (
    <POSLayout title="Sales Reports">
      <div className="space-y-4">
        {/* Date range controls */}
        <div className="flex flex-wrap items-end gap-2">
          <div>
            <Label className="text-xs">From</Label>
            <Input type="date" value={from} onChange={(e) => setFrom(e.target.value)} />
          </div>
          <div>
            <Label className="text-xs">To</Label>
            <Input type="date" value={to} onChange={(e) => setTo(e.target.value)} />
          </div>
          <Button variant="outline" size="sm" onClick={setToday}>Today</Button>
          <Button variant="outline" size="sm" onClick={setThisWeek}>This Week</Button>
          <Button variant="outline" size="sm" onClick={setThisMonth}>This Month</Button>
          <Button variant="outline" className="gap-2" onClick={exportCsv}>
            <Table2 className="w-4 h-4" /> Export CSV
          </Button>
        </div>

        {loading ? (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-24 rounded-xl" />
            ))}
          </div>
        ) : (
          <>
            {/* Summary cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
              {[
                { label: "Revenue", value: money(stats.revenue), icon: TrendingUp },
                { label: "Orders", value: String(stats.count), icon: Receipt },
                { label: "Avg. order", value: money(Math.round(stats.avg)), icon: Wallet },
                {
                  label: "Top payment",
                  value: stats.topPaymentMethod.replace(/_/g, " "),
                  icon: CreditCard,
                },
              ].map((s) => (
                <Card key={s.label} className="p-4">
                  <div className="flex items-center gap-2 text-muted-foreground text-xs">
                    <s.icon className="w-4 h-4" /> {s.label}
                  </div>
                  <p className="text-xl font-bold mt-1 capitalize">{s.value}</p>
                </Card>
              ))}
            </div>

            {/* Hourly bar chart — single day only */}
            {isSingleDay && (
              <Card className="p-4">
                <h3 className="font-heading font-bold text-sm mb-3">Hourly sales — {from}</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={hourlyData} margin={{ top: 0, right: 8, left: 0, bottom: 0 }}>
                    <XAxis
                      dataKey="hour"
                      tick={{ fontSize: 10 }}
                      interval={2}
                    />
                    <YAxis tick={{ fontSize: 10 }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                    <Tooltip formatter={(v: number) => money(v)} />
                    <Bar dataKey="sales" fill="#f97316" radius={[3, 3, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            )}

            {/* Daily mini bar chart */}
            <Card className="p-4">
              <h3 className="font-heading font-bold text-sm mb-3">Daily sales</h3>
              <div className="space-y-1.5">
                {stats.daily.length === 0 && (
                  <p className="text-xs text-muted-foreground">No sales in this range.</p>
                )}
                {stats.daily.map(([day, v]) => (
                  <div key={day} className="flex items-center gap-2 text-xs">
                    <span className="w-24 shrink-0 text-muted-foreground">{day}</span>
                    <div className="flex-1 h-3 rounded bg-muted overflow-hidden">
                      <div
                        className="h-full bg-primary"
                        style={{ width: `${(v.total / stats.maxDaily) * 100}%` }}
                      />
                    </div>
                    <span className="w-24 text-right font-semibold">{money(v.total)}</span>
                  </div>
                ))}
              </div>
            </Card>

            {/* Breakdown cards + pie chart */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <Breakdown title="By payment method" data={stats.byPayment} />
              <Card className="p-4">
                <h3 className="font-heading font-bold text-sm mb-3">Order type breakdown</h3>
                {pieData.length === 0 ? (
                  <p className="text-xs text-muted-foreground">No data</p>
                ) : (
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={70}
                        label={({ name, percent }) =>
                          `${name} ${(percent * 100).toFixed(0)}%`
                        }
                        labelLine={false}
                      >
                        {pieData.map((_, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={PIE_COLORS[index % PIE_COLORS.length]}
                          />
                        ))}
                      </Pie>
                      <PieTooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                )}
              </Card>
            </div>

            {/* Top 10 items table */}
            {top10Items.length > 0 && (
              <Card className="p-4">
                <h3 className="font-heading font-bold text-sm mb-3">Top 10 items sold</h3>
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-xs text-muted-foreground border-b">
                      <th className="pb-2 w-8">#</th>
                      <th className="pb-2">Item</th>
                      <th className="pb-2 text-right">Qty sold</th>
                    </tr>
                  </thead>
                  <tbody>
                    {top10Items.map(([name, qty], i) => (
                      <tr key={name} className="border-b last:border-0">
                        <td className="py-1.5 text-muted-foreground">{i + 1}</td>
                        <td className="py-1.5 font-medium">{name}</td>
                        <td className="py-1.5 text-right font-bold">{qty}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </Card>
            )}
          </>
        )}
      </div>
    </POSLayout>
  );
}
