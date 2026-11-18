import { useCallback, useEffect, useMemo, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";
import POSLayout from "@/components/pos/POSLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Plus, Trash2, Wallet, Pencil } from "lucide-react";

interface Expense {
  id: string;
  title: string;
  amount: number;
  category: string;
  note: string | null;
  created_at: string;
}

const money = (n: number) => `Rs. ${Number(n || 0).toLocaleString()}`;
const isoDate = (d: Date) => d.toISOString().slice(0, 10);

const CATEGORIES = [
  "Raw Materials",
  "Utilities",
  "Staff",
  "Transport",
  "Maintenance",
  "Kitchen",
  "Other",
];

const emptyForm = { title: "", amount: "", category: "Kitchen", note: "" };

export default function POSExpenses() {
  const { toast } = useToast();
  const { user } = useAuth();
  const [rows, setRows] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [editId, setEditId] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [dateFilter, setDateFilter] = useState(isoDate(new Date()));
  const [yesterdayTotal, setYesterdayTotal] = useState(0);

  const load = useCallback(async () => {
    const { data, error } = await supabase
      .from("pos_expenses" as any)
      .select("*")
      .order("created_at", { ascending: false });
    if (error) toast({ title: "Load failed", description: error.message, variant: "destructive" });
    setRows((data as unknown as Expense[]) || []);
    setLoading(false);
  }, [toast]);

  // Fetch yesterday's total separately
  const loadYesterday = useCallback(async () => {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const start = `${isoDate(yesterday)}T00:00:00.000Z`;
    const end = `${isoDate(yesterday)}T23:59:59.999Z`;
    const { data } = await supabase
      .from("pos_expenses" as any)
      .select("amount")
      .gte("created_at", start)
      .lte("created_at", end);
    const total = ((data as any[]) || []).reduce((s: number, r: any) => s + Number(r.amount || 0), 0);
    setYesterdayTotal(total);
  }, []);

  useEffect(() => {
    load();
    loadYesterday();
  }, [load, loadYesterday]);

  const todayTotal = useMemo(() => {
    const today = new Date().toDateString();
    return rows
      .filter((r) => new Date(r.created_at).toDateString() === today)
      .reduce((s, r) => s + Number(r.amount), 0);
  }, [rows]);

  const monthTotal = useMemo(() => {
    const now = new Date();
    return rows
      .filter((r) => {
        const d = new Date(r.created_at);
        return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
      })
      .reduce((s, r) => s + Number(r.amount), 0);
  }, [rows]);

  // Filter displayed rows to the selected date
  const filteredRows = useMemo(() => {
    return rows.filter((r) => r.created_at.slice(0, 10) === dateFilter);
  }, [rows, dateFilter]);

  const openAddDialog = () => {
    setEditId(null);
    setForm(emptyForm);
    setOpen(true);
  };

  const openEditDialog = (expense: Expense) => {
    setEditId(expense.id);
    setForm({
      title: expense.title,
      amount: String(expense.amount),
      category: expense.category || "Kitchen",
      note: expense.note || "",
    });
    setOpen(true);
  };

  const save = async () => {
    if (!form.title.trim() || !form.amount.trim()) {
      toast({ title: "Title and amount are required", variant: "destructive" });
      return;
    }
    setSaving(true);

    if (editId) {
      // UPDATE existing
      const { error } = await supabase
        .from("pos_expenses" as any)
        .update({
          title: form.title.trim(),
          amount: Number(form.amount) || 0,
          category: form.category || "Other",
          note: form.note.trim() || null,
        } as never)
        .eq("id", editId);
      setSaving(false);
      if (error) {
        toast({ title: "Update failed", description: error.message, variant: "destructive" });
        return;
      }
      toast({ title: "Expense updated" });
    } else {
      // INSERT new
      const { error } = await supabase.from("pos_expenses" as any).insert({
        title: form.title.trim(),
        amount: Number(form.amount) || 0,
        category: form.category || "Other",
        note: form.note.trim() || null,
        created_by: user?.id ?? null,
      } as never);
      setSaving(false);
      if (error) {
        toast({ title: "Save failed", description: error.message, variant: "destructive" });
        return;
      }
      toast({ title: "Expense recorded" });
    }

    setForm(emptyForm);
    setEditId(null);
    setOpen(false);
    load();
    loadYesterday();
  };

  const remove = async (e: Expense) => {
    const { error } = await supabase.from("pos_expenses" as any).delete().eq("id", e.id);
    if (error) {
      toast({ title: "Delete failed", description: error.message, variant: "destructive" });
      return;
    }
    setRows((prev) => prev.filter((x) => x.id !== e.id));
  };

  return (
    <POSLayout title="Daily expenses">
      <div className="space-y-4">
        {/* Summary cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Card className="p-4">
            <p className="text-xs text-muted-foreground">Today</p>
            <p className="text-xl font-bold text-primary">{money(todayTotal)}</p>
          </Card>
          <Card className="p-4">
            <p className="text-xs text-muted-foreground">Yesterday</p>
            <p className="text-xl font-bold text-muted-foreground">{money(yesterdayTotal)}</p>
          </Card>
          <Card className="p-4">
            <p className="text-xs text-muted-foreground">This month</p>
            <p className="text-xl font-bold">{money(monthTotal)}</p>
          </Card>
          <Card className="p-4">
            <p className="text-xs text-muted-foreground">Filtered date total</p>
            <p className="text-xl font-bold">{money(filteredRows.reduce((s, r) => s + Number(r.amount), 0))}</p>
          </Card>
        </div>

        {/* Date filter + Add button */}
        <div className="flex flex-wrap items-end gap-2">
          <div>
            <Label className="text-xs">Filter by date</Label>
            <Input
              type="date"
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              className="w-44"
            />
          </div>
          <Dialog
            open={open}
            onOpenChange={(v) => {
              setOpen(v);
              if (!v) {
                setEditId(null);
                setForm(emptyForm);
              }
            }}
          >
            <DialogTrigger asChild>
              <Button className="gap-2" onClick={openAddDialog}>
                <Plus className="w-4 h-4" /> Add expense
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>{editId ? "Edit expense" : "New expense"}</DialogTitle>
              </DialogHeader>
              <div className="space-y-3">
                <div>
                  <Label>Title</Label>
                  <Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label>Amount (PKR)</Label>
                    <Input
                      inputMode="decimal"
                      value={form.amount}
                      onChange={(e) => setForm({ ...form, amount: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label>Category</Label>
                    <select
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                      value={form.category}
                      onChange={(e) => setForm({ ...form, category: e.target.value })}
                    >
                      {CATEGORIES.map((c) => (
                        <option key={c} value={c}>
                          {c}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <div>
                  <Label>Note</Label>
                  <Input value={form.note} onChange={(e) => setForm({ ...form, note: e.target.value })} />
                </div>
                <Button className="w-full" disabled={saving} onClick={save}>
                  {saving ? "Saving…" : editId ? "Update expense" : "Save expense"}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {loading ? (
          <div className="space-y-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-16 rounded-xl" />
            ))}
          </div>
        ) : filteredRows.length === 0 ? (
          <Card className="p-12 text-center text-muted-foreground">
            <Wallet className="w-8 h-8 mx-auto mb-2" />
            No expenses for {dateFilter}.
          </Card>
        ) : (
          <div className="space-y-2">
            {filteredRows.map((r) => (
              <Card key={r.id} className="p-4 flex items-center gap-3">
                <div className="min-w-0 flex-1">
                  <p className="font-medium truncate">{r.title}</p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(r.created_at).toLocaleString()} {r.note ? `· ${r.note}` : ""}
                  </p>
                </div>
                <Badge variant="secondary" className="shrink-0">
                  {r.category}
                </Badge>
                <p className="font-bold shrink-0">{money(Number(r.amount))}</p>
                <Button size="sm" variant="ghost" onClick={() => openEditDialog(r)}>
                  <Pencil className="w-4 h-4 text-muted-foreground" />
                </Button>
                <Button size="sm" variant="ghost" onClick={() => remove(r)}>
                  <Trash2 className="w-4 h-4 text-destructive" />
                </Button>
              </Card>
            ))}
          </div>
        )}
      </div>
    </POSLayout>
  );
}
