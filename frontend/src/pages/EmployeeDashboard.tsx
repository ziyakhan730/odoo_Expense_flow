import DashboardLayout from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { 
  LayoutDashboard, 
  Upload, 
  History, 
  User,
  Plus,
  DollarSign,
  Clock,
  CheckCircle2,
  XCircle
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

const navItems = [
  { label: "Dashboard", path: "/employee", icon: LayoutDashboard },
  { label: "Submit Expense", path: "/employee/submit", icon: Upload },
  { label: "History", path: "/employee/history", icon: History },
  { label: "Profile", path: "/employee/profile", icon: User },
];

const mockExpenses = [
  { id: 1, amount: 250, currency: "USD", category: "Travel", date: "2024-01-15", status: "approved", description: "Client meeting taxi" },
  { id: 2, amount: 1200, currency: "USD", category: "Hotel", date: "2024-01-14", status: "pending", description: "Conference accommodation" },
  { id: 3, amount: 85, currency: "USD", category: "Meals", date: "2024-01-13", status: "rejected", description: "Team lunch" },
  { id: 4, amount: 45, currency: "USD", category: "Office", date: "2024-01-12", status: "approved", description: "Office supplies" },
];

const EmployeeDashboard = () => {
  const [showSubmitForm, setShowSubmitForm] = useState(false);

  const handleSubmitExpense = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success("Expense submitted successfully!");
    setShowSubmitForm(false);
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      approved: "success" as const,
      rejected: "destructive" as const,
      pending: "warning" as const,
    };
    return <Badge variant={variants[status as keyof typeof variants]}>{status}</Badge>;
  };

  const stats = [
    { label: "Total Submitted", value: "$1,580", icon: DollarSign, color: "text-primary" },
    { label: "Pending", value: "$1,200", icon: Clock, color: "text-warning" },
    { label: "Approved", value: "$295", icon: CheckCircle2, color: "text-success" },
    { label: "Rejected", value: "$85", icon: XCircle, color: "text-destructive" },
  ];

  return (
    <DashboardLayout role="employee" navItems={navItems}>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Employee Dashboard</h1>
            <p className="text-muted-foreground">Manage your expense claims</p>
          </div>
          <Button onClick={() => setShowSubmitForm(true)} size="lg">
            <Plus className="mr-2 h-4 w-4" />
            Submit Expense
          </Button>
        </div>

        {/* Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <Card key={stat.label}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">{stat.label}</CardTitle>
                  <Icon className={cn("h-4 w-4", stat.color)} />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stat.value}</div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Submit Form */}
        {showSubmitForm && (
          <Card className="border-2 border-primary">
            <CardHeader>
              <CardTitle>Submit New Expense</CardTitle>
              <CardDescription>Fill in the details and upload your receipt</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmitExpense} className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="amount">Amount</Label>
                    <Input id="amount" type="number" placeholder="0.00" required />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="currency">Currency</Label>
                    <Select defaultValue="usd" required>
                      <SelectTrigger id="currency">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="usd">USD - US Dollar</SelectItem>
                        <SelectItem value="eur">EUR - Euro</SelectItem>
                        <SelectItem value="gbp">GBP - British Pound</SelectItem>
                        <SelectItem value="jpy">JPY - Japanese Yen</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="category">Category</Label>
                    <Select required>
                      <SelectTrigger id="category">
                        <SelectValue placeholder="Select category" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="travel">Travel</SelectItem>
                        <SelectItem value="meals">Meals</SelectItem>
                        <SelectItem value="hotel">Hotel</SelectItem>
                        <SelectItem value="office">Office Supplies</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="date">Date</Label>
                    <Input id="date" type="date" required />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea id="description" placeholder="Brief description of the expense" required />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="receipt">Receipt Upload (OCR enabled)</Label>
                  <Input id="receipt" type="file" accept="image/*" />
                  <p className="text-xs text-muted-foreground">
                    Upload a photo of your receipt. Our AI will auto-fill the details.
                  </p>
                </div>

                <div className="flex gap-2">
                  <Button type="submit" className="flex-1">Submit Expense</Button>
                  <Button type="button" variant="outline" onClick={() => setShowSubmitForm(false)}>
                    Cancel
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Expense History */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Expenses</CardTitle>
            <CardDescription>Your latest expense submissions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockExpenses.map((expense) => (
                <div
                  key={expense.id}
                  className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-accent/50 transition-colors"
                >
                  <div className="space-y-1">
                    <p className="font-medium">{expense.description}</p>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <span>{expense.category}</span>
                      <span>•</span>
                      <span>{expense.date}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="font-bold">
                        {expense.amount} {expense.currency}
                      </p>
                    </div>
                    {getStatusBadge(expense.status)}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default EmployeeDashboard;
