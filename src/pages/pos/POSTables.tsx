import { useCallback, useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";
import POSLayout from "@/components/pos/POSLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Switch } from "@/components/ui/switch";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Plus, Trash2, Pencil, LayoutGrid, RefreshCw, Settings2 } from "lucide-react";

interface PosTable {
  id: string;
  table_no: number;
  name: string;
  seats: number;
  area: string;
  reserved: boolean;
  active: boolean;
}

interface DineInOrder {
  id: string;
  table_no: number;
  items: { title: string; quantity: number; price: number }[];
  total: number;
  status: string;
  created_at: string;
}

const empty = { table_no: "", name: "", seats: "4", area: "Main hall" };

export default function POSTables() {
  const { toast } = useToast();
  const [rows, setRows] = useState<PosTable[]>([]);
  const [loading, setLoading] = useState(true);
  // CRUD dialog
  const [crudOpen, setCrudOpen] = useState(false);
  const [manageOpen, setManageOpen] = useState(false);
  const [editing, setEditing] = useState<PosTable | null>(null);
  const [form, setForm] = useState(empty);
  const [saving, setSaving] = useState(false);
  // Active order dialog
  const [activeTable, setActiveTable] = useState<PosTable | null>(null);
  const [activeOrder, setActiveOrder] = useState<DineInOrder | null>(null);
  const [orderLoading, setOrderLoading] = useState(false);
  const [settling, setSettling] = useState(false);

  const load = useCallback(async () => {
    const { data, error } = await supabase.from("pos_tables" as any).select("*").order("table_no");
    if (error) toast({ title: "Load failed", description: error.message, variant: "destructive" });
    setRows((data as unknown as PosTable[]) || []);
    setLoading(false);
  }, [toast]);

  useEffect(() => {
    load();
    const ch = supabase
      .channel("pos-tables-rt")
      .on("postgres_changes", { event: "*", schema: "public", table: "pos_tables" }, () => load())
      .subscribe();
    return () => { supabase.removeChannel(ch); };
  }, [load]);

  const openTableOrder = async (t: PosTable) => {
    if (!t.reserved) return; // only occupied tables have orders to show
    setActiveTable(t);
    setActiveOrder(null);
    setOrderLoading(true);
    const { data, error } = await (supabase as any)
      .from("dine_in_orders")
      .select("*")
      .eq("table_no", t.table_no)
      .in("status", ["pending", "accepted", "preparing", "ready", "served"])
      .order("created_at", { ascending: false })
      .limit(1);
    setOrderLoading(false);
    if (error) {
      toast({ title: "Order load failed", description: error.message, variant: "destructive" });
      return;
    }
    setActiveOrder((data?.[0] as DineInOrder) ?? null);
  };

  const settle = async () => {
    if (!activeOrder || !activeTable) return;
    setSettling(true);
    const { error: e1 } = await (supabase as any)
      .from("dine_in_orders")
      .update({ status: "completed" })
      .eq("id", activeOrder.id);
    const { error: e2 } = await (supabase as any)
      .from("pos_tables")
      .update({ reserved: false })
      .eq("id", activeTable.id);
    setSettling(false);
    if (e1 || e2) {
      toast({ title: "Settle failed", description: (e1 || e2)!.message, variant: "destructive" });
      return;
    }
    toast({ title: `Table ${activeTable.table_no} freed` });
    setActiveTable(null);
    setActiveOrder(null);
    load();
  };

  // CRUD
  const startAdd = () => {
    setEditing(null);
    setForm({ ...empty, table_no: String((rows.at(-1)?.table_no || 0) + 1) });
    setCrudOpen(true);
  };

  const startEdit = (t: PosTable) => {
    setEditing(t);
    setForm({ table_no: String(t.table_no), name: t.name, seats: String(t.seats), area: t.area });
    setCrudOpen(true);
  };

  const save = async () => {
    if (!form.table_no.trim() || !form.name.trim()) {
      toast({ title: "Table number and name are required", variant: "destructive" });
      return;
    }
    setSaving(true);
    const payload = {
      table_no: Number(form.table_no),
      name: form.name.trim(),
      seats: Number(form.seats) || 2,
      area: form.area.trim() || "Main hall",
    };
    const { error } = editing
      ? await supabase.from("pos_tables" as any).update(payload as never).eq("id", editing.id)
      : await supabase.from("pos_tables" as any).insert(payload as never);
    setSaving(false);
    if (error) {
      toast({ title: "Save failed", description: error.message, variant: "destructive" });
      return;
    }
    setCrudOpen(false);
    toast({ title: editing ? "Table updated" : "Table added" });
    load();
  };

  const toggle = async (t: PosTable, field: "reserved" | "active") => {
    const { error } = await supabase
      .from("pos_tables" as any)
      .update({ [field]: !t[field] } as never)
      .eq("id", t.id);
    if (error) {
      toast({ title: "Update failed", description: error.message, variant: "destructive" });
      return;
    }
    setRows((prev) => prev.map((x) => (x.id === t.id ? { ...x, [field]: !t[field] } : x)));
  };

  const remove = async (t: PosTable) => {
    const { error } = await supabase.from("pos_tables" as any).delete().eq("id", t.id);
    if (error) {
      toast({ title: "Delete failed", description: error.message, variant: "destructive" });
      return;
    }
    setRows((prev) => prev.filter((x) => x.id !== t.id));
    toast({ title: "Table removed" });
  };

  const tableCardClass = (t: PosTable) => {
    if (!t.active) return "bg-gray-50 border-gray-300 dark:bg-gray-900";
    if (t.reserved) return "bg-red-50 border-red-400 dark:bg-red-950 cursor-pointer";
    return "bg-green-50 border-green-400 dark:bg-green-950";
  };

  return (
    <POSLayout title="Dine in tables">
      <div className="space-y-4">
        {/* Toolbar */}
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <p className="text-sm text-muted-foreground">{rows.length} tables</p>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="gap-2" onClick={load}>
              <RefreshCw className="w-4 h-4" /> Refresh
            </Button>
            {/* Manage Tables dialog (CRUD) */}
            <Dialog open={manageOpen} onOpenChange={setManageOpen}>
              <DialogTrigger asChild>
                <Button variant="outline" size="sm" className="gap-2">
                  <Settings2 className="w-4 h-4" /> Manage Tables
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>Manage Tables</DialogTitle>
                </DialogHeader>
                <div className="space-y-3">
                  <Button className="gap-2" size="sm" onClick={startAdd}>
                    <Plus className="w-4 h-4" /> Add table
                  </Button>
                  {rows.map((t) => (
                    <Card key={t.id} className="p-3 flex items-center gap-3">
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-sm truncate">{t.name}</p>
                        <p className="text-xs text-muted-foreground">
                          #{t.table_no} · {t.seats} seats · {t.area}
                        </p>
                      </div>
                      <div className="flex items-center gap-2 text-xs shrink-0">
                        <span>Reserved</span>
                        <Switch checked={t.reserved} onCheckedChange={() => toggle(t, "reserved")} />
                        <span>Active</span>
                        <Switch checked={t.active} onCheckedChange={() => toggle(t, "active")} />
                      </div>
                      <Button size="sm" variant="outline" onClick={() => startEdit(t)}>
                        <Pencil className="w-3.5 h-3.5" />
                      </Button>
                      <Button size="sm" variant="ghost" onClick={() => remove(t)}>
                        <Trash2 className="w-3.5 h-3.5 text-destructive" />
                      </Button>
                    </Card>
                  ))}
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {/* Floor map grid */}
        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-3">
            {Array.from({ length: 10 }).map((_, i) => (
              <Skeleton key={i} className="h-32 rounded-xl" />
            ))}
          </div>
        ) : rows.length === 0 ? (
          <Card className="p-10 text-center text-muted-foreground">
            <LayoutGrid className="w-8 h-8 mx-auto mb-2" />
            No tables yet. Use "Manage Tables" to add tables.
          </Card>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-3">
            {rows.map((t) => (
              <Card
                key={t.id}
                className={`p-4 border-2 space-y-1 transition-all ${tableCardClass(t)}`}
                onClick={() => t.reserved ? openTableOrder(t) : undefined}
              >
                <div className="text-3xl font-black text-center">{t.table_no}</div>
                <div className="text-center text-sm font-medium truncate">{t.name}</div>
                <div className="text-center text-xs text-muted-foreground">{t.seats} seats · {t.area}</div>
                <div className="flex justify-center pt-1">
                  {!t.active ? (
                    <Badge variant="secondary">Inactive</Badge>
                  ) : t.reserved ? (
                    <Badge variant="destructive">Occupied</Badge>
                  ) : (
                    <Badge className="bg-green-600 hover:bg-green-700">Free</Badge>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Add / Edit table CRUD dialog */}
      <Dialog open={crudOpen} onOpenChange={setCrudOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{editing ? "Edit table" : "New table"}</DialogTitle>
          </DialogHeader>
          <div className="space-y-3">
            <div>
              <Label>Table number</Label>
              <Input
                inputMode="numeric"
                value={form.table_no}
                onChange={(e) => setForm({ ...form, table_no: e.target.value })}
              />
            </div>
            <div>
              <Label>Name</Label>
              <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label>Seats</Label>
                <Input
                  inputMode="numeric"
                  value={form.seats}
                  onChange={(e) => setForm({ ...form, seats: e.target.value })}
                />
              </div>
              <div>
                <Label>Area</Label>
                <Input value={form.area} onChange={(e) => setForm({ ...form, area: e.target.value })} />
              </div>
            </div>
            <Button className="w-full" disabled={saving} onClick={save}>
              {saving ? "Saving…" : "Save table"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Active order dialog */}
      <Dialog open={!!activeTable} onOpenChange={(o) => { if (!o) { setActiveTable(null); setActiveOrder(null); } }}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Table {activeTable?.table_no} — {activeTable?.name}</DialogTitle>
          </DialogHeader>
          {orderLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-6 w-full" />
              <Skeleton className="h-6 w-3/4" />
            </div>
          ) : activeOrder ? (
            <div className="space-y-4">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-muted-foreground border-b">
                    <th className="text-left pb-1">Item</th>
                    <th className="text-center pb-1">Qty</th>
                    <th className="text-right pb-1">Price</th>
                  </tr>
                </thead>
                <tbody>
                  {(activeOrder.items || []).map((it, idx) => (
                    <tr key={idx} className="border-b last:border-0">
                      <td className="py-1">{it.title}</td>
                      <td className="text-center">{it.quantity}</td>
                      <td className="text-right">Rs {Number(it.price) * it.quantity}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="flex justify-between font-bold text-base pt-1 border-t">
                <span>Total</span>
                <span>Rs {Number(activeOrder.total)}</span>
              </div>
              <div className="flex gap-2 pt-2">
                <Button variant="outline" className="flex-1" onClick={() => window.print()}>
                  Print Bill
                </Button>
                <Button className="flex-1" disabled={settling} onClick={settle}>
                  {settling ? "Settling…" : "Settle & Free Table"}
                </Button>
              </div>
            </div>
          ) : (
            <p className="text-muted-foreground text-sm">No active order found for this table.</p>
          )}
        </DialogContent>
      </Dialog>
    </POSLayout>
  );
}
